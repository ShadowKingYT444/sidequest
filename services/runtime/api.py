"""Authenticated local computer API for the Sidequest runtime."""

from __future__ import annotations

import ast
import base64
import hashlib
import hmac
import json
import os
import re
from decimal import Decimal
from typing import Any, Callable

from fastapi import Depends, FastAPI, Query, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .adapters import AdapterRunner, _safe_message
from .artifacts import ArtifactStore, text_preview
from .config import RuntimeConfig
from .models import (
    CommandRequest,
    JobCreate,
    ProjectRegistration,
    canonical_json,
)
from .policy import ErrorCode, RuntimeFault
from .scheduler import Scheduler, is_local_git_inspection_from_stored
from .store import RuntimeStore

_MAX_PAGE_BYTES = 256 * 1024
_MAX_TEXT_LINE_BYTES = 256 * 1024
_MAX_MANIFEST_BYTES = 16 * 1024 * 1024
_MAX_MANIFEST_FILES = 100_000
_MAX_COMMAND_BYTES = 4 * 1024 * 1024
_LAYOUT_NODE_KINDS = {"lookout", "board", "workstation", "test_lab", "approval", "workshop"}
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:_-]{0,199}$")
_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_PUBLIC_RUN_TYPES = {"status", "tool_started", "tool_finished", "output", "warning", "usage"}


class _CommandBodyLimit:
    """Bound the mutation body, including chunked requests without Content-Length."""

    def __init__(self, app: Any):
        self.app = app

    async def __call__(self, scope: dict[str, Any], receive: Callable[..., Any], send: Callable[..., Any]) -> None:
        if scope.get("type") != "http" or scope.get("method") != "POST" or scope.get("path") != "/v1/commands":
            await self.app(scope, receive, send)
            return
        body: list[dict[str, Any]] = []
        size = 0
        while True:
            message = await receive()
            if message["type"] != "http.request":
                await self.app(scope, receive, send)
                return
            chunk = message.get("body", b"")
            size += len(chunk)
            if size > _MAX_COMMAND_BYTES:
                response = JSONResponse(_fault_body(ErrorCode.INVALID_INPUT, "request body exceeds 4 MiB"), status_code=400)
                await response(scope, receive, send)
                return
            body.append(message)
            if not message.get("more_body", False):
                break
        position = 0

        async def replay() -> dict[str, Any]:
            nonlocal position
            if position < len(body):
                message = body[position]
                position += 1
                return message
            return await receive()

        await self.app(scope, replay, send)


def _http_status(code: str) -> int:
    return {
        ErrorCode.INVALID_INPUT: 400,
        ErrorCode.NOT_FOUND: 404,
        ErrorCode.VERSION_CONFLICT: 409,
        ErrorCode.POLICY_DENIED: 403,
        ErrorCode.BUDGET_LIMIT: 429,
        ErrorCode.DEPENDENCY_FAILED: 424,
        ErrorCode.UNAVAILABLE: 503,
        ErrorCode.INTERNAL: 500,
    }.get(code, 500)


def _fault_body(code: str, message: str, retryable: bool = False) -> dict[str, Any]:
    return {"v": 1, "error": {"code": code, "message": message[:512], "retryable": retryable}}


def _serialized_json_size(value: Any) -> int:
    """Measure the exact compact UTF-8 JSON representation returned by JSONResponse."""
    return len(JSONResponse(content=value).body)


def _utf8_prefix(value: str, max_bytes: int) -> str:
    raw = value.encode("utf-8")[:max_bytes]
    while True:
        try:
            return raw.decode("utf-8", "strict")
        except UnicodeDecodeError:
            raw = raw[:-1]


def _json_error(status: int, code: str, message: str, retryable: bool = False) -> JSONResponse:
    return JSONResponse(_fault_body(code, message, retryable), status_code=status)


def _usd(micro: int | None) -> float | None:
    return None if micro is None else float(Decimal(micro) / Decimal(1_000_000))


def _artifact_public(store: RuntimeStore, raw: dict[str, Any]) -> dict[str, Any]:
    source_revision: str | None = None
    if raw.get("run_id"):
        try:
            source_revision = store.get_run(raw["run_id"])["base_revision"]
        except RuntimeFault:
            source_revision = None
    return {
        "id": raw["id"],
        "kind": raw["kind"],
        "sha256": raw["sha256"],
        "job_id": raw["job_id"],
        "source_revision": source_revision,
        "relative_path": raw["display_name"],
        "run_id": raw.get("run_id"),
        "media_type": raw["media_type"],
        "size_bytes": raw["size_bytes"],
        "candidate_id": raw.get("candidate_id"),
        "immutable": bool(raw["immutable"]),
        "display_name": raw["display_name"],
    }


