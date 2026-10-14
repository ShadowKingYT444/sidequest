"""Host-configured, one-shot B/D subprocess transport."""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
import re
import signal
import time
from typing import Any, Awaitable, Callable
from uuid import uuid4

from .config import RuntimeConfig
from .models import canonical_json
from .policy import ErrorCode, RuntimeFault

_MAX_PROTOCOL_BYTES = 4 * 1024 * 1024
_MAX_STDERR_BYTES = 64 * 1024
_MAX_PROGRESS_BYTES = 10 * 1024 * 1024
_MAX_PROGRESS_RECORD_BYTES = 4 * 1024
_MAX_PROGRESS_PER_SECOND = 10
_SAFE_REQUEST_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")

ProgressCallback = Callable[[dict[str, Any]], Awaitable[None]]


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON field")
        result[key] = value
    return result


def _safe_message(value: str) -> str:
    # Strip ANSI CSI/OSC sequences and controls before a message reaches run history.
    value = re.sub(r"\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)", "", value)
    value = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", value)
    return "".join(ch for ch in value if ch in "\n\t\r" or ord(ch) >= 32 and ord(ch) != 127)[:4096]


class AdapterRunner:
    """Runs only explicitly allowed operations with a scrubbed child environment."""

    def __init__(self, config: RuntimeConfig):
        self.config = config
        for directory in (
            config.workspaces_dir,
            config.adapter_output_dir,
            config.adapter_input_dir,
            config.artifacts_dir,
            config.delivery_disabled_dir,
            config.runtime_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True, mode=0o700)
            if directory.is_symlink():
                raise RuntimeFault(ErrorCode.POLICY_DENIED, "runtime adapter directory cannot be a symlink")
        self.progress_dir = config.workspaces_dir / "progress"
        self.progress_dir.mkdir(exist_ok=True, mode=0o700)
        self.child_home = config.runtime_dir / "adapter-home"
        self.child_home.mkdir(exist_ok=True, mode=0o700)
        os.chmod(self.child_home, 0o700)
        self.repo_root = Path(__file__).resolve().parents[2]

    def _argv(self, adapter: str) -> tuple[str, ...]:
        if adapter == "B":
            return self.config.b_argv
        if adapter == "D":
            return self.config.d_argv
        raise RuntimeFault(ErrorCode.INTERNAL, "adapter selection is invalid")

    def _environment(self) -> dict[str, str]:
        # Deliberately do not inherit arbitrary host values or provider/account tokens.
        env = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "HOME": str(self.child_home),
            "TMPDIR": str(self.config.runtime_dir),
            "PYTHONPATH": str(self.repo_root),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "SIDEQUEST_ALLOWED_REPO_ROOTS": os.pathsep.join(str(path.resolve()) for path in self.config.allowed_roots),
            "SIDEQUEST_STAGING_ROOTS": str(self.config.workspaces_dir.resolve()),
            "SIDEQUEST_ARTIFACT_ROOTS": str(self.config.adapter_output_dir.resolve()),
            "SIDEQUEST_DELIVERY_ROOTS": str(self.config.delivery_disabled_dir.resolve()),
            "SIDEQUEST_DELIVERY_APPROVAL_ROOT": str((self.config.delivery_disabled_dir / "approvals").resolve()),
            "SIDEQUEST_DELIVERY_STATE_ROOT": str((self.config.delivery_disabled_dir / "state").resolve()),
        }
        # Defense in depth if the host has this token in its environment.
        env.pop("SIDEQUEST_API_TOKEN", None)
        return env

    async def _read_bounded(self, stream: asyncio.StreamReader, limit: int) -> bytes:
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = await stream.read(min(64 * 1024, limit + 1 - total))
            if not chunk:
                break
            total += len(chunk)
            if total > limit:
                raise RuntimeFault(ErrorCode.INVALID_INPUT, "adapter output exceeded its protocol limit")
            chunks.append(chunk)
        return b"".join(chunks)

    async def _terminate(self, process: asyncio.subprocess.Process) -> None:
        if process.returncode is not None:
            return
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            return
        try:
            await asyncio.wait_for(process.wait(), timeout=1.0)
        except asyncio.TimeoutError:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            await process.wait()

    async def _tail_progress(
        self,
        path: Path,
        request_id: str,
        process: asyncio.subprocess.Process,
        callback: ProgressCallback | None,
    ) -> None:
        offset = 0
        total = 0
        pending = bytearray()
        sequence = 0
        times: list[float] = []
        while True:
            try:
                info = path.lstat()
                if not os.path.isfile(path) or path.is_symlink() or info.st_size > _MAX_PROGRESS_BYTES:
                    raise RuntimeFault(ErrorCode.INVALID_INPUT, "adapter progress file is invalid")
                flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
                fd = os.open(path, flags)
                try:
                    os.lseek(fd, offset, os.SEEK_SET)
                    chunk = os.read(fd, min(64 * 1024, _MAX_PROGRESS_BYTES + 1 - total))
                finally:
                    os.close(fd)
                total += len(chunk)
                offset += len(chunk)
                if total > _MAX_PROGRESS_BYTES:
                    raise RuntimeFault(ErrorCode.INVALID_INPUT, "adapter progress exceeded its size limit")
                pending.extend(chunk)
                while b"\n" in pending:
                    raw, _, remainder = pending.partition(b"\n")
                    pending = bytearray(remainder)
                    if len(raw) > _MAX_PROGRESS_RECORD_BYTES:
                        raise RuntimeFault(ErrorCode.INVALID_INPUT, "adapter progress record is too large")
                    try:
                        item = json.loads(raw.decode("utf-8", "strict"), object_pairs_hook=_unique_object)
                    except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
                        raise RuntimeFault(ErrorCode.INVALID_INPUT, "adapter progress record is malformed") from None
                    if (
                        not isinstance(item, dict)
                        or item.get("v") != 1
                        or item.get("request_id") != request_id
                        or not isinstance(item.get("seq"), int)
                        or isinstance(item.get("seq"), bool)
                        or item["seq"] != sequence + 1
                        or item.get("type") not in {"status", "tool_started", "tool_finished", "output", "warning", "usage"}
                        or not isinstance(item.get("message"), str)
                        or len(item["message"].encode("utf-8")) > 4096
                    ):
                        raise RuntimeFault(ErrorCode.INVALID_INPUT, "adapter progress record failed validation")
                    now = time.monotonic()
                    times = [stamp for stamp in times if now - stamp < 1.0]
                    if len(times) >= _MAX_PROGRESS_PER_SECOND:
                        raise RuntimeFault(ErrorCode.INVALID_INPUT, "adapter progress exceeded its rate limit")
                    sequence += 1
                    times.append(now)
                    if callback is not None:
                        await callback({"type": item["type"], "message": _safe_message(item["message"])})
            except FileNotFoundError:
                pass
            if process.returncode is not None:
                # A final partial record is intentionally ignored by the wire contract.
                return
            await asyncio.sleep(0.1)

    async def call(
        self,
        adapter: str,
        *,
        op: str,
        job_id: str,
        workspace: Path,
        payload: dict[str, Any],
        context: dict[str, Any],
        progress_callback: ProgressCallback | None = None,
    ) -> dict[str, Any]:
        allowed = {"repo.inspect", "repo.prepare", "artifacts.freeze"} if adapter == "B" else {"check.run"}
        if op not in allowed:
            raise RuntimeFault(ErrorCode.POLICY_DENIED, "adapter operation is not enabled in this runtime profile")
        argv = self._argv(adapter)
        if not argv:
            raise RuntimeFault(ErrorCode.UNAVAILABLE, f"{adapter} adapter command is not configured")
        request_id = str(uuid4())
        progress_path = self.progress_dir / f"{request_id}.jsonl"
        if progress_path.exists() or progress_path.is_symlink():
            raise RuntimeFault(ErrorCode.VERSION_CONFLICT, "adapter progress identifier already exists")
        ctx = dict(context)
        ctx["progress_path"] = str(progress_path)
        request = {
            "v": 1,
            "request_id": request_id,
            "op": op,
            "job_id": job_id,
            "workspace": str(workspace),
            "payload": payload,
            "context": ctx,
        }
        try:
            encoded = (canonical_json(request) + "\n").encode("utf-8")
        except (TypeError, ValueError):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "adapter request is not valid JSON") from None
        if len(encoded) > _MAX_PROTOCOL_BYTES:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "adapter request exceeded its protocol limit")
        try:
            process = await asyncio.create_subprocess_exec(
                *argv,
                cwd=self.repo_root,
                env=self._environment(),
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                start_new_session=True,
            )
        except FileNotFoundError:
            raise RuntimeFault(ErrorCode.UNAVAILABLE, f"{adapter} adapter executable is unavailable") from None
        except OSError:
            raise RuntimeFault(ErrorCode.UNAVAILABLE, f"{adapter} adapter could not be started") from None
        assert process.stdin and process.stdout and process.stderr
        process.stdin.write(encoded)
        await process.stdin.drain()
        process.stdin.close()
        stdout_task = asyncio.create_task(self._read_bounded(process.stdout, _MAX_PROTOCOL_BYTES))
        stderr_task = asyncio.create_task(self._read_bounded(process.stderr, _MAX_STDERR_BYTES))
        progress_task = asyncio.create_task(self._tail_progress(progress_path, request_id, process, progress_callback))
        try:
            await asyncio.wait_for(process.wait(), timeout=self.config.adapter_timeout_seconds)
            stdout, stderr = await asyncio.gather(stdout_task, stderr_task)
            await progress_task
        except asyncio.TimeoutError:
            await self._terminate(process)
            raise RuntimeFault(ErrorCode.UNAVAILABLE, f"{adapter} adapter timed out", retryable=True) from None
        except asyncio.CancelledError:
            await self._terminate(process)
            raise
        except Exception:
            await self._terminate(process)
            raise
        finally:
            for task in (stdout_task, stderr_task, progress_task):
                if not task.done():
                    task.cancel()
            try:
                progress_path.unlink()
            except OSError:
                pass
        if process.returncode != 0:
            raise RuntimeFault(ErrorCode.UNAVAILABLE, f"{adapter} adapter exited unsuccessfully")
        if not stdout.endswith(b"\n") or stdout.count(b"\n") != 1:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, f"{adapter} adapter returned an invalid response envelope")
        try:
            response = json.loads(stdout[:-1].decode("utf-8", "strict"), object_pairs_hook=_unique_object)
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, f"{adapter} adapter returned malformed JSON") from None
        if (
            not isinstance(response, dict)
            or response.get("v") != 1
            or response.get("request_id") != request_id
            or not isinstance(response.get("ok"), bool)
            or not isinstance(response.get("data"), dict)
            or not isinstance(response.get("artifacts"), list)
        ):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, f"{adapter} adapter returned an unexpected envelope")
        if not response["ok"]:
            error = response.get("error", {})
            code = error.get("code") if isinstance(error, dict) else None
            message = error.get("message") if isinstance(error, dict) else None
            allowed_codes = {ErrorCode.INVALID_INPUT, ErrorCode.NOT_FOUND, ErrorCode.VERSION_CONFLICT, ErrorCode.POLICY_DENIED, ErrorCode.DEPENDENCY_FAILED, ErrorCode.UNAVAILABLE, ErrorCode.BUDGET_LIMIT}
            if code not in allowed_codes or not isinstance(message, str):
                raise RuntimeFault(ErrorCode.INVALID_INPUT, f"{adapter} adapter returned an invalid error envelope")
            raise RuntimeFault(code, _safe_message(message)[:512])
        response["_request_id"] = request_id
        response["_stderr"] = _safe_message(stderr.decode("utf-8", "replace"))[:1024]
        response["_progress_path"] = str(progress_path)
        return response
