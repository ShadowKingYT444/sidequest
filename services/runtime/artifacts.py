"""Hash-checked import and scoped reads for immutable runtime artifacts."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
from typing import Any
from uuid import uuid4

from .policy import ErrorCode, RuntimeFault
from .store import RuntimeStore

_MAX_IMPORTED_BYTES = 128 * 1024 * 1024
_MAX_PREVIEW_BYTES = 256 * 1024
_FILE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,119}$")
_FILE_STATUSES = {"added", "modified", "deleted", "renamed", "unchanged"}


def _safe_relative_path(value: Any) -> str:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise RuntimeFault(ErrorCode.INVALID_INPUT, "artifact path is invalid")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in value.split("/")) or path.as_posix() != value:
        raise RuntimeFault(ErrorCode.POLICY_DENIED, "artifact path is outside its host-assigned root")
    return value


def _contained_file(root: Path, relative: str) -> Path:
    relative = _safe_relative_path(relative)
    base = root.resolve(strict=True)
    target = base.joinpath(*PurePosixPath(relative).parts)
    cursor = base
    for part in PurePosixPath(relative).parts:
        cursor = cursor / part
        try:
            info = cursor.lstat()
        except OSError:
            raise RuntimeFault(ErrorCode.POLICY_DENIED, "artifact file is unavailable") from None
        if stat.S_ISLNK(info.st_mode):
            raise RuntimeFault(ErrorCode.POLICY_DENIED, "artifact path contains a symlink")
    try:
        resolved = target.resolve(strict=True)
        resolved.relative_to(base)
        info = resolved.lstat()
    except (OSError, ValueError):
        raise RuntimeFault(ErrorCode.POLICY_DENIED, "artifact path is outside its host-assigned root") from None
    if not stat.S_ISREG(info.st_mode) or info.st_size > _MAX_IMPORTED_BYTES:
        raise RuntimeFault(ErrorCode.INVALID_INPUT, "artifact must be a bounded regular file")
    return resolved


def _read_regular(path: Path) -> bytes:
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(path, flags)
    except OSError:
        raise RuntimeFault(ErrorCode.POLICY_DENIED, "artifact could not be opened safely") from None
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_size > _MAX_IMPORTED_BYTES:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "artifact size or file type is invalid")
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(fd, min(1024 * 1024, _MAX_IMPORTED_BYTES + 1 - total))
            if not chunk:
                break
            total += len(chunk)
            if total > _MAX_IMPORTED_BYTES:
                raise RuntimeFault(ErrorCode.INVALID_INPUT, "artifact exceeds the import limit")
            chunks.append(chunk)
        return b"".join(chunks)
    finally:
        os.close(fd)


class ArtifactStore:
    """Stores bytes by digest and returns only registered, hash-checked content."""

    def __init__(self, root: Path, store: RuntimeStore):
        self.root = Path(root)
        self.store = store
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        if self.root.is_symlink():
            raise RuntimeFault(ErrorCode.POLICY_DENIED, "artifact root cannot be a symlink")

    def _write_content(self, data: bytes, expected_sha256: str) -> str:
        digest = hashlib.sha256(data).hexdigest()
        if digest != expected_sha256:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "artifact digest does not match its bytes")
        directory = self.root / digest
        directory.mkdir(mode=0o700, exist_ok=True)
        if directory.is_symlink():
            raise RuntimeFault(ErrorCode.POLICY_DENIED, "artifact storage contains a symlink")
        target = directory / "content"
        if target.exists():
            existing = _read_regular(target)
            if hashlib.sha256(existing).hexdigest() != digest:
                raise RuntimeFault(ErrorCode.INTERNAL, "stored artifact failed its digest check")
            return f"{digest}/content"
        os.chmod(directory, 0o700, follow_symlinks=False)
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        try:
            fd = os.open(target, flags, 0o400)
        except FileExistsError:
            return self._write_content(data, expected_sha256)
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
        os.chmod(target, 0o444, follow_symlinks=False)
        os.chmod(directory, 0o555, follow_symlinks=False)
        return f"{digest}/content"

    def import_file(
        self,
        path: Path,
        *,
        expected_sha256: str,
        job_id: str,
        run_id: str,
        kind: str,
        media_type: str,
        display_name: str,
        artifact_id: str | None = None,
    ) -> str:
        info = Path(path).lstat()
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode) or info.st_size > _MAX_IMPORTED_BYTES:
            raise RuntimeFault(ErrorCode.POLICY_DENIED, "artifact must be a bounded regular file")
        data = _read_regular(Path(path))
        storage_key = self._write_content(data, expected_sha256)
        return self.store.create_artifact(
            job_id=job_id,
            run_id=run_id,
            artifact_id=artifact_id,
            kind=kind,
            media_type=media_type,
            display_name=display_name,
            sha256=expected_sha256,
            size_bytes=len(data),
            storage_key=storage_key,
            immutable=True,
        )

    def import_adapter_records(
        self,
        output_root: Path,
        records: Any,
        *,
        job_id: str,
        run_id: str,
        candidate_id: str | None = None,
    ) -> list[str]:
        if not isinstance(records, list) or len(records) > 2000:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "adapter artifact list is invalid")
        imported: list[str] = []
        seen: set[str] = set()
        for record in records:
            if not isinstance(record, dict):
                raise RuntimeFault(ErrorCode.INVALID_INPUT, "adapter artifact record is invalid")
            artifact_id = record.get("id")
            if not isinstance(artifact_id, str) or artifact_id in seen:
                raise RuntimeFault(ErrorCode.INVALID_INPUT, "adapter artifact identifiers are invalid or duplicated")
            relative = _safe_relative_path(record.get("relative_path"))
            path = _contained_file(Path(output_root), relative)
            if record.get("job_id") not in {None, job_id} or record.get("run_id") not in {None, run_id}:
                raise RuntimeFault(ErrorCode.POLICY_DENIED, "adapter artifact ownership does not match the request")
            if candidate_id is not None and record.get("candidate_id") not in {None, candidate_id}:
                raise RuntimeFault(ErrorCode.POLICY_DENIED, "adapter artifact candidate does not match the request")
            if record.get("immutable") is not True:
                raise RuntimeFault(ErrorCode.POLICY_DENIED, "adapter artifact is not immutable")
            digest = record.get("sha256")
            size_bytes = record.get("size_bytes")
            kind = record.get("kind", "text")
            media_type = record.get("media_type", "application/octet-stream")
            display_name = record.get("display_name", kind)
            if (
                not isinstance(size_bytes, int)
                or isinstance(size_bytes, bool)
                or not isinstance(kind, str)
                or not isinstance(media_type, str)
                or not isinstance(display_name, str)
                or not kind
                or len(kind) > 80
                or not media_type
                or len(media_type) > 255
                or not display_name
                or len(display_name) > 4096
            ):
                raise RuntimeFault(ErrorCode.INVALID_INPUT, "adapter artifact metadata is invalid")
            if not isinstance(digest, str) or len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
                raise RuntimeFault(ErrorCode.INVALID_INPUT, "adapter artifact digest is invalid")
            if size_bytes != path.stat().st_size:
                raise RuntimeFault(ErrorCode.INVALID_INPUT, "adapter artifact size does not match its record")
            artifact_id = self.import_file(
                path,
                expected_sha256=digest,
                job_id=job_id,
                run_id=run_id,
                kind=kind,
                media_type=media_type,
                display_name=display_name,
                artifact_id=artifact_id,
            )
            imported.append(artifact_id)
            seen.add(artifact_id)
        return imported

    def import_candidate_snapshot(
        self,
        manifest: dict[str, Any],
        snapshot_root: Path,
        *,
        job_id: str,
        run_id: str,
        candidate_id: str,
    ) -> tuple[list[str], dict[str, str], Path]:
        candidate = manifest["candidate"]
        files = manifest["files"]
        if not isinstance(files, list) or len(files) > 100_000:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "manifest file list exceeds the configured limit")
        if not isinstance(candidate_id, str) or candidate.get("id") != candidate_id:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "candidate identity differs from its manifest")
        expected: dict[str, dict[str, Any]] = {}
        tree_rows: list[dict[str, Any]] = []
        seen_file_ids: set[str] = set()
        for entry in files:
            if not isinstance(entry, dict):
                raise RuntimeFault(ErrorCode.INVALID_INPUT, "manifest file record is invalid")
            path = _safe_relative_path(entry.get("path"))
            status = entry.get("status")
            file_id = entry.get("file_id")
            old_path = entry.get("old_path")
            if (
                not isinstance(file_id, str)
                or not _FILE_ID_RE.fullmatch(file_id)
                or file_id in seen_file_ids
                or status not in _FILE_STATUSES
                or (old_path is not None and status != "renamed")
                or (status == "renamed" and (not isinstance(old_path, str) or old_path == path))
                or (old_path is not None and _safe_relative_path(old_path) != old_path)
                or not isinstance(entry.get("binary"), bool)
                or any(
                    not isinstance(entry.get(name), int)
                    or isinstance(entry.get(name), bool)
                    or entry.get(name) < 0
                    for name in ("added_lines", "deleted_lines", "size_bytes")
                )
                or not isinstance(entry.get("media_type"), str)
                or not 1 <= len(entry["media_type"]) <= 255
            ):
                raise RuntimeFault(ErrorCode.INVALID_INPUT, "manifest file metadata is invalid")
            seen_file_ids.add(file_id)
            if status == "deleted":
                if entry.get("sha256") is not None:
                    raise RuntimeFault(ErrorCode.INVALID_INPUT, "deleted manifest file has a content digest")
                if entry.get("mode") not in {"100644", "100755"}:
                    raise RuntimeFault(ErrorCode.INVALID_INPUT, "deleted manifest file mode is invalid")
                continue
            digest = entry.get("sha256")
            mode = entry.get("mode")
            size = entry.get("size_bytes")
            if (
                not isinstance(digest, str)
                or len(digest) != 64
                or any(ch not in "0123456789abcdef" for ch in digest)
                or mode not in {"100644", "100755"}
                or not isinstance(size, int)
                or isinstance(size, bool)
                or size < 0
            ):
                raise RuntimeFault(ErrorCode.INVALID_INPUT, "manifest file identity is invalid")
            if path in expected:
                raise RuntimeFault(ErrorCode.INVALID_INPUT, "manifest contains duplicate paths")
            expected[path] = entry
            tree_rows.append({"path": path, "mode": mode, "size_bytes": size, "sha256": digest})
        canonical = json.dumps(
            {"v": 1, "files": sorted(tree_rows, key=lambda item: item["path"])},
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        if hashlib.sha256(canonical).hexdigest() != candidate.get("tree_sha256"):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "manifest tree digest does not match its file list")

        snapshot = Path(snapshot_root)
        if snapshot.is_symlink() or not snapshot.is_dir():
            raise RuntimeFault(ErrorCode.POLICY_DENIED, "candidate snapshot is not a regular directory")
        seen: set[str] = set()
        pending = [snapshot]
        while pending:
            directory = pending.pop()
            for child in os.scandir(directory):
                child_path = Path(child.path)
                info = child.stat(follow_symlinks=False)
                if stat.S_ISLNK(info.st_mode):
                    raise RuntimeFault(ErrorCode.POLICY_DENIED, "candidate snapshot contains a symlink")
                relative = child_path.relative_to(snapshot).as_posix()
                _safe_relative_path(relative)
                if stat.S_ISDIR(info.st_mode):
                    pending.append(child_path)
                elif stat.S_ISREG(info.st_mode):
                    seen.add(relative)
                else:
                    raise RuntimeFault(ErrorCode.POLICY_DENIED, "candidate snapshot contains a special file")
        if seen != set(expected):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "candidate snapshot files do not match its manifest")

        file_artifacts: list[str] = []
        file_ids: dict[str, str] = {}
        for relative, entry in expected.items():
            source = _contained_file(snapshot, relative)
            data = _read_regular(source)
            digest = hashlib.sha256(data).hexdigest()
            expected_mode = entry["mode"]
            mode = "100755" if source.stat().st_mode & stat.S_IXUSR else "100644"
            if digest != entry["sha256"] or len(data) != entry["size_bytes"] or mode != expected_mode:
                raise RuntimeFault(ErrorCode.INVALID_INPUT, "candidate snapshot file differs from its manifest")
            artifact_id = self._register_file_bytes(
                data,
                expected_sha256=digest,
                job_id=job_id,
                run_id=run_id,
                kind="source_file",
                media_type=str(entry.get("media_type", "application/octet-stream")),
                display_name=relative,
            )
            file_artifacts.append(artifact_id)
            file_ids[relative] = artifact_id

        runtime_snapshot = self._write_readonly_snapshot(candidate_id, snapshot, expected)
        return file_artifacts, file_ids, runtime_snapshot

    def _register_file_bytes(
        self,
        data: bytes,
        *,
        expected_sha256: str,
        job_id: str,
        run_id: str,
        kind: str,
        media_type: str,
        display_name: str,
    ) -> str:
        storage_key = self._write_content(data, expected_sha256)
        return self.store.create_artifact(
            job_id=job_id,
            run_id=run_id,
            kind=kind,
            media_type=media_type,
            display_name=display_name,
            sha256=expected_sha256,
            size_bytes=len(data),
            storage_key=storage_key,
            immutable=True,
        )

    def _write_readonly_snapshot(
        self,
        candidate_id: str,
        source: Path,
        entries: dict[str, dict[str, Any]],
    ) -> Path:
        safe_id = "".join(ch for ch in candidate_id if ch.isalnum() or ch in "._-")
        if safe_id != candidate_id or not safe_id or len(safe_id) > 128:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "candidate identifier cannot name a snapshot")
        parent = self.root.parent / "workspaces" / "frozen"
        parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        if parent.is_symlink():
            raise RuntimeFault(ErrorCode.POLICY_DENIED, "frozen workspace root cannot be a symlink")
        target = parent / safe_id
        if target.exists() or target.is_symlink():
            raise RuntimeFault(ErrorCode.VERSION_CONFLICT, "candidate snapshot already exists")
        target.mkdir(mode=0o700)
        directories: set[Path] = {target}
        try:
            for relative, entry in entries.items():
                source_path = _contained_file(source, relative)
                data = _read_regular(source_path)
                destination = target.joinpath(*PurePosixPath(relative).parts)
                destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                cursor = destination.parent
                while cursor != target:
                    directories.add(cursor)
                    cursor = cursor.parent
                flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
                if hasattr(os, "O_NOFOLLOW"):
                    flags |= os.O_NOFOLLOW
                fd = os.open(destination, flags, 0o400)
                with os.fdopen(fd, "wb") as stream:
                    stream.write(data)
                    stream.flush()
                    os.fsync(stream.fileno())
                os.chmod(destination, 0o555 if entry["mode"] == "100755" else 0o444, follow_symlinks=False)
            for directory in sorted(directories, key=lambda item: len(item.parts), reverse=True):
                os.chmod(directory, 0o555, follow_symlinks=False)
        except Exception:
            # A partial read-only snapshot is never registered or passed to an adapter.
            for directory in sorted(target.rglob("*"), key=lambda item: len(item.parts), reverse=True):
                try:
                    if directory.is_dir() and not directory.is_symlink():
                        os.chmod(directory, 0o700)
                    else:
                        os.chmod(directory, 0o600, follow_symlinks=False)
                except OSError:
                    pass
            try:
                os.chmod(target, 0o700)
                import shutil
                shutil.rmtree(target)
            except OSError:
                pass
            raise
        return target.resolve(strict=True)

    def stage_manifest(self, artifact: dict[str, Any], *, candidate_id: str, input_root: Path) -> Path:
        raw = self.read_artifact(artifact)
        parent = Path(input_root) / candidate_id
        parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        if parent.is_symlink():
            raise RuntimeFault(ErrorCode.POLICY_DENIED, "artifact input root cannot be a symlink")
        target = parent / "manifest.json"
        if target.exists() or target.is_symlink():
            raise RuntimeFault(ErrorCode.VERSION_CONFLICT, "staged manifest already exists")
        fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o400)
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        return target.resolve(strict=True)

    def read_artifact(self, artifact: dict[str, Any]) -> bytes:
        relative = _safe_relative_path(artifact["storage_key"])
        path = _contained_file(self.root, relative)
        data = _read_regular(path)
        if hashlib.sha256(data).hexdigest() != artifact["sha256"] or len(data) != artifact["size_bytes"]:
            raise RuntimeFault(ErrorCode.INTERNAL, "stored artifact failed its digest check")
        return data

    def read_manifest(self, artifact: dict[str, Any]) -> dict[str, Any]:
        if artifact["kind"] != "file_manifest":
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "artifact is not a file manifest")
        raw = self.read_artifact(artifact)
        try:
            parsed = json.loads(raw.decode("utf-8", "strict"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "artifact manifest is malformed") from None
        if not isinstance(parsed, dict) or parsed.get("v") != 1 or not isinstance(parsed.get("candidate"), dict) or not isinstance(parsed.get("files"), list):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "artifact manifest shape is invalid")
        return parsed

    def restore_candidate_for_followup(self, candidate_id: str, parent_run_id: str,
                                       workspace: Path, write_paths: list[str]) -> str:
        """Restore verified prior edits into a fresh original-base disposable clone."""
        from .sessions import _directory
        candidate = self.store.get_candidate(candidate_id)
        parent_run = self.store.get_run(parent_run_id)
        job = self.store.get_job(parent_run['job_id'])
        if candidate['job_id'] != parent_run['job_id'] or job['candidate_id'] != candidate_id:
            raise RuntimeFault(ErrorCode.POLICY_DENIED, 'Follow-up candidate belongs to a different run.')
        manifest = self.read_manifest(self.store.get_artifact(candidate['manifest_artifact_id']))
        if any(manifest['candidate'].get(key) != candidate[key] for key in
               ('id','base_revision','candidate_revision','tree_sha256','patch_sha256')):
            raise RuntimeFault(ErrorCode.POLICY_DENIED, 'Prior candidate manifest identity changed.')
        source_artifacts = {item['display_name']: item for item in self.store.list_candidate_artifacts(candidate_id)
                            if item['kind'] == 'source_file'}
        changed = [entry for entry in manifest['files'] if entry['status'] != 'unchanged']
        removals: set[str] = set()
        # Validate all paths before mutating the disposable clone. Then remove
        # old files before materializing replacements, independent of manifest order.
        for entry in changed:
            path = _safe_relative_path(entry['path'])
            paths = [path] + ([entry['old_path']] if entry.get('old_path') else [])
            for relative in paths:
                _safe_relative_path(relative)
                if any(part in {'.git','.codex'} for part in relative.split('/')) or not any(
                    relative == prefix or relative.startswith(prefix.rstrip('/') + '/') for prefix in write_paths):
                    raise RuntimeFault(ErrorCode.POLICY_DENIED, 'Prior candidate exceeds the original follow-up scope.')
            if entry['status'] == 'deleted': removals.add(path)
            if entry.get('old_path'): removals.add(entry['old_path'])
        for relative in sorted(removals, key=lambda p: (-len(PurePosixPath(p).parts),p)):
            directory_fd = _directory(workspace.joinpath(*PurePosixPath(relative).parts[:-1]))
            try:
                name = PurePosixPath(relative).name
                try:
                    info = os.stat(name,dir_fd=directory_fd,follow_symlinks=False)
                    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                        raise RuntimeFault(ErrorCode.POLICY_DENIED, 'Prior candidate deletion is not a single-link file.')
                    os.unlink(name,dir_fd=directory_fd)
                except FileNotFoundError: pass
            finally: os.close(directory_fd)
        empty_parents: set[PurePosixPath] = set()
        for relative in removals:
            parent = PurePosixPath(relative).parent
            while str(parent) != '.':
                if any(str(parent)==prefix or str(parent).startswith(prefix.rstrip('/')+'/') for prefix in write_paths):
                    empty_parents.add(parent)
                parent=parent.parent
        for parent in sorted(empty_parents,key=lambda p:(-len(p.parts),str(p))):
            directory_fd=_directory(workspace.joinpath(*parent.parts[:-1]))
            try:
                try: os.rmdir(parent.name,dir_fd=directory_fd)
                except OSError: pass  # Nonempty or absent directories are retained.
            finally: os.close(directory_fd)
        for entry in changed:
            if entry['status'] == 'deleted': continue
            path = _safe_relative_path(entry['path'])
            raw = source_artifacts.get(path)
            if (not raw or raw['sha256'] != entry['sha256'] or raw['size_bytes'] != entry['size_bytes']):
                raise RuntimeFault(ErrorCode.POLICY_DENIED, 'Prior candidate source artifact is missing or changed.')
            data = self.read_artifact(raw)
            directory_fd = _directory(workspace.joinpath(*PurePosixPath(path).parts[:-1]))
            try:
                name = PurePosixPath(path).name
                try:
                    info = os.stat(name,dir_fd=directory_fd,follow_symlinks=False)
                    if stat.S_ISDIR(info.st_mode):
                        # Only an empty directory may be replaced. Never recursively
                        # remove contents absent from the verified deletion manifest.
                        try: os.rmdir(name,dir_fd=directory_fd)
                        except OSError:
                            raise RuntimeFault(ErrorCode.POLICY_DENIED, 'Prior candidate directory still contains unverified files.') from None
                    elif stat.S_ISREG(info.st_mode) and info.st_nlink == 1:
                        os.unlink(name,dir_fd=directory_fd)
                    else:
                        raise RuntimeFault(ErrorCode.POLICY_DENIED, 'Follow-up destination is not a regular file or empty directory.')
                except FileNotFoundError: pass
                fd = os.open(name,os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                             0o755 if entry['mode']=='100755' else 0o644,dir_fd=directory_fd)
                with os.fdopen(fd,'wb') as stream:
                    stream.write(data);stream.flush();os.fsync(stream.fileno())
            finally: os.close(directory_fd)
        return candidate['tree_sha256']

    def read_path(self, storage_key: str, expected_sha256: str) -> bytes:
        path = _contained_file(self.root, _safe_relative_path(storage_key))
        data = _read_regular(path)
        if hashlib.sha256(data).hexdigest() != expected_sha256:
            raise RuntimeFault(ErrorCode.INTERNAL, "stored file failed its digest check")
        return data


def text_preview(data: bytes, *, max_bytes: int = _MAX_PREVIEW_BYTES) -> str | None:
    if len(data) > max_bytes:
        data = data[:max_bytes]
    try:
        return data.decode("utf-8", "strict")
    except UnicodeDecodeError:
        return None
