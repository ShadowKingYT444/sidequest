from __future__ import annotations

import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import threading
import unittest
from unittest import mock
import uuid

TOOLS_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from codex_bridge import AppServer, AppServerFailure, execute_agent
from config import ConfigurationError, Settings
from git_ops import AdapterError
from main import dispatch
from protocol import ProgressLog
from test_git_artifacts import GitFixture, git


class CodexBridgeTests(GitFixture):
    model = "gpt-6-luna"
    effort = "max"

    def _fake_executable(self, mode: str) -> tuple[Path, Path]:
        log_path = self.root / f"codex-{mode}-{uuid.uuid4().hex}.jsonl"
        script_path = self.root / f"fake-codex-{mode}-{uuid.uuid4().hex}.py"
        script = f'''#!{sys.executable}
import json, os, pathlib, sys
MODE = {mode!r}
MODEL = {self.model!r}
EFFORT = {self.effort!r}
LOG = {str(log_path)!r}

def log(value):
    with open(LOG, "a", encoding="utf-8") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\\n")

def emit(value):
    sys.stdout.write(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\\n")
    sys.stdout.flush()

def initialize_result():
    return {{"codexHome": "/fixture/codex-home", "platformFamily": "unix", "platformOs": "linux", "userAgent": "sidequest-fake-codex/1"}}

def response(request, result=None, error=None):
    value = {{"jsonrpc": "2.0", "id": request.get("id")}}
    if error is not None:
        value["error"] = error
    else:
        value["result"] = result or {{}}
    if MODE == "native_marker_free":
        value.pop("jsonrpc", None)
    emit(value)

log({{"kind": "startup", "argv": sys.argv[1:], "home": os.environ.get("HOME"), "codex_home": os.environ.get("CODEX_HOME"), "env_names": sorted(os.environ)}})
for raw in sys.stdin:
    try:
        request = json.loads(raw)
    except Exception:
        continue
    method = request.get("method")
    params = request.get("params") or {{}}
    log({{"kind": "rpc", "method": method, "params": params}})
    if method == "initialize":
        if MODE == "malformed":
            sys.stdout.write('{{"jsonrpc":"2.0","id":1,"result":[}}\\n')
            sys.stdout.flush()
            break
        if MODE == "truncated":
            sys.stdout.write('{{"jsonrpc":"2.0","id":')
            sys.stdout.flush()
            break
        if MODE == "boolean_response_id":
            emit({{"jsonrpc": "2.0", "id": True, "result": initialize_result()}})
            continue
        if MODE == "wrong_jsonrpc":
            emit({{"jsonrpc": "1.0", "id": request.get("id"), "result": initialize_result()}})
            continue
        if MODE == "invalid_initialize_schema":
            response(request, {{"serverInfo": {{"name": "fixture-app-server", "version": "1"}}}})
            continue
        response(request, initialize_result())
    elif method == "initialized":
        continue
    elif method == "model/list":
        if MODE == "provider_error":
            response(request, error={{"code": -32000, "message": "fixture provider diagnostic contains no public detail"}})
        else:
            model_id = "other-model" if MODE == "unsupported_model" else MODEL
            supported = [{{"reasoningEffort": "low"}}] if MODE == "unsupported_effort" else [{{"reasoningEffort": EFFORT}}]
            response(request, {{"data": [{{"id": model_id, "model": model_id, "supportedReasoningEfforts": supported}}], "nextCursor": None}})
    elif method == "account/read":
        account_type = "apiKey" if MODE == "api_key" else "chatgpt"
        response(request, {{"account": {{"type": account_type, "email": "fixture-private@example.invalid"}}}})
    elif method == "account/rateLimits/read":
        if MODE == "quota_numeric":
            response(request, {{"ordinaryUsageAllowed": True, "rateLimits": {{
                "primary": {{"usedPercent": 15}}, "secondary": {{"usedPercent": 25}},
                "credits": {{"hasCredits": False}},
            }}}})
        elif MODE == "quota_missing":
            response(request, {{"rateLimits": {{"credits": {{"hasCredits": 1, "unlimited": False, "balance": "fixture-private-balance"}}}}}})
        else:
            quota_value = MODE in ("quota_true", "success")
            response(request, {{
                "accountId": "fixture-private-account-id",
                "ordinaryUsageAllowed": quota_value,
                "rateLimits": {{"credits": {{"hasCredits": quota_value, "unlimited": False, "balance": "fixture-private-balance"}}}},
            }})
    elif method in ("thread/start", "thread/resume"):
        thread_id = params.get("threadId", "fixture-thread")
        response(request, {{"thread": {{"id": thread_id, "model": MODEL, "reasoningEffort": "low"}}}})
    elif method == "thread/settings/update":
        response(request, {{}})
    elif method == "thread/read":
        response(request, {{"thread": {{"id": params.get("threadId"), "model": MODEL, "reasoningEffort": EFFORT}}}})
    elif method == "thread/goal/get":
        response(request, {{"goal": {{"threadId": params.get("threadId"), "objective": "fixture objective", "status": "active", "tokenBudget": 30000}}}})
    elif method == "thread/goal/set":
        response(request, {{"goal": params}})
    elif method == "turn/start":
        workspace = pathlib.Path(params["cwd"])
        target = workspace / "src" / "edit.txt"
        target.write_text("changed by disposable fake transport\\n", encoding="utf-8")
        response(request, {{"turn": {{"id": "fixture-turn", "status": "inProgress"}}}})
        emit({{"jsonrpc": "2.0", "method": "turn/started", "params": {{"threadId": params.get("threadId"), "turn": {{"id": "fixture-turn", "status": "inProgress"}}}}}})
        if MODE == "action":
            emit({{"jsonrpc": "2.0", "id": 777, "method": "item/commandExecution/requestApproval", "params": {{"command": "untrusted"}}}})
        elif MODE not in ("timeout", "cancel"):
            emit({{"jsonrpc": "2.0", "method": "item/agentMessage/delta", "params": {{"delta": "Done \\u001b[31msafely\\u001b[0m."}}}})
            emit({{"jsonrpc": "2.0", "method": "item/completed", "params": {{"item": {{"id": "agent-one", "type": "agentMessage", "text": "Done \\u001b[31msafely\\u001b[0m."}}}}}})
            emit({{"jsonrpc": "2.0", "method": "item/agentMessage/delta", "params": {{"delta": "API_TOKEN="}}}})
            emit({{"jsonrpc": "2.0", "method": "item/completed", "params": {{"item": {{"id": "agent-two", "type": "agentMessage", "text": "API_TOKEN="}}}}}})
            emit({{"jsonrpc": "2.0", "method": "item/agentMessage/delta", "params": {{"delta": "fixture_secret_value_that_must_not_escape"}}}})
            emit({{"jsonrpc": "2.0", "method": "item/completed", "params": {{"item": {{"id": "agent-three", "type": "agentMessage", "text": "fixture_secret_value_that_must_not_escape"}}}}}})
            emit({{"jsonrpc": "2.0", "method": "item/reasoning/summaryTextDelta", "params": {{"delta": "hidden reasoning fixture_secret_value_that_must_not_escape"}}}})
            emit({{"jsonrpc": "2.0", "method": "item/commandExecution/outputDelta", "params": {{"delta": "tool output fixture_secret_value_that_must_not_escape"}}}})
            total = 40 if MODE == "token_budget" else 15
            usage = {{"inputTokens": 10, "cachedInputTokens": 1, "outputTokens": 5, "reasoningOutputTokens": 0, "totalTokens": total}}
            emit({{"jsonrpc": "2.0", "method": "thread/tokenUsage/updated", "params": {{"threadId": params.get("threadId"), "turnId": "fixture-turn", "tokenUsage": {{"last": usage, "total": usage}}}}}})
            if MODE in ("success", "token_budget", "resume", "native_marker_free"):
                emit({{"jsonrpc": "2.0", "method": "turn/completed", "params": {{"threadId": params.get("threadId"), "turn": {{"id": "fixture-turn", "status": "completed"}}}}}})
    elif method == "turn/interrupt":
        response(request, {{}})
        emit({{"jsonrpc": "2.0", "method": "turn/completed", "params": {{"threadId": params.get("threadId"), "turn": {{"id": params.get("turnId"), "status": "interrupted"}}}}}})
    else:
        response(request, {{}})
'''
        script_path.write_text(script, encoding="utf-8")
        script_path.chmod(script_path.stat().st_mode | stat.S_IXUSR)
        return script_path, log_path

    def _settings(self, mode: str, *, token_budget: int = 30000, max_seconds: int = 15) -> tuple[Settings, Path, Path]:
        executable, log_path = self._fake_executable(mode)
        runtime = self.root / f"codex-state-{uuid.uuid4().hex}"
        runtime.mkdir(mode=0o700)
        settings = Settings(**{
            **self.settings.__dict__,
            "codex_enabled": True,
            "codex_consent": True,
            "codex_executable": executable,
            "codex_model": self.model,
            "codex_effort": self.effort,
            "codex_max_seconds": max_seconds,
            "codex_token_budget": token_budget,
            "codex_state_dir": runtime,
        })
        return settings, executable, log_path

    def _request(self, workspace: Path, *, objective: str = "change the fixture file", max_seconds: int = 10, provider_thread_id: str | None = None):
        context = {
            "source_revision": self.base,
            "write_paths": ["src"],
            "project_id": "fixture-project",
            "output_root": str(self.artifacts),
        }
        if provider_thread_id is not None:
            context["provider_thread_id"] = provider_thread_id
        return {
            "v": 1,
            "request_id": "codex-fixture-request",
            "op": "agent.execute",
            "job_id": "codex-fixture-job",
            "workspace": str(workspace),
            "payload": {
                "objective": objective,
                "check_ids": ["candidate.frozen_identity"],
                "limits": {"max_seconds": max_seconds, "max_cost_usd": 0.05},
            },
            "context": context,
        }

    def _run(self, mode: str, *, token_budget: int = 30000, max_seconds: int = 10, objective: str = "change the fixture file", provider_thread_id: str | None = None, cancel_event: threading.Event | None = None):
        workspace = self.prepare("codex-" + uuid.uuid4().hex)
        settings, executable, log_path = self._settings(mode, token_budget=token_budget, max_seconds=max_seconds)
        request = self._request(workspace, objective=objective, max_seconds=max_seconds, provider_thread_id=provider_thread_id)
        progress_path = self.staging / f"codex-progress-{uuid.uuid4().hex}.jsonl"
        progress = ProgressLog(progress_path, request["request_id"], self.settings.staging_roots)
        # This private test-only opt-in exercises the unmetered lifecycle using
        # a deterministic fake app-server; production dispatch never passes it.
        response = execute_agent(request, settings, progress, cancel_event=cancel_event, _test_only_allow_unmetered=True)
        return response, log_path, progress_path, executable

    def _rpc_log(self, path: Path) -> list[dict[str, object]]:
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]

    def test_fake_app_server_runs_verified_thread_goal_turn_and_freeze(self) -> None:
        sentinel = "objective text ; touch /tmp/sidequest-codex-argv-sentinel"
        (self.root / "sidequest-codex-argv-sentinel").unlink(missing_ok=True)
        (self.root / "sidequest-codex-argv-sentinel").unlink(missing_ok=True)
        (data, artifacts, usage), log_path, progress_path, executable = self._run("success", objective=sentinel)
        self.assertEqual(data["status"], "candidate")
        self.assertTrue(data["model_verified"])
        self.assertTrue(data["effort_verified"])
        self.assertEqual((data["model"], data["effort"]), (self.model, self.effort))
        self.assertEqual(data["provider_thread_id"], "fixture-thread")
        self.assertEqual(data["provider_turn_id"], "fixture-turn")
        self.assertEqual(usage["input_tokens"], 10)
        self.assertIsNone(usage["cost_usd"])
        self.assertTrue(usage["uncertain"])
        self.assertTrue(artifacts)
        self.assertFalse((self.root / "sidequest-codex-argv-sentinel").exists())
        records = self._rpc_log(log_path)
        methods = [row["method"] for row in records if row["kind"] == "rpc"]
        self.assertEqual(methods[:6], ["initialize", "initialized", "model/list", "account/read", "thread/start", "thread/settings/update"])
        initialize_params = next(row["params"] for row in records if row.get("method") == "initialize")
        self.assertEqual(set(initialize_params), {"clientInfo"})
        self.assertIn("thread/read", methods)
        self.assertIn("thread/goal/set", methods)
        start_params = next(row["params"] for row in records if row.get("method") == "thread/start")
        self.assertFalse(start_params["allowProviderModelFallback"])
        self.assertFalse(start_params["ephemeral"])
        self.assertNotIn("effort", start_params)
        turn_start = next(row["params"] for row in records if row.get("method") == "turn/start")
        prompt = turn_start["input"][0]["text"]
        self.assertIn(sentinel, prompt)
        self.assertEqual(turn_start["sandboxPolicy"]["networkAccess"], False)
        startup = next(row for row in records if row["kind"] == "startup")
        self.assertNotIn(sentinel, startup["argv"])
        self.assertNotIn("--no-sandbox", startup["argv"])
        progress_rows = [json.loads(line) for line in progress_path.read_text(encoding="utf-8").splitlines()]
        session_rows = [row for row in progress_rows if row["type"] == "session"]
        self.assertEqual(len(session_rows), 2)
        self.assertEqual(session_rows[0]["provider_thread_id"], "fixture-thread")
        self.assertIsNone(session_rows[0]["provider_turn_id"])
        self.assertEqual(session_rows[1]["provider_thread_id"], "fixture-thread")
        self.assertEqual(session_rows[1]["provider_turn_id"], "fixture-turn")
        self.assertNotIn("provider_thread_id", session_rows[0]["message"])
        self.assertNotIn("provider_turn_id", session_rows[1]["message"])

    def test_native_marker_free_app_server_replies_follow_installed_schema(self) -> None:
        (data, artifacts, usage), log_path, _progress_path, _executable = self._run("native_marker_free")
        self.assertEqual(data["status"], "candidate")
        self.assertEqual(data["provider_thread_id"], "fixture-thread")
        self.assertEqual(data["provider_turn_id"], "fixture-turn")
        self.assertTrue(artifacts)
        self.assertTrue(usage["uncertain"])
        records = self._rpc_log(log_path)
        methods = [row.get("method") for row in records if row["kind"] == "rpc"]
        self.assertIn("model/list", methods)
        self.assertIn("account/read", methods)
        self.assertIn("thread/start", methods)
        self.assertIn("turn/start", methods)

    def test_catalog_gates_unsupported_model_and_effort_before_any_thread_or_turn(self) -> None:
        for mode in ("unsupported_model", "unsupported_effort", "provider_error", "api_key"):
            with self.subTest(mode=mode):
                workspace = self.prepare("codex-gate-" + uuid.uuid4().hex)
                settings, _, log_path = self._settings(mode)
                request = self._request(workspace)
                with self.assertRaises(AdapterError):
                    execute_agent(request, settings, ProgressLog(None, request["request_id"]), _test_only_allow_unmetered=True)
                methods = [row.get("method") for row in self._rpc_log(log_path) if row["kind"] == "rpc"]
                self.assertNotIn("thread/start", methods)
                self.assertNotIn("thread/resume", methods)
                self.assertNotIn("turn/start", methods)

    def test_subscription_reserve_parses_only_finite_percentages_and_requires_both_windows(self) -> None:
        app = AppServer.__new__(AppServer)
        cases = [
            (0, 40.5, 59.5, True),
            (89, 89.9, 10.1, True),
            (90, 20, 10, False),
            (100, 0, 0, False),
            (None, 0, None, None),
            (True, 0, None, None),
            ("20", 0, None, None),
            (-1, 0, None, None),
            (101, 0, None, None),
            (float("nan"), 0, None, None),
            (float("inf"), 0, None, None),
        ]
        for primary, secondary, remaining, ready in cases:
            with self.subTest(primary=primary, secondary=secondary):
                reply = {"ordinaryUsageAllowed": True, "rateLimits": {
                    "primary": {"usedPercent": primary},
                    "secondary": {"usedPercent": secondary},
                    "credits": {"hasCredits": False},
                }}
                with mock.patch.object(app, "request", return_value=reply) as request:
                    quota, reserve = app.read_subscription_readiness(1)
                request.assert_called_once_with("account/rateLimits/read", {}, 1)
                self.assertEqual(quota, {"ordinary_usage_allowed": True, "purchased_credits_available": False})
                if remaining is None:
                    self.assertIsNone(reserve["remaining_percent"])
                else:
                    self.assertAlmostEqual(reserve["remaining_percent"], remaining)
                self.assertEqual(reserve["ready"], ready)
                self.assertEqual(reserve["required_percent"], 10)
                if remaining is None:
                    self.assertIsNone(reserve["primary_used_percent"])
        for reply in ({}, {"rateLimits": []}, {"rateLimits": {"primary": [], "secondary": None}}):
            with mock.patch.object(app, "request", return_value=reply):
                quota, reserve = app.read_subscription_readiness(1)
            self.assertIsNone(reserve["ready"])
            self.assertIsNone(reserve["remaining_percent"])

    def test_capabilities_numeric_reserve_is_readiness_only_and_never_authorizes_execution(self) -> None:
        settings, _executable, log_path = self._settings("quota_numeric")
        request = {
            "v": 1, "request_id": "reserve-fixture", "op": "agent.capabilities",
            "job_id": "reserve-fixture-job", "workspace": str(self.staging),
            "payload": {}, "context": {},
        }
        data, artifacts, usage = dispatch(request, settings)
        self.assertEqual(data["subscription_reserve"], {
            "primary_used_percent": 15, "secondary_used_percent": 25,
            "remaining_percent": 75, "required_percent": 10, "ready": True,
        })
        self.assertEqual(data["state"], "unavailable")
        self.assertFalse(data["usd_cost_enforced"])
        self.assertIn("USD spend ceiling", data["reason"])
        self.assertEqual(artifacts, [])
        self.assertIsNone(usage)
        methods = [row.get("method") for row in self._rpc_log(log_path) if row["kind"] == "rpc"]
        self.assertEqual(methods, ["initialize", "initialized", "model/list", "account/read", "account/rateLimits/read"])

    def test_capabilities_probe_reads_catalog_account_and_subscription_quota_without_consent(self) -> None:
        settings, _executable, log_path = self._settings("success")
        settings = Settings(**{**settings.__dict__, "codex_consent": False})
        request = {
            "v": 1,
            "request_id": "capabilities-fixture",
            "op": "agent.capabilities",
            "job_id": "capabilities-fixture-job",
            "workspace": str(self.staging),
            "payload": {},
            "context": {},
        }
        data, artifacts, usage = dispatch(request, settings)
        self.assertEqual(data["state"], "unavailable")
        self.assertEqual(data["provider"], "codex-app-server")
        self.assertEqual(data["model"], {"id": self.model, "verified": True})
        self.assertEqual(data["effort"], {"id": self.effort, "verified": True})
        self.assertEqual(data["account_type"], "chatgpt")
        self.assertFalse(data["usd_cost_enforced"])
        self.assertEqual(data["subscription_quota"], {"ordinary_usage_allowed": True, "purchased_credits_available": True})
        self.assertIn("USD spend ceiling", data["reason"])
        self.assertEqual(artifacts, [])
        self.assertTrue(usage is None)
        records = self._rpc_log(log_path)
        methods = [row.get("method") for row in records if row["kind"] == "rpc"]
        self.assertEqual(methods, ["initialize", "initialized", "model/list", "account/read", "account/rateLimits/read"])
        self.assertNotIn("thread/start", methods)
        self.assertNotIn("thread/resume", methods)
        self.assertNotIn("turn/start", methods)
        account_read = next(row["params"] for row in records if row.get("method") == "account/read")
        self.assertEqual(account_read, {"refreshToken": False})
        quota_read = next(row["params"] for row in records if row.get("method") == "account/rateLimits/read")
        self.assertEqual(quota_read, {})
        serialized = json.dumps(data)
        for private_value in ("fixture-private@example.invalid", "fixture-private-account-id", "fixture-private-balance"):
            self.assertNotIn(private_value, serialized)

    def test_capabilities_quota_flags_are_strict_nullable_booleans(self) -> None:
        expected = {
            "quota_true": {"ordinary_usage_allowed": True, "purchased_credits_available": True},
            "quota_false": {"ordinary_usage_allowed": False, "purchased_credits_available": False},
            "quota_missing": {"ordinary_usage_allowed": None, "purchased_credits_available": None},
        }
        for mode, quota in expected.items():
            with self.subTest(mode=mode):
                settings, _executable, log_path = self._settings(mode)
                request = {
                    "v": 1,
                    "request_id": "capabilities-quota-fixture",
                    "op": "agent.capabilities",
                    "job_id": "capabilities-quota-fixture-job",
                    "workspace": str(self.staging),
                    "payload": {},
                    "context": {},
                }
                data, artifacts, usage = dispatch(request, settings)
                self.assertEqual(data["subscription_quota"], quota)
                self.assertEqual(data["state"], "unavailable")
                self.assertFalse(data["usd_cost_enforced"])
                self.assertEqual(artifacts, [])
                self.assertIsNone(usage)
                records = self._rpc_log(log_path)
                methods = [row.get("method") for row in records if row["kind"] == "rpc"]
                self.assertIn("account/rateLimits/read", methods)
                self.assertNotIn("thread/start", methods)
                self.assertNotIn("thread/resume", methods)
                self.assertNotIn("turn/start", methods)
                serialized = json.dumps(data)
                self.assertNotIn("fixture-private-account-id", serialized)
                self.assertNotIn("fixture-private-balance", serialized)

    def test_capabilities_failure_is_structured_and_never_claims_verification(self) -> None:
        for mode in ("unsupported_model", "unsupported_effort", "api_key", "malformed", "invalid_initialize_schema"):
            with self.subTest(mode=mode):
                settings, _executable, log_path = self._settings(mode)
                request = {
                    "v": 1,
                    "request_id": "capabilities-fixture",
                    "op": "agent.capabilities",
                    "job_id": "capabilities-fixture-job",
                    "workspace": str(self.staging),
                    "payload": {},
                    "context": {},
                }
                data, _artifacts, _usage = dispatch(request, settings)
                self.assertEqual(data["state"], "unavailable")
                self.assertFalse(data["usd_cost_enforced"])
                if mode == "unsupported_model":
                    self.assertFalse(data["model"]["verified"])
                    self.assertEqual(data["account_type"], "chatgpt")
                if mode == "unsupported_effort":
                    self.assertTrue(data["model"]["verified"])
                    self.assertFalse(data["effort"]["verified"])
                if mode == "malformed":
                    self.assertFalse(data["model"]["verified"])
                    self.assertEqual(data["account_type"], "unknown")
                if mode == "api_key":
                    self.assertEqual(data["subscription_quota"], {"ordinary_usage_allowed": None, "purchased_credits_available": None})
                methods = [row.get("method") for row in self._rpc_log(log_path) if row["kind"] == "rpc"]
                self.assertNotIn("thread/start", methods)
                if mode == "api_key":
                    self.assertNotIn("account/rateLimits/read", methods)
                self.assertNotIn("turn/start", methods)

    def test_capabilities_requires_an_existing_auth_locator_without_inventing_one(self) -> None:
        settings, _executable, log_path = self._settings("success")
        request = {
            "v": 1,
            "request_id": "capabilities-no-locator",
            "op": "agent.capabilities",
            "job_id": "capabilities-no-locator-job",
            "workspace": str(self.staging),
            "payload": {},
            "context": {},
        }
        with mock.patch.dict(os.environ, {}, clear=True):
            data, _artifacts, _usage = dispatch(request, settings)
        self.assertEqual(data["state"], "unavailable")
        self.assertEqual(data["account_type"], "unknown")
        self.assertFalse(data["usd_cost_enforced"])
        self.assertIn("authentication location", data["reason"])
        self.assertFalse(log_path.exists())

    def test_public_execute_rejects_unknown_usd_cost_before_starting_app_server(self) -> None:
        workspace = self.prepare("codex-unmetered-wire-" + uuid.uuid4().hex)
        settings, _executable, log_path = self._settings("success")
        request = self._request(workspace)
        with self.assertRaisesRegex(AdapterError, "cannot enforce a verified USD spend ceiling") as caught:
            dispatch(request, settings)
        self.assertEqual(caught.exception.code, "POLICY_DENIED")
        self.assertFalse(log_path.exists())
        with self.assertRaisesRegex(AdapterError, "cannot enforce a verified USD spend ceiling"):
            execute_agent(request, settings, ProgressLog(None, request["request_id"]))
        self.assertFalse(log_path.exists())

    def test_unknown_provider_action_is_never_answered_and_turn_is_interrupted(self) -> None:
        (data, artifacts, usage), log_path, _progress_path, _executable = self._run("action")
        self.assertEqual(data["status"], "blocked")
        self.assertEqual(artifacts, [])
        self.assertIsNone(usage["cost_usd"])
        records = self._rpc_log(log_path)
        methods = [row.get("method") for row in records if row["kind"] == "rpc"]
        self.assertIn("turn/interrupt", methods)
        self.assertFalse(any(row.get("id") == 777 for row in records if row["kind"] == "rpc"))

    def test_token_budget_and_time_limit_stop_and_interrupt_without_freezing(self) -> None:
        (data, artifacts, usage), log_path, _progress_path, _executable = self._run("token_budget", token_budget=40)
        self.assertEqual(data["status"], "blocked")
        self.assertEqual(artifacts, [])
        self.assertEqual(usage["total_tokens"], 40)
        self.assertIn("turn/interrupt", [row.get("method") for row in self._rpc_log(log_path) if row["kind"] == "rpc"])

        (data, artifacts, _usage), log_path, _progress_path, _executable = self._run("timeout", max_seconds=1)
        self.assertEqual(data["status"], "blocked")
        self.assertEqual(artifacts, [])
        self.assertIn("turn/interrupt", [row.get("method") for row in self._rpc_log(log_path) if row["kind"] == "rpc"])

    def test_host_cancellation_interrupts_and_host_owned_resume_is_persisted(self) -> None:
        cancel = threading.Event()
        timer = threading.Timer(0.5, cancel.set)
        timer.start()
        try:
            (data, artifacts, _usage), log_path, _progress_path, _executable = self._run("cancel", cancel_event=cancel)
        finally:
            timer.cancel()
        self.assertEqual(data["status"], "blocked")
        self.assertEqual(artifacts, [])
        self.assertIn("turn/interrupt", [row.get("method") for row in self._rpc_log(log_path) if row["kind"] == "rpc"])

        (data, artifacts, _usage), log_path, _progress_path, _executable = self._run("resume", provider_thread_id="host-persisted-thread", objective="fixture objective")
        self.assertEqual(data["status"], "candidate")
        self.assertEqual(data["provider_thread_id"], "host-persisted-thread")
        records = self._rpc_log(log_path)
        methods = [row.get("method") for row in records if row["kind"] == "rpc"]
        self.assertIn("thread/resume", methods)
        self.assertIn("thread/goal/get", methods)
        resume = next(row["params"] for row in records if row.get("method") == "thread/resume")
        self.assertEqual(resume["threadId"], "host-persisted-thread")
        self.assertNotIn("ephemeral", resume)
        self.assertNotIn("allowProviderModelFallback", resume)

    def test_secret_ansi_and_private_activity_are_not_exported(self) -> None:
        (data, _artifacts, _usage), _log_path, progress_path, _executable = self._run("success")
        combined = json.dumps(data, ensure_ascii=False)
        self.assertNotIn("fixture_secret_value_that_must_not_escape", combined)
        self.assertNotIn("API_TOKEN", combined)
        self.assertIn("withheld", data["summary"])
        records = progress_path.read_text(encoding="utf-8")
        self.assertNotIn("fixture_secret_value_that_must_not_escape", records)
        self.assertNotIn("API_TOKEN", records)
        self.assertNotIn("\\u001b", records)
        self.assertIn("unrecognized activity event", records)

    def test_malformed_and_truncated_app_server_output_fail_closed(self) -> None:
        for mode, expected in (
            ("malformed", "malformed JSON-RPC"),
            ("truncated", "truncated event"),
            ("boolean_response_id", "invalid JSON-RPC identifier"),
            ("wrong_jsonrpc", "invalid JSON-RPC message"),
            ("invalid_initialize_schema", "invalid initialization response"),
        ):
            with self.subTest(mode=mode):
                workspace = self.prepare("codex-bad-wire-" + uuid.uuid4().hex)
                settings, _executable, _log = self._settings(mode)
                request = self._request(workspace)
                with self.assertRaises(AdapterError) as caught:
                    execute_agent(request, settings, ProgressLog(None, request["request_id"]), _test_only_allow_unmetered=True)
                self.assertIn(expected, caught.exception.message)

    def test_host_environment_is_allowlisted_and_persisted_settings_cannot_come_from_job_payload(self) -> None:
        workspace = self.prepare("codex-env-" + uuid.uuid4().hex)
        settings, _executable, log_path = self._settings("success")
        test_home = self.root / "host-home"
        test_codex_home = self.root / "host-codex-home"
        test_home.mkdir()
        test_codex_home.mkdir()
        request = self._request(workspace)
        env_secret_name = "API_" + "".join(("TO", "KEN"))
        env_secret_value = "".join(("fi", "xt", "ur", "e", "-env-token-never-forward"))
        with mock.patch.dict(os.environ, {"HOME": str(test_home), "CODEX_HOME": str(test_codex_home), env_secret_name: env_secret_value}, clear=False):
            execute_agent(request, settings, ProgressLog(None, request["request_id"]), _test_only_allow_unmetered=True)
        startup = next(row for row in self._rpc_log(log_path) if row["kind"] == "startup")
        self.assertEqual(startup["home"], str(test_home))
        self.assertEqual(startup["codex_home"], str(test_codex_home))
        self.assertNotIn("API_TOKEN", startup["env_names"])
        self.assertNotIn("fixture-env-token-never-forward", json.dumps(startup))

        malformed = self._request(workspace)
        malformed["payload"]["provider_thread_id"] = "attacker-selected"
        settings, _executable, _log = self._settings("success")
        with self.assertRaises(AdapterError):
            execute_agent(malformed, settings, ProgressLog(None, malformed["request_id"]), _test_only_allow_unmetered=True)

    def test_runtime_state_must_not_overlap_host_auth_or_protected_roots(self) -> None:
        workspace = self.prepare("codex-state-overlap-" + uuid.uuid4().hex)
        settings, _executable, _log = self._settings("success")
        bad_settings = Settings(**{**settings.__dict__, "codex_state_dir": self.source / ".codex-state"})
        request = self._request(workspace)
        with self.assertRaises(AdapterError) as caught:
            execute_agent(request, bad_settings, ProgressLog(None, request["request_id"]), _test_only_allow_unmetered=True)
        self.assertEqual(caught.exception.code, "POLICY_DENIED")

    def test_repository_codex_config_hooks_and_mcp_are_rejected_before_server_start(self) -> None:
        self._write(self.source, ".codex/config.toml", b'[mcp_servers.fixture]\ncommand = "fixture"\n')
        self._commit(self.source, "fixture project Codex config")
        self.base = git(self.source, "rev-parse", "HEAD").decode().strip()
        workspace = self.prepare("codex-project-config")
        settings, _executable, log_path = self._settings("success")
        request = self._request(workspace)
        with self.assertRaises(AdapterError) as caught:
            execute_agent(request, settings, ProgressLog(None, request["request_id"]), _test_only_allow_unmetered=True)
        self.assertEqual(caught.exception.code, "POLICY_DENIED")
        self.assertFalse(log_path.exists())

    def test_disabled_or_unconsented_host_codex_never_starts_executable(self) -> None:
        workspace = self.prepare("codex-disabled")
        settings, _executable, log_path = self._settings("success")
        request = self._request(workspace)
        for changes in ({"codex_enabled": False}, {"codex_consent": False}):
            with self.subTest(changes=changes):
                restricted = Settings(**{**settings.__dict__, **changes})
                with self.assertRaises(AdapterError) as caught:
                    execute_agent(request, restricted, ProgressLog(None, request["request_id"]), _test_only_allow_unmetered=True)
                self.assertEqual(caught.exception.code, "POLICY_DENIED")
                self.assertFalse(log_path.exists())

    def test_settings_require_integer_limits_and_host_owned_catalog_choices(self) -> None:
        env = {
            "SIDEQUEST_ALLOWED_REPO_ROOTS": str(self.repos),
            "SIDEQUEST_STAGING_ROOTS": str(self.staging),
            "SIDEQUEST_ARTIFACT_ROOTS": str(self.artifacts),
            "SIDEQUEST_DELIVERY_ROOTS": str(self.delivery),
            "SIDEQUEST_DELIVERY_APPROVAL_ROOT": str(self.approvals),
            "SIDEQUEST_DELIVERY_STATE_ROOT": str(self.state),
            "SIDEQUEST_CODEX_ENABLED": "true",
            "SIDEQUEST_CODEX_CONSENT": "true",
            "SIDEQUEST_CODEX_EXECUTABLE": sys.executable,
            "SIDEQUEST_CODEX_MODEL": self.model,
            "SIDEQUEST_CODEX_EFFORT": self.effort,
            "SIDEQUEST_CODEX_STATE_DIR": str(self.root / "runtime"),
        }
        with self.assertRaises(ConfigurationError):
            Settings.from_env({**env, "SIDEQUEST_CODEX_MAX_SECONDS": "1.5"})
        with self.assertRaises(ConfigurationError):
            Settings.from_env({**env, "SIDEQUEST_CODEX_TOKEN_BUDGET": "30.0"})
        parsed = Settings.from_env(env)
        self.assertTrue(parsed.codex_enabled)
        self.assertTrue(parsed.codex_consent)
        self.assertEqual(parsed.codex_token_budget, 30000)


if __name__ == "__main__":
    unittest.main()
