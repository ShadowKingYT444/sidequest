"""Isolated Chromium journeys against registered, local disposable fixtures."""

from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from playwright.sync_api import Browser, Error as PlaywrightError, TimeoutError as PlaywrightTimeoutError, sync_playwright

from .config import (
    BROWSER_TIMEOUT_MS,
    BROWSER_TOTAL_TIMEOUT_SECONDS,
    MAX_HTML_BYTES,
    MAX_BROWSER_REQUESTS,
    MAX_SCREENSHOT_BYTES,
    chromium_path,
)


class BrowserUnavailableError(RuntimeError):
    pass


class _JourneyDeadline(Exception):
    pass


@dataclass
class JourneyResult:
    state: str
    code: str
    message: str
    browser_version: str | None
    origin: str
    before_png: bytes | None
    after_png: bytes | None
    log: dict[str, Any]


class _FixtureHandler(BaseHTTPRequestHandler):
    server_version = "SidequestDisposableFixture/1"
    sys_version = ""

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        server = self.server
        fixture_root: Path = server.fixture_root  # type: ignore[attr-defined]
        route = urlsplit(self.path).path
        fixture_files = {
            "/": "index.html",
            "/members/welcome": "members/welcome.html",
            "/members/signup": "members/signup.html",
        }
        relative = fixture_files.get(route)
        if relative is None:
            self.send_error(404, "Not found")
            return
        target = fixture_root / relative
        try:
            info = target.lstat()
            if not target.is_file() or target.is_symlink() or info.st_size > MAX_HTML_BYTES:
                self.send_error(404, "Not found")
                return
            content = target.read_bytes()
        except OSError:
            self.send_error(404, "Not found")
            return
        if len(content) > MAX_HTML_BYTES:
            self.send_error(413, "Fixture too large")
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self' https:; img-src 'self' https: data:; script-src 'none'; object-src 'none'; base-uri 'none'; form-action 'self'",
        )
        self.end_headers()
        try:
            self.wfile.write(content)
        except (BrokenPipeError, ConnectionResetError):
            return

    def log_message(self, _format: str, *_args: Any) -> None:
        # Candidate URLs and strings are untrusted; keep them out of service logs.
        return


class _FixtureHTTPServer(ThreadingHTTPServer):
    def handle_error(self, _request, _client_address) -> None:
        # A bounded browser timeout may close its socket before a static response ends.
        return


class _FixtureServer:
    def __init__(self, fixture_root: Path):
        self._server = _FixtureHTTPServer(("127.0.0.1", 0), _FixtureHandler)
        self._server.daemon_threads = True
        self._server.fixture_root = fixture_root  # type: ignore[attr-defined]
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)

    @property
    def origin(self) -> str:
        host, port = self._server.server_address
        return f"http://{host}:{port}"

    def __enter__(self) -> "_FixtureServer":
        self._thread.start()
        return self

    def __exit__(self, *_args: Any) -> None:
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=2)


def new_isolated_context(browser: Browser):
    """Return a fresh context with no imported storage, permissions, or workers."""
    return browser.new_context(
        viewport={"width": 1280, "height": 800},
        device_scale_factor=1,
        service_workers="block",
        accept_downloads=False,
    )


def is_registered_origin(url: str, origin: str) -> bool:
    parsed = urlsplit(url)
    return f"{parsed.scheme}://{parsed.netloc}" == origin


def _safe_screenshot(page, *, timeout_ms: int = BROWSER_TIMEOUT_MS) -> bytes | None:
    try:
        image = page.screenshot(type="png", full_page=False, timeout=timeout_ms)
    except PlaywrightError:
        return None
    if not image.startswith(b"\x89PNG\r\n\x1a\n") or len(image) > MAX_SCREENSHOT_BYTES:
        return None
    return image


