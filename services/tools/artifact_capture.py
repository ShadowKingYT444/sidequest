"""Freeze a Git candidate into verified artifacts and support exact local delivery."""

from __future__ import annotations

from contextlib import contextmanager
import fcntl
import hashlib
import json
import mimetypes
import os
from pathlib import Path
import re
import stat
import tempfile
import time
import uuid
from typing import Any, Iterable

try:
    from .config import Settings
    from .protocol import AdapterError
    from .git_ops import (
        FileData,
        TreeEntry,
        _canonical_under,
        _repo_root,
        blob_oid,
        changed_names,
        candidate_tree,
        create_candidate_commit,
        ensure_safe_clone,
        git_diff,
        inspect_worktree,
        is_sensitive_path,
        list_tree,
        numstat,
        object_format,
        read_blobs,
        resolve_commit,
        run_git,
        validate_relative_path,
        validate_repo_path,
        validate_workspace_path,
        walk_files,
    )
except ImportError:  # Direct script execution by the adapter host.
    from config import Settings
    from protocol import AdapterError
    from git_ops import (
        FileData,
        TreeEntry,
        _canonical_under,
        _repo_root,
        blob_oid,
        changed_names,
        candidate_tree,
        create_candidate_commit,
        ensure_safe_clone,
        git_diff,
        inspect_worktree,
        is_sensitive_path,
        list_tree,
        numstat,
        object_format,
        read_blobs,
        resolve_commit,
        run_git,
        validate_relative_path,
        validate_repo_path,
        validate_workspace_path,
        walk_files,
    )


_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_OBJECT_ID = re.compile(r"^[0-9a-f]{40,64}$")
_SAFE_ID = re.compile(r"^[A-Za-z0-9._-]{1,128}$")


def _fail(code: str, message: str, retryable: bool = False) -> AdapterError:
    return AdapterError(code, message, retryable)


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def tree_digest(files: Iterable[dict[str, Any]]) -> str:
    normalized = []
    for entry in files:
        if entry.get("status") == "deleted":
            continue
        path = validate_relative_path(entry.get("path"))
        mode = entry.get("mode")
        size = entry.get("size_bytes")
        digest = entry.get("sha256")
        if mode not in {"100644", "100755"} or not isinstance(size, int) or size < 0 or not isinstance(digest, str) or not _SHA256.fullmatch(digest):
            raise _fail("INVALID_INPUT", "Manifest contains invalid tree metadata.")
        normalized.append({"path": path, "mode": mode, "size_bytes": size, "sha256": digest})
    normalized.sort(key=lambda row: row["path"])
    canonical = canonical_json({"v": 1, "files": normalized})
    return hashlib.sha256(canonical).hexdigest()


def _hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _checked_output_root(raw: str, settings: Settings, workspace: Path) -> Path:
    output_root = _canonical_under(raw, settings.artifact_roots, must_exist=False)
    try:
        output_root.relative_to(workspace)
        raise _fail("POLICY_DENIED", "Artifact output cannot be inside the mutable candidate workspace.")
    except ValueError:
        pass
    try:
        workspace.relative_to(output_root)
        raise _fail("POLICY_DENIED", "Artifact output cannot contain the mutable candidate workspace.")
    except ValueError:
        pass
    _ensure_directory(output_root, settings.artifact_roots[0] if _is_within(output_root, settings.artifact_roots[0]) else next(root for root in settings.artifact_roots if _is_within(output_root, root)))
    output_root = _canonical_under(str(output_root), settings.artifact_roots, must_exist=True)
    if not output_root.is_dir():
        raise _fail("POLICY_DENIED", "Artifact output root must be a directory.")
    return output_root


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root.resolve(strict=False))
        return True
    except ValueError:
        return False


def _ensure_directory(path: Path, root: Path) -> None:
    canonical_root = root.resolve(strict=False)
    try:
        relative = path.relative_to(canonical_root)
    except ValueError as exc:
        raise _fail("POLICY_DENIED", "Output directory is outside its configured root.") from exc
    cursor = canonical_root
    if not cursor.exists():
        cursor.mkdir(parents=True, exist_ok=True, mode=0o700)
    info = cursor.lstat()
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
        raise _fail("POLICY_DENIED", "Configured output root must be a real directory.")
    for component in relative.parts:
        cursor = cursor / component
        try:
            cursor.mkdir(mode=0o700)
        except FileExistsError:
            pass
        except OSError as exc:
            raise _fail("POLICY_DENIED", "Output directory could not be created safely.") from exc
        try:
            info = cursor.lstat()
        except OSError as exc:
            raise _fail("POLICY_DENIED", "Output directory could not be inspected safely.") from exc
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise _fail("POLICY_DENIED", "Output paths cannot contain symlinks or files.")


def _write_immutable(path: Path, data: bytes, mode: int = 0o400) -> None:
    # Callers provide content-addressed paths below a checked root; recheck the
    # parent components so a pre-created symlink cannot redirect the write.
    base = None
    for ancestor in (path.parent, *path.parents):
        if ancestor == ancestor.parent:
            break
        if ancestor.exists() and not ancestor.is_symlink():
            base = ancestor
            break
    if base is None:
        raise _fail("POLICY_DENIED", "Artifact output parent is unavailable.")
    _ensure_directory(path.parent, base)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(path, flags, mode)
    except FileExistsError:
        info = path.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_nlink > 1:
            raise _fail("POLICY_DENIED", "Artifact output path is not a regular file.")
        existing = _read_regular_file(path, len(data))
        if existing != data:
            raise _fail("POLICY_DENIED", "Immutable artifact path already contains different bytes.")
        return
    try:
        view = memoryview(data)
        while view:
            written = os.write(fd, view)
            view = view[written:]
        os.fsync(fd)
    finally:
        os.close(fd)
    os.chmod(path, mode, follow_symlinks=False)


