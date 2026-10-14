"""Validation for host-staged manifests and frozen candidate trees."""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
from pathlib import Path, PurePosixPath
from typing import Any

from .config import (
    MAX_ARTIFACT_INPUT_BYTES,
    MAX_CANDIDATE_BYTES,
    MAX_CANDIDATE_FILES,
)

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_SAFE_ID = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
_SAFE_COMPONENT = re.compile(r"^[^\x00-\x1f\x7f]+$")
_WRITABLE = stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH


class IdentityError(ValueError):
    """A candidate or host-staged artifact did not match its frozen identity."""


def _safe_relative_path(raw: Any) -> str:
    if not isinstance(raw, str) or not raw or "\\" in raw:
        raise IdentityError("Unsafe candidate path.")
    if not _SAFE_COMPONENT.fullmatch(raw):
        raise IdentityError("Unsafe candidate path.")
    path = PurePosixPath(raw)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise IdentityError("Unsafe candidate path.")
    if ".git" in path.parts:
        raise IdentityError("Candidate contains a forbidden path.")
    normalized = path.as_posix()
    if normalized != raw:
        raise IdentityError("Candidate path is not canonical.")
    return normalized


def _path_has_symlink_component(path: Path) -> bool:
    absolute = Path(os.path.abspath(path))
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current = current / part
        try:
            if stat.S_ISLNK(current.lstat().st_mode):
                return True
        except FileNotFoundError:
            return True
    return False


def assigned_directory(raw: Any, *, name: str) -> Path:
    """Validate a host-assigned absolute directory path and reject symlink paths."""
    if not isinstance(raw, str) or not raw or "\x00" in raw:
        raise IdentityError(f"Host-assigned {name} path is missing.")
    path = Path(raw)
    if not path.is_absolute() or ".." in path.parts:
        raise IdentityError(f"Host-assigned {name} path is unsafe.")
    if _path_has_symlink_component(path):
        raise IdentityError(f"Host-assigned {name} path contains a symlink or missing component.")
    try:
        resolved = path.resolve(strict=True)
    except OSError as exc:
        raise IdentityError(f"Host-assigned {name} path is unavailable.") from exc
    if resolved != path:
        raise IdentityError(f"Host-assigned {name} path is not canonical.")
    if not resolved.is_dir():
        raise IdentityError(f"Host-assigned {name} path is not a directory.")
    return resolved


def assigned_file(raw: Any, *, name: str) -> Path:
    """Validate a host-staged regular file without following symlinks."""
    if not isinstance(raw, str) or not raw or "\x00" in raw:
        raise IdentityError(f"Host-assigned {name} path is missing.")
    path = Path(raw)
    if not path.is_absolute() or ".." in path.parts:
        raise IdentityError(f"Host-assigned {name} path is unsafe.")
    if _path_has_symlink_component(path):
        raise IdentityError(f"Host-assigned {name} path contains a symlink or missing component.")
    try:
        resolved = path.resolve(strict=True)
        info = resolved.lstat()
    except OSError as exc:
        raise IdentityError(f"Host-assigned {name} is unavailable.") from exc
    if resolved != path or not stat.S_ISREG(info.st_mode):
        raise IdentityError(f"Host-assigned {name} is not a regular file.")
    return resolved


def _read_regular_file(path: Path, limit: int) -> tuple[bytes, int]:
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise IdentityError("Candidate file could not be opened safely.") from exc
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_size > limit:
            raise IdentityError("Candidate file has an unsupported type or size.")
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(fd, min(1024 * 1024, limit + 1 - total))
            if not chunk:
                break
            total += len(chunk)
            if total > limit:
                raise IdentityError("Candidate file exceeds the size limit.")
            chunks.append(chunk)
        return b"".join(chunks), info.st_mode
    finally:
        os.close(fd)


def _git_blob_mode(mode: int) -> str:
    if not stat.S_ISREG(mode):
        raise IdentityError("Candidate contains a non-regular file.")
    return "100755" if mode & stat.S_IXUSR else "100644"


