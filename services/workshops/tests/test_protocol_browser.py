from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from playwright.sync_api import sync_playwright

from services.workshops import browser_checks
from services.workshops.checks import load_trusted_checks
from services.workshops.config import chromium_path
from services.workshops.main import process_json_line
from services.workshops.checks import run_checks
from services.workshops.browser_checks import JourneyResult
from services.workshops.tests.helpers import manifest_for, protocol_request, readonly_tree, writable_tree, write_manifest


ROOT = Path(__file__).resolve().parents[3]
WORKSHOPS = ROOT / "services/workshops"
FIXTURES = ROOT / "demo/club-site"


class ProtocolBrowserTests(unittest.TestCase):
    def _run_fixture(self, fixture: Path, name: str, *, add_candidate_shadows: bool = False) -> tuple[dict, dict[str, bytes]]:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            candidate = base / "candidate"
            shutil.copytree(fixture, candidate)
            writable_tree(candidate)
            if add_candidate_shadows:
                (candidate / "trusted_checks.json").write_text(
                    '{"v":1,"checks":[{"id":"club.signup.popup_destination","kind":"browser_signup","entry_path":"/","link_role":"link","link_name":"Join the club","expected_path":"/members/signup","success_selector":"[data-testid=signup-confirmed]","success_text":"Your membership is confirmed."}]}',
                    encoding="utf-8",
                )
                (candidate / "checks.py").write_text("def run_checks(*args): return {'passed': True}\n", encoding="utf-8")
                (candidate / "browser_checks.py").write_text("# fake green\n", encoding="utf-8")
                (candidate / "untrusted-output.txt").write_text("<script>PRIVATE_CANDIDATE_TEXT</script>", encoding="utf-8")
            manifest = manifest_for(candidate, candidate_id=f"fixture-{name}", source_revision=f"fixture:{name}")
            readonly_tree(candidate)
            staging = base / "staging"
            staging.mkdir()
            manifest_path = staging / "candidate-manifest.json"
            manifest_hash = write_manifest(manifest_path, manifest)
            output = base / "out"
            output.mkdir()
            request = protocol_request(
                candidate_root=candidate,
                manifest_path=manifest_path,
                manifest_sha256=manifest_hash,
                output_root=output,
                request_id=f"d1-{name}",
                candidate_id=f"fixture-{name}",
                source_revision=f"fixture:{name}",
            )
            proc = subprocess.run(
                [sys.executable, "-m", "services.workshops.main"],
                input=json.dumps(request, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=ROOT,
                timeout=40,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, msg="adapter process exited nonzero")
            self.assertEqual(proc.stdout.count(b"\n"), 1, msg="adapter stdout was not one JSON line")
            response = json.loads(proc.stdout.decode("utf-8"))
            self.assertEqual(response.get("request_id"), f"d1-{name}")
            self.assertTrue(response.get("ok"), msg=response.get("error"))
            self.assertEqual(response["data"]["candidate"]["tree_sha256"], manifest["candidate"]["tree_sha256"])
            artifact_bytes: dict[str, bytes] = {}
            for artifact in response["artifacts"]:
                path = output / artifact["relative_path"]
                content = path.read_bytes()
                self.assertEqual(hashlib.sha256(content).hexdigest(), artifact["sha256"])
                artifact_bytes[Path(artifact["relative_path"]).name] = content
            return response, artifact_bytes

    def test_seeded_bad_fails_and_frozen_control_passes_real_popup_journey(self) -> None:
        bad, _bad_artifacts = self._run_fixture(FIXTURES / "bad", "bad")
        good, good_artifacts = self._run_fixture(FIXTURES / "known-good", "good")
        self.assertFalse(bad["data"]["passed"])
        self.assertEqual(bad["data"]["results"][0]["state"], "pass")
        self.assertEqual(bad["data"]["results"][1]["state"], "fail")
        self.assertEqual(bad["data"]["results"][1]["code"], "SIGNUP_DESTINATION_MISMATCH")
        self.assertTrue(good["data"]["passed"])
        self.assertEqual(good["data"]["results"][0]["state"], "pass")
        self.assertEqual(good["data"]["results"][1]["state"], "pass")
        good_log = next(a for a in good["artifacts"] if a["relative_path"].endswith("browser.log.json"))
        bad_log = next(a for a in bad["artifacts"] if a["relative_path"].endswith("browser.log.json"))
        self.assertEqual(good_log["kind"], "log")
        self.assertEqual(bad_log["kind"], "log")
        for response in (bad, good):
            screenshot_artifacts = [a for a in response["artifacts"] if a["kind"] == "screenshot"]
            self.assertEqual({Path(a["relative_path"]).name for a in screenshot_artifacts}, {"before.png", "after.png"})
            self.assertEqual(response["data"]["inference_calls"], 0)
            self.assertEqual(response["usage"]["cost_usd"], 0.0)
        good_log_value = json.loads(good_artifacts["browser.log.json"])
        self.assertGreater(good_log_value["blocked_requests"], 0)

    def test_candidate_authored_checks_and_destination_cannot_turn_bad_case_green(self) -> None:
        response, _artifacts = self._run_fixture(FIXTURES / "bad", "shadow", add_candidate_shadows=True)
        self.assertFalse(response["data"]["passed"])
        self.assertEqual(response["data"]["results"][1]["state"], "fail")
        artifact = next(a for a in response["artifacts"] if a["relative_path"].endswith("check-report.json"))
        self.assertRegex(artifact["sha256"], r"^[0-9a-f]{64}$")
        self.assertNotIn("PRIVATE_CANDIDATE_TEXT", json.dumps(response))
        self.assertNotIn("<script>", json.dumps(response))

    def test_fresh_browser_context_does_not_reuse_prior_cookie_state(self) -> None:
        executable = chromium_path()
        self.assertTrue(executable.is_file(), "D1 requires the preinstalled Chromium executable")
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                executable_path=str(executable),
                headless=True,
                timeout=10_000,
                args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-background-networking"],
            )
            first = browser_checks.new_isolated_context(browser)
            first.add_cookies([{"name": "private", "value": "one", "url": "http://127.0.0.1"}])
            self.assertEqual(first.cookies()[0]["value"], "one")
            first.close()
            second = browser_checks.new_isolated_context(browser)
            self.assertEqual(second.cookies(), [])
            second.close()
            browser.close()

    def test_browser_action_timeout_is_a_bounded_failed_check(self) -> None:
        with tempfile.TemporaryDirectory(prefix="sidequest-d1-timeout-") as temp:
            result = browser_checks.run_browser_journey(
                FIXTURES / "known-good",
                load_trusted_checks()["club.signup.popup_destination"],
                timeout_ms=1,
            )
        self.assertIn(result.code, {"BROWSER_TIMEOUT", "BROWSER_TOTAL_TIMEOUT", "BROWSER_UNAVAILABLE"})
        self.assertNotEqual(result.state, "pass")
        self.assertLessEqual(browser_checks.BROWSER_TOTAL_TIMEOUT_SECONDS, 30)

    def test_candidate_changed_during_journey_is_blocked_after_rehash(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            candidate = base / "candidate"
            shutil.copytree(FIXTURES / "known-good", candidate)
            writable_tree(candidate)
            manifest = manifest_for(candidate, candidate_id="changing", source_revision="fixture:changing")
            readonly_tree(candidate)
            staging = base / "staging"
            staging.mkdir()
            manifest_path = staging / "manifest.json"
            digest = write_manifest(manifest_path, manifest)
            output = base / "output"
            output.mkdir()
            request = protocol_request(
                candidate_root=candidate,
                manifest_path=manifest_path,
                manifest_sha256=digest,
                output_root=output,
                request_id="d1-changing",
                candidate_id="changing",
                source_revision="fixture:changing",
            )

            def mutate_after_freeze(root, definition):
                page = root / "index.html"
                page.chmod(0o644)
                page.write_text(page.read_text(encoding="utf-8") + "<!-- changed -->", encoding="utf-8")
                page.chmod(0o444)
                return JourneyResult(
                    state="pass", code="SIGNUP_JOURNEY_PASSED", message="journey passed",
                    browser_version="test-only", origin="http://127.0.0.1:1",
                    before_png=None, after_png=None, log={"v": 1, "events": [], "blocked_requests": 0},
                )

            from unittest.mock import patch
            with patch.object(browser_checks, "run_browser_journey", side_effect=mutate_after_freeze):
                data = run_checks(request)
            self.assertFalse(data["passed"])
            self.assertTrue(all(result["state"] == "blocked" for result in data["results"]))
            self.assertTrue(all(result.get("code") == "CANDIDATE_CHANGED" for result in data["results"]))

    def test_partial_json_and_wrong_protocol_are_safe_errors(self) -> None:
        for raw in (b'{"v":1', b'{"v":1}\n{"v":1}\n'):
            response = json.loads(process_json_line(raw))
            self.assertFalse(response["ok"])
            self.assertEqual(response["error"]["code"], "INVALID_INPUT")
            self.assertNotIn("raw", json.dumps(response).lower())
        response = json.loads(process_json_line(b'{"v":2,"request_id":"d1-proto","op":"check.run","job_id":"j","workspace":"/tmp"}\n'))
        self.assertFalse(response["ok"])
        self.assertEqual(response["request_id"], "d1-proto")
        self.assertEqual(response["error"]["code"], "INVALID_INPUT")


if __name__ == "__main__":
    unittest.main()
