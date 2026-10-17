from __future__ import annotations

import asyncio
import hashlib
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from uuid import uuid4
from unittest.mock import patch

import httpx

from services.runtime.adapters import AdapterRunner
from services.runtime.api import create_app
from services.runtime.artifacts import ArtifactStore
from services.runtime.config import RuntimeConfig, codex_catalog_is_fresh, codex_configuration_fingerprint, codex_readiness_is_fresh
from services.runtime.models import JobCreate, Source, TaskPlan, TaskSpec, canonical_json
from services.runtime.policy import ErrorCode, RuntimeFault
from services.runtime.scheduler import Scheduler
from services.runtime.store import RuntimeStore, utc_now
from services.runtime.tests.test_support import open_fixture


TOKEN = "codex-lifecycle-test-" + "x" * 40
CAPABILITY = {
    "state": "available",
    "provider": "codex-app-server",
    "model": {"id": "fixture-model", "verified": True},
    "effort": {"id": "high", "verified": True},
    "account_type": "chatgpt",
    # Test-only synthetic capability used by the internal fake lifecycle.
    # The native B app-server capability always reports this as false today.
    "usd_cost_enforced": True,
    "reason": None,
}


def codex_config(config: RuntimeConfig) -> RuntimeConfig:
    return replace(
        config,
        codex_enabled=True,
        codex_consent=True,
        codex_executable=Path("/usr/bin/true"),
        codex_model="fixture-model",
        codex_effort="high",
        codex_max_seconds=60,
        codex_token_budget=5000,
        codex_state_dir=config.data_dir.parent / "codex-state",
    )


def create_codex_job(store: RuntimeStore, project_id: str) -> str:
    result = store.create_job(
        str(uuid4()),
        store.revision,
        JobCreate(
            project_id=project_id,
            title="Temporary Codex lifecycle fixture",
            source=Source(kind="typed", uri="sidequest:test", text="Make a bounded fixture change."),
            checks=["candidate.frozen_identity"],
            budget_usd="0.200000",
            allowed_actions=["read_repo", "propose_patch", "run_checks"],
            plan=TaskPlan(tasks=[TaskSpec(
                id="codex-task",
                objective="Change one temporary fixture file inside src/.",
                write_paths=["src"],
                check_ids=["candidate.frozen_identity"],
            )]),
        ),
    )
    return result["result"]["job_id"]


def start_codex_attempt(store: RuntimeStore, job_id: str) -> tuple[str, str, dict]:
    store.set_job_command(str(uuid4()), store.revision, "job.run", job_id, codex_ready=True)
    worker = store.create_worker("builder", configuration={"host_codex": True})
    claim = store.claim_ready_task(worker, 200_000, job_id=job_id)
    assert claim is not None
    return worker, claim["attempt_id"], claim


class FakeAdapters:
    def __init__(self, capability: dict | None = None):
        self.calls: list[dict] = []
        self.capability = capability or CAPABILITY

    async def call(self, adapter: str, **kwargs):
        self.calls.append({"adapter": adapter, **kwargs})
        return {"data": self.capability, "artifacts": [], "usage": {}}


class FakeScheduler:
    def __init__(self):
        self.adapters = FakeAdapters()
        self.enqueued: list[str] = []

    def start(self) -> None:
        pass

    async def stop(self) -> None:
        pass

    def enqueue(self, job_id: str) -> None:
        self.enqueued.append(job_id)

    async def pause_job(self, _job_id: str) -> None:
        pass

    async def cancel_job(self, _job_id: str) -> None:
        pass


