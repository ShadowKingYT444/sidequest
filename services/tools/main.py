"""One-shot JSON-line entry point for Sidequest lane B."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

try:
    from .artifact_capture import deliver_candidate, freeze_candidate
    from .config import ConfigurationError, Settings
    from .codex_bridge import probe_capabilities
    from .git_ops import (
        AdapterError,
        _repo_root,
        inspect_worktree,
        resolve_commit,
        validate_repo_path,
    )
    from .protocol import (
        ProgressLog,
        diagnostic,
        error_response,
        read_request,
        success_response,
        write_response,
    )
except ImportError:  # Direct script execution by the adapter host.
    from artifact_capture import deliver_candidate, freeze_candidate
    from config import ConfigurationError, Settings
    from codex_bridge import probe_capabilities
    from git_ops import AdapterError, _repo_root, inspect_worktree, resolve_commit, validate_repo_path
    from protocol import ProgressLog, diagnostic, error_response, read_request, success_response, write_response


def _progress_log(request: dict[str, Any], settings: Settings) -> ProgressLog:
    context = request.get("context", {})
    raw = context.get("progress_path")
    if raw is None:
        return ProgressLog(None, request["request_id"])
    if not isinstance(raw, str) or not Path(raw).is_absolute():
        raise AdapterError("POLICY_DENIED", "Progress path must be host-assigned and absolute.")
    try:
        from .git_ops import _canonical_under
    except ImportError:
        from git_ops import _canonical_under
    path = _canonical_under(raw, settings.staging_roots, must_exist=False)
    return ProgressLog(path, request["request_id"], settings.staging_roots)


def dispatch(request: dict[str, Any], settings: Settings) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any] | None]:
    op = request["op"]
    payload = request["payload"]
    context = request.get("context", {})
    progress = _progress_log(request, settings)
    if op == "repo.inspect":
        if set(payload) != {"repo_path", "revision"} or not isinstance(payload["repo_path"], str) or not isinstance(payload["revision"], str):
            raise AdapterError("INVALID_INPUT", "repo.inspect requires repo_path and revision.")
        repo = validate_repo_path(payload["repo_path"], settings.allowed_repo_roots)
        _repo_root(repo, settings)
        revision = resolve_commit(repo, payload["revision"], settings)
        entries, actual, clean = inspect_worktree(repo, revision, settings)
        paths = sorted(set(entries) | set(actual))
        if sum(len(path.encode("utf-8")) + 4 for path in paths) > 2 * 1024 * 1024:
            raise AdapterError("POLICY_DENIED", "Repository file listing exceeds the protocol response budget.")
        progress.append("status", "Repository inspection completed.")
        return {"revision": revision, "clean": clean, "files": paths}, [], None
    if op == "repo.prepare":
        if set(payload) != {"repo_path", "revision"} or not isinstance(payload["repo_path"], str) or not isinstance(payload["revision"], str):
            raise AdapterError("INVALID_INPUT", "repo.prepare requires repo_path and revision.")
        try:
            from .git_ops import prepare_clone
        except ImportError:
            from git_ops import prepare_clone
        workspace, revision = prepare_clone(payload["repo_path"], payload["revision"], request["workspace"], settings)
        progress.append("status", "Independent repository clone prepared.")
        return {"workspace": str(workspace), "revision": revision}, [], None
    if op == "artifacts.freeze":
        progress.append("status", "Validating candidate scope and Git tree.")
        data, artifacts = freeze_candidate(request, settings)
        progress.append("status", "Immutable candidate artifacts frozen.", data["manifest_artifact_id"])
        return data, artifacts, None
    if op == "repo.deliver":
        progress.append("status", "Validating exact host approval and delivery identity.")
        data, artifacts = deliver_candidate(request, settings)
        progress.append("status", "Approved local delivery reconciled.")
        return data, artifacts, None
    if op == "agent.capabilities":
        if payload != {}:
            raise AdapterError("INVALID_INPUT", "agent.capabilities requires an empty payload.")
        return probe_capabilities(settings, progress), [], None
    if op == "agent.execute":
        raise AdapterError("POLICY_DENIED", "Codex execution is disabled because the app-server cannot enforce a verified USD spend ceiling.")
    raise AdapterError("INVALID_INPUT", "Unsupported B operation.")


def _args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sidequest B adapter: isolated Git, Codex app-server and immutable artifacts.")
    parser.add_argument("--version", action="version", version="Sidequest B adapter v1")
    return parser.parse_args(argv)


def run(argv: list[str] | None = None) -> int:
    _args(argv)  # argparse handles --help without requiring runtime configuration.
    request: dict[str, Any] | None = None
    try:
        request = read_request()
        settings = Settings.from_env()
        data, artifacts, usage = dispatch(request, settings)
        response = success_response(request, data, artifacts, usage)
    except AdapterError as exc:
        diagnostic(f"{exc.code}: {exc.message}")
        response = error_response(request.get("request_id") if request else None, exc)
    except ConfigurationError as exc:
        error = AdapterError("UNAVAILABLE", str(exc))
        diagnostic(f"{error.code}: {error.message}")
        response = error_response(request.get("request_id") if request else None, error)
    except Exception as exc:
        diagnostic(f"INTERNAL: adapter failed ({type(exc).__name__})")
        response = error_response(request.get("request_id") if request else None, AdapterError("INTERNAL", "B adapter failed safely."))
    try:
        write_response(response)
    except AdapterError as exc:
        diagnostic(f"{exc.code}: {exc.message}")
        fallback_id = request.get("request_id") if request else None
        fallback = error_response(fallback_id, AdapterError("INTERNAL", "Final response exceeded the protocol limit."))
        write_response(fallback)
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