def run_browser_journey(
    fixture_root: Path,
    definition: dict[str, Any],
    *,
    timeout_ms: int = BROWSER_TIMEOUT_MS,
) -> JourneyResult:
    """Run the trusted signup check in a new browser context and registered origin."""
    events: list[dict[str, Any]] = []
    blocked_requests = 0
    outside_origin_blocked = 0
    request_cap_blocked = 0
    requests_seen = 0
    request_cap_exceeded = False
    origin = ""
    browser_version: str | None = None
    before_png: bytes | None = None
    after_png: bytes | None = None
    code = "BROWSER_ERROR"
    message = "The trusted browser journey could not be completed."
    state = "blocked"
    deadline = time.monotonic() + BROWSER_TOTAL_TIMEOUT_SECONDS

    def step_timeout() -> int:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise _JourneyDeadline
        return max(1, min(timeout_ms, BROWSER_TIMEOUT_MS, int(remaining * 1000)))

    def record(event: str, **details: Any) -> None:
        # Only fixed event names and trusted values are passed here.
        events.append({"event": event, **details})

    executable = chromium_path()
    if not executable.is_file() or not executable.stat().st_mode & 0o111:
        return JourneyResult(
            state="blocked",
            code="BROWSER_UNAVAILABLE",
            message="Configured Chromium executable is unavailable.",
            browser_version=None,
            origin="",
            before_png=None,
            after_png=None,
            log={
                "v": 1,
                "events": [{"event": "browser_unavailable"}],
                "blocked_requests": 0,
                "outside_origin_blocked": 0,
                "request_cap_blocked": 0,
                "requests_seen": 0,
                "request_cap_exceeded": False,
            },
        )

    try:
        with _FixtureServer(fixture_root) as fixture:
            origin = fixture.origin
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(
                    executable_path=str(executable),
                    headless=True,
                    timeout=min(BROWSER_TIMEOUT_MS * 2, int(max(0.001, deadline - time.monotonic()) * 1000)),
                    args=[
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-background-networking",
                        "--disable-component-update",
                        "--disable-default-apps",
                        "--no-first-run",
                        "--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE 127.0.0.1",
                    ],
                )
                browser_version = browser.version
                context = new_isolated_context(browser)

                def constrain_request(route) -> None:
                    nonlocal blocked_requests, outside_origin_blocked, request_cap_blocked, requests_seen, request_cap_exceeded
                    requests_seen += 1
                    if requests_seen > MAX_BROWSER_REQUESTS:
                        request_cap_exceeded = True
                        blocked_requests += 1
                        request_cap_blocked += 1
                        route.abort("blockedbyclient")
                    elif is_registered_origin(route.request.url, origin):
                        route.continue_()
                    else:
                        blocked_requests += 1
                        outside_origin_blocked += 1
                        route.abort("blockedbyclient")

                context.route("**/*", constrain_request)
                page = context.new_page()
                page.set_default_timeout(max(1, min(timeout_ms, BROWSER_TIMEOUT_MS)))
                record("browser_started", browser_version=browser_version)
                record("origin_registered", origin=origin)
                try:
                    page.goto(
                        f"{origin}{definition['entry_path']}",
                        wait_until="domcontentloaded",
                        timeout=step_timeout(),
                    )
                    page.wait_for_load_state("networkidle", timeout=step_timeout())
                    record("entry_loaded")
                    before_png = _safe_screenshot(page, timeout_ms=step_timeout())
                    if before_png is None:
                        code, message = "SCREENSHOT_FAILED", "The before screenshot could not be captured."
                    else:
                        link = page.get_by_role(definition["link_role"], name=definition["link_name"], exact=True)
                        count = link.count()
                        if count != 1:
                            state = "fail"
                            code = "SIGNUP_LINK_MISSING" if count == 0 else "SIGNUP_LINK_AMBIGUOUS"
                            message = "The trusted signup link was not uniquely available."
                            record(code.lower())
                        else:
                            popup = None
                            try:
                                with page.expect_popup(timeout=step_timeout()) as popup_info:
                                    link.click(timeout=step_timeout())
                                popup = popup_info.value
                                record("signup_popup_opened")
                            except PlaywrightTimeoutError:
                                state = "fail"
                                code = "SIGNUP_POPUP_MISSING"
                                message = "The signup action did not open its destination in a popup."
                                record("signup_popup_missing")
                            if popup is not None:
                                popup.set_default_timeout(step_timeout())
                                popup.wait_for_load_state(
                                    "domcontentloaded",
                                    timeout=step_timeout(),
                                )
                                dest = urlsplit(popup.url)
                                actual_origin = f"{dest.scheme}://{dest.netloc}"
                                if (
                                    actual_origin != origin
                                    or dest.path != definition["expected_path"]
                                    or dest.query
                                    or dest.fragment
                                ):
                                    state = "fail"
                                    code = "SIGNUP_DESTINATION_MISMATCH"
                                    message = "The signup popup reached a destination outside the trusted expectation."
                                    record("signup_destination_mismatch")
                                else:
                                    record("signup_destination_matched", path=definition["expected_path"])
                                    confirmation = popup.locator(definition["success_selector"])
                                    if confirmation.count() != 1 or not confirmation.is_visible():
                                        state = "fail"
                                        code = "SIGNUP_CONFIRMATION_MISSING"
                                        message = "The trusted signup destination did not show its confirmation."
                                        record("signup_confirmation_missing")
                                    else:
                                        text = " ".join(confirmation.inner_text().split())
                                        if text != definition["success_text"]:
                                            state = "fail"
                                            code = "SIGNUP_CONFIRMATION_MISMATCH"
                                            message = "The trusted signup destination showed an unexpected confirmation."
                                            record("signup_confirmation_mismatch")
                                        else:
                                            code = "SIGNUP_JOURNEY_PASSED"
                                            message = "The signup popup reached and confirmed the trusted destination."
                                            state = "pass"
                                            record("signup_confirmation_matched")
                                after_png = _safe_screenshot(popup, timeout_ms=step_timeout())
                                if after_png is None:
                                    state = "blocked"
                                    code = "SCREENSHOT_FAILED"
                                    message = "The after screenshot could not be captured."
                            else:
                                after_png = _safe_screenshot(page, timeout_ms=step_timeout())
                                if after_png is None:
                                    state = "blocked"
                                    code = "SCREENSHOT_FAILED"
                                    message = "The after screenshot could not be captured."
                except _JourneyDeadline:
                    code = "BROWSER_TOTAL_TIMEOUT"
                    message = "The trusted browser journey exceeded its total time limit."
                    record("browser_total_timeout")
                    try:
                        after_png = _safe_screenshot(page, timeout_ms=1)
                    except Exception:
                        after_png = None
                except PlaywrightTimeoutError:
                    code = "BROWSER_TIMEOUT"
                    message = "The trusted browser journey exceeded its time limit."
                    record("browser_timeout")
                    try:
                        after_png = _safe_screenshot(page, timeout_ms=step_timeout())
                    except (_JourneyDeadline, PlaywrightError):
                        after_png = None
                except PlaywrightError:
                    code = "BROWSER_PROTOCOL_ERROR"
                    message = "Chromium reported a browser protocol error during the journey."
                    record("browser_protocol_error")
                    try:
                        after_png = _safe_screenshot(page, timeout_ms=step_timeout())
                    except (_JourneyDeadline, PlaywrightError):
                        after_png = None
                finally:
                    context.close()
                    browser.close()
                if outside_origin_blocked:
                    record("outside_origin_requests_blocked", count=outside_origin_blocked)
                if request_cap_blocked:
                    record("browser_request_cap_blocked", count=request_cap_blocked)
                if request_cap_exceeded:
                    record("browser_request_cap_exceeded")
                if time.monotonic() > deadline:
                    state = "blocked"
                    code = "BROWSER_TOTAL_TIMEOUT"
                    message = "The trusted browser journey exceeded its total time limit."
                    record("browser_total_timeout")
    except PlaywrightError:
        state = "blocked"
        code = "BROWSER_UNAVAILABLE"
        message = "Chromium could not start the trusted browser journey."
        record("browser_unavailable")
    except OSError:
        state = "blocked"
        code = "FIXTURE_SERVER_ERROR"
        message = "The disposable fixture server could not be started."
        record("fixture_server_error")

    return JourneyResult(
        state=state,
        code=code,
        message=message,
        browser_version=browser_version,
        origin=origin,
        before_png=before_png,
        after_png=after_png,
        log={
            "v": 1,
            "events": events,
            "blocked_requests": blocked_requests,
            "outside_origin_blocked": outside_origin_blocked,
            "request_cap_blocked": request_cap_blocked,
            "requests_seen": min(requests_seen, MAX_BROWSER_REQUESTS + 1),
            "request_cap_exceeded": request_cap_exceeded,
        },
    )


def serialize_log(log: dict[str, Any]) -> bytes:
    return json.dumps(log, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
