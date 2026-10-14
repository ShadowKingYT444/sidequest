"""Bounded, plain-data evidence artifacts for deterministic checks."""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
from pathlib import Path
from typing import Any

from .config import MAX_REPORT_BYTES, MAX_SCREENSHOT_BYTES

_SAFE_NAME = re.compile(r"^[a-z0-9][a-z0-9._-]{0,80}$")


class ReportError(ValueError):
    pass


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _safe_output_dir(output_root: Path, request_id: str) -> Path:
    if not _SAFE_NAME.fullmatch(request_id):
        raise ReportError("Request identifier is not safe for an output directory.")
    if output_root.is_symlink() or not output_root.is_dir():
        raise ReportError("Host-assigned output root is not a regular directory.")
    destination = output_root / f"check-{request_id}"
    try:
        destination.mkdir(mode=0o700)
    except FileExistsError as exc:
        raise ReportError("Output directory already exists for this request.") from exc
    info = destination.lstat()
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
        raise ReportError("Output directory is not a regular directory.")
    return destination


def create_run_directory(output_root: Path, request_id: str) -> Path:
    return _safe_output_dir(output_root, request_id)


def write_artifact(run_dir: Path, name: str, data: bytes, *, kind: str, media_type: str) -> dict[str, Any]:
    if not _SAFE_NAME.fullmatch(name):
        raise ReportError("Evidence artifact name is unsafe.")
    limit = MAX_SCREENSHOT_BYTES if kind == "screenshot" else MAX_REPORT_BYTES
    if len(data) > limit:
        raise ReportError("Evidence artifact exceeds the size limit.")
    target = run_dir / name
    if target.exists() or target.is_symlink():
        raise ReportError("Evidence artifact path already exists.")
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        try:
            target.unlink()
        except OSError:
            pass
        raise
    digest = hashlib.sha256(data).hexdigest()
    return {
        "id": f"sha256:{digest}",
        "kind": kind,
        "sha256": digest,
        "relative_path": f"{run_dir.name}/{name}",
        "media_type": media_type,
        "size_bytes": len(data),
        "immutable": True,
    }


def build_report(
    *,
    request_id: str,
    source_revision: str,
    candidate_id: str,
    tree_sha256: str,
    manifest_artifact_id: str,
    results: list[dict[str, Any]],
    browser_version: str | None,
    origin: str | None,
    inference_calls: int = 0,
) -> dict[str, Any]:
    return {
        "v": 1,
        "request_id": request_id,
        "op": "check.run",
        "source_revision": source_revision,
        "candidate": {
            "id": candidate_id,
            "tree_sha256": tree_sha256,
            "manifest_artifact_id": manifest_artifact_id,
        },
        "results": results,
        "browser": {"version": browser_version, "registered_origin": origin},
        "inference_calls": inference_calls,
    }
