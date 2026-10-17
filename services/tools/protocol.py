"""Strict one-request/one-response JSON-line adapter protocol."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import stat
import sys
import time
from typing import Any, BinaryIO


MAX_MESSAGE_BYTES = 4 * 1024 * 1024
MAX_PROGRESS_BYTES = 10 * 1024 * 1024
MAX_PROGRESS_RECORD_BYTES = 4 * 1024
MAX_PROGRESS_PER_SECOND = 10


class AdapterError(Exception):
    def __init__(self, code: str, message: str, retryable: bool = False):
        super().__init__(message)
        self.code = code
        self.message = message
        self.retryable = retryable


def _open_absolute_directory(path: Path) -> int:
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        raise AdapterError("DEPENDENCY_FAILED", "No-follow directory access is unavailable on this platform.")
    absolute = Path(os.path.abspath(path))
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
    try:
        fd = os.open(os.sep, flags)
    except OSError as exc:
        raise AdapterError("POLICY_DENIED", "Progress directory could not be opened safely.") from exc
    try:
        for component in absolute.parts[1:]:
            try:
                before = os.stat(component, dir_fd=fd, follow_symlinks=False)
                if not stat.S_ISDIR(before.st_mode):
                    raise AdapterError("POLICY_DENIED", "Progress path cannot contain symlinks or files.")
                child = os.open(component, flags, dir_fd=fd)
            except AdapterError:
                raise
            except OSError as exc:
                raise AdapterError("POLICY_DENIED", "Progress directory could not be opened safely.") from exc
            after = os.fstat(child)
            if (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino):
                os.close(child)
                raise AdapterError("POLICY_DENIED", "Progress directory changed while it was opened.")
            os.close(fd)
            fd = child
        return fd
    except Exception:
        os.close(fd)
        raise


def _reject_constant(value: str) -> None:
    raise ValueError(f"invalid JSON constant {value}")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for key, value in pairs:
        if key in output:
            raise ValueError(f"duplicate JSON field {key}")
        output[key] = value
    return output


def read_request(stream: BinaryIO | None = None) -> dict[str, Any]:
    source = stream or sys.stdin.buffer
    raw = source.read(MAX_MESSAGE_BYTES + 1)
    if len(raw) > MAX_MESSAGE_BYTES:
        raise AdapterError("INVALID_INPUT", "Request exceeds the 4 MiB limit.")
    if not raw:
        raise AdapterError("INVALID_INPUT", "Expected one JSON-line request.")
    if raw.count(b"\n") > 1 or (b"\n" in raw and not raw.endswith(b"\n")):
        raise AdapterError("INVALID_INPUT", "Expected exactly one JSON line.")
    line = raw[:-1] if raw.endswith(b"\n") else raw
    if line.endswith(b"\r"):
        line = line[:-1]
    try:
        decoded = json.loads(
            line.decode("utf-8"),
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
    except ValueError as exc:
        if str(exc).startswith("duplicate JSON field"):
            raise AdapterError("INVALID_INPUT", str(exc)) from exc
        raise AdapterError("INVALID_INPUT", "Request is not valid UTF-8 JSON.") from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AdapterError("INVALID_INPUT", "Request is not valid UTF-8 JSON.") from exc
    if not isinstance(decoded, dict):
        raise AdapterError("INVALID_INPUT", "Request must be a JSON object.")
    validate_request(decoded)
    return decoded


def validate_request(request: dict[str, Any]) -> None:
    required = {"v", "request_id", "op", "job_id", "workspace", "payload"}
    allowed = required | {"context"}
    if not required.issubset(request) or set(request) - allowed:
        raise AdapterError("INVALID_INPUT", "Request fields do not match protocol v1.")
    if request.get("v") != 1:
        raise AdapterError("INVALID_INPUT", "Only protocol version 1 is supported.")
    for key in ("request_id", "op", "job_id", "workspace"):
        value = request.get(key)
        if not isinstance(value, str) or not value or len(value) > 512 or any(ord(c) < 0x20 for c in value):
            raise AdapterError("INVALID_INPUT", f"{key} must be a non-empty string.")
    if not isinstance(request.get("payload"), dict):
        raise AdapterError("INVALID_INPUT", "payload must be an object.")
    if "context" in request and not isinstance(request["context"], dict):
        raise AdapterError("INVALID_INPUT", "context must be an object.")


def success_response(
    request: dict[str, Any],
    data: dict[str, Any],
    artifacts: list[dict[str, Any]] | None = None,
    usage: dict[str, Any] | None = None,
) -> dict[str, Any]:
    reported_usage = usage or {"cost_usd": None, "uncertain": True}
    # Cost remains unknown unless an independently verified provider measure is
    # available. Token fields are additive metadata; null means unmeasured.
    reported_usage = {
        "input_tokens": reported_usage.get("input_tokens"),
        "cached_input_tokens": reported_usage.get("cached_input_tokens"),
        "output_tokens": reported_usage.get("output_tokens"),
        "total_tokens": reported_usage.get("total_tokens"),
        "cost_usd": reported_usage.get("cost_usd"),
        "uncertain": bool(reported_usage.get("uncertain", True)),
    }
    return {
        "v": 1,
        "request_id": request["request_id"],
        "ok": True,
        "data": data,
        "artifacts": artifacts or [],
        "usage": reported_usage,
    }


def error_response(request_id: str | None, error: AdapterError) -> dict[str, Any]:
    return {
        "v": 1,
        "request_id": request_id or "unknown",
        "ok": False,
        "data": {},
        "artifacts": [],
        "error": {"code": error.code, "message": error.message, "retryable": error.retryable},
    }


def write_response(response: dict[str, Any], stream: BinaryIO | None = None) -> None:
    target = stream or sys.stdout.buffer
    try:
        encoded = json.dumps(response, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8") + b"\n"
    except (TypeError, ValueError) as exc:
        raise AdapterError("INTERNAL", "Response could not be encoded.") from exc
    if len(encoded) > MAX_MESSAGE_BYTES:
        raise AdapterError("INTERNAL", "Response exceeds the 4 MiB limit.")
    target.write(encoded)
    target.flush()


def diagnostic(message: str) -> None:
    safe = " ".join(str(message).replace("\x1b", "").split())[:1000]
    print(f"sidequest-tools: {safe}", file=sys.stderr, flush=True)


class ProgressLog:
    """Append bounded activity records to the host-assigned progress file."""

    def __init__(self, path: Path | None, request_id: str, allowed_roots: tuple[Path, ...] = ()):
        self.path = path
        self.request_id = request_id
        self.allowed_roots = allowed_roots
        self.seq = 0
        self._times: list[float] = []

    def append(
        self,
        kind: str,
        message: str,
        artifact_id: str | None = None,
        *,
        session: dict[str, Any] | None = None,
    ) -> None:
        if kind == "session":
            if artifact_id is not None or not isinstance(session, dict) or set(session) != {"provider_thread_id", "provider_turn_id"}:
                raise AdapterError("INVALID_INPUT", "Session progress requires only provider thread and turn IDs.")
            thread_id = session["provider_thread_id"]
            turn_id = session["provider_turn_id"]

            def valid_session_id(value: Any) -> bool:
                return isinstance(value, str) and bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,511}", value))

            if not valid_session_id(thread_id) or (turn_id is not None and not valid_session_id(turn_id)):
                raise AdapterError("INVALID_INPUT", "Session progress contains a malformed provider ID.")
            if message != "Codex provider session is available.":
                raise AdapterError("INVALID_INPUT", "Session progress must use the generic session message.")
        elif session is not None:
            raise AdapterError("INVALID_INPUT", "Provider session IDs are allowed only on session progress records.")
        if self.path is None:
            return
        now = time.monotonic()
        self._times = [stamp for stamp in self._times if now - stamp < 1.0]
        if kind != "session" and len(self._times) >= MAX_PROGRESS_PER_SECOND:
            return
        safe_message = " ".join(str(message).replace("\x1b", "").split())[:3000]
        record: dict[str, Any] = {"v": 1, "request_id": self.request_id, "seq": self.seq + 1, "type": kind, "message": safe_message}
        if artifact_id is not None:
            record["artifact_id"] = artifact_id
        if session is not None:
            record.update(session)
        encoded = json.dumps(record, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + b"\n"
        if len(encoded) > MAX_PROGRESS_RECORD_BYTES:
            return
        name = self.path.name
        if not name or name in {".", ".."}:
            raise AdapterError("POLICY_DENIED", "Progress file path is invalid.")
        if self.allowed_roots:
            try:
                from .git_ops import open_directory_beneath
            except ImportError:
                from git_ops import open_directory_beneath
            parent_fd = open_directory_beneath(self.path.parent, self.allowed_roots, create=True)
        else:
            parent_fd = _open_absolute_directory(self.path.parent)
        temporary: str | None = None
        fd: int | None = None
        try:
            try:
                before = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
            except FileNotFoundError:
                before = None
            except OSError as exc:
                raise AdapterError("POLICY_DENIED", "Progress file could not be inspected safely.") from exc
            if before is not None and (
                stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode) or before.st_nlink != 1
            ):
                raise AdapterError("POLICY_DENIED", "Progress file must be a single-link regular file.")
            existing = b""
            if before is not None:
                if before.st_size > MAX_PROGRESS_BYTES:
                    return
                fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0), dir_fd=parent_fd)
                opened = os.fstat(fd)
                if not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1 or (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
                    raise AdapterError("POLICY_DENIED", "Progress file changed while it was being read.")
                chunks = bytearray()
                while len(chunks) <= MAX_PROGRESS_BYTES:
                    chunk = os.read(fd, min(1024 * 1024, MAX_PROGRESS_BYTES + 1 - len(chunks)))
                    if not chunk:
                        break
                    chunks.extend(chunk)
                if len(chunks) > MAX_PROGRESS_BYTES or len(chunks) != opened.st_size:
                    return
                existing = bytes(chunks)
                os.close(fd)
                fd = None
                named = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
                if (named.st_dev, named.st_ino) != (opened.st_dev, opened.st_ino) or named.st_nlink != 1:
                    raise AdapterError("POLICY_DENIED", "Progress file changed while it was read.")
            updated = existing + encoded
            if len(updated) > MAX_PROGRESS_BYTES:
                return
            temporary = ".sidequest-progress-" + os.urandom(16).hex() + ".tmp"
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
            fd = os.open(temporary, flags, 0o600, dir_fd=parent_fd)
            opened = os.fstat(fd)
            if not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1:
                raise AdapterError("POLICY_DENIED", "Progress temporary file is not a single-link regular file.")
            view = memoryview(updated)
            while view:
                written = os.write(fd, view)
                view = view[written:]
            os.fsync(fd)
            os.close(fd)
            fd = None
            staged = os.stat(temporary, dir_fd=parent_fd, follow_symlinks=False)
            if not stat.S_ISREG(staged.st_mode) or staged.st_nlink != 1 or staged.st_size != len(updated):
                raise AdapterError("POLICY_DENIED", "Progress temporary file changed before installation.")
            try:
                current = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
            except FileNotFoundError:
                current = None
            if before is None and current is not None:
                raise AdapterError("POLICY_DENIED", "Progress file appeared while it was being written.")
            if before is not None and (
                current is None
                or not stat.S_ISREG(current.st_mode)
                or current.st_nlink != 1
                or (current.st_dev, current.st_ino) != (before.st_dev, before.st_ino)
            ):
                raise AdapterError("POLICY_DENIED", "Progress file changed before it was updated.")
            os.replace(temporary, name, src_dir_fd=parent_fd, dst_dir_fd=parent_fd)
            installed = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
            if (installed.st_dev, installed.st_ino) != (staged.st_dev, staged.st_ino) or installed.st_nlink != 1:
                raise AdapterError("POLICY_DENIED", "Progress file installation could not be verified.")
            os.fsync(parent_fd)
        except OSError as exc:
            raise AdapterError("POLICY_DENIED", "Progress file could not be written safely.") from exc
        finally:
            if fd is not None:
                os.close(fd)
            if temporary is not None:
                try:
                    os.unlink(temporary, dir_fd=parent_fd)
                except OSError:
                    pass
            os.close(parent_fd)
        self.seq += 1
        if kind != "session":
            self._times.append(now)
