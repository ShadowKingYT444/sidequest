"""Strict one-request/one-response JSON-line adapter protocol."""

from __future__ import annotations

import json
import os
from pathlib import Path
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


def success_response(request: dict[str, Any], data: dict[str, Any], artifacts: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {
        "v": 1,
        "request_id": request["request_id"],
        "ok": True,
        "data": data,
        "artifacts": artifacts or [],
        "usage": {"cost_usd": None, "uncertain": True},
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

    def __init__(self, path: Path | None, request_id: str):
        self.path = path
        self.request_id = request_id
        self.seq = 0
        self._times: list[float] = []

    def append(self, kind: str, message: str, artifact_id: str | None = None) -> None:
        if self.path is None:
            return
        now = time.monotonic()
        self._times = [stamp for stamp in self._times if now - stamp < 1.0]
        if len(self._times) >= MAX_PROGRESS_PER_SECOND:
            return
        safe_message = " ".join(str(message).replace("\x1b", "").split())[:3000]
        record: dict[str, Any] = {"v": 1, "request_id": self.request_id, "seq": self.seq + 1, "type": kind, "message": safe_message}
        if artifact_id is not None:
            record["artifact_id"] = artifact_id
        encoded = json.dumps(record, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + b"\n"
        if len(encoded) > MAX_PROGRESS_RECORD_BYTES:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            current_size = self.path.stat().st_size
        except FileNotFoundError:
            current_size = 0
        if current_size + len(encoded) > MAX_PROGRESS_BYTES:
            return
        flags = os.O_APPEND | os.O_CREAT | os.O_WRONLY
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        fd = os.open(self.path, flags, 0o600)
        try:
            os.write(fd, encoded)
        finally:
            os.close(fd)
        self.seq += 1
        self._times.append(now)
