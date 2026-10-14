"""Protocol-fake provider transport tests: no real Codex process or model calls."""

from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path
import sys
import uuid

TOOLS_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from codex_bridge import execute_agent
from artifact_capture import tree_digest
from git_ops import AdapterError, inspect_worktree
from main import dispatch
from protocol import ProgressLog
from test_git_artifacts import GitFixture
import test_codex_bridge as bridge_tests


class ProviderTransportTests(GitFixture):
    model = "gpt-6-luna"
    effort = "max"
    _fake_executable = bridge_tests.CodexBridgeTests._fake_executable
    _settings = bridge_tests.CodexBridgeTests._settings
    _request = bridge_tests.CodexBridgeTests._request
    _rpc_log = bridge_tests.CodexBridgeTests._rpc_log

    def attachment(self, data: bytes, *, name: str = "context.txt", media_type: str = "text/plain") -> dict:
        path = self.artifacts / f"attachment-{uuid.uuid4().hex}"
        path.write_bytes(data)
        return {
            "attachment_id": "attachment-" + uuid.uuid4().hex,
            "name": name,
            "media_type": media_type,
            "size_bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "path": str(path),
        }

    def request_fixture(self, mode: str = "success", *, followup: bool = False):
        workspace = self.prepare("transport-" + uuid.uuid4().hex)
        settings, _executable, log_path = self._settings(mode)
        request = self._request(workspace, objective="fixture objective", provider_thread_id="host-persisted-thread" if followup else None)
        if followup:
            request["payload"]["followup"] = {"message_id": "message-fixture", "prompt": "Please change the fixture again."}
            request["context"]["provider_turn_id"] = "prior-turn"
        return request, settings, log_path

    def run_fake(self, request, settings):
        return execute_agent(request, settings, ProgressLog(None, request["request_id"]), _test_only_allow_unmetered=True)

    def test_text_and_image_attachment_bytes_reach_fake_turn_without_host_paths(self):
        request, settings, log_path = self.request_fixture()
        text = self.attachment("Attached context: café\n".encode("utf-8"))
        # Valid one-pixel PNG fixture. The app-server itself is a fake.
        png = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+yRZkAAAAASUVORK5CYII=")
        image = self.attachment(png, name="reference.png", media_type="image/png")
        request["context"]["attachments"] = [text, image]
        data, _artifacts, _usage = self.run_fake(request, settings)
        self.assertEqual(data["status"], "candidate")
        records = self._rpc_log(log_path)
        turn = next(row["params"] for row in records if row.get("method") == "turn/start")
        self.assertEqual(len(turn["input"]), 3)
        self.assertIn("Attached context: café\n", turn["input"][1]["text"])
        self.assertIn("untrusted", turn["input"][1]["text"])
        self.assertEqual(turn["input"][2], {"type": "image", "url": "data:image/png;base64," + base64.b64encode(png).decode("ascii")})
        for descriptor in (text, image):
            self.assertNotIn(descriptor["path"], json.dumps(turn))
        self.assertFalse(turn["sandboxPolicy"]["networkAccess"])
        self.assertTrue(turn["sandboxPolicy"]["excludeSlashTmp"])

    def test_followup_resumes_same_thread_and_preserves_goal_and_token_ceiling(self):
        request, settings, log_path = self.request_fixture("followup", followup=True)
        data, _artifacts, _usage = self.run_fake(request, settings)
        self.assertEqual(data["status"], "candidate")
        self.assertEqual(data["provider_thread_id"], "host-persisted-thread")
        records = self._rpc_log(log_path)
        methods = [row.get("method") for row in records if row["kind"] == "rpc"]
        self.assertNotIn("thread/start", methods)
        self.assertEqual(methods.count("turn/start"), 1)
        goal = next(row["params"] for row in records if row.get("method") == "thread/goal/set")
        self.assertEqual(goal["objective"], "fixture objective")
        self.assertEqual(goal["tokenBudget"], 30000)
        turn = next(row["params"] for row in records if row.get("method") == "turn/start")
        self.assertIn("Please change the fixture again.", turn["input"][0]["text"])
        self.assertIn("fixture objective", turn["input"][0]["text"])
        self.assertEqual(data["message_id"], "message-fixture")

    def test_followup_uncertain_anchor_or_usage_never_starts_another_turn(self):
        for mode in ("followup_anchor_changed", "followup_active", "followup_unknown_usage", "followup_unknown_status", "followup_budget"):
            with self.subTest(mode=mode):
                request, settings, log_path = self.request_fixture(mode, followup=True)
                data, artifacts, _usage = self.run_fake(request, settings)
                self.assertEqual(data["status"], "blocked")
                self.assertFalse(artifacts)
                methods = [row.get("method") for row in self._rpc_log(log_path) if row["kind"] == "rpc"]
                self.assertNotIn("turn/start", methods)
                self.assertNotIn("thread/goal/set", methods)

    def test_followup_cumulative_token_counter_cannot_reset(self):
        request, settings, log_path = self.request_fixture("followup_goal_reset", followup=True)
        data, artifacts, _usage = self.run_fake(request, settings)
        self.assertEqual(data["status"], "blocked")
        self.assertFalse(artifacts)
        methods = [row.get("method") for row in self._rpc_log(log_path) if row["kind"] == "rpc"]
        self.assertNotIn("turn/start", methods)

    def test_attachment_tamper_links_unsupported_and_overflow_fail_before_provider_start(self):
        cases = ("digest", "size", "symlink", "hardlink", "outside", "binary", "image_type", "utf8", "secret", "overflow", "duplicate", "count")
        for case in cases:
            with self.subTest(case=case):
                request, settings, log_path = self.request_fixture()
                attachment = self.attachment(b"safe context")
                path = Path(attachment["path"])
                if case == "digest": attachment["sha256"] = "0" * 64
                elif case == "size": attachment["size_bytes"] += 1
                elif case == "symlink":
                    target = self.artifacts / (path.name + "-real")
                    path.rename(target)
                    path.symlink_to(target)
                elif case == "hardlink": os.link(path, self.artifacts / (path.name + "-link"))
                elif case == "outside":
                    outside = self.root / "outside.txt"
                    outside.write_bytes(path.read_bytes())
                    attachment["path"] = str(outside)
                elif case == "binary": attachment["media_type"] = "application/octet-stream"
                elif case == "image_type": attachment["media_type"] = "image/png"
                elif case == "utf8": attachment = self.attachment(b"\xff", media_type="text/plain")
                elif case == "secret":
                    attachment = self.attachment(("API_" + "TOKEN=" + "fixture_sensitive_value_for_filter").encode())
                elif case == "overflow": attachment = self.attachment(b"x" * (1024 * 1024 + 1))
                request["context"]["attachments"] = [attachment, attachment] if case == "duplicate" else [attachment]
                if case == "count": request["context"]["attachments"] = [self.attachment(b"safe context") for _ in range(11)]
                with self.assertRaises(AdapterError): self.run_fake(request, settings)
                self.assertFalse(log_path.exists())

    def test_followup_identity_must_be_host_anchored_and_bounded(self):
        for case in ("no_thread", "no_turn", "bad_turn", "no_message", "empty_prompt", "overflow_prompt", "unknown_field"):
            with self.subTest(case=case):
                request, settings, log_path = self.request_fixture("followup", followup=True)
                if case == "no_thread": request["context"].pop("provider_thread_id")
                elif case == "no_turn": request["context"].pop("provider_turn_id")
                elif case == "bad_turn": request["context"]["provider_turn_id"] = "unsafe turn"
                elif case == "no_message": request["payload"]["followup"].pop("message_id")
                elif case == "empty_prompt": request["payload"]["followup"]["prompt"] = " "
                elif case == "overflow_prompt": request["payload"]["followup"]["prompt"] = "x" * (32 * 1024 + 1)
                elif case == "unknown_field": request["payload"]["followup"]["model"] = "other-model"
                with self.assertRaises(AdapterError): self.run_fake(request, settings)
                self.assertFalse(log_path.exists())

    def test_production_followup_and_attachments_stay_blocked_before_provider_start(self):
        request, settings, log_path = self.request_fixture("followup", followup=True)
        request["context"]["attachments"] = [self.attachment(b"safe context")]
        with self.assertRaisesRegex(AdapterError, "cannot enforce a verified USD spend ceiling"):
            dispatch(request, settings)
        self.assertFalse(log_path.exists())

    def initial_tree(self, request, settings):
        _entries, actual, _clean = inspect_worktree(Path(request["workspace"]), self.base, settings)
        return tree_digest([{"path": path, "mode": file.mode, "size_bytes": len(file.data), "sha256": hashlib.sha256(file.data).hexdigest()} for path, file in actual.items()])

    def test_followup_accepts_only_exact_host_materialized_scoped_candidate(self):
        request, settings, log_path = self.request_fixture("followup", followup=True)
        Path(request["workspace"], "src/edit.txt").write_text("prior frozen candidate\n")
        request["context"]["initial_tree_sha256"] = self.initial_tree(request, settings)
        data, _artifacts, _usage = self.run_fake(request, settings)
        self.assertEqual(data["status"], "candidate")
        self.assertEqual(data["provider_thread_id"], "host-persisted-thread")
        self.assertEqual(sum(row.get("method") == "turn/start" for row in self._rpc_log(log_path)), 1)

    def test_untrusted_initial_dirty_tree_or_scope_never_starts_provider(self):
        for case in ("missing", "mismatch", "outside_scope", "not_followup", "malformed", "project_config"):
            with self.subTest(case=case):
                request, settings, log_path = self.request_fixture("followup", followup=True)
                Path(request["workspace"], "src/edit.txt").write_text("prior frozen candidate\n")
                if case == "outside_scope": Path(request["workspace"], "README.md").write_text("outside scope\n")
                if case == "project_config":
                    Path(request["workspace"], ".codex").mkdir()
                    Path(request["workspace"], ".codex/config.toml").write_text('[hooks]\ncommand="fixture"\n')
                    request["context"]["write_paths"].append(".codex")
                request["context"]["initial_tree_sha256"] = self.initial_tree(request, settings)
                if case == "missing": request["context"].pop("initial_tree_sha256")
                elif case == "mismatch": request["context"]["initial_tree_sha256"] = "0" * 64
                elif case == "not_followup": request["payload"].pop("followup")
                elif case == "malformed": request["context"]["initial_tree_sha256"] = "bad"
                with self.assertRaises(AdapterError): self.run_fake(request, settings)
                self.assertFalse(log_path.exists())
