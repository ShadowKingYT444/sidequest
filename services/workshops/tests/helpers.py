from __future__ import annotations

import hashlib
import json
import os
import stat
from pathlib import Path
from typing import Any


def readonly_tree(root: Path) -> None:
    for directory, subdirs, files in os.walk(root, topdown=False, followlinks=False):
        for name in files:
            path = Path(directory) / name
            mode = path.stat(follow_symlinks=False).st_mode
            path.chmod(0o555 if mode & stat.S_IXUSR else 0o444)
        for name in subdirs:
            (Path(directory) / name).chmod(0o555)
    root.chmod(0o555)


def writable_tree(root: Path) -> None:
    for directory, subdirs, files in os.walk(root, topdown=True, followlinks=False):
        Path(directory).chmod(0o755)
        for name in files:
            path = Path(directory) / name
            mode = path.stat(follow_symlinks=False).st_mode
            path.chmod(0o755 if mode & stat.S_IXUSR else 0o644)
        for name in subdirs:
            (Path(directory) / name).chmod(0o755)


def manifest_for(root: Path, *, candidate_id: str, source_revision: str) -> dict[str, Any]:
    files = []
    for directory, subdirs, names in os.walk(root, topdown=True, followlinks=False):
        subdirs.sort()
        names.sort()
        for name in names:
            path = Path(directory) / name
            info = path.lstat()
            if not stat.S_ISREG(info.st_mode):
                raise AssertionError("test manifest builder only accepts regular files")
            content = path.read_bytes()
            mode = "100755" if info.st_mode & stat.S_IXUSR else "100644"
            files.append({
                "path": path.relative_to(root).as_posix(),
                "mode": mode,
                "size_bytes": len(content),
                "sha256": hashlib.sha256(content).hexdigest(),
                "status": "unchanged",
            })
    records = [{key: item[key] for key in ("path", "mode", "size_bytes", "sha256")} for item in files]
    records.sort(key=lambda item: item["path"])
    canonical = json.dumps({"v": 1, "files": records}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    tree_hash = hashlib.sha256(canonical).hexdigest()
    return {
        "v": 1,
        "candidate": {
            "id": candidate_id,
            "base_revision": "fixture:base",
            "candidate_revision": source_revision,
            "tree_sha256": tree_hash,
        },
        "files": files,
    }


def write_manifest(path: Path, value: dict[str, Any]) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    path.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def protocol_request(
    *,
    candidate_root: Path,
    manifest_path: Path,
    manifest_sha256: str,
    output_root: Path,
    request_id: str,
    candidate_id: str,
    source_revision: str,
    check_ids: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "v": 1,
        "request_id": request_id,
        "op": "check.run",
        "job_id": "fixture-job-d1",
        "workspace": str(candidate_root),
        "payload": {
            "check_ids": check_ids or ["candidate.frozen_identity", "club.signup.popup_destination"],
            "source_revision": source_revision,
        },
        "context": {
            "source_revision": source_revision,
            "artifact_inputs": [{
                "id": f"manifest:{candidate_id}",
                "sha256": manifest_sha256,
                "staged_path": str(manifest_path),
            }],
            "output_root": str(output_root),
        },
    }