def _normalize_manifest_mode(value: Any) -> str:
    """Validate a Git file mode while preserving its original JSON type for hashing."""
    if isinstance(value, bool):
        raise IdentityError("Candidate manifest mode is invalid.")
    if isinstance(value, int):
        if value in {0o100644, 0o100755}:
            return f"{value:o}"
        if value in {0o644, 0o755}:
            return "100755" if value & stat.S_IXUSR else "100644"
        raise IdentityError("Candidate manifest mode is invalid.")
    if isinstance(value, str):
        if value in {"100644", "100755"}:
            return value
        if value.isdecimal():
            try:
                numeric = int(value)
            except ValueError as exc:
                raise IdentityError("Candidate manifest mode is invalid.") from exc
            if numeric in {0o100644, 0o100755}:
                return f"{numeric:o}"
            if numeric in {0o644, 0o755}:
                return "100755" if numeric & stat.S_IXUSR else "100644"
    raise IdentityError("Candidate manifest mode is invalid.")


def _canonical_tree_hash(records: list[dict[str, Any]]) -> str:
    payload = {"v": 1, "files": records}
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _walk_tree(root: Path, *, require_read_only: bool) -> tuple[list[dict[str, Any]], dict[str, bytes]]:
    root_info = root.lstat()
    if not stat.S_ISDIR(root_info.st_mode) or stat.S_ISLNK(root_info.st_mode):
        raise IdentityError("Candidate root is not a regular directory.")
    if require_read_only and root_info.st_mode & _WRITABLE:
        raise IdentityError("Candidate root is writable.")
    records: list[dict[str, Any]] = []
    contents: dict[str, bytes] = {}
    total_bytes = 0
    pending = [root]
    while pending:
        directory = pending.pop()
        try:
            entries = sorted(os.scandir(directory), key=lambda item: item.name)
        except OSError as exc:
            raise IdentityError("Candidate directory could not be read.") from exc
        for entry in entries:
            path = Path(entry.path)
            rel = path.relative_to(root).as_posix()
            _safe_relative_path(rel)
            info = entry.stat(follow_symlinks=False)
            if stat.S_ISLNK(info.st_mode):
                raise IdentityError("Candidate contains a symlink.")
            if stat.S_ISDIR(info.st_mode):
                if require_read_only and info.st_mode & _WRITABLE:
                    raise IdentityError("Candidate directory is writable.")
                pending.append(path)
                continue
            if not stat.S_ISREG(info.st_mode):
                raise IdentityError("Candidate contains a special file.")
            if require_read_only and info.st_mode & _WRITABLE:
                raise IdentityError("Candidate file is writable.")
            file_bytes, opened_mode = _read_regular_file(path, MAX_CANDIDATE_BYTES)
            if _git_blob_mode(opened_mode) != _git_blob_mode(info.st_mode):
                raise IdentityError("Candidate file changed while it was read.")
            total_bytes += len(file_bytes)
            if total_bytes > MAX_CANDIDATE_BYTES:
                raise IdentityError("Candidate exceeds the total size limit.")
            record = {
                "path": rel,
                "mode": _git_blob_mode(info.st_mode),
                "size_bytes": len(file_bytes),
                "sha256": hashlib.sha256(file_bytes).hexdigest(),
            }
            records.append(record)
            contents[rel] = file_bytes
            if len(records) > MAX_CANDIDATE_FILES:
                raise IdentityError("Candidate exceeds the file count limit.")
    records.sort(key=lambda item: item["path"])
    return records, contents


def verify_host_artifact_inputs(raw_inputs: Any) -> list[tuple[dict[str, Any], bytes]]:
    if not isinstance(raw_inputs, list) or not raw_inputs:
        raise IdentityError("A host-staged candidate manifest is required.")
    if len(raw_inputs) > 100:
        raise IdentityError("Too many host-staged artifact inputs.")
    verified: list[tuple[dict[str, Any], bytes]] = []
    seen_ids: set[str] = set()
    total_bytes = 0
    for item in raw_inputs:
        if not isinstance(item, dict):
            raise IdentityError("Host-staged artifact input is invalid.")
        artifact_id = item.get("id")
        expected = item.get("sha256")
        if (
            not isinstance(artifact_id, str)
            or not _SAFE_ID.fullmatch(artifact_id)
            or artifact_id in seen_ids
            or not isinstance(expected, str)
            or not _SHA256.fullmatch(expected)
        ):
            raise IdentityError("Host-staged artifact identity is invalid.")
        seen_ids.add(artifact_id)
        path = assigned_file(item.get("staged_path"), name="artifact input")
        data, _mode = _read_regular_file(path, MAX_ARTIFACT_INPUT_BYTES)
        total_bytes += len(data)
        if total_bytes > MAX_ARTIFACT_INPUT_BYTES:
            raise IdentityError("Host-staged artifact inputs exceed the total size limit.")
        actual = hashlib.sha256(data).hexdigest()
        if actual != expected:
            raise IdentityError("Host-staged artifact digest does not match.")
        verified.append((item, data))
    return verified


