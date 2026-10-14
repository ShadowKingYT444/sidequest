"""Wire-v1 JSON-lines entry point for the independent workshop checker."""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any

from .checks import CheckError, run_checks
from .config import MAX_REQUEST_BYTES, PROTOCOL_VERSION

_SAFE_REQUEST_ID = re.compile(r"^[a-z0-9][a-z0-9._:-]{0,127}$")


def _failure(request_id: str, code: str, message: str, *, retryable: bool = False) -> dict[str, Any]:
    return {
        "v": PROTOCOL_VERSION,
        "request_id": request_id,
        "ok": False,
        "data": {},
        "artifacts": [],
        "usage": {"cost_usd": 0.0, "uncertain": False},
        "error": {"code": code, "message": message, "retryable": retryable},
    }


def process_request(request: Any) -> dict[str, Any]:
    request_id = "invalid"
    if isinstance(request, dict):
        supplied_id = request.get("request_id")
        if isinstance(supplied_id, str) and _SAFE_REQUEST_ID.fullmatch(supplied_id):
            request_id = supplied_id
    if not isinstance(request, dict):
        return _failure(request_id, "INVALID_INPUT", "Request must be a JSON object.")
    if request.get("v") != PROTOCOL_VERSION:
        return _failure(request_id, "INVALID_INPUT", "Unsupported protocol version.")
    if not isinstance(request.get("request_id"), str) or not _SAFE_REQUEST_ID.fullmatch(request["request_id"]):
        return _failure(request_id, "INVALID_INPUT", "A bounded request identifier is required.")
    if request.get("op") != "check.run":
        return _failure(request_id, "INVALID_INPUT", "Unsupported workshop operation.")
    if not isinstance(request.get("job_id"), str) or not request["job_id"] or len(request["job_id"]) > 128:
        return _failure(request_id, "INVALID_INPUT", "A bounded job identifier is required.")
    if not isinstance(request.get("workspace"), str):
        return _failure(request_id, "INVALID_INPUT", "Host-assigned candidate workspace is required.")
    try:
        data = run_checks(request)
    except CheckError as exc:
        return _failure(request_id, exc.code, exc.message)
    except Exception:
        # Never echo exception strings, which can contain candidate-controlled text or paths.
        return _failure(request_id, "INTERNAL", "Trusted check execution failed safely.", retryable=True)
    artifacts = data.pop("artifacts", [])
    return {
        "v": PROTOCOL_VERSION,
        "request_id": request_id,
        "ok": True,
        "data": data,
        "artifacts": artifacts,
        "usage": {"cost_usd": 0.0, "uncertain": False},
    }


def process_json_line(raw: bytes) -> bytes:
    if len(raw) > MAX_REQUEST_BYTES:
        response = _failure("invalid", "INVALID_INPUT", "Request exceeds the size limit.")
    elif not raw.endswith(b"\n") or raw.count(b"\n") != 1:
        response = _failure("invalid", "INVALID_INPUT", "Request must contain exactly one complete JSON line.")
    else:
        line = raw[:-1]
        if line.endswith(b"\r"):
            line = line[:-1]
        try:
            decoded = line.decode("utf-8", errors="strict")
            request = json.loads(decoded)
        except (UnicodeDecodeError, json.JSONDecodeError):
            response = _failure("invalid", "INVALID_INPUT", "Request JSON is malformed or incomplete.")
        else:
            response = process_request(request)
    return json.dumps(response, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8") + b"\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run trusted Sidequest browser checks against a frozen candidate.")
    parser.add_argument("--version", action="version", version="sidequest-workshops wire-v1")
    parser.parse_args(argv)
    raw = sys.stdin.buffer.read(MAX_REQUEST_BYTES + 1)
    if len(raw) > MAX_REQUEST_BYTES:
        response = _failure("invalid", "INVALID_INPUT", "Request exceeds the size limit.")
        output = json.dumps(response, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n"
    else:
        output = process_json_line(raw)
    sys.stdout.buffer.write(output)
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
