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

from protocol import AdapterError, ProgressLog, error_response, read_request, success_response, write_response

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class ProtocolTests(unittest.TestCase):
    def test_progress_log_updates_atomically_with_bounded_json_records(self) -> None:
        with tempfile.TemporaryDirectory(prefix="sidequest-progress-ok-") as temp:
            root = Path(temp)
            progress = root / "nested" / "progress.jsonl"
            log = ProgressLog(progress, "request", (root,))
            log.append("status", "first")
            log.append("status", "second")
            rows = [json.loads(line) for line in progress.read_text().splitlines()]
            self.assertEqual([row["seq"] for row in rows], [1, 2])
            self.assertEqual([row["message"] for row in rows], ["first", "second"])

    def test_session_progress_has_typed_top_level_ids_and_generic_message(self) -> None:
        with tempfile.TemporaryDirectory(prefix="sidequest-progress-session-") as temp:
            progress = Path(temp) / "progress.jsonl"
            log = ProgressLog(progress, "request")
            log.append(
                "session",
                "Codex provider session is available.",
                session={"provider_thread_id": "thread-fixture", "provider_turn_id": None},
            )
            log.append(
                "session",
                "Codex provider session is available.",
                session={"provider_thread_id": "thread-fixture", "provider_turn_id": "turn-fixture"},
            )
            rows = [json.loads(line) for line in progress.read_text().splitlines()]
            self.assertEqual([row["seq"] for row in rows], [1, 2])
            self.assertEqual(
                set(rows[0]),
                {"v", "request_id", "seq", "type", "message", "provider_thread_id", "provider_turn_id"},
            )
            self.assertEqual(rows[0]["type"], "session")
            self.assertEqual(rows[0]["provider_thread_id"], "thread-fixture")
            self.assertIsNone(rows[0]["provider_turn_id"])
            self.assertEqual(rows[1]["provider_turn_id"], "turn-fixture")
            self.assertNotIn("thread-fixture", rows[0]["message"])
            self.assertNotIn("turn-fixture", rows[1]["message"])

    def test_session_progress_rejects_malformed_or_misplaced_ids(self) -> None:
        log = ProgressLog(None, "request")
        with self.assertRaisesRegex(AdapterError, "malformed provider ID"):
            log.append(
                "session",
                "Codex provider session is available.",
                session={"provider_thread_id": "thread\ninvalid", "provider_turn_id": None},
            )
        with self.assertRaisesRegex(AdapterError, "only on session"):
            log.append("status", "no session IDs here", session={"provider_thread_id": "thread", "provider_turn_id": None})

    def test_progress_log_rejects_hardlink_without_appending_to_external_file(self) -> None:
        with tempfile.TemporaryDirectory(prefix="sidequest-progress-") as temp:
            root = Path(temp)
            external = root / "external.log"
            external.write_bytes(b"external sentinel\n")
            progress = root / "progress.jsonl"
            os.link(external, progress)
            before = external.read_bytes()

            with self.assertRaises(AdapterError) as caught:
                ProgressLog(progress, "request", (root,)).append("status", "must not write")

            self.assertEqual(caught.exception.code, "POLICY_DENIED")
            self.assertEqual(external.read_bytes(), before)
            self.assertEqual(progress.read_bytes(), before)

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