def _read_regular_file(path: Path, limit: int) -> bytes:
    try:
        info = path.lstat()
    except OSError as exc:
        raise _fail("POLICY_DENIED", "Staged artifact path could not be inspected.") from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode) or info.st_nlink > 1 or info.st_size > limit:
        raise _fail("POLICY_DENIED", "Staged artifact must be a bounded regular file.")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags)
        try:
            current = os.fstat(fd)
            if not stat.S_ISREG(current.st_mode) or current.st_nlink > 1 or current.st_size > limit:
                raise _fail("POLICY_DENIED", "Staged artifact changed while it was inspected.")
            data = bytearray()
            while len(data) <= limit:
                chunk = os.read(fd, min(1024 * 1024, limit + 1 - len(data)))
                if not chunk:
                    break
                data.extend(chunk)
            if len(data) > limit or len(data) != current.st_size:
                raise _fail("POLICY_DENIED", "Staged artifact changed while it was read.")
            return bytes(data)
        finally:
            os.close(fd)
    except AdapterError:
        raise
    except OSError as exc:
        raise _fail("POLICY_DENIED", "Staged artifact could not be read safely.") from exc


def _write_candidate_snapshot(root: Path, candidate_id: str, files: dict[str, FileData]) -> Path:
    snapshot = root / f"candidate-{candidate_id}"
    try:
        snapshot.mkdir(mode=0o700)
    except FileExistsError as exc:
        raise _fail("POLICY_DENIED", "Candidate snapshot path already exists.") from exc
    directories = {snapshot}
    for rel, file in sorted(files.items()):
        validate_relative_path(rel)
        target = snapshot.joinpath(*rel.split("/"))
        parent = target.parent
        chain: list[Path] = []
        while parent != snapshot:
            chain.append(parent)
            parent = parent.parent
        for directory in reversed(chain):
            if directory not in directories:
                directory.mkdir(mode=0o700)
                directories.add(directory)
        # Candidate data has already been scanned and is copied without following links.
        _write_immutable(target, file.data, 0o555 if file.mode == "100755" else 0o444)
    for directory in sorted(directories, key=lambda item: len(item.parts), reverse=True):
        os.chmod(directory, 0o555, follow_symlinks=False)
    return snapshot


def _artifact_record(
    *,
    artifact_id: str,
    kind: str,
    digest: str,
    job_id: str,
    source_revision: str,
    relative_path: str,
    data: bytes,
    candidate_id: str,
    run_id: str | None,
    media_type: str,
    display_name: str,
) -> dict[str, Any]:
    return {
        "id": artifact_id,
        "kind": kind,
        "sha256": digest,
        "job_id": job_id,
        "source_revision": source_revision,
        "relative_path": relative_path,
        "candidate_id": candidate_id,
        "run_id": run_id,
        "media_type": media_type,
        "size_bytes": len(data),
        "immutable": True,
        "display_name": display_name,
    }


def _write_artifact(
    root: Path,
    *,
    artifact_id: str,
    kind: str,
    extension: str,
    media_type: str,
    data: bytes,
    job_id: str,
    source_revision: str,
    candidate_id: str,
    run_id: str | None,
    display_name: str,
) -> dict[str, Any]:
    digest = _hash_bytes(data)
    relative = f"artifacts/{kind}-{digest}.{extension}"
    _ensure_directory(root / "artifacts", root)
    _write_immutable(root / relative, data)
    return _artifact_record(
        artifact_id=artifact_id,
        kind=kind,
        digest=digest,
        job_id=job_id,
        source_revision=source_revision,
        relative_path=relative,
        data=data,
        candidate_id=candidate_id,
        run_id=run_id,
        media_type=media_type,
        display_name=display_name,
    )


def _changed_scope(write_paths: Any, changed: list[tuple[str, str, str | None]]) -> tuple[str, ...]:
    if not isinstance(write_paths, list) or not write_paths or any(not isinstance(item, str) for item in write_paths):
        raise _fail("POLICY_DENIED", "A host-assigned write scope is required.")
    prefixes: list[str] = []
    for prefix in write_paths:
        normalized = prefix.rstrip("/")
        prefixes.append(validate_relative_path(normalized))
    for status, path, old_path in changed:
        for candidate_path in (path, old_path):
            if candidate_path is None:
                continue
            if not any(candidate_path == prefix or candidate_path.startswith(prefix + "/") for prefix in prefixes):
                raise _fail("POLICY_DENIED", "Candidate changes extend outside the assigned write scope.")
    return tuple(prefixes)