class FakeCodexPipelineAdapters:
    """In-process deterministic adapter fixture; it never launches Codex or a provider."""

    def __init__(self, base_revision: str, project_id: str):
        self.base_revision = base_revision
        self.project_id = project_id
        self.calls: list[str] = []

    @staticmethod
    def _record(root: Path, artifact_id: str, kind: str, name: str, data: bytes, request: dict, candidate_id: str | None = None) -> dict:
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        result = {
            "id": artifact_id,
            "kind": kind,
            "relative_path": name,
            "media_type": "application/json" if kind in {"file_manifest", "test_report"} else "text/plain",
            "size_bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "display_name": name,
            "immutable": True,
            "job_id": request["job_id"],
            "run_id": request["context"]["run_id"],
        }
        if candidate_id:
            result["candidate_id"] = candidate_id
        return result

    async def call(self, lane: str, **request) -> dict:
        op = request["op"]
        self.calls.append(f"{lane}.{op}")
        if lane == "B" and op == "repo.inspect":
            return {"data": {"revision": self.base_revision, "clean": True, "files": ["README.md"]}, "artifacts": []}
        if lane == "B" and op == "repo.prepare":
            workspace = Path(request["workspace"])
            workspace.mkdir(parents=True)
            (workspace / "README.md").write_text("Temporary committed fixture.\n", encoding="utf-8")
            return {"data": {"workspace": str(workspace), "revision": self.base_revision}, "artifacts": []}
        if lane == "B" and op == "agent.execute":
            output_root = Path(request["context"]["output_root"])
            candidate_id = "cand_fixture_codex"
            snapshot = output_root / "snapshots" / candidate_id
            (snapshot / "src").mkdir(parents=True)
            data = b"fixture candidate from a fake Codex adapter\n"
            (snapshot / "src" / "output.txt").write_bytes(data)
            digest = hashlib.sha256(data).hexdigest()
            tree_rows = [{"path": "src/output.txt", "mode": "100644", "size_bytes": len(data), "sha256": digest}]
            tree_sha = hashlib.sha256(canonical_json({"v": 1, "files": tree_rows}).encode("utf-8")).hexdigest()
            candidate_revision = hashlib.sha1(b"fixture candidate revision").hexdigest()
            manifest_id = "art_fixture_manifest"
            candidate = {
                "id": candidate_id,
                "project_id": self.project_id,
                "base_revision": self.base_revision,
                "candidate_revision": candidate_revision,
                "tree_sha256": tree_sha,
                "patch_sha256": hashlib.sha256(b"fixture patch\n").hexdigest(),
                "manifest_artifact_id": manifest_id,
                "verified_check_ids": [],
            }
            entry = {
                "file_id": "f_fixture_source",
                "path": "src/output.txt",
                "old_path": None,
                "status": "added",
                "media_type": "text/plain",
                "size_bytes": len(data),
                "sha256": digest,
                "added_lines": 1,
                "deleted_lines": 0,
                "binary": False,
                "mode": "100644",
            }
            manifest = (canonical_json({"v": 1, "candidate": candidate, "files": [entry]}) + "\n").encode()
            records = [
                self._record(output_root, manifest_id, "file_manifest", "manifest.json", manifest, request, candidate_id),
                self._record(output_root, "art_fixture_diff", "diff", "diff.txt", b"+fixture\n", request, candidate_id),
                self._record(output_root, "art_fixture_patch", "patch", "patch.txt", b"fixture patch\n", request, candidate_id),
            ]
            return {
                "data": {
                    "status": "candidate",
                    "summary": "A fake Codex session created one fixture file.",
                    "candidate": candidate,
                    "manifest_artifact_id": manifest_id,
                    "snapshot_root": str(snapshot),
                    "provider_thread_id": "thread-fixture-codex",
                    "provider_turn_id": "turn-fixture-codex",
                    "model": "fixture-model",
                    "effort": "high",
                    "model_verified": True,
                    "effort_verified": True,
                    "check_ids": ["candidate.frozen_identity"],
                },
                "artifacts": records,
                "usage": {"input_tokens": 12, "cached_input_tokens": 0, "output_tokens": 5, "total_tokens": 17, "cost_usd": None, "uncertain": True},
                "_cancel_requested": False,
            }
        if lane == "D" and op == "check.run":
            context = request["context"]
            manifest_path = Path(context["artifact_inputs"][0]["staged_path"])
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            candidate = manifest["candidate"]
            entry = manifest["files"][0]
            path = Path(request["workspace"]) / entry["path"]
            if hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
                raise AssertionError("fake D fixture snapshot did not match its manifest")
            result = {
                "id": "candidate.frozen_identity",
                "state": "pass",
                "evidence_artifact_id": candidate["manifest_artifact_id"],
                "message": "The read-only candidate matches its host-staged file manifest.",
            }
            report = {
                "source_revision": context["source_revision"],
                "candidate": candidate,
                "inference_calls": 0,
                "results": [result],
            }
            root = Path(context["output_root"])
            report_record = self._record(
                root,
                "art_fixture_report",
                "test_report",
                "report.json",
                (canonical_json(report) + "\n").encode(),
                request,
            )
            return {
                "data": {
                    "passed": True,
                    "results": [result],
                    "candidate": {"id": candidate["id"], "tree_sha256": candidate["tree_sha256"], "source_revision": context["source_revision"]},
                    "inference_calls": 0,
                },
                "artifacts": [report_record],
                "usage": {"cost_usd": 0.0, "uncertain": False},
            }
        raise AssertionError(f"unexpected fake adapter call: {lane}.{op}")


class BlockingCodexPipelineAdapters(FakeCodexPipelineAdapters):
    """Fake a turn that returns only after the host requests cancellation."""

    def __init__(self, base_revision: str, project_id: str):
        super().__init__(base_revision, project_id)
        self.agent_started = asyncio.Event()

    async def call(self, lane: str, **request) -> dict:
        if lane == "B" and request["op"] == "agent.execute":
            self.calls.append("B.agent.execute")
            self.agent_started.set()
            await request["cancel_event"].wait()
            return {
                "data": {
                    "status": "blocked",
                    "provider_thread_id": "thread-cancelled-fixture",
                    "provider_turn_id": None,
                },
                "artifacts": [],
                "usage": {
                    "input_tokens": None,
                    "cached_input_tokens": None,
                    "output_tokens": None,
                    "total_tokens": None,
                    "cost_usd": None,
                    "uncertain": True,
                },
                "_cancel_requested": True,
            }
        return await super().call(lane, **request)


class CodexLifecycleTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="sidequest-codex-a-")
        self.root = Path(self.temporary.name)
        base_store, base_config, self.project_id = open_fixture(self.root)
        base_store.close()
        self.config = codex_config(base_config)
        self.store = RuntimeStore(self.config)

    async def asyncTearDown(self) -> None:
        self.store.close()
        self.temporary.cleanup()

    def _set_project_policy(self, actions: list[str], **extra: object) -> dict:
        policy = {"allowed_actions": actions, **extra}
        with self.store.transaction() as connection:
            connection.execute(
                "UPDATE projects SET policy_json = ? WHERE id = ?",
                (canonical_json(policy), self.project_id),
            )
            self.store._bump_revision(connection)
        return policy

    async def test_readiness_refresh_is_explicit_cached_and_idempotent(self) -> None:
        scheduler = FakeScheduler()
        app = create_app(self.config, token=TOKEN, store=self.store, scheduler=scheduler)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://runtime") as client:
            auth = {"Authorization": f"Bearer {TOKEN}"}
            initial = await client.get("/v1/capabilities", headers=auth)
            self.assertFalse(initial.json()["features"]["coding"])
            self.assertTrue(initial.json()["codex"]["host_enabled"])
            self.assertEqual(scheduler.adapters.calls, [])

            command = {
                "v": 1,
                "command_id": str(uuid4()),
                "type": "system.codex.refresh",
                "expected_revision": self.store.revision,
                "payload": {},
            }
            first = await client.post("/v1/commands", headers=auth, json=command)
            self.assertEqual(first.status_code, 202)
            replay = await client.post("/v1/commands", headers=auth, json=command)
            self.assertEqual(replay.status_code, 202)
            self.assertEqual(len(scheduler.adapters.calls), 1)
            self.assertEqual(scheduler.adapters.calls[0]["op"], "agent.capabilities")

            job_id = create_codex_job(self.store, self.project_id)
            run_body = {
                "v": 1,
                "command_id": str(uuid4()),
                "type": "job.run",
                "expected_revision": self.store.revision,
                "payload": {"job_id": job_id},
            }
            run = await client.post("/v1/commands", headers=auth, json=run_body)
            self.assertEqual(run.status_code, 202)
            self.assertEqual(scheduler.enqueued, [job_id])
            self.assertEqual((await client.get("/v1/capabilities", headers=auth)).json()["features"]["coding"], True)
            self.assertEqual(len(scheduler.adapters.calls), 1)

    async def test_job_run_requires_cached_verified_readiness_and_consent(self) -> None:
        job_id = create_codex_job(self.store, self.project_id)
        with self.assertRaises(RuntimeFault) as denied:
            self.store.set_job_command(str(uuid4()), self.store.revision, "job.run", job_id, codex_ready=False)
        self.assertEqual(denied.exception.code, ErrorCode.POLICY_DENIED)

    async def test_failed_refresh_reports_current_failure_without_claiming_catalog_verification(self) -> None:
        reason = "Codex app-server cannot start because its state is on a read-only filesystem."
        capability = {
            **CAPABILITY, "state": "unavailable", "usd_cost_enforced": False,
            "model": {"id": self.config.codex_model, "verified": False},
            "effort": {"id": self.config.codex_effort, "verified": False},
            "account_type": "unknown", "reason": reason,
        }
        scheduler = FakeScheduler()
        scheduler.adapters = FakeAdapters(capability)
        app = create_app(self.config, token=TOKEN, store=self.store, scheduler=scheduler)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://runtime") as client:
            auth = {"Authorization": f"Bearer {TOKEN}"}
            response = await client.post("/v1/commands", headers=auth, json={
                "v": 1, "command_id": str(uuid4()), "type": "system.codex.refresh",
                "expected_revision": self.store.revision, "payload": {},
            })
            self.assertEqual(response.status_code, 202)
            caps = (await client.get("/v1/capabilities", headers=auth)).json()
            self.assertEqual(caps["codex"]["state"], "unavailable")
            self.assertEqual(caps["codex"]["reason"], reason)
            self.assertIsNotNone(caps["codex"]["refreshed_at"])
            self.assertFalse(caps["codex"]["catalog_verified"])
            self.assertFalse(caps["features"]["coding"])
            self.assertIn(reason, caps["reasons"])
            self.assertEqual(len(scheduler.adapters.calls), 1)

            # A changed model/account configuration must not present a prior
            # failure, old model identity, or verified flag as current evidence.
            changed = replace(self.config, codex_model="different-model")
            changed_app = create_app(changed, token=TOKEN, store=self.store, scheduler=scheduler)
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=changed_app), base_url="http://runtime") as changed_client:
                caps = (await changed_client.get("/v1/capabilities", headers=auth)).json()
            self.assertEqual(caps["codex"]["state"], "unverified")
            self.assertIsNone(caps["codex"]["reason"])
            self.assertIsNone(caps["codex"]["refreshed_at"])
            self.assertEqual(caps["codex"]["model"], {"id": "different-model", "verified": False})
            self.assertNotIn(reason, caps["reasons"])
            self.assertEqual(len(scheduler.adapters.calls), 1)

    async def test_subscription_reserve_survives_refresh_without_granting_execution(self) -> None:
        scheduler = FakeScheduler()
        scheduler.adapters = FakeAdapters({
            **CAPABILITY,
            "usd_cost_enforced": False,
            "subscription_reserve": {
                "primary_used_percent": 15,
                "secondary_used_percent": 25.5,
                "remaining_percent": 999,
                "required_percent": 0,
                "ready": False,
                "account_id": "must-not-leak",
            },
        })
        app = create_app(self.config, token=TOKEN, store=self.store, scheduler=scheduler)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://runtime") as client:
            auth = {"Authorization": f"Bearer {TOKEN}"}
            response = await client.post("/v1/commands", headers=auth, json={
                "v": 1, "command_id": str(uuid4()), "type": "system.codex.refresh",
                "expected_revision": self.store.revision, "payload": {},
            })
            self.assertEqual(response.status_code, 202)
            caps = (await client.get("/v1/capabilities", headers=auth)).json()
            self.assertEqual(caps["codex"].get("subscription_reserve"), {
                "primary_used_percent": 15,
                "secondary_used_percent": 25.5,
                "remaining_percent": 74.5,
                "required_percent": 10,
                "ready": True,
            })
            self.assertFalse(caps["features"]["coding"])
            self.assertFalse(caps["codex"]["usd_cost_enforced"])
            self.assertNotIn("must-not-leak", json.dumps(caps))
            self.assertEqual(len(scheduler.adapters.calls), 1)

    async def test_subscription_reserve_unknown_boundary_and_stale_reads(self) -> None:
        scheduler = FakeScheduler()
        app = create_app(self.config, token=TOKEN, store=self.store, scheduler=scheduler)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://runtime") as client:
            auth = {"Authorization": f"Bearer {TOKEN}"}
            for secondary, remaining, ready in [(90, 10, False), (89.5, 10.5, True),
                                                ("25", None, None), (True, None, None),
                                                (-1, None, None), (101, None, None), (None, None, None)]:
                with self.subTest(secondary=secondary):
                    self.store.record_codex_readiness(
                        str(uuid4()), self.store.revision,
                        config_sha256=codex_configuration_fingerprint(self.config),
                        capability={**CAPABILITY, "usd_cost_enforced": False,
                                    "subscription_reserve": {"primary_used_percent": 15,
                                                             "secondary_used_percent": secondary,
                                                             "ready": True}},
                        refreshed_at=utc_now(),
                    )
                    caps = (await client.get("/v1/capabilities", headers=auth)).json()
                    reserve = caps["codex"].get("subscription_reserve")
                    self.assertIsInstance(reserve, dict)
                    self.assertEqual(reserve["remaining_percent"], remaining)
                    self.assertIs(reserve["ready"], ready)
                    self.assertFalse(caps["features"]["coding"])
            self.store.record_codex_readiness(
                str(uuid4()), self.store.revision,
                config_sha256=codex_configuration_fingerprint(self.config),
                capability={**CAPABILITY, "subscription_reserve": {
                    "primary_used_percent": 0, "secondary_used_percent": 0, "ready": True}},
                refreshed_at="2000-01-01T00:00:00Z",
            )
            caps = (await client.get("/v1/capabilities", headers=auth)).json()
            self.assertNotIn("subscription_reserve", caps["codex"])
            self.assertEqual(scheduler.adapters.calls, [])

    async def test_native_capability_without_verified_usd_ceiling_cannot_dispatch(self) -> None:
        capability = {
            **CAPABILITY,
            "usd_cost_enforced": False,
            "subscription_quota": {
                "ordinary_usage_allowed": True,
                "purchased_credits_available": "unverified",
                "account_id": "must-not-leak",
                "balance_usd": 123.45,
            },
        }
        scheduler = FakeScheduler()
        scheduler.adapters = FakeAdapters(capability)
        app = create_app(self.config, token=TOKEN, store=self.store, scheduler=scheduler)
        job_id = create_codex_job(self.store, self.project_id)
        original_policy = self._set_project_policy(["read_repo", "run_checks", "local_deliver"], custom="keep")
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://runtime") as client:
            auth = {"Authorization": f"Bearer {TOKEN}"}
            refresh = await client.post("/v1/commands", headers=auth, json={
                "v": 1,
                "command_id": str(uuid4()),
                "type": "system.codex.refresh",
                "expected_revision": self.store.revision,
                "payload": {},
            })
            self.assertEqual(refresh.status_code, 202)
            capabilities = await client.get("/v1/capabilities", headers=auth)
            self.assertEqual(capabilities.status_code, 200)
            self.assertFalse(capabilities.json()["features"]["coding"])
            self.assertFalse(capabilities.json()["features"]["codex_session"])
            self.assertTrue(capabilities.json()["worker_model"]["verified"])
            self.assertTrue(capabilities.json()["codex"]["catalog_verified"])
            self.assertEqual(capabilities.json()["codex"]["state"], "unavailable")
            self.assertIsNotNone(capabilities.json()["codex"]["refreshed_at"])
            self.assertFalse(capabilities.json()["codex"]["usd_cost_enforced"])
            self.assertEqual(capabilities.json()["codex"]["subscription_quota"], {
                "ordinary_usage_allowed": True,
                "purchased_credits_available": None,
            })
            self.assertNotIn("must-not-leak", json.dumps(capabilities.json()))
            self.assertNotIn("balance_usd", json.dumps(capabilities.json()))
            # Fresh GETs are cached reads and must not dispatch another capability process.
            self.assertEqual((await client.get("/v1/capabilities", headers=auth)).status_code, 200)
            self.assertEqual(len(scheduler.adapters.calls), 1)

            run = await client.post("/v1/commands", headers=auth, json={
                "v": 1,
                "command_id": str(uuid4()),
                "type": "job.run",
                "expected_revision": self.store.revision,
                "payload": {"job_id": job_id},
            })
            self.assertEqual(run.status_code, 403)
            self.assertEqual(scheduler.enqueued, [])
            self.assertEqual(len(scheduler.adapters.calls), 1)
            enable = await client.post("/v1/commands", headers=auth, json={
                "v": 1,
                "command_id": str(uuid4()),
                "type": "project.enable_coding",
                "expected_revision": self.store.revision,
                "payload": {"project_id": self.project_id},
            })
            self.assertEqual(enable.status_code, 403)
            self.assertEqual(self.store.get_project(self.project_id)["policy"], original_policy)

    async def test_project_enable_coding_requires_running_host_and_replays_exactly(self) -> None:
        original_policy = self._set_project_policy(["read_repo", "run_checks", "local_deliver"], custom="preserve")
        scheduler = FakeScheduler()
        app = create_app(self.config, token=TOKEN, store=self.store, scheduler=scheduler)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://runtime") as client:
            auth = {"Authorization": f"Bearer {TOKEN}"}
            command = {
                "v": 1,
                "command_id": str(uuid4()),
                "type": "system.codex.refresh",
                "expected_revision": self.store.revision,
                "payload": {},
            }
            refresh = await client.post("/v1/commands", headers=auth, json=command)
            self.assertEqual(refresh.status_code, 202)
            before = await client.get("/v1/snapshot", headers=auth)
            self.assertEqual(before.status_code, 200)
            project = next(item for item in before.json()["projects"] if item["id"] == self.project_id)
            self.assertEqual(project["policy"], {"allowed_actions": original_policy["allowed_actions"]})

            enable_command = {
                "v": 1,
                "command_id": str(uuid4()),
                "type": "project.enable_coding",
                "expected_revision": self.store.revision,
                "payload": {"project_id": self.project_id},
            }
            enabled = await client.post("/v1/commands", headers=auth, json=enable_command)
            self.assertEqual(enabled.status_code, 202)
            revision = self.store.revision
            policy = self.store.get_project(self.project_id)["policy"]
            self.assertEqual(policy, {
                "allowed_actions": ["read_repo", "run_checks", "local_deliver", "propose_patch"],
                "custom": "preserve",
            })
            after = await client.get("/v1/snapshot", headers=auth)
            self.assertEqual(after.status_code, 200)
            updated_project = next(item for item in after.json()["projects"] if item["id"] == self.project_id)
            self.assertEqual(updated_project["policy"], {"allowed_actions": policy["allowed_actions"]})
            replay = await client.post("/v1/commands", headers=auth, json=enable_command)
            self.assertEqual(replay.status_code, 202)
            self.assertEqual(replay.json(), enabled.json())
            self.assertEqual(self.store.revision, revision)
            self.assertEqual(self.store.get_project(self.project_id)["policy"], policy)
            self.assertEqual(len(scheduler.adapters.calls), 1)
            malformed = await client.post("/v1/commands", headers=auth, json={
                "v": 1,
                "command_id": str(uuid4()),
                "type": "project.enable_coding",
                "expected_revision": self.store.revision,
                "payload": {"project_id": self.project_id, "allowed_actions": ["github_pr"]},
            })
            self.assertEqual(malformed.status_code, 400)
            self.assertEqual(self.store.get_project(self.project_id)["policy"], policy)

    async def test_project_enable_coding_requires_host_consent(self) -> None:
        original_policy = self._set_project_policy(["read_repo", "run_checks"], custom="preserve")
        self.config = replace(self.config, codex_consent=False)
        self.store.config = self.config
        scheduler = FakeScheduler()
        app = create_app(self.config, token=TOKEN, store=self.store, scheduler=scheduler)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://runtime") as client:
            auth = {"Authorization": f"Bearer {TOKEN}"}
            refresh = await client.post("/v1/commands", headers=auth, json={
                "v": 1,
                "command_id": str(uuid4()),
                "type": "system.codex.refresh",
                "expected_revision": self.store.revision,
                "payload": {},
            })
            self.assertEqual(refresh.status_code, 202)
            enable = await client.post("/v1/commands", headers=auth, json={
                "v": 1,
                "command_id": str(uuid4()),
                "type": "project.enable_coding",
                "expected_revision": self.store.revision,
                "payload": {"project_id": self.project_id},
            })
            self.assertEqual(enable.status_code, 403)
            self.assertEqual(self.store.get_project(self.project_id)["policy"], original_policy)
            self.assertEqual(len(scheduler.adapters.calls), 1)

    async def test_project_enable_coding_is_denied_after_runtime_stop(self) -> None:
        original_policy = self._set_project_policy(["read_repo", "run_checks"], custom="preserve")
        scheduler = FakeScheduler()
        app = create_app(self.config, token=TOKEN, store=self.store, scheduler=scheduler)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://runtime") as client:
            auth = {"Authorization": f"Bearer {TOKEN}"}
            refresh = await client.post("/v1/commands", headers=auth, json={
                "v": 1,
                "command_id": str(uuid4()),
                "type": "system.codex.refresh",
                "expected_revision": self.store.revision,
                "payload": {},
            })
            self.assertEqual(refresh.status_code, 202)
            stopped = await client.post("/v1/commands", headers=auth, json={
                "v": 1,
                "command_id": str(uuid4()),
                "type": "system.stop",
                "expected_revision": self.store.revision,
                "payload": {},
            })
            self.assertEqual(stopped.status_code, 202)
            enable = await client.post("/v1/commands", headers=auth, json={
                "v": 1,
                "command_id": str(uuid4()),
                "type": "project.enable_coding",
                "expected_revision": self.store.revision,
                "payload": {"project_id": self.project_id},
            })
            self.assertEqual(enable.status_code, 403)
            self.assertEqual(self.store.get_project(self.project_id)["policy"], original_policy)

    async def test_cached_capability_without_usd_signal_keeps_catalog_verified_but_blocks_execution(self) -> None:
        capability = {key: value for key, value in CAPABILITY.items() if key != "usd_cost_enforced"}
        self.store.record_codex_readiness(
            str(uuid4()),
            self.store.revision,
            config_sha256=codex_configuration_fingerprint(self.config),
            capability=capability,
            refreshed_at=utc_now(),
        )
        self.assertFalse(codex_readiness_is_fresh(self.config, self.store.get_codex_readiness()))
        self.assertTrue(codex_catalog_is_fresh(self.config, self.store.get_codex_readiness()))
        job_id = create_codex_job(self.store, self.project_id)
        scheduler = FakeScheduler()
        app = create_app(self.config, token=TOKEN, store=self.store, scheduler=scheduler)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://runtime") as client:
            auth = {"Authorization": f"Bearer {TOKEN}"}
            capabilities = await client.get("/v1/capabilities", headers=auth)
            self.assertEqual(capabilities.status_code, 200)
            self.assertTrue(capabilities.json()["worker_model"]["verified"])
            self.assertTrue(capabilities.json()["codex"]["catalog_verified"])
            self.assertEqual(capabilities.json()["codex"]["state"], "available")
            self.assertIsNotNone(capabilities.json()["codex"]["refreshed_at"])
            self.assertFalse(capabilities.json()["codex"]["usd_cost_enforced"])
            self.assertFalse(capabilities.json()["features"]["coding"])
            self.assertEqual(scheduler.adapters.calls, [])
            run = await client.post("/v1/commands", headers=auth, json={
                "v": 1,
                "command_id": str(uuid4()),
                "type": "job.run",
                "expected_revision": self.store.revision,
                "payload": {"job_id": job_id},
            })
            self.assertEqual(run.status_code, 403)
            self.assertEqual(scheduler.enqueued, [])
            self.assertEqual(scheduler.adapters.calls, [])

    async def test_timezone_less_readiness_is_stale_not_an_http_500(self) -> None:
        self.store.record_codex_readiness(
            str(uuid4()),
            self.store.revision,
            config_sha256=codex_configuration_fingerprint(self.config),
            capability=CAPABILITY,
            refreshed_at="2026-10-14T05:00:00",
        )
        self.assertFalse(codex_catalog_is_fresh(self.config, self.store.get_codex_readiness()))
        job_id = create_codex_job(self.store, self.project_id)
        scheduler = FakeScheduler()
        app = create_app(self.config, token=TOKEN, store=self.store, scheduler=scheduler)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://runtime") as client:
            auth = {"Authorization": f"Bearer {TOKEN}"}
            capabilities = await client.get("/v1/capabilities", headers=auth)
            self.assertEqual(capabilities.status_code, 200)
            self.assertFalse(capabilities.json()["features"]["coding"])
            self.assertFalse(capabilities.json()["worker_model"]["verified"])
            self.assertFalse(capabilities.json()["codex"]["catalog_verified"])
            self.assertEqual(capabilities.json()["codex"]["state"], "unverified")
            self.assertIsNone(capabilities.json()["codex"]["refreshed_at"])
            run = await client.post("/v1/commands", headers=auth, json={
                "v": 1,
                "command_id": str(uuid4()),
                "type": "job.run",
                "expected_revision": self.store.revision,
                "payload": {"job_id": job_id},
            })
            self.assertEqual(run.status_code, 403)
            self.assertEqual(scheduler.enqueued, [])
            self.assertEqual(scheduler.adapters.calls, [])

    async def test_restart_marks_unknown_usage_ambiguous_and_explicit_resume_reuses_attempt(self) -> None:
        job_id = create_codex_job(self.store, self.project_id)
        worker_id, attempt_id, initial_claim = start_codex_attempt(self.store, job_id)
        reservation_id = initial_claim["reservation_id"]
        self.store.record_provider_session(
            attempt_id,
            provider_thread_id="thread-fixture-001",
            provider_turn_id="turn-fixture-001",
            model="fixture-model",
            effort="high",
        )
        self.store.close()
        self.store = RuntimeStore(self.config)
        self.assertEqual(self.store.reconcile_interrupted_attempts(), 1)
        run = self.store.get_run(attempt_id)
        budget = self.store.get_budget(job_id)
        self.assertEqual(run["state"], "ambiguous")
        self.assertIsNone(run["cost_micro"])
        self.assertTrue(run["usage_uncertain"])
        self.assertEqual(budget["reserved_micro"], 200_000)
        self.assertIsNone(budget["spent_micro"])
        self.assertTrue(budget["uncertain"])

        resumed = self.store.set_job_command(
            str(uuid4()), self.store.revision, "job.resume", job_id, codex_ready=True
        )
        claim = self.store.claim_ready_task(worker_id, 0, job_id=job_id)
        self.assertIsNotNone(claim)
        assert claim is not None
        self.assertTrue(claim["resume"])
        self.assertEqual(claim["attempt_id"], attempt_id)
        self.assertEqual(claim["reservation_id"], reservation_id)
        self.assertEqual(claim["reserved_micro"], 200_000)
        self.assertEqual(claim["provider_thread_id"], "thread-fixture-001")
        with self.store.read_connection() as connection:
            attempts = connection.execute("SELECT COUNT(*) FROM attempts WHERE task_id = ?", (claim["task_id"],)).fetchone()[0]
            resume_count = connection.execute("SELECT resume_count FROM attempts WHERE id = ?", (attempt_id,)).fetchone()[0]
        self.assertEqual(attempts, 1)
        self.assertEqual(resume_count, 1)
        self.assertEqual(resumed["result"]["resumed"], True)

    async def test_session_progress_is_persisted_before_only_generic_event_is_published(self) -> None:
        job_id = create_codex_job(self.store, self.project_id)
        _worker_id, attempt_id, _claim = start_codex_attempt(self.store, job_id)
        scheduler = Scheduler(self.store, self.config, AdapterRunner(self.config), ArtifactStore(self.config.artifacts_dir, self.store))
        await scheduler._progress(job_id, attempt_id, {
            "type": "session",
            "message": "Codex provider session is available.",
            "provider_thread_id": "thread-private-001",
            "provider_turn_id": None,
        })
        await scheduler._progress(job_id, attempt_id, {
            "type": "session",
            "message": "Codex provider session is available.",
            "provider_thread_id": "thread-private-001",
            "provider_turn_id": "turn-private-001",
        })
        run = self.store.get_run(attempt_id)
        events = self.store.list_run_events(attempt_id)
        self.assertEqual(run["provider_thread_id"], "thread-private-001")
        self.assertEqual(run["provider_turn_id"], "turn-private-001")
        self.assertNotIn("thread-private-001", " ".join(event["message"] for event in events))
        self.assertNotIn("turn-private-001", " ".join(event["message"] for event in events))
        self.assertEqual(
            sum(event["message"] == "Codex session progress was saved." for event in events),
            2,
        )

    async def test_provider_thread_identity_cannot_change_within_attempt(self) -> None:
        job_id = create_codex_job(self.store, self.project_id)
        _worker_id, attempt_id, _claim = start_codex_attempt(self.store, job_id)
        self.store.record_provider_session(
            attempt_id,
            provider_thread_id="thread-stable-001",
            provider_turn_id=None,
            model=None,
            effort=None,
        )
        with self.assertRaises(RuntimeFault) as changed:
            self.store.record_provider_session(
                attempt_id,
                provider_thread_id="thread-other-001",
                provider_turn_id="turn-001",
                model=None,
                effort=None,
            )
        self.assertEqual(changed.exception.code, ErrorCode.VERSION_CONFLICT)

    async def test_provider_session_ids_match_the_bounded_adapter_contract(self) -> None:
        job_id = create_codex_job(self.store, self.project_id)
        _worker_id, attempt_id, _claim = start_codex_attempt(self.store, job_id)
        maximum_id = "t" + "x" * 511
        self.store.record_provider_session(
            attempt_id,
            provider_thread_id=maximum_id,
            provider_turn_id=None,
            model=None,
            effort=None,
        )
        self.assertEqual(self.store.get_run(attempt_id)["provider_thread_id"], maximum_id)
        with self.assertRaises(RuntimeFault) as oversized:
            self.store.record_provider_session(
                attempt_id,
                provider_thread_id="t" + "x" * 512,
                provider_turn_id=None,
                model=None,
                effort=None,
            )
        self.assertEqual(oversized.exception.code, ErrorCode.INVALID_INPUT)

    async def test_codex_auth_locators_are_forwarded_only_on_codex_operations(self) -> None:
        runner = AdapterRunner(self.config)
        host_home = str(self.root / "host-home")
        host_codex_home = str(self.root / "host-codex-home")
        with patch.dict("os.environ", {
            "HOME": host_home,
            "CODEX_HOME": host_codex_home,
            "SIDEQUEST_API_TOKEN": "secret-local-api-token",
            "UNRELATED_CREDENTIAL": "never-forward-this",
        }, clear=False):
            codex_env = runner._environment(codex_operation=True)
            git_env = runner._environment(codex_operation=False)
        self.assertEqual(codex_env["HOME"], host_home)
        self.assertEqual(codex_env["CODEX_HOME"], host_codex_home)
        self.assertNotIn("CODEX_HOME", git_env)
        self.assertNotEqual(git_env["HOME"], host_home)
        for environment in (codex_env, git_env):
            self.assertNotIn("SIDEQUEST_API_TOKEN", environment)
            self.assertNotIn("UNRELATED_CREDENTIAL", environment)

    async def test_scheduler_pipeline_uses_only_fake_codex_and_preserves_unknown_usage(self) -> None:
        project = self.store.get_project(self.project_id)
        self.store.record_codex_readiness(
            str(uuid4()),
            self.store.revision,
            config_sha256=codex_configuration_fingerprint(self.config),
            capability=CAPABILITY,
            refreshed_at=utc_now(),
        )
        job_id = create_codex_job(self.store, self.project_id)
        fake = FakeCodexPipelineAdapters(project["base_revision"], self.project_id)
        scheduler = Scheduler(self.store, self.config, fake, ArtifactStore(self.config.artifacts_dir, self.store))
        scheduler.start()
        try:
            self.store.set_job_command(str(uuid4()), self.store.revision, "job.run", job_id, codex_ready=True)
            scheduler.enqueue(job_id)
            for _ in range(200):
                current = self.store.get_job(job_id)
                if current["state"] not in {"queued", "running"}:
                    break
                await asyncio.sleep(0.025)
            self.assertEqual(current["state"], "verifying", {"job": current, "calls": fake.calls, "events": self.store.list_run_events(self.store.list_job_runs(job_id)[0]["id"])})
            self.assertEqual(fake.calls, ["B.repo.inspect", "B.repo.prepare", "B.agent.execute", "D.check.run"])
            self.assertEqual(current["candidate_id"], "cand_fixture_codex")
            run = self.store.list_job_runs(job_id)[0]
            budget = self.store.get_budget(job_id)
            self.assertEqual(run["state"], "completed")
            self.assertEqual(run["provider_thread_id"], "thread-fixture-codex")
            self.assertEqual(run["provider_turn_id"], "turn-fixture-codex")
            self.assertEqual(run["model"], "fixture-model")
            self.assertIsNone(run["cost_micro"])
            self.assertEqual(run["input_tokens"], 12)
            self.assertTrue(run["usage_uncertain"])
            self.assertGreater(budget["reserved_micro"], 0)
            self.assertIsNone(budget["spent_micro"])
            self.assertTrue(budget["uncertain"])
            self.assertTrue(any(item["kind"] == "file_manifest" for item in self.store.list_job_artifacts(job_id)))
            self.assertFalse(any("repo.deliver" in call for call in fake.calls))
        finally:
            await scheduler.stop()

    async def test_pause_interrupts_codex_and_keeps_attempt_ambiguous_without_retry(self) -> None:
        project = self.store.get_project(self.project_id)
        self.store.record_codex_readiness(
            str(uuid4()),
            self.store.revision,
            config_sha256=codex_configuration_fingerprint(self.config),
            capability=CAPABILITY,
            refreshed_at=utc_now(),
        )
        job_id = create_codex_job(self.store, self.project_id)
        fake = BlockingCodexPipelineAdapters(project["base_revision"], self.project_id)
        scheduler = Scheduler(self.store, self.config, fake, ArtifactStore(self.config.artifacts_dir, self.store))
        scheduler.start()
        try:
            self.store.set_job_command(str(uuid4()), self.store.revision, "job.run", job_id, codex_ready=True)
            scheduler.enqueue(job_id)
            await asyncio.wait_for(fake.agent_started.wait(), timeout=2.0)
            self.store.set_job_command(str(uuid4()), self.store.revision, "job.pause", job_id)
            await scheduler.pause_job(job_id)

            current = self.store.get_job(job_id)
            self.assertEqual(current["state"], "paused")
            runs = self.store.list_job_runs(job_id)
            self.assertEqual(len(runs), 1)
            self.assertEqual(runs[0]["state"], "ambiguous")
            self.assertEqual(runs[0]["provider_thread_id"], "thread-cancelled-fixture")
            self.assertIsNone(runs[0]["cost_micro"])
            budget = self.store.get_budget(job_id)
            self.assertGreater(budget["reserved_micro"], 0)
            self.assertTrue(budget["uncertain"])
            self.assertEqual(fake.calls, ["B.repo.inspect", "B.repo.prepare", "B.agent.execute"])
        finally:
            await scheduler.stop()
