from __future__ import annotations

import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from protocol import AdapterError, error_response, read_request, success_response, write_response

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class ProtocolTests(unittest.TestCase):
    def test_reads_one_json_line_and_rejects_extra_data_or_duplicate_keys(self) -> None:
        request = b'{"v":1,"request_id":"r","op":"repo.inspect","job_id":"j","workspace":"/tmp/w","payload":{}}\n'
        self.assertEqual(read_request(io.BytesIO(request))["request_id"], "r")
        with self.assertRaisesRegex(AdapterError, "one JSON line"):
            read_request(io.BytesIO(request + request))
        with self.assertRaisesRegex(AdapterError, "duplicate JSON field"):
            read_request(io.BytesIO(b'{"v":1,"v":1,"request_id":"r","op":"x","job_id":"j","workspace":"/tmp","payload":{}}\n'))
        with self.assertRaisesRegex(AdapterError, "valid UTF-8 JSON"):
            read_request(io.BytesIO(b"{bad}\n"))

    def test_response_is_one_json_line_and_error_shape_is_complete(self) -> None:
        request = {"v": 1, "request_id": "r", "op": "repo.inspect", "job_id": "j", "workspace": "/tmp/w", "payload": {}}
        output = io.BytesIO()
        write_response(success_response(request, {"revision": "abc", "clean": True, "files": []}), output)
        raw = output.getvalue()
        self.assertEqual(raw.count(b"\n"), 1)
        self.assertTrue(raw.endswith(b"\n"))
        self.assertTrue(__import__("json").loads(raw)["ok"])
        error = error_response("r", AdapterError("INVALID_INPUT", "bad request"))
        self.assertEqual(set(error), {"v", "request_id", "ok", "data", "artifacts", "error"})
        self.assertFalse(error["ok"])

    def test_cli_emits_exactly_one_response_line_even_for_malformed_input(self) -> None:
        env = dict(os.environ)
        env.pop("GIT_DIR", None)
        env.pop("GIT_WORK_TREE", None)
        result = subprocess.run(
            [sys.executable, "-m", "services.tools.main"],
            cwd=PROJECT_ROOT,
            input=b"{bad}\n",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            check=False,
        )
        self.assertEqual(result.stdout.count(b"\n"), 1)
        self.assertTrue(result.stdout.endswith(b"\n"))
        response = json.loads(result.stdout)
        self.assertFalse(response["ok"])
        self.assertEqual(response["error"]["code"], "INVALID_INPUT")
        self.assertIn(b"sidequest-tools:", result.stderr)


if __name__ == "__main__":
    unittest.main()