def _run_public(raw: dict[str, Any]) -> dict[str, Any]:
    cost = _usd(raw["cost_micro"])
    return {
        "id": raw["id"],
        "job_id": raw["job_id"],
        "task_id": raw["task_id"],
        "worker_id": raw.get("worker_id"),
        "attempt": raw["number"],
        "state": raw["state"],
        "model": raw.get("model"),
        "effort": raw.get("effort"),
        "started_at": raw["started_at"],
        "ended_at": raw.get("ended_at"),
        "usage": {
            "input_tokens": raw.get("input_tokens"),
            "cached_input_tokens": raw.get("cached_input_tokens"),
            "output_tokens": raw.get("output_tokens"),
            "total_tokens": raw.get("total_tokens"),
            "cost_usd": cost,
            "uncertain": bool(raw["usage_uncertain"]),
        },
    }


def _job_public(store: RuntimeStore, job_id: str, *, detail: bool) -> dict[str, Any]:
    job = store.get_job(job_id)
    profile_data = {
        "source": job["source"],
        "checks": job["checks"],
        "allowed_actions": job["allowed_actions"],
        "budget_micro": job["budget_micro"],
        "plan": None if len(job["tasks"]) == 1 and job["tasks"][0]["kind"] == "verify" else job["tasks"],
    }
    runs = store.list_job_runs(job_id)
    recent_artifacts = store.list_job_artifacts(job_id, limit=100)
    with store.read_connection() as connection:
        event_rows = connection.execute(
            "SELECT id, at, type, message, artifact_id FROM events WHERE job_id = ? ORDER BY id DESC LIMIT ?",
            (job_id, 50 if detail else 5),
        ).fetchall()
    events = [
        {
            "id": row["id"],
            "at": row["at"],
            "type": row["type"] if row["type"] in _PUBLIC_RUN_TYPES else "status",
            "message": _safe_message(row["message"]),
            "artifact_id": row["artifact_id"],
        }
        for row in reversed(event_rows)
    ]
    current_worker = next((task.get("worker_id") for task in job["tasks"] if task.get("worker_id")), None)
    if current_worker is None:
        active_run = next((run for run in reversed(runs) if run["state"] == "running"), None)
        current_worker = active_run.get("worker_id") if active_run else None
    if job["state"] == "verifying":
        check_state = "pass"
    elif job["state"] in {"blocked", "failed", "cancelled"}:
        check_state = "blocked" if job["state"] == "blocked" else "fail"
    else:
        check_state = "pending"
    public = {
        "id": job["id"],
        "project_id": job["project_id"],
        "title": job["title"],
        "source": job["source"],
        "state": job["state"],
        "checks": [
            {
                "id": check_id,
                "state": check_state,
                "evidence_artifact_id": next((item["id"] for item in recent_artifacts if item["kind"] == "test_report"), None),
            }
            for check_id in job["checks"]
        ],
        "allowed_actions": job["allowed_actions"],
        "budget_usd": _usd(job["budget_micro"]),
        "spent_usd": _usd(job["spent_micro"]),
        "worker_id": current_worker,
        "artifact_ids": [item["id"] for item in recent_artifacts],
        "events": events,
        "blocked_reason": job["blocked_reason"],
        "workflow_version": job["workflow_version"],
        "run_ids": [run["id"] for run in runs[-100:]],
        "tasks": [
            {
                "id": task["id"],
                "state": task["state"],
                "depends_on": task["depends_on"],
                "worker_id": task["worker_id"] or next(
                    (run["worker_id"] for run in reversed(runs) if run["task_id"] == task["id"]), None
                ),
                "attempt_id": task["current_attempt_id"],
            }
            for task in job["tasks"]
        ],
        "candidate_id": job["candidate_id"],
        "execution_profile": "local_git_inspection" if is_local_git_inspection_from_stored(profile_data) else None,
        "delivery_state": "disabled",
    }
    if detail:
        public["outcome"] = job["outcome"]
        public["runs"] = [_run_public(run) for run in runs[-100:]]
    return public