def freeze_candidate(request: dict[str, Any], settings: Settings) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    payload = request["payload"]
    context = request.get("context", {})
    required_payload = {"base_revision", "write_paths"}
    if set(payload) != required_payload:
        raise _fail("INVALID_INPUT", "artifacts.freeze requires base_revision and write_paths.")
    if payload["base_revision"] != context.get("source_revision"):
        raise _fail("POLICY_DENIED", "Candidate base revision does not match the host-assigned source revision.")
    if payload["write_paths"] != context.get("write_paths"):
        raise _fail("POLICY_DENIED", "Candidate write scope does not match host assignment.")
    base_revision = context.get("source_revision")
    if not isinstance(base_revision, str) or not _OBJECT_ID.fullmatch(base_revision):
        raise _fail("INVALID_INPUT", "Host-assigned source revision must be a full commit identifier.")
    workspace = validate_workspace_path(request["workspace"], settings.staging_roots, must_exist=True)
    output_raw = context.get("output_root")
    if not isinstance(output_raw, str):
        raise _fail("POLICY_DENIED", "Host-assigned artifact output root is required.")
    output_root = _checked_output_root(output_raw, settings, workspace)
    repo = validate_repo_path(str(workspace), settings.staging_roots)
    # Reset potentially worker-edited config before interpreting Git metadata.
    ensure_safe_clone(repo, settings)
    resolved_base = resolve_commit(repo, base_revision, settings)
    if resolved_base != base_revision.lower():
        raise _fail("POLICY_DENIED", "Workspace source revision no longer matches the assigned base.")
    head = run_git(repo, ["rev-parse", "--verify", "HEAD^{commit}"], settings=settings, output_limit=4096).decode("ascii").strip().lower()
    if head != resolved_base:
        raise _fail("POLICY_DENIED", "Candidate workspace HEAD moved from the assigned base.")
    base_entries = list_tree(repo, resolved_base, settings)
    base_blobs = read_blobs(repo, base_entries.values(), settings)
    candidate_files = walk_files(repo, settings)
    if sum(len(file.data) for file in candidate_files.values()) > settings.max_total_bytes:
        raise _fail("POLICY_DENIED", "Candidate exceeds the configured 100 MiB limit.")
    tree, object_ids = candidate_tree(repo, resolved_base, candidate_files, settings)
    candidate_revision = create_candidate_commit(repo, tree, resolved_base, settings)
    changes = changed_names(repo, resolved_base, candidate_revision, settings)
    _changed_scope(context.get("write_paths"), changes)
    if len(changes) > settings.max_files:
        raise _fail("POLICY_DENIED", "Candidate exceeds the 1,000 changed-file limit.")
    raw_patch = git_diff(repo, resolved_base, candidate_revision, settings, binary=True)
    human_diff = git_diff(repo, resolved_base, candidate_revision, settings, binary=False)
    if len(raw_patch) > settings.max_total_bytes:
        raise _fail("POLICY_DENIED", "Candidate patch exceeds the configured size limit.")
    stats = numstat(repo, resolved_base, candidate_revision, settings)
    change_by_new: dict[str, tuple[str, str | None]] = {}
    deleted: dict[str, str] = {}
    renamed_old: set[str] = set()
    for status, path, old_path in changes:
        if status == "D":
            deleted[path] = status
        elif status == "R":
            change_by_new[path] = ("renamed", old_path)
            if old_path:
                renamed_old.add(old_path)
        elif status == "A":
            change_by_new[path] = ("added", None)
        else:
            change_by_new[path] = ("modified", None)
    manifest_files: list[dict[str, Any]] = []
    tree_rows: list[dict[str, Any]] = []
    candidate_id = "cand_" + uuid.uuid4().hex
    for path in sorted(candidate_files):
        file = candidate_files[path]
        status, old_path = change_by_new.get(path, ("unchanged", None))
        base = base_entries.get(path)
        line_counts = stats.get(path, (0, 0))
        binary = b"\x00" in file.data or _not_utf8(file.data)
        row: dict[str, Any] = {
            "file_id": "f_" + hashlib.sha256((candidate_id + "\x00" + path).encode("utf-8")).hexdigest()[:32],
            "path": path,
            "old_path": old_path,
            "status": status,
            "media_type": _media_type(path, file.data),
            "size_bytes": len(file.data),
            "sha256": _hash_bytes(file.data),
            "added_lines": line_counts[0],
            "deleted_lines": line_counts[1],
            "binary": binary,
            "mode": file.mode,
        }
        if base and base.mode != file.mode:
            row["old_mode"] = base.mode
        manifest_files.append(row)
        tree_rows.append({"path": path, "mode": file.mode, "size_bytes": len(file.data), "sha256": row["sha256"]})
    for path in sorted(deleted):
        if path in renamed_old:
            continue
        entry = base_entries[path]
        content = base_blobs[path]
        line_counts = stats.get(path, (0, 0))
        manifest_files.append({
            "file_id": "f_" + hashlib.sha256((candidate_id + "\x00" + path).encode("utf-8")).hexdigest()[:32],
            "path": path,
            "old_path": None,
            "status": "deleted",
            "media_type": _media_type(path, content),
            "size_bytes": len(content),
            "sha256": None,
            "added_lines": line_counts[0],
            "deleted_lines": line_counts[1],
            "binary": b"\x00" in content or _not_utf8(content),
            "mode": entry.mode,
        })
    manifest_files.sort(key=lambda item: item["path"])
    tree_sha = tree_digest(tree_rows)
    patch_sha = _hash_bytes(raw_patch)
    manifest_id = "art_" + uuid.uuid4().hex
    diff_id = "art_" + uuid.uuid4().hex
    patch_id = "art_" + uuid.uuid4().hex
    candidate = {
        "id": candidate_id,
        "project_id": context.get("project_id"),
        "base_revision": resolved_base,
        "candidate_revision": candidate_revision,
        "tree_sha256": tree_sha,
        "patch_sha256": patch_sha,
        "manifest_artifact_id": manifest_id,
        "verified_check_ids": [],
    }
    manifest = {"v": 1, "candidate": candidate, "files": manifest_files}
    manifest_bytes = canonical_json(manifest) + b"\n"
    snapshot_root = _write_candidate_snapshot(output_root, candidate_id, candidate_files)
    artifacts = [
        _write_artifact(
            output_root,
            artifact_id=manifest_id,
            kind="file_manifest",
            extension="json",
            media_type="application/json",
            data=manifest_bytes,
            job_id=request["job_id"],
            source_revision=resolved_base,
            candidate_id=candidate_id,
            run_id=context.get("run_id") if isinstance(context.get("run_id"), str) else None,
            display_name="Frozen candidate manifest",
        ),
        _write_artifact(
            output_root,
            artifact_id=diff_id,
            kind="diff",
            extension="diff",
            media_type="text/x-diff; charset=utf-8",
            data=human_diff,
            job_id=request["job_id"],
            source_revision=resolved_base,
            candidate_id=candidate_id,
            run_id=context.get("run_id") if isinstance(context.get("run_id"), str) else None,
            display_name="Frozen candidate diff",
        ),
        _write_artifact(
            output_root,
            artifact_id=patch_id,
            kind="patch",
            extension="patch",
            media_type="application/x-git-patch",
            data=raw_patch,
            job_id=request["job_id"],
            source_revision=resolved_base,
            candidate_id=candidate_id,
            run_id=context.get("run_id") if isinstance(context.get("run_id"), str) else None,
            display_name="Frozen candidate patch",
        ),
    ]
    data = {
        "candidate": candidate,
        "manifest_artifact_id": manifest_id,
        "diff_artifact_id": diff_id,
        "patch_artifact_id": patch_id,
        "snapshot_root": str(snapshot_root),
    }
    return data, artifacts


