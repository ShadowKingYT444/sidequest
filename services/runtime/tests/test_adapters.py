from __future__ import annotations

import asyncio
import os
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from services.runtime.adapters import AdapterRunner
from services.runtime.config import RuntimeConfig
from services.runtime.policy import ErrorCode, RuntimeFault


_DESCENDANT_ADAPTER = r'''import json, subprocess, sys, time
from pathlib import Path

mode = sys.argv[1]
request = json.loads(sys.stdin.buffer.readline())
pid_path = Path(request["context"]["pid_path"])
kwargs = {} if mode == "timeout" else {"stdout":subprocess.DEVNULL,"stderr":subprocess.DEVNULL}
child = subprocess.Popen([sys.executable,"-c","import time; time.sleep(30)"], **kwargs)
pid_path.write_text(str(child.pid), encoding="ascii")
if mode == "cancel":
    time.sleep(30)
response = {"v":1,"request_id":"wrong" if mode == "malformed" else request["request_id"],"ok":True,"data":{},"artifacts":[]}
sys.stdout.write(json.dumps(response, separators=(",",":")) + "\n")
sys.stdout.flush()
if mode == "timeout":
    sys.exit(0)
'''


def _process_is_live(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    try:
        status = Path(f"/proc/{pid}/stat").read_text(encoding="ascii")
        state = status.rsplit(")", 1)[1].strip().split()[0]
        return state != "Z"
    except (FileNotFoundError, OSError, IndexError):
        return True


class AdapterDescendantTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="sidequest-adapter-child-")
        self.root = Path(self.temporary.name)
        self.script = self.root / "fake_adapter.py"
        self.script.write_text(_DESCENDANT_ADAPTER, encoding="utf-8")

    async def asyncTearDown(self) -> None:
        self.temporary.cleanup()

    def _runner(self, mode: str, timeout: float = 0.4) -> AdapterRunner:
        config = RuntimeConfig(
            data_dir=self.root / "data",
            config_dir=self.root / "config",
            runtime_dir=self.root / "runtime",
            b_argv=(sys.executable, str(self.script), mode),
            d_argv=(sys.executable, str(self.script), mode),
            adapter_timeout_seconds=timeout,
        )
        return AdapterRunner(config)

    async def _call(self, runner: AdapterRunner, pid_path: Path) -> dict:
        return await runner.call(
            "B",
            op="repo.inspect",
            job_id="job_adapter_test",
            workspace=self.root / "workspace",
            payload={},
            context={"pid_path": str(pid_path)},
        )

    async def _read_pid(self, path: Path) -> int:
        for _ in range(300):
            if path.exists():
                return int(path.read_text(encoding="ascii"))
            await asyncio.sleep(0.01)
        self.fail("fake adapter did not start its descendant")

    async def _assert_descendant_stopped(self, pid: int) -> None:
        for _ in range(300):
            if not _process_is_live(pid):
                return
            await asyncio.sleep(0.01)
        self.fail(f"adapter descendant {pid} remained alive")

    async def test_timeout_kills_descendant_after_parent_exit_with_inherited_pipes(self) -> None:
        pid_path = self.root / "timeout.pid"
        runner = self._runner("timeout")
        with self.assertRaises(RuntimeFault) as raised:
            await self._call(runner, pid_path)
        self.assertEqual(raised.exception.code, ErrorCode.UNAVAILABLE)
        self.assertIn("timed out", raised.exception.message)
        await self._assert_descendant_stopped(await self._read_pid(pid_path))

    async def test_cancellation_kills_adapter_group_and_descendant(self) -> None:
        pid_path = self.root / "cancel.pid"
        runner = self._runner("cancel", timeout=10)
        call = asyncio.create_task(self._call(runner, pid_path))
        pid = await self._read_pid(pid_path)
        call.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await asyncio.wait_for(call, timeout=3)
        await self._assert_descendant_stopped(pid)

    async def test_malformed_response_kills_descendant_even_after_parent_exit(self) -> None:
        pid_path = self.root / "malformed.pid"
        runner = self._runner("malformed")
        with self.assertRaises(RuntimeFault) as raised:
            await self._call(runner, pid_path)
        self.assertEqual(raised.exception.code, ErrorCode.INVALID_INPUT)
        await self._assert_descendant_stopped(await self._read_pid(pid_path))


if __name__ == "__main__":
    unittest.main()