def _manifest_for_artifact(store: RuntimeStore, artifacts: ArtifactStore, artifact: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    if artifact["kind"] == "file_manifest":
        manifest_artifact = artifact
    elif artifact.get("candidate_id"):
        candidate = store.get_candidate(artifact["candidate_id"])
        manifest_artifact = store.get_artifact(candidate["manifest_artifact_id"])
    else:
        raise RuntimeFault(ErrorCode.INVALID_INPUT, "artifact has no frozen file manifest")
    if manifest_artifact["kind"] != "file_manifest":
        raise RuntimeFault(ErrorCode.INVALID_INPUT, "candidate file manifest is unavailable")
    if manifest_artifact["size_bytes"] > _MAX_MANIFEST_BYTES:
        raise RuntimeFault(ErrorCode.INVALID_INPUT, "file manifest exceeds the bounded read limit")
    manifest = artifacts.read_manifest(manifest_artifact)
    if len(manifest["files"]) > _MAX_MANIFEST_FILES:
        raise RuntimeFault(ErrorCode.INVALID_INPUT, "file manifest contains too many entries")
    return manifest_artifact, manifest


def _candidate_file_artifacts(
    store: RuntimeStore,
    candidate_id: str,
    paths: list[str],
) -> dict[str, dict[str, Any]]:
    files: dict[str, dict[str, Any]] = {}
    for item in store.list_candidate_artifacts(candidate_id, display_names=paths):
        files[item["display_name"]] = item
    return files


def _git_unquote_path(raw: str) -> str | None:
    value = raw.strip()
    if value.startswith('"'):
        try:
            value = ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return None
    if value == "/dev/null":
        return None
    if value.startswith("a/") or value.startswith("b/"):
        value = value[2:]
    return value


def _diff_rows_for_file(diff: bytes, entry: dict[str, Any]) -> list[dict[str, Any]]:
    try:
        text = diff.decode("utf-8", "strict")
    except UnicodeDecodeError:
        raise RuntimeFault(ErrorCode.INVALID_INPUT, "diff artifact is not valid UTF-8") from None
    chunks: list[list[str]] = []
    for line in text.splitlines():
        if line.startswith("diff --git "):
            chunks.append([line])
        elif chunks:
            chunks[-1].append(line)
    wanted = {entry.get("path"), entry.get("old_path")}
    selected: list[str] | None = None
    for chunk in chunks:
        old_path = new_path = None
        header = chunk[0][len("diff --git "):]
        try:
            import shlex
            header_paths = shlex.split(header, posix=True)
        except ValueError:
            header_paths = []
        if len(header_paths) == 2:
            old_path = _git_unquote_path(header_paths[0])
            new_path = _git_unquote_path(header_paths[1])
        for line in chunk:
            if line.startswith("--- "):
                old_path = _git_unquote_path(line[4:])
            elif line.startswith("+++ "):
                new_path = _git_unquote_path(line[4:])
                break
        if (new_path or old_path) in wanted:
            selected = chunk
            break
    if selected is None:
        return []
    rows: list[dict[str, Any]] = []
    old_line = new_line = 0
    in_hunk = False
    for line in selected:
        if line.startswith("@@ "):
            match = re.match(r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@", line)
            if match:
                old_line, new_line = int(match.group(1)), int(match.group(2))
            in_hunk = True
            rows.append({"kind": "hunk_header", "old_line": None, "new_line": None, "text": line})
            continue
        if line.startswith("Binary files ") or line == "GIT binary patch":
            rows.append({"kind": "binary", "old_line": None, "new_line": None, "text": "Binary file; no text diff is available."})
            in_hunk = False
            continue
        if not in_hunk:
            if line.startswith("\\ No newline at end of file"):
                rows.append({"kind": "no_newline", "old_line": None, "new_line": None, "text": line})
            else:
                rows.append({"kind": "file_header", "old_line": None, "new_line": None, "text": line})
            continue
        prefix = line[:1]
        if prefix == " ":
            rows.append({"kind": "context", "old_line": old_line, "new_line": new_line, "text": line[1:]})
            old_line += 1
            new_line += 1
        elif prefix == "+":
            rows.append({"kind": "add", "old_line": None, "new_line": new_line, "text": line[1:]})
            new_line += 1
        elif prefix == "-":
            rows.append({"kind": "remove", "old_line": old_line, "new_line": None, "text": line[1:]})
            old_line += 1
        elif line.startswith("\\ No newline at end of file"):
            rows.append({"kind": "no_newline", "old_line": None, "new_line": None, "text": line})
    return rows


def _layout_validate(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict) or set(payload) != {"nodes", "edges"}:
        raise RuntimeFault(ErrorCode.INVALID_INPUT, "layout must contain nodes and edges")
    nodes, edges = payload["nodes"], payload["edges"]
    if not isinstance(nodes, list) or len(nodes) > 128 or not isinstance(edges, list) or len(edges) > 512:
        raise RuntimeFault(ErrorCode.INVALID_INPUT, "layout exceeds the node or edge limit")
    by_id: dict[str, dict[str, Any]] = {}
    for node in nodes:
        if not isinstance(node, dict) or set(node) != {"id", "kind", "x", "y"}:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "layout node shape is invalid")
        node_id, kind, x, y = node["id"], node["kind"], node["x"], node["y"]
        if (
            not isinstance(node_id, str)
            or not _ID.fullmatch(node_id)
            or node_id in by_id
            or not isinstance(kind, str)
            or kind not in _LAYOUT_NODE_KINDS
            or any(not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 15 for value in (x, y))
        ):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "layout node identity, kind or position is invalid")
        by_id[node_id] = node
    outgoing: dict[str, list[str]] = {node_id: [] for node_id in by_id}
    for edge in edges:
        if not isinstance(edge, dict) or set(edge) != {"from", "to"}:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "layout edge shape is invalid")
        source, target = edge["from"], edge["to"]
        if not isinstance(source, str) or not isinstance(target, str) or source not in by_id or target not in by_id or source == target:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "layout edge references an invalid node")
        outgoing[source].append(target)
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node_id: str) -> None:
        if node_id in visiting:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "layout edges must be acyclic")
        if node_id in visited:
            return
        visiting.add(node_id)
        for target in outgoing[node_id]:
            visit(target)
        visiting.remove(node_id)
        visited.add(node_id)

    for node_id in by_id:
        visit(node_id)
    return {"nodes": nodes, "edges": edges}


