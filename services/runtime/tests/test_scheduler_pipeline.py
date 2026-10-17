from __future__ import annotations

import asyncio
import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from uuid import uuid4

import httpx

from services.runtime.adapters import AdapterRunner
from services.runtime.api import create_app
from services.runtime.artifacts import ArtifactStore
from services.runtime.models import JobCreate, Source
from services.runtime.scheduler import Scheduler
from services.runtime.tests.test_support import open_fixture


_FAKE_ADAPTER = r'''import hashlib, json, os, shutil, sys
from pathlib import Path

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def record(root, artifact_id, kind, name, data, job_id, run_id, candidate_id=None):
    rel = name
    target = Path(root) / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    item = {"id":artifact_id,"kind":kind,"relative_path":rel,"media_type":"application/json" if kind in {"file_manifest","test_report"} else "text/x-diff; charset=utf-8",
      "size_bytes":len(data),"sha256":hashlib.sha256(data).hexdigest(),"display_name":name,"immutable":True,"job_id":job_id,"run_id":run_id}
    if candidate_id:
        item["candidate_id"] = candidate_id
    return item

req = json.loads(sys.stdin.buffer.readline())
with open(Path(__file__).with_name("calls.log"), "a", encoding="utf-8") as log:
    log.write(sys.argv[1] + " " + req["op"] + "\n")
lane = sys.argv[1]
op = req["op"]
data = {}
artifacts = []
if lane == "B" and op == "repo.inspect":
    data = {"revision":req["payload"]["revision"], "clean":True, "files":["README.md"]}
elif lane == "B" and op == "repo.prepare":
    workspace = Path(req["workspace"])
    workspace.mkdir(parents=True)
    source = Path(req["payload"]["repo_path"])
    shutil.copyfile(source / "README.md", workspace / "README.md")
    data = {"workspace":str(workspace), "revision":req["payload"]["revision"]}
elif lane == "B" and op == "artifacts.freeze":
    root = Path(req["context"]["output_root"])
    snapshot = root / "snapshot"
    snapshot.mkdir()
    raw = (Path(req["workspace"]) / "README.md").read_bytes()
    (snapshot / "README.md").write_bytes(raw)
    digest = hashlib.sha256(raw).hexdigest()
    base = req["context"]["source_revision"]
    rows = [{"path":"README.md","mode":"100644","size_bytes":len(raw),"sha256":digest}]
    tree_sha = hashlib.sha256(canonical({"v":1,"files":rows}).encode("utf-8")).hexdigest()
    candidate_id = "cand_" + req["request_id"].replace("-", "")
    manifest_id = "art_" + req["request_id"].replace("-", "") + "_manifest"
    diff_id = "art_" + req["request_id"].replace("-", "") + "_diff"
    patch_id = "art_" + req["request_id"].replace("-", "") + "_patch"
    candidate = {"id":candidate_id,"project_id":req["context"]["project_id"],"base_revision":base,"candidate_revision":base,"tree_sha256":tree_sha,"patch_sha256":hashlib.sha256(b"").hexdigest(),"manifest_artifact_id":manifest_id,"verified_check_ids":[]}
    entry = {"file_id":"f_" + hashlib.sha256((candidate_id + "\0README.md").encode()).hexdigest()[:32],"path":"README.md","old_path":None,"status":"unchanged","media_type":"text/plain","size_bytes":len(raw),"sha256":digest,"added_lines":0,"deleted_lines":0,"binary":False,"mode":"100644"}
    manifest = (canonical({"v":1,"candidate":candidate,"files":[entry]}) + "\n").encode("utf-8")
    artifacts = [
      record(root, manifest_id, "file_manifest", "manifest.json", manifest, req["job_id"], req["context"]["run_id"], candidate_id),
      record(root, diff_id, "diff", "diff.diff", b"", req["job_id"], req["context"]["run_id"], candidate_id),
      record(root, patch_id, "patch", "patch.patch", b"", req["job_id"], req["context"]["run_id"], candidate_id),
    ]
    data = {"candidate":candidate,"manifest_artifact_id":manifest_id,"diff_artifact_id":diff_id,"patch_artifact_id":patch_id,"snapshot_root":str(snapshot)}
elif lane == "D" and op == "check.run":
    context = req["context"]
    manifest_path = Path(context["artifact_inputs"][0]["staged_path"])
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    candidate = manifest["candidate"]
    entry = manifest["files"][0]
    raw = (Path(req["workspace"]) / entry["path"]).read_bytes()
    if hashlib.sha256(raw).hexdigest() != entry["sha256"] or len(raw) != entry["size_bytes"]:
        raise SystemExit("candidate mismatch")
    result = {"id":"candidate.frozen_identity","state":"pass","evidence_artifact_id":candidate["manifest_artifact_id"],"message":"The read-only candidate matches its host-staged file manifest."}
    data = {"passed":True,"results":[result],"candidate":{"id":candidate["id"],"tree_sha256":candidate["tree_sha256"],"source_revision":context["source_revision"]},"inference_calls":0}
    report = {"source_revision":context["source_revision"],"candidate":candidate,"inference_calls":0,"results":[result]}
    artifacts = [record(Path(context["output_root"]),"art_" + req["request_id"].replace("-", "") + "_report","test_report","test_report.json",(canonical(report)+"\n").encode(),req["job_id"],context["run_id"])]
else:
    raise SystemExit("unexpected fake operation")
response = {"v":1,"request_id":req["request_id"],"ok":True,"data":data,"artifacts":artifacts}
if lane == "D":
    response["usage"] = {"cost_usd":0.0,"uncertain":False}
sys.stdout.write(canonical(response) + "\n")
'''


class SchedulerPipelineTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.store, original, self.project_id = open_fixture(self.root)
        fake_b = self.root / "fake-b.py"
        fake_d = self.root / "fake-d.py"
        fake_b.write_text(_FAKE_ADAPTER, encoding="utf-8")
        fake_d.write_text(_FAKE_ADAPTER, encoding="utf-8")
        self.config = replace(
            original,
            max_parallel=1,
            b_argv=(sys.executable, str(fake_b), "B"),
            d_argv=(sys.executable, str(fake_d), "D"),
            adapter_timeout_seconds=10,
        )
        self.artifacts = ArtifactStore(self.config.artifacts_dir, self.store)
        self.runner = AdapterRunner(self.config)
        self.scheduler = Scheduler(self.store, self.config, self.runner, self.artifacts)
        self.app = create_app(self.config, token="fake-adapter-token-" + "x" * 40, store=self.store, scheduler=self.scheduler)
        self.http = httpx.AsyncClient(transport=httpx.ASGITransport(app=self.app), base_url="http://runtime")
        self.auth = {"Authorization": "Bearer " + "fake-adapter-token-" + "x" * 40}
        self.scheduler.start()

    async def asyncTearDown(self) -> None:
        await self.scheduler.stop()
        await self.http.aclose()
        self.store.close()
        self.temporary.cleanup()

    async def test_job_runs_real_bounded_pipeline_with_fake_host_adapters(self) -> None:
        create = await self.http.post("/v1/commands", headers=self.auth, json={
            "v": 1,
            "command_id": str(uuid4()),
            "type": "job.create",
            "expected_revision": self.store.revision,
            "payload": {
                "project_id": self.project_id,
                "title": "Fake adapter local inspection",
                "source": {"kind": "typed", "uri": "sidequest:local-git-inspection", "text": "Inspect the committed fixture."},
                "checks": ["candidate.frozen_identity"],
                "budget_usd": 0,
                "allowed_actions": ["read_repo", "run_checks"],
            },
        })
        self.assertEqual(create.status_code, 202, create.text)
        job_id = create.json()["result"]["job_id"]
        run = await self.http.post("/v1/commands", headers=self.auth, json={
            "v": 1,
            "command_id": str(uuid4()),
            "type": "job.run",
            "expected_revision": create.json()["revision"],
            "payload": {"job_id": job_id},
        })
        self.assertEqual(run.status_code, 202, run.text)

        for _ in range(200):
            current = self.store.get_job(job_id)
            if current["state"] not in {"running", "queued"}:
                break
            await asyncio.sleep(0.025)
        self.assertEqual(current["state"], "verifying", current)
        self.assertEqual(current["spent_micro"], 0)
        detailed = (await self.http.get(f"/v1/jobs/{job_id}", headers=self.auth)).json()["job"]
        self.assertEqual(detailed["execution_profile"], "local_git_inspection")
        self.assertEqual(detailed["spent_usd"], 0.0)
        self.assertEqual(detailed["checks"][0]["state"], "pass")
        self.assertEqual(len(detailed["run_ids"]), 1)
        self.assertTrue(detailed["candidate_id"].startswith("cand_"))
        page = (await self.http.get(f"/v1/jobs/{job_id}/artifacts?limit=100", headers=self.auth)).json()
        self.assertEqual({item["kind"] for item in page["items"]} >= {"file_manifest", "diff", "patch", "source_file", "test_report"}, True)
        manifest_id = next(item["id"] for item in page["items"] if item["kind"] == "file_manifest")
        files = (await self.http.get(f"/v1/artifacts/{manifest_id}/files", headers=self.auth)).json()
        self.assertEqual(files["files"][0]["path"], "README.md")
        self.assertTrue(files["files"][0]["artifact_id"])
        events = (await self.http.get(f"/v1/runs/{detailed['run_ids'][0]}/events", headers=self.auth)).json()
        self.assertGreaterEqual(len(events["items"]), 2)
        self.assertTrue(all(item["type"] in {"status", "tool_started", "tool_finished", "output", "warning", "usage"} for item in events["items"]))

        calls = (self.root / "calls.log").read_text(encoding="utf-8").splitlines()
        self.assertEqual(calls, ["B repo.inspect", "B repo.prepare", "B artifacts.freeze", "D check.run"])
        self.assertFalse(any("agent.execute" in item or "repo.deliver" in item for item in calls))
        self.assertFalse(self.store.list_workers()[0]["configuration"].get("provider_dispatch", False))

    async def test_actual_b_and_d_modules_on_temporary_git_fixture(self) -> None:
        config = replace(
            self.config,
            b_argv=(sys.executable, "-m", "services.tools.main"),
            d_argv=(sys.executable, "-m", "services.workshops.main"),
            adapter_timeout_seconds=30,
        )
        artifacts = ArtifactStore(config.artifacts_dir, self.store)
        scheduler = Scheduler(self.store, config, AdapterRunner(config), artifacts)
        scheduler.start()
        try:
            created = self.store.create_job(
                str(uuid4()),
                self.store.revision,
                JobCreate(
                    project_id=self.project_id,
                    title="Actual B and D fixture inspection",
                    source=Source(
                        kind="typed",
                        uri="sidequest:local-git-inspection",
                        text="Inspect a temporary committed Git fixture without modifying it.",
                    ),
                    checks=["candidate.frozen_identity"],
                    budget_usd=0,
                    allowed_actions=["read_repo", "run_checks"],
                ),
            )
            job_id = created["result"]["job_id"]
            self.store.set_job_command(str(uuid4()), self.store.revision, "job.run", job_id)
            scheduler.enqueue(job_id)
            for _ in range(600):
                current = self.store.get_job(job_id)
                if current["state"] not in {"queued", "running"}:
                    break
                await asyncio.sleep(0.05)
            self.assertEqual(current["state"], "verifying", current)
            self.assertEqual(current["spent_micro"], 0)
            self.assertIsNotNone(current["candidate_id"])
            imported = self.store.list_job_artifacts(job_id, limit=100)
            self.assertTrue(any(item["kind"] == "file_manifest" for item in imported))
            self.assertTrue(any(item["kind"] == "diff" for item in imported))
            self.assertTrue(any(item["kind"] == "source_file" for item in imported))
            self.assertTrue(any(item["kind"] == "test_report" for item in imported))
        finally:
            await scheduler.stop()

    async def test_malformed_b_response_kills_descendant_and_stops_pipeline(self) -> None:
        pid_path = self.root / "malformed-descendant.pid"
        calls_path = self.root / "malformed-calls.log"
        adapter_path = self.root / "malformed-adapter.py"
        adapter_path.write_text(r'''import json, subprocess, sys
from pathlib import Path

lane = sys.argv[1]
pid_path = Path(sys.argv[2])
calls_path = Path(sys.argv[3])
request = json.loads(sys.stdin.buffer.readline())
with calls_path.open("a", encoding="utf-8") as stream:
    stream.write(lane + " " + request["op"] + "\n")
child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
pid_path.write_text(str(child.pid), encoding="ascii")
response = {"v":1,"request_id":"wrong-request-id","ok":True,"data":{},"artifacts":[]}
sys.stdout.write(json.dumps(response, separators=(",",":")) + "\n")
sys.stdout.flush()
''', encoding="utf-8")
        config = replace(
            self.config,
            b_argv=(sys.executable, str(adapter_path), "B", str(pid_path), str(calls_path)),
            d_argv=(sys.executable, str(adapter_path), "D", str(pid_path), str(calls_path)),
            adapter_timeout_seconds=5,
        )
        scheduler = Scheduler(
            self.store,
            config,
            AdapterRunner(config),
            ArtifactStore(config.artifacts_dir, self.store),
        )
        scheduler.start()
        try:
            created = self.store.create_job(
                str(uuid4()),
                self.store.revision,
                JobCreate(
                    project_id=self.project_id,
                    title="Malformed adapter boundary fixture",
                    source=Source(kind="typed", uri="sidequest:malformed-adapter", text="Inspect the fixture."),
                    checks=["candidate.frozen_identity"],
                    budget_usd=0,
                    allowed_actions=["read_repo", "run_checks"],
                ),
            )
            job_id = created["result"]["job_id"]
            self.store.set_job_command(str(uuid4()), self.store.revision, "job.run", job_id)
            scheduler.enqueue(job_id)
            for _ in range(300):
                current = self.store.get_job(job_id)
                if current["state"] not in {"queued", "running"}:
                    break
                await asyncio.sleep(0.01)
            self.assertEqual(current["state"], "blocked", current)
            self.assertEqual(calls_path.read_text(encoding="utf-8").splitlines(), ["B repo.inspect"])
            for _ in range(300):
                pid = int(pid_path.read_text(encoding="ascii")) if pid_path.exists() else None
                if pid is not None:
                    try:
                        os.kill(pid, 0)
                        proc_stat = Path(f"/proc/{pid}/stat")
                        if proc_stat.exists() and proc_stat.read_text(encoding="ascii").rsplit(")", 1)[1].strip().split()[0] == "Z":
                            break
                    except ProcessLookupError:
                        break
                await asyncio.sleep(0.01)
            else:
                self.fail("malformed adapter descendant remained alive")
        finally:
            await scheduler.stop()


if __name__ == "__main__":
    unittest.main()