def _not_utf8(data: bytes) -> bool:
    try:
        data.decode("utf-8", "strict")
        return False
    except UnicodeDecodeError:
        return True


def _media_type(path: str, data: bytes) -> str:
    if b"\x00" in data or _not_utf8(data):
        return "application/octet-stream"
    return mimetypes.guess_type(path)[0] or "text/plain"


def _load_artifact_inputs(context: dict[str, Any], settings: Settings, workspace: Path) -> dict[str, tuple[dict[str, Any], bytes]]:
    raw_inputs = context.get("artifact_inputs")
    if not isinstance(raw_inputs, list):
        raise _fail("POLICY_DENIED", "Host-staged artifact inputs are required.")
    roots = tuple(settings.staging_roots) + tuple(settings.artifact_roots)
    result: dict[str, tuple[dict[str, Any], bytes]] = {}
    for item in raw_inputs:
        if not isinstance(item, dict) or set(item) != {"id", "sha256", "staged_path"}:
            raise _fail("INVALID_INPUT", "Staged artifact metadata is malformed.")
        artifact_id, digest, raw_path = item["id"], item["sha256"], item["staged_path"]
        if not isinstance(artifact_id, str) or not artifact_id or not isinstance(digest, str) or not _SHA256.fullmatch(digest) or not isinstance(raw_path, str):
            raise _fail("INVALID_INPUT", "Staged artifact metadata is malformed.")
        if artifact_id in result:
            raise _fail("INVALID_INPUT", "Staged artifact IDs must be unique.")
        path = _canonical_under(raw_path, roots, must_exist=True)
        if _is_within(path, workspace) or _is_within(workspace, path):
            raise _fail("POLICY_DENIED", "Host-staged artifacts must be separate from the mutable worker workspace.")
        data = _read_regular_file(path, settings.max_total_bytes)
        if _hash_bytes(data) != digest:
            raise _fail("POLICY_DENIED", "A staged artifact digest does not match its host record.")
        result[artifact_id] = (item, data)
    return result