def create_app(
    config: RuntimeConfig,
    *,
    token: str | None = None,
    store: RuntimeStore | None = None,
    scheduler: Scheduler | None = None,
) -> FastAPI:
    """Construct the HTTP app; tests can supply isolated storage and fake adapters."""
    secret = token if token is not None else config.service_token
    if not isinstance(secret, str) or not 32 <= len(secret) <= 512 or any(ch in secret for ch in "\r\n\x00"):
        raise ValueError("a local session token with at least 32 characters is required")
    runtime_store = store or RuntimeStore(config)
    artifact_store = ArtifactStore(config.artifacts_dir, runtime_store)
    if scheduler is None:
        scheduler = Scheduler(runtime_store, config, AdapterRunner(config), artifact_store)

    async def lifespan(_app: FastAPI):
        scheduler.start()
        yield
        await scheduler.stop()
        if store is None:
            runtime_store.close()

    app = FastAPI(title="Sidequest Runtime", version="1.1", docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)
    app.add_middleware(_CommandBodyLimit)
    app.state.runtime_store = runtime_store
    app.state.artifact_store = artifact_store
    app.state.scheduler = scheduler
    app.state.config = config

    @app.exception_handler(RuntimeFault)
    async def runtime_fault_handler(_request: Request, exc: RuntimeFault) -> JSONResponse:
        return _json_error(_http_status(exc.code), exc.code, exc.message, exc.retryable)

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(_request: Request, _exc: RequestValidationError) -> JSONResponse:
        return _json_error(400, ErrorCode.INVALID_INPUT, "request fields are invalid")

    @app.exception_handler(ValidationError)
    async def validation_handler(_request: Request, _exc: ValidationError) -> JSONResponse:
        return _json_error(400, ErrorCode.INVALID_INPUT, "request fields are invalid")

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
        if exc.status_code == 404:
            return _json_error(404, ErrorCode.NOT_FOUND, "endpoint was not found")
        if exc.status_code == 405:
            return _json_error(400, ErrorCode.INVALID_INPUT, "request method is not supported")
        return _json_error(400, ErrorCode.INVALID_INPUT, "request could not be processed")

    async def authenticate(request: Request) -> None:
        header = request.headers.get("authorization", "")
        prefix = "Bearer "
        supplied = header[len(prefix):] if header.startswith(prefix) else ""
        if not hmac.compare_digest(supplied.encode("utf-8", "ignore"), secret.encode("utf-8")):
            raise RuntimeFault(ErrorCode.POLICY_DENIED, "a valid local session token is required")

    @app.middleware("http")
    async def bound_request_body(request: Request, call_next: Callable[..., Any]):
        length = request.headers.get("content-length")
        if length:
            try:
                if int(length) > 4 * 1024 * 1024:
                    return _json_error(400, ErrorCode.INVALID_INPUT, "request body exceeds 4 MiB")
            except ValueError:
                return _json_error(400, ErrorCode.INVALID_INPUT, "content length is invalid")
        return await call_next(request)

    @app.get("/health")
    async def health() -> dict[str, Any]:
        return {"v": 1, "service": "sidequest-runtime", "mode": "live"}

    @app.get("/v1/capabilities", dependencies=[Depends(authenticate)])
    async def capabilities() -> dict[str, Any]:
        roots = []
        for root in config.allowed_roots:
            try:
                resolved = root.resolve(strict=True)
                if resolved.is_dir():
                    roots.append(resolved)
            except OSError:
                continue
        local_enabled = bool(roots and config.b_argv and config.d_argv)
        reasons = ["No coding model is verified; coding jobs are unavailable."]
        if not local_enabled:
            reasons.append("Configure an allowed local Git root and both host adapters to enable read-only inspection.")
        return {
            "v": 1,
            "contract_revision": "1.1",
            "features": {
                "computer_artifacts": True,
                "screen_watch": "unavailable",
                "github_delivery": False,
                "local_git_inspection": local_enabled,
                "coding": False,
            },
            "worker_model": {"id": "none", "effort": "unavailable", "verified": False, "coding_available": False},
            "limits": {"max_parallel": config.max_parallel, "max_tasks_per_plan": config.max_tasks_per_plan},
            "reasons": reasons,
        }

    @app.get("/v1/snapshot", dependencies=[Depends(authenticate)])
    async def snapshot() -> dict[str, Any]:
        projects = runtime_store.list_projects()
        selected_id = runtime_store.get_setting("selected_project_id")
        jobs = runtime_store.list_jobs(project_id=selected_id, limit=20) if selected_id else runtime_store.list_jobs(limit=20)
        with runtime_store.read_connection() as connection:
            total_budget, total_spent = connection.execute(
                "SELECT COALESCE(SUM(budget_micro), 0), CASE WHEN COUNT(*) = 0 THEN 0 "
                "WHEN SUM(CASE WHEN spent_micro IS NULL THEN 1 ELSE 0 END) > 0 THEN NULL ELSE SUM(spent_micro) END "
                "FROM jobs"
            ).fetchone()
            reserved = connection.execute(
                "SELECT COALESCE(SUM(reserved_micro),0) FROM budget_reservations WHERE state IN ('active','uncertain')"
            ).fetchone()[0]
            uncertain = bool(connection.execute("SELECT EXISTS(SELECT 1 FROM attempts WHERE usage_uncertain = 1)").fetchone()[0])
        budget = {"limit_usd": _usd(total_budget), "reserved_usd": _usd(reserved), "spent_usd": _usd(total_spent), "uncertain": uncertain}
        return {
            "v": 1,
            "revision": runtime_store.revision,
            "mode": "local-git",
            "projects": [{"id": item["id"], "name": item["name"], "base_revision": item["base_revision"], "status": item["status"]} for item in projects],
            "jobs": [_job_public(runtime_store, item["id"], detail=False) for item in jobs],
            "workers": [
                {"id": item["id"], "role": item["role"], "state": item["state"], "job_id": item["current_job_id"]}
                for item in runtime_store.list_workers()[:50]
            ],
            "workshops": [],
            "approvals": runtime_store.list_approvals(),
            "layout": runtime_store.get_setting("layout", {"version": 0, "nodes": [], "edges": []}),
            "budget": budget,
            "stopped": bool(runtime_store.get_setting("stopped", False)),
        }

    @app.get("/v1/jobs/{job_id}", dependencies=[Depends(authenticate)])
    async def job(job_id: str) -> dict[str, Any]:
        return {"v": 1, "job": _job_public(runtime_store, job_id, detail=True)}

    @app.get("/v1/jobs/{job_id}/artifacts", dependencies=[Depends(authenticate)])
    async def job_artifacts(
        job_id: str,
        cursor: str = "",
        limit: int = Query(default=100, ge=1, le=100),
    ) -> dict[str, Any]:
        runtime_store.get_job(job_id)
        offset = _read_cursor(secret, cursor, {"scope": "job-artifacts", "job_id": job_id}) if cursor else 0
        rows = runtime_store.list_job_artifacts(job_id, limit=limit + 1, offset=offset)
        more = len(rows) > limit
        page = rows[:limit]
        next_cursor = _make_cursor(secret, {"scope": "job-artifacts", "job_id": job_id}, offset + limit) if more else None
        return {"v": 1, "job_id": job_id, "items": [_artifact_public(runtime_store, item) for item in page], "next_cursor": next_cursor}

    @app.get("/v1/runs/{run_id}", dependencies=[Depends(authenticate)])
    async def run(run_id: str) -> dict[str, Any]:
        return {"v": 1, "run": _run_public(runtime_store.get_run(run_id))}

    @app.get("/v1/runs/{run_id}/events", dependencies=[Depends(authenticate)])
    async def run_events(
        run_id: str,
        after_seq: int = Query(default=0, ge=0),
        limit: int = Query(default=200, ge=1, le=200),
    ) -> dict[str, Any]:
        run_data = runtime_store.get_run(run_id)
        rows = runtime_store.list_run_events(run_id, after_seq=after_seq, limit=limit)
        has_more = len(rows) > limit
        page = rows[:limit]
        for row in page:
            row["task_id"] = run_data["task_id"]
            if row["type"] not in _PUBLIC_RUN_TYPES:
                row["type"] = "status"
            row["message"] = _safe_message(row["message"])
        return {
            "v": 1,
            "run_id": run_id,
            "items": page,
            "next_after_seq": page[-1]["seq"] if page else after_seq,
            "has_more": has_more,
        }

    @app.get("/v1/artifacts/{artifact_id}", dependencies=[Depends(authenticate)])
    async def artifact(artifact_id: str) -> dict[str, Any]:
        raw = runtime_store.get_artifact(artifact_id)
        content = artifact_store.read_artifact(raw)
        preview = text_preview(content)
        if preview is not None:
            preview = _safe_message(preview)
        return {"v": 1, "artifact": _artifact_public(runtime_store, raw), "preview_text": preview}

    @app.get("/v1/artifacts/{artifact_id}/files", dependencies=[Depends(authenticate)])
    async def artifact_files(
        artifact_id: str,
        cursor: str = "",
        limit: int = Query(default=100, ge=1, le=100),
    ) -> dict[str, Any]:
        raw = runtime_store.get_artifact(artifact_id)
        if raw["kind"] != "file_manifest":
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "files are available only from a frozen file manifest")
        manifest_artifact, manifest = _manifest_for_artifact(runtime_store, artifact_store, raw)
        candidate = manifest["candidate"]
        candidate_id = candidate.get("id")
        if not isinstance(candidate_id, str) or raw.get("candidate_id") != candidate_id:
            raise RuntimeFault(ErrorCode.VERSION_CONFLICT, "manifest is not linked to its frozen candidate")
        offset = _read_cursor(secret, cursor, {"scope": "manifest-files", "sha256": raw["sha256"]}) if cursor else 0
        entries = manifest["files"]
        page = entries[offset:offset + limit]
        more = offset + limit < len(entries)
        by_path = _candidate_file_artifacts(
            runtime_store,
            candidate_id,
            [item.get("path") for item in page if isinstance(item, dict) and item.get("status") != "deleted" and isinstance(item.get("path"), str)],
        )
        files: list[dict[str, Any]] = []
        for item in page:
            if not isinstance(item, dict) or not isinstance(item.get("file_id"), str):
                raise RuntimeFault(ErrorCode.INVALID_INPUT, "manifest file entry is invalid")
            public = {key: item.get(key) for key in ("file_id", "path", "old_path", "status", "media_type", "size_bytes", "sha256", "added_lines", "deleted_lines", "binary")}
            linked = by_path.get(item.get("path")) if item.get("status") != "deleted" else None
            public["artifact_id"] = linked["id"] if linked else None

            candidate_files = [*files, public]
            consumed = offset + len(candidate_files)
            next_cursor = (
                _make_cursor(secret, {"scope": "manifest-files", "sha256": raw["sha256"]}, consumed)
                if consumed < len(entries)
                else None
            )
            candidate_body = {
                "v": 1,
                "artifact_id": artifact_id,
                "candidate_id": candidate_id,
                "files": candidate_files,
                "next_cursor": next_cursor,
            }
            if _serialized_json_size(candidate_body) > _MAX_PAGE_BYTES:
                if not files:
                    raise RuntimeFault(ErrorCode.INVALID_INPUT, "manifest entry exceeds the bounded response page")
                break
            files.append(public)

        consumed = offset + len(files)
        next_cursor = (
            _make_cursor(secret, {"scope": "manifest-files", "sha256": raw["sha256"]}, consumed)
            if consumed < len(entries)
            else None
        )
        response = {
            "v": 1,
            "artifact_id": artifact_id,
            "candidate_id": candidate_id,
            "files": files,
            "next_cursor": next_cursor,
        }
        if _serialized_json_size(response) > _MAX_PAGE_BYTES:
            raise RuntimeFault(ErrorCode.INTERNAL, "manifest response exceeded its bounded page size")
        return response

    @app.get("/v1/artifacts/{artifact_id}/text", dependencies=[Depends(authenticate)])
    async def artifact_text(
        artifact_id: str,
        file_id: str,
        start_line: int = Query(default=1, ge=1, le=1_000_000_000),
        limit: int = Query(default=200, ge=1, le=200),
    ) -> dict[str, Any]:
        raw = runtime_store.get_artifact(artifact_id)
        manifest_artifact, manifest = _manifest_for_artifact(runtime_store, artifact_store, raw)
        if raw["job_id"] != manifest_artifact["job_id"]:
            raise RuntimeFault(ErrorCode.POLICY_DENIED, "artifact is outside the requested candidate job")
        candidate = manifest["candidate"]
        entry = next((item for item in manifest["files"] if isinstance(item, dict) and item.get("file_id") == file_id), None)
        if not entry or entry.get("status") == "deleted" or entry.get("binary") is True:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "file has no readable text content")
        source_artifact = _candidate_file_artifacts(runtime_store, candidate["id"], [entry["path"]]).get(entry["path"])
        if not source_artifact:
            raise RuntimeFault(ErrorCode.NOT_FOUND, "registered file content was not found")
        if source_artifact["size_bytes"] > 16 * 1024 * 1024:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "file exceeds the text-view size limit")
        data = artifact_store.read_artifact(source_artifact)
        try:
            decoded = data.decode("utf-8", "strict")
        except UnicodeDecodeError:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "file encoding is not supported for text view") from None
        source_lines = decoded.splitlines(keepends=True)
        if not source_lines and decoded == "":
            source_lines = []
        selected: list[dict[str, Any]] = []
        index = start_line - 1
        while index < len(source_lines) and len(selected) < limit:
            original = source_lines[index]
            content = original[:-2] if original.endswith("\r\n") else original[:-1] if original.endswith(("\n", "\r")) else original
            raw_bytes = content.encode("utf-8")
            clipped = False
            if len(raw_bytes) > _MAX_TEXT_LINE_BYTES:
                content = _utf8_prefix(content, _MAX_TEXT_LINE_BYTES)
                clipped = True

            line = {"number": index + 1, "text": _CONTROL.sub("", content), "clipped": clipped}

            def text_page(lines: list[dict[str, Any]], consumed: int) -> dict[str, Any]:
                return {
                    "v": 1,
                    "artifact_id": artifact_id,
                    "file_id": file_id,
                    "sha256": source_artifact["sha256"],
                    "start_line": start_line,
                    "lines": lines,
                    "next_line": consumed + 1 if consumed < len(source_lines) else None,
                    "encoding": "utf-8",
                    "immutable": bool(source_artifact["immutable"]),
                }

            candidate_lines = [*selected, line]
            if _serialized_json_size(text_page(candidate_lines, index + 1)) <= _MAX_PAGE_BYTES:
                selected.append(line)
                index += 1
                if clipped:
                    break
                continue

            # If earlier rows fill this page, leave this line for the next page
            # so its text remains complete. Only clip when it cannot fit alone.
            if selected:
                break

            low, high = 0, len(line["text"])
            best: dict[str, Any] | None = None
            while low <= high:
                middle = (low + high) // 2
                clipped_line = {"number": index + 1, "text": line["text"][:middle], "clipped": True}
                if _serialized_json_size(text_page([clipped_line], index + 1)) <= _MAX_PAGE_BYTES:
                    best = clipped_line
                    low = middle + 1
                else:
                    high = middle - 1
            if best is None:
                raise RuntimeFault(ErrorCode.INTERNAL, "text line metadata exceeds the bounded response page")
            selected.append(best)
            index += 1
            break

        response = text_page(selected, index)
        if _serialized_json_size(response) > _MAX_PAGE_BYTES:
            raise RuntimeFault(ErrorCode.INTERNAL, "text response exceeded its bounded page size")
        return response

    @app.get("/v1/artifacts/{artifact_id}/diff", dependencies=[Depends(authenticate)])
    async def artifact_diff(
        artifact_id: str,
        file_id: str,
        cursor: str = "",
        limit: int = Query(default=200, ge=1, le=200),
    ) -> dict[str, Any]:
        raw = runtime_store.get_artifact(artifact_id)
        if raw["kind"] != "diff" or not raw.get("candidate_id"):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "artifact is not a frozen candidate diff")
        manifest_artifact, manifest = _manifest_for_artifact(runtime_store, artifact_store, raw)
        candidate = manifest["candidate"]
        entry = next((item for item in manifest["files"] if isinstance(item, dict) and item.get("file_id") == file_id), None)
        if not entry:
            raise RuntimeFault(ErrorCode.NOT_FOUND, "file is not in this candidate manifest")
        scope = {"scope": "candidate-diff", "sha256": raw["sha256"], "file_id": file_id}
        offset = _read_cursor(secret, cursor, scope) if cursor else 0
        if raw["size_bytes"] > 16 * 1024 * 1024:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "diff exceeds the bounded row parser limit")
        rows = _diff_rows_for_file(artifact_store.read_artifact(raw), entry)
        page: list[dict[str, Any]] = []

        def diff_page(page_rows: list[dict[str, Any]], consumed: int) -> dict[str, Any]:
            return {
                "v": 1,
                "artifact_id": artifact_id,
                "candidate_id": candidate["id"],
                "base_revision": candidate["base_revision"],
                "candidate_revision": candidate["candidate_revision"],
                "rows": page_rows,
                "next_cursor": _make_cursor(secret, scope, consumed) if consumed < len(rows) else None,
            }

        index = offset
        while index < min(len(rows), offset + limit):
            row = {**rows[index], "text": _CONTROL.sub("", rows[index]["text"])}
            candidate_rows = [*page, row]
            if _serialized_json_size(diff_page(candidate_rows, index + 1)) <= _MAX_PAGE_BYTES:
                page.append(row)
                index += 1
                continue

            if page:
                break

            low, high = 0, len(row["text"])
            best: dict[str, Any] | None = None
            while low <= high:
                middle = (low + high) // 2
                clipped_row = {**row, "text": row["text"][:middle], "clipped": True}
                if _serialized_json_size(diff_page([clipped_row], index + 1)) <= _MAX_PAGE_BYTES:
                    best = clipped_row
                    low = middle + 1
                else:
                    high = middle - 1
            if best is None:
                raise RuntimeFault(ErrorCode.INTERNAL, "diff row metadata exceeds the bounded response page")
            page.append(best)
            index += 1
            break

        response = diff_page(page, index)
        if _serialized_json_size(response) > _MAX_PAGE_BYTES:
            raise RuntimeFault(ErrorCode.INTERNAL, "diff response exceeded its bounded page size")
        return response

    @app.get("/v1/artifacts/{artifact_id}/content", dependencies=[Depends(authenticate)])
    async def artifact_content(artifact_id: str) -> Response:
        raw = runtime_store.get_artifact(artifact_id)
        data = artifact_store.read_artifact(raw)
        safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", raw["display_name"])[-100:] or "artifact.bin"
        return Response(
            content=data,
            media_type="application/octet-stream",
            headers={
                "Content-Length": str(len(data)),
                "ETag": f'"{raw["sha256"]}"',
                "X-Content-Type-Options": "nosniff",
                "Content-Disposition": f'attachment; filename="{safe_name}"',
                "Cache-Control": "no-store",
            },
        )

    @app.get("/v1/watchers", dependencies=[Depends(authenticate)])
    async def watchers() -> dict[str, Any]:
        return {"v": 1, "items": []}

    @app.post("/v1/commands", status_code=202, dependencies=[Depends(authenticate)])
    async def commands(command: CommandRequest) -> JSONResponse:
        payload = command.payload
        expected = command.expected_revision
        if command.type == "project.register":
            if expected is None:
                raise RuntimeFault(ErrorCode.INVALID_INPUT, "expected_revision is required for project registration")
            registration = ProjectRegistration.model_validate(payload)
            result = runtime_store.register_project(command.command_id, expected, registration)
        elif command.type == "project.select":
            if expected is None or set(payload) != {"project_id"}:
                raise RuntimeFault(ErrorCode.INVALID_INPUT, "project.select requires expected_revision and project_id")
            result = runtime_store.select_project(command.command_id, expected, payload["project_id"])
        elif command.type == "job.create":
            create = JobCreate.model_validate(payload)
            result = runtime_store.create_job(command.command_id, expected, create)
        elif command.type in {"job.run", "job.pause", "job.cancel"}:
            if expected is None or set(payload) != {"job_id"}:
                raise RuntimeFault(ErrorCode.INVALID_INPUT, "job command requires expected_revision and job_id")
            if command.type == "job.run" and runtime_store.get_setting("stopped", False):
                raise RuntimeFault(ErrorCode.POLICY_DENIED, "runtime dispatch is stopped")
            result = runtime_store.set_job_command(command.command_id, expected, command.type, payload["job_id"])
            if command.type == "job.run":
                scheduler.enqueue(payload["job_id"])
            elif command.type == "job.pause":
                await scheduler.pause_job(payload["job_id"])
            else:
                await scheduler.cancel_job(payload["job_id"])
        elif command.type == "job.assign":
            if expected is None or set(payload) != {"job_id", "worker_id"}:
                raise RuntimeFault(ErrorCode.INVALID_INPUT, "job.assign requires job_id and worker_id")
            result = runtime_store.assign_worker(
                command.command_id,
                expected,
                payload["job_id"],
                payload["worker_id"],
            )
        elif command.type == "system.stop":
            if payload:
                raise RuntimeFault(ErrorCode.INVALID_INPUT, "system.stop takes an empty payload")
            result = runtime_store.system_stop(command.command_id, expected, True)
            await scheduler.stop()
        elif command.type == "layout.save":
            if expected is None:
                raise RuntimeFault(ErrorCode.INVALID_INPUT, "expected_revision is required for layout.save")
            result = runtime_store.save_layout(command.command_id, expected, _layout_validate(payload))
        else:
            raise RuntimeFault(ErrorCode.POLICY_DENIED, "command is not enabled in this local runtime profile")
        return JSONResponse(result, status_code=202)

    return app