def validate_manifest(data: bytes) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    try:
        manifest = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IdentityError("Host-staged candidate manifest is invalid JSON.") from exc
    if not isinstance(manifest, dict) or manifest.get("v") != 1:
        raise IdentityError("Host-staged candidate manifest version is unsupported.")
    candidate = manifest.get("candidate")
    files = manifest.get("files")
    if not isinstance(candidate, dict) or not isinstance(files, list):
        raise IdentityError("Host-staged candidate manifest has an invalid shape.")
    candidate_id = candidate.get("id")
    candidate_hash = candidate.get("tree_sha256")
    if (
        not isinstance(candidate_id, str)
        or not _SAFE_ID.fullmatch(candidate_id)
        or not isinstance(candidate_hash, str)
        or not _SHA256.fullmatch(candidate_hash)
    ):
        raise IdentityError("Host-staged candidate identity is invalid.")

    active: list[dict[str, Any]] = []
    seen: set[str] = set()
    for entry in files:
        if not isinstance(entry, dict):
            raise IdentityError("Candidate manifest file entry is invalid.")
        path = _safe_relative_path(entry.get("path"))
        status = entry.get("status")
        if status not in {"added", "modified", "deleted", "renamed", "unchanged"}:
            raise IdentityError("Candidate manifest file status is invalid.")
        if path in seen:
            raise IdentityError("Candidate manifest contains duplicate paths.")
        seen.add(path)
        if status == "deleted":
            continue
        mode = entry.get("mode")
        _normalize_manifest_mode(mode)
        size = entry.get("size_bytes")
        digest = entry.get("sha256")
        if (
            not isinstance(size, int)
            or isinstance(size, bool)
            or size < 0
            or size > MAX_CANDIDATE_BYTES
            or not isinstance(digest, str)
            or not _SHA256.fullmatch(digest)
        ):
            raise IdentityError("Candidate manifest file identity is invalid.")
        active.append({"path": path, "mode": mode, "size_bytes": size, "sha256": digest})
    active.sort(key=lambda item: item["path"])
    calculated = _canonical_tree_hash(active)
    if calculated != candidate_hash:
        raise IdentityError("Candidate manifest tree digest does not match.")
    return candidate, active


def verify_candidate_tree(
    root: Path,
    manifest_files: list[dict[str, Any]],
    *,
    require_read_only: bool = True,
) -> tuple[str, dict[str, bytes]]:
    actual, contents = _walk_tree(root, require_read_only=require_read_only)
    expected_physical = [
        {
            "path": record["path"],
            "mode": _normalize_manifest_mode(record["mode"]),
            "size_bytes": record["size_bytes"],
            "sha256": record["sha256"],
        }
        for record in manifest_files
    ]
    if actual != expected_physical:
        raise IdentityError("Candidate files do not match the host-staged manifest.")
    return _canonical_tree_hash(manifest_files), contents


def verify_artifact_manifest(
    verified_inputs: list[tuple[dict[str, Any], bytes]],
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    manifests = []
    for artifact, data in verified_inputs:
        try:
            value = json.loads(data.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
        if isinstance(value, dict) and value.get("v") == 1 and isinstance(value.get("files"), list):
            manifests.append((artifact, data, value))
    if len(manifests) != 1:
        raise IdentityError("Exactly one host-staged candidate manifest is required.")
    artifact, data, value = manifests[0]
    candidate, files = validate_manifest(data)
    return candidate, files, artifact


def tree_digest_from_records(records: list[dict[str, Any]]) -> str:
    normalized = sorted(records, key=lambda item: item["path"])
    return _canonical_tree_hash(normalized)