def _strict_json(data: bytes, message: str) -> dict[str, Any]:
    try:
        value = json.loads(data.decode("utf-8"), object_pairs_hook=_unique_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise _fail("INVALID_INPUT", message) from exc
    if not isinstance(value, dict):
        raise _fail("INVALID_INPUT", message)
    return value


def _unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate key")
        result[key] = value
    return result


def _manifest_tree_rows(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    raw_files = manifest.get("files")
    if manifest.get("v") != 1 or not isinstance(raw_files, list):
        raise _fail("INVALID_INPUT", "Candidate manifest is invalid.")
    rows: list[dict[str, Any]] = []
    paths: set[str] = set()
    for item in raw_files:
        if not isinstance(item, dict):
            raise _fail("INVALID_INPUT", "Candidate manifest contains an invalid file row.")
        path = validate_relative_path(item.get("path"))
        if is_sensitive_path(path) or path in paths:
            raise _fail("POLICY_DENIED", "Candidate manifest contains an unsafe or duplicate path.")
        paths.add(path)
        if item.get("status") == "deleted":
            if item.get("sha256") is not None:
                raise _fail("INVALID_INPUT", "Deleted candidate rows cannot have a content digest.")
            continue
        mode, size, digest = item.get("mode"), item.get("size_bytes"), item.get("sha256")
        if mode not in {"100644", "100755"} or not isinstance(size, int) or size < 0 or not isinstance(digest, str) or not _SHA256.fullmatch(digest):
            raise _fail("INVALID_INPUT", "Candidate manifest contains invalid tree metadata.")
        rows.append({"path": path, "mode": mode, "size_bytes": size, "sha256": digest})
    return rows


def _approval_record(context: dict[str, Any], settings: Settings, workspace: Path) -> dict[str, Any]:
    ref = context.get("approval_record")
    if not isinstance(ref, dict) or set(ref) != {"id", "sha256", "staged_path"}:
        raise _fail("POLICY_DENIED", "A separate host-staged approval record is required.")
    if not isinstance(ref["id"], str) or not ref["id"] or not isinstance(ref["sha256"], str) or not _SHA256.fullmatch(ref["sha256"]) or not isinstance(ref["staged_path"], str):
        raise _fail("POLICY_DENIED", "Host-staged approval reference is malformed.")
    if not settings.approval_root.exists():
        raise _fail("POLICY_DENIED", "Configured approval root is unavailable.")
    approval_root = _canonical_under(str(settings.approval_root), (settings.approval_root,), must_exist=True)
    if not approval_root.is_dir():
        raise _fail("POLICY_DENIED", "Configured approval root must be a directory.")
    if _is_within(approval_root, workspace) or _is_within(workspace, approval_root):
        raise _fail("POLICY_DENIED", "Approval storage must be separate from the worker workspace.")
    path = _canonical_under(ref["staged_path"], (approval_root,), must_exist=True)
    try:
        path.relative_to(workspace)
        raise _fail("POLICY_DENIED", "Approval records must be outside the worker workspace.")
    except ValueError:
        pass
    raw = _read_regular_file(path, 1024 * 1024)
    if _hash_bytes(raw) != ref["sha256"]:
        raise _fail("POLICY_DENIED", "Host approval record digest does not match.")
    record = _strict_json(raw, "Host approval record is not valid JSON.")
    if record.get("id") != ref["id"] or record.get("state") != "approved":
        raise _fail("POLICY_DENIED", "Host approval record is missing or not approved.")
    return record


def _state_paths(settings: Settings, delivery_id: str) -> tuple[Path, Path]:
    if not isinstance(delivery_id, str) or not _SAFE_ID.fullmatch(delivery_id):
        raise _fail("INVALID_INPUT", "delivery_id must be a bounded stable identifier.")
    root = _canonical_under(str(settings.delivery_state_root), (settings.delivery_state_root,), must_exist=False)
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    root = _canonical_under(str(root), (root,), must_exist=True)
    if not root.is_dir():
        raise _fail("POLICY_DENIED", "Delivery state root must be a directory.")
    suffix = hashlib.sha256(delivery_id.encode("utf-8")).hexdigest()
    return root / f"{suffix}.json", root / f"{suffix}.lock"


@contextmanager
def _exclusive_lock(path: Path):
    fd = os.open(path, os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def _write_state(path: Path, value: dict[str, Any]) -> None:
    data = canonical_json(value) + b"\n"
    temporary = path.with_name(path.name + ".tmp-" + uuid.uuid4().hex)
    _write_immutable(temporary, data, 0o600)
    os.replace(temporary, path)
    directory_fd = os.open(path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0))
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def _read_state(path: Path) -> dict[str, Any] | None:
    try:
        path.lstat()
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise _fail("UNCERTAIN_OUTCOME", "Stored delivery state is not safely readable.") from exc
    try:
        data = _read_regular_file(path, 1024 * 1024)
    except AdapterError as exc:
        raise _fail("UNCERTAIN_OUTCOME", "Stored delivery state is not safely readable.") from exc
    try:
        return _strict_json(data, "Stored delivery state is invalid.")
    except AdapterError as exc:
        raise _fail("UNCERTAIN_OUTCOME", "Stored delivery state is corrupt; host reconciliation is required.") from exc


def _index_entries(repo: Path, index_path: Path, settings: Settings) -> dict[str, TreeEntry]:
    raw = run_git(repo, ["ls-files", "-s", "-z"], settings=settings, extra_env={"GIT_INDEX_FILE": str(index_path)})
    result: dict[str, TreeEntry] = {}
    for record in raw.split(b"\x00"):
        if not record:
            continue
        try:
            metadata, raw_path = record.split(b"\t", 1)
            mode_b, oid_b, stage_b = metadata.split(b" ", 2)
            path = raw_path.decode("utf-8", "strict")
            mode = mode_b.decode("ascii")
            oid = oid_b.decode("ascii").lower()
            stage = int(stage_b)
        except (ValueError, UnicodeDecodeError) as exc:
            raise _fail("INVALID_INPUT", "Git index contains malformed path data.") from exc
        validate_relative_path(path)
        if stage != 0 or mode not in {"100644", "100755"} or not _OBJECT_ID.fullmatch(oid) or path in result:
            raise _fail("POLICY_DENIED", "Git index contains an unsupported file entry.")
        result[path] = TreeEntry(mode, oid, path)
    return result


def _verify_manifest_index(
    repo: Path,
    index_path: Path,
    manifest: dict[str, Any],
    expected_tree_digest: str,
    settings: Settings,
) -> str:
    entries = _index_entries(repo, index_path, settings)
    blobs = read_blobs(repo, entries.values(), settings)
    manifest_rows = _manifest_tree_rows(manifest)
    expected = {row["path"]: row for row in manifest_rows}
    if set(entries) != set(expected):
        raise _fail("POLICY_DENIED", "Candidate patch does not produce the approved manifest file set.")
    digest_rows = []
    for path, entry in entries.items():
        content = blobs[path]
        row = expected[path]
        digest = _hash_bytes(content)
        if entry.mode != row["mode"] or len(content) != row["size_bytes"] or digest != row["sha256"]:
            raise _fail("POLICY_DENIED", "Candidate patch bytes or modes do not match the approved manifest.")
        digest_rows.append({"path": path, "mode": entry.mode, "size_bytes": len(content), "sha256": digest})
    recomputed = tree_digest(digest_rows)
    if recomputed != expected_tree_digest:
        raise _fail("POLICY_DENIED", "Candidate tree digest does not match the approved identity.")
    return run_git(repo, ["write-tree"], settings=settings, extra_env={"GIT_INDEX_FILE": str(index_path)}, output_limit=256).decode("ascii").strip().lower()


def _reproduce_candidate_commit(repo: Path, tree: str, parent: str, settings: Settings) -> str:
    fixed_identity = {
        "GIT_AUTHOR_NAME": "Sidequest Candidate",
        "GIT_AUTHOR_EMAIL": "sidequest-local@invalid",
        "GIT_COMMITTER_NAME": "Sidequest Candidate",
        "GIT_COMMITTER_EMAIL": "sidequest-local@invalid",
        "GIT_AUTHOR_DATE": "2000-01-01T00:00:00+0000",
        "GIT_COMMITTER_DATE": "2000-01-01T00:00:00+0000",
    }
    return run_git(
        repo,
        ["commit-tree", tree, "-p", parent],
        input_data=b"Sidequest frozen candidate\n",
        settings=settings,
        extra_env=fixed_identity,
        output_limit=256,
    ).decode("ascii", "strict").strip().lower()


def _verify_destination_worktree(repo: Path, expected: dict[str, TreeEntry], settings: Settings) -> None:
    actual = walk_files(repo, settings)
    if set(actual) != set(expected):
        raise _fail("UNCERTAIN_OUTCOME", "Delivered worktree does not match the approved candidate.")
    fmt = object_format(repo, settings)
    for path, entry in expected.items():
        file = actual[path]
        if file.mode != entry.mode or blob_oid(file.data, fmt) != entry.oid:
            raise _fail("UNCERTAIN_OUTCOME", "Delivered worktree does not match the approved candidate.")


def _safe_parent_directory(root: Path, relative: str) -> Path:
    validate_relative_path(relative)
    parts = relative.split("/")[:-1]
    current = root
    for part in parts:
        current = current / part
        try:
            info = current.lstat()
        except FileNotFoundError:
            try:
                current.mkdir(mode=0o755)
                info = current.lstat()
            except OSError as exc:
                raise _fail("UNCERTAIN_OUTCOME", "Destination directory could not be created safely.") from exc
        except OSError as exc:
            raise _fail("UNCERTAIN_OUTCOME", "Destination directory could not be inspected safely.") from exc
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise _fail("POLICY_DENIED", "Destination path contains a symlink or non-directory.")
    return current


def _write_delivery_file(root: Path, path: str, content: bytes, mode: str) -> None:
    parent = _safe_parent_directory(root, path)
    target = parent / path.rsplit("/", 1)[-1]
    try:
        info = target.lstat()
    except FileNotFoundError:
        info = None
    except OSError as exc:
        raise _fail("UNCERTAIN_OUTCOME", "Destination file could not be inspected safely.") from exc
    if info is not None and (stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode) or info.st_nlink > 1):
        raise _fail("POLICY_DENIED", "Destination file is a symlink, special file or hard link.")
    temporary = parent / (".sidequest-" + uuid.uuid4().hex + ".tmp")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(temporary, flags, 0o600)
    try:
        view = memoryview(content)
        while view:
            written = os.write(fd, view)
            view = view[written:]
        os.fchmod(fd, 0o755 if mode == "100755" else 0o644)
        os.fsync(fd)
    finally:
        os.close(fd)
    os.replace(temporary, target)


def _remove_delivery_file(root: Path, path: str) -> None:
    parent = _safe_parent_directory(root, path)
    target = parent / path.rsplit("/", 1)[-1]
    try:
        info = target.lstat()
    except FileNotFoundError:
        raise _fail("UNCERTAIN_OUTCOME", "Expected destination file disappeared during delivery.")
    except OSError as exc:
        raise _fail("UNCERTAIN_OUTCOME", "Destination file could not be inspected safely.") from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode) or info.st_nlink > 1:
        raise _fail("POLICY_DENIED", "Destination file is a symlink, special file or hard link.")
    target.unlink()