def _make_cursor(secret: str, scope: dict[str, Any], offset: int) -> str:
    payload = {**scope, "offset": offset}
    raw = canonical_json(payload).encode("utf-8")
    signature = hmac.new(secret.encode("utf-8"), raw, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(raw + signature).decode("ascii").rstrip("=")


def _read_cursor(secret: str, cursor: str, expected_scope: dict[str, Any]) -> int:
    if not isinstance(cursor, str) or len(cursor) > 2048 or not cursor:
        raise RuntimeFault(ErrorCode.INVALID_INPUT, "pagination cursor is invalid")
    try:
        padding = "=" * ((4 - len(cursor) % 4) % 4)
        combined = base64.urlsafe_b64decode(cursor + padding)
        # urlsafe_b64decode accepts non-canonical encodings whose unused tail
        # bits differ while decoding to the same bytes. Require the emitted
        # token to be the one canonical representation before checking its MAC.
        if base64.urlsafe_b64encode(combined).decode("ascii").rstrip("=") != cursor:
            raise ValueError
        if len(combined) < 34:
            raise ValueError
        raw, signature = combined[:-32], combined[-32:]
        expected = hmac.new(secret.encode("utf-8"), raw, hashlib.sha256).digest()
        if not hmac.compare_digest(signature, expected):
            raise ValueError
        payload = json.loads(raw.decode("utf-8", "strict"))
        if not isinstance(payload, dict) or any(payload.get(key) != value for key, value in expected_scope.items()):
            raise ValueError
        offset = payload.get("offset")
        if not isinstance(offset, int) or isinstance(offset, bool) or offset < 0:
            raise ValueError
        return offset
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError, base64.binascii.Error):
        raise RuntimeFault(ErrorCode.INVALID_INPUT, "pagination cursor is invalid or belongs to another artifact") from None


__all__ = ["create_app"]