def _install_index(repo: Path, source_index: Path) -> None:
    metadata = repo / ".git"
    index = metadata / "index"
    lock = metadata / "index.lock"
    try:
        info = metadata.lstat()
    except OSError as exc:
        raise _fail("UNCERTAIN_OUTCOME", "Destination Git metadata disappeared during delivery.") from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
        raise _fail("POLICY_DENIED", "Destination Git metadata must be a local directory.")
    try:
        index_info = index.lstat()
        if stat.S_ISLNK(index_info.st_mode) or not stat.S_ISREG(index_info.st_mode):
            raise _fail("POLICY_DENIED", "Destination Git index must be a regular file.")
    except FileNotFoundError:
        pass
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(lock, flags, 0o600)
    except FileExistsError as exc:
        raise _fail("POLICY_DENIED", "Destination Git index is locked by another operation.", retryable=True) from exc
    try:
        with source_index.open("rb") as source:
            while True:
                chunk = source.read(1024 * 1024)
                if not chunk:
                    break
                view = memoryview(chunk)
                while view:
                    written = os.write(fd, view)
                    view = view[written:]
        os.fchmod(fd, 0o644)
        os.fsync(fd)
    finally:
        os.close(fd)
    os.replace(lock, index)


def deliver_candidate(request: dict[str, Any], settings: Settings) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    payload = request["payload"]
    context = request.get("context", {})
    required = {"patch_artifact_id", "artifact_sha256", "source_revision", "destination", "approval"}
    if set(payload) != required:
        raise _fail("INVALID_INPUT", "repo.deliver payload fields do not match protocol v1.")
    delivery_id = context.get("delivery_id")
    action_id = context.get("action_id")
    if not isinstance(delivery_id, str) or not isinstance(action_id, str) or delivery_id != action_id:
        raise _fail("POLICY_DENIED", "Host delivery_id and action_id must match.")
    workspace = validate_workspace_path(request["workspace"], settings.staging_roots, must_exist=True)
    approval = _approval_record(context, settings, workspace)
    approval_identity = payload["approval"]
    if not isinstance(approval_identity, dict):
        raise _fail("POLICY_DENIED", "Approval identity metadata is required.")
    inputs = _load_artifact_inputs(context, settings, workspace)
    patch_id = payload["patch_artifact_id"]
    if patch_id not in inputs or inputs[patch_id][0]["sha256"] != payload["artifact_sha256"]:
        raise _fail("POLICY_DENIED", "Patch artifact is not present in host-staged inputs.")
    patch_bytes = inputs[patch_id][1]
    manifest_id = approval.get("manifest_artifact_id")
    if not isinstance(manifest_id, str) or manifest_id not in inputs:
        raise _fail("POLICY_DENIED", "Approved manifest is not present in host-staged inputs.")
    manifest = _strict_json(inputs[manifest_id][1], "Candidate manifest is not valid JSON.")
    candidate = manifest.get("candidate")
    if not isinstance(candidate, dict) or candidate.get("id") != approval.get("candidate_id"):
        raise _fail("POLICY_DENIED", "Candidate manifest identity does not match host approval.")
    candidate_id = candidate["id"]
    candidate_revision = candidate.get("candidate_revision")
    source_revision = payload["source_revision"]
    patch_sha = _hash_bytes(patch_bytes)
    tree_sha = tree_digest(_manifest_tree_rows(manifest))
    destination_raw = payload["destination"]
    destination = _canonical_under(destination_raw, settings.delivery_roots, must_exist=True)
    destination = validate_repo_path(str(destination), settings.delivery_roots)
    if _is_within(destination, workspace) or _is_within(workspace, destination):
        raise _fail("POLICY_DENIED", "Delivery destination must be separate from the worker workspace.")
    _repo_root(destination, settings)
    expected_identity = {
        "id": approval.get("id"),
        "candidate_id": candidate_id,
        "candidate_revision": candidate_revision,
        "candidate_tree_sha256": tree_sha,
        "patch_sha256": patch_sha,
        "source_revision": source_revision,
        "action": "local_deliver",
        "action_id": action_id,
        "delivery_id": delivery_id,
        "destination": str(destination),
        "manifest_artifact_id": manifest_id,
    }
    if approval.get("action") != "local_deliver" or approval.get("state") != "approved":
        raise _fail("POLICY_DENIED", "Host approval is not for an approved local delivery.")
    for key, expected_value in expected_identity.items():
        if approval.get(key) != expected_value:
            raise _fail("POLICY_DENIED", f"Host approval does not match {key}.")
    if source_revision != candidate.get("base_revision") or candidate.get("tree_sha256") != tree_sha or candidate.get("patch_sha256") != patch_sha:
        raise _fail("POLICY_DENIED", "Patch and manifest do not match the frozen candidate identity.")
    host_scope = context.get("write_paths")
    scope_changes = []
    for row in manifest.get("files", []):
        if isinstance(row, dict) and row.get("status") != "unchanged":
            scope_changes.append((str(row.get("status")), row.get("path"), row.get("old_path") if row.get("status") == "renamed" else None))
    _changed_scope(host_scope, scope_changes)
    for key, value in {
        "id": approval.get("id"),
        "candidate_id": candidate_id,
        "candidate_revision": candidate_revision,
        "candidate_tree_sha256": tree_sha,
        "source_revision": source_revision,
        "action": "local_deliver",
        "destination": str(destination),
    }.items():
        if approval_identity.get(key) != value:
            raise _fail("POLICY_DENIED", f"Caller approval identity does not match {key}.")
    if not isinstance(candidate_revision, str) or not _OBJECT_ID.fullmatch(candidate_revision):
        raise _fail("INVALID_INPUT", "Candidate revision is invalid.")
    if not isinstance(source_revision, str) or not _OBJECT_ID.fullmatch(source_revision):
        raise _fail("INVALID_INPUT", "Source revision is invalid.")
    fingerprint = _hash_bytes(canonical_json({
        "delivery_id": delivery_id,
        "action_id": action_id,
        "candidate_id": candidate_id,
        "candidate_revision": candidate_revision,
        "tree_sha256": tree_sha,
        "patch_sha256": patch_sha,
        "source_revision": source_revision,
        "destination": str(destination),
        "approval_id": approval.get("id"),
    }))
    state_path, lock_path = _state_paths(settings, delivery_id)
    state_root = Path(settings.delivery_state_root).resolve(strict=False)
    if _is_within(state_root, workspace) or _is_within(workspace, state_root):
        raise _fail("POLICY_DENIED", "Delivery state storage must be separate from the worker workspace.")
    with _exclusive_lock(lock_path):
        old = _read_state(state_path)
        if old is not None:
            if old.get("fingerprint") != fingerprint:
                raise _fail("POLICY_DENIED", "delivery_id was already used for a different action.")
            if old.get("status") == "completed":
                return {"status": "delivered", "delivery_id": delivery_id}, []
            raise _fail("UNCERTAIN_OUTCOME", "A prior local delivery has an uncertain outcome and must be reconciled by the host.")
        head = resolve_commit(destination, "HEAD", settings)
        if head != source_revision.lower():
            raise _fail("POLICY_DENIED", "Destination HEAD no longer matches the approved source revision.")
        destination_entries, _, clean = inspect_worktree(destination, head, settings)
        if not clean:
            raise _fail("POLICY_DENIED", "Destination repository must be clean before delivery.")
        temp_index = Path(settings.delivery_state_root) / f".preflight-{uuid.uuid4().hex}.index"
        env = {"GIT_INDEX_FILE": str(temp_index)}
        try:
            run_git(destination, ["read-tree", head], settings=settings, extra_env=env, output_limit=4096)
            run_git(destination, ["apply", "--cached", "--check", "--binary", "--"], input_data=patch_bytes, settings=settings, extra_env=env)
            run_git(destination, ["apply", "--cached", "--binary", "--"], input_data=patch_bytes, settings=settings, extra_env=env)
            candidate_git_tree = _verify_manifest_index(destination, temp_index, manifest, tree_sha, settings)
            reproduced_commit = _reproduce_candidate_commit(destination, candidate_git_tree, source_revision, settings)
            if reproduced_commit != candidate_revision.lower():
                raise _fail("POLICY_DENIED", "Candidate commit does not match the approved candidate revision.")
            expected_entries = _index_entries(destination, temp_index, settings)
            expected_blobs = read_blobs(destination, expected_entries.values(), settings)
        except Exception:
            try:
                temp_index.unlink()
            except OSError:
                pass
            raise
        state = {"v": 1, "delivery_id": delivery_id, "action_id": action_id, "fingerprint": fingerprint, "status": "started", "destination": str(destination), "candidate_id": candidate_id, "started_at": time.time()}
        try:
            _write_state(state_path, state)
        except Exception:
            try:
                temp_index.unlink()
            except OSError:
                pass
            raise
        try:
            # Revalidate after the durable uncertain marker and as close as possible to the write.
            destination = validate_repo_path(
                str(_canonical_under(str(destination), settings.delivery_roots, must_exist=True)),
                settings.delivery_roots,
            )
            _repo_root(destination, settings)
            head_again = resolve_commit(destination, "HEAD", settings)
            _, _, clean_again = inspect_worktree(destination, head_again, settings)
            if head_again != source_revision.lower() or not clean_again:
                raise _fail("UNCERTAIN_OUTCOME", "Destination changed after delivery was staged; host reconciliation is required.")
            base_entries_again, _, _ = inspect_worktree(destination, head_again, settings)
            _install_index(destination, temp_index)
            for path in sorted(set(base_entries_again) - set(expected_entries)):
                _remove_delivery_file(destination, path)
            for path, entry in sorted(expected_entries.items()):
                old = base_entries_again.get(path)
                if old is None or old.oid != entry.oid or old.mode != entry.mode:
                    _write_delivery_file(destination, path, expected_blobs[path], entry.mode)
            _verify_destination_worktree(destination, expected_entries, settings)
            installed_entries = _index_entries(destination, destination / ".git" / "index", settings)
            if installed_entries != expected_entries:
                raise _fail("UNCERTAIN_OUTCOME", "Installed Git index does not match the approved candidate.")
            completed = dict(state)
            completed["status"] = "completed"
            completed["completed_at"] = time.time()
            _write_state(state_path, completed)
        except AdapterError as exc:
            if exc.code == "UNCERTAIN_OUTCOME":
                raise
            raise _fail("UNCERTAIN_OUTCOME", "Local delivery may have started; host reconciliation is required.") from exc
        except Exception as exc:
            raise _fail("UNCERTAIN_OUTCOME", "Local delivery may have started; host reconciliation is required.") from exc
        finally:
            try:
                temp_index.unlink()
            except OSError:
                pass
    return {"status": "delivered", "delivery_id": delivery_id}, []
