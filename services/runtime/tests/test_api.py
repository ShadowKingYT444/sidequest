from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from uuid import uuid4

import httpx

from services.runtime.api import create_app
from services.runtime.artifacts import ArtifactStore
from services.runtime.models import CandidateCreate, JobCreate, Source, canonical_json
from services.runtime.tests.test_support import open_fixture


TOKEN = "local-test-token-" + "x" * 40


class FakeScheduler:
    def __init__(self):
        self.enqueued: list[str] = []
        self.stopped = False

    def start(self) -> None:
        pass

    async def stop(self) -> None:
        self.stopped = True

    def enqueue(self, job_id: str) -> None:
        self.enqueued.append(job_id)

    async def pause_job(self, _job_id: str) -> None:
        pass

    async def cancel_job(self, _job_id: str) -> None:
        pass


class RuntimeApiTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.store, original, self.project_id = open_fixture(self.root)
        self.config = replace(original, b_argv=("fake-b",), d_argv=("fake-d",))
        self.scheduler = FakeScheduler()
        self.app = create_app(self.config, token=TOKEN, store=self.store, scheduler=self.scheduler)
        self.http = httpx.AsyncClient(transport=httpx.ASGITransport(app=self.app), base_url="http://runtime")
        self.artifacts = self.app.state.artifact_store
        self.job_id, self.run_id, self.candidate_id, self.manifest_id, self.diff_id, self.file_ids = self._seed_inspection()
        self.auth = {"Authorization": f"Bearer {TOKEN}"}

    async def asyncTearDown(self) -> None:
        await self.http.aclose()
        self.store.close()
        self.temporary.cleanup()

    def _register_bytes(
        self,
        *,
        artifact_id: str,
        job_id: str,
        run_id: str,
        kind: str,
        name: str,
        data: bytes,
        candidate_id: str | None = None,
    ) -> str:
        digest = hashlib.sha256(data).hexdigest()
        key = self.artifacts._write_content(data, digest)
        created = self.store.create_artifact(
            artifact_id=artifact_id,
            job_id=job_id,
            run_id=run_id,
            kind=kind,
            media_type="application/octet-stream" if b"\x00" in data else "text/plain; charset=utf-8",
            display_name=name,
            sha256=digest,
            size_bytes=len(data),
            storage_key=key,
            immutable=True,
        )
        if candidate_id is not None:
            self.store.attach_artifacts_to_candidate(candidate_id, [created])
        return created

    def _seed_inspection(self) -> tuple[str, str, str, str, str, dict[str, str]]:
        response = self.store.create_job(
            str(uuid4()),
            self.store.revision,
            JobCreate(
                project_id=self.project_id,
                title="Read-only fixture inspection",
                source=Source(kind="typed", uri="sidequest:test", text="Inspect the temporary fixture."),
                checks=["candidate.frozen_identity"],
                budget_usd=0,
                allowed_actions=["read_repo", "run_checks"],
            ),
        )
        job_id = response["result"]["job_id"]
        worker_id = self.store.create_worker("verifier", trusted_deterministic_internal=True)
        claim = self.store.claim_ready_task(worker_id, 0, job_id=job_id)
        self.assertIsNotNone(claim)
        assert claim is not None
        run_id = claim["attempt_id"]
        self.store.settle_attempt(run_id, cost_micro=0, uncertain=False, state="completed")
        base = self.store.get_project(self.project_id)["base_revision"]
        candidate_id = "cand_api_fixture"
        file_bytes = {
            "alpha.txt": b"first <script>alert(1)</script>\x1b[31m\nsecond line\n",
            "binary.dat": b"\x00\xff\x10",
            "zeta.txt": b"unchanged\n",
        }
        file_ids = {"alpha.txt": "f_alpha", "binary.dat": "f_binary", "zeta.txt": "f_zeta"}
        entries = []
        tree_rows = []
        for path, data in file_bytes.items():
            digest = hashlib.sha256(data).hexdigest()
            mode = "100644"
            entries.append({
                "file_id": file_ids[path],
                "path": path,
                "old_path": None,
                "status": "unchanged",
                "media_type": "application/octet-stream" if path.endswith(".dat") else "text/plain",
                "size_bytes": len(data),
                "sha256": digest,
                "added_lines": 0,
                "deleted_lines": 0,
                "binary": path.endswith(".dat"),
                "mode": mode,
            })
            tree_rows.append({"path": path, "mode": mode, "size_bytes": len(data), "sha256": digest})
        tree_sha = hashlib.sha256(canonical_json({"v": 1, "files": tree_rows}).encode("utf-8")).hexdigest()
        patch_sha = hashlib.sha256(b"fixture patch\n").hexdigest()
        manifest_id = "art_api_manifest"
        candidate = {
            "id": candidate_id,
            "project_id": self.project_id,
            "base_revision": base,
            "candidate_revision": base,
            "tree_sha256": tree_sha,
            "patch_sha256": patch_sha,
            "manifest_artifact_id": manifest_id,
            "verified_check_ids": [],
        }
        manifest = {"v": 1, "candidate": candidate, "files": entries}
        manifest_bytes = (canonical_json(manifest) + "\n").encode("utf-8")
        self._register_bytes(
            artifact_id=manifest_id,
            job_id=job_id,
            run_id=run_id,
            kind="file_manifest",
            name="Frozen candidate manifest",
            data=manifest_bytes,
        )
        source_artifact_ids: dict[str, str] = {}
        for index, (path, data) in enumerate(file_bytes.items()):
            artifact_id = f"art_api_file_{index}"
            self._register_bytes(
                artifact_id=artifact_id,
                job_id=job_id,
                run_id=run_id,
                kind="source_file",
                name=path,
                data=data,
            )
            source_artifact_ids[path] = artifact_id
        diff = (
            b"diff --git a/alpha.txt b/alpha.txt\nindex 1111111..2222222 100644\n"
            b"--- a/alpha.txt\n+++ b/alpha.txt\n@@ -1,2 +1,2 @@\n-old line\n+new line\n context line\n"
            b"diff --git a/binary.dat b/binary.dat\nindex 1111111..2222222 100644\nBinary files a/binary.dat and b/binary.dat differ\n"
        )
        diff_id = "art_api_diff"
        self._register_bytes(
            artifact_id=diff_id,
            job_id=job_id,
            run_id=run_id,
            kind="diff",
            name="Frozen candidate diff",
            data=diff,
        )
        patch_id = "art_api_patch"
        self._register_bytes(
            artifact_id=patch_id,
            job_id=job_id,
            run_id=run_id,
            kind="patch",
            name="Frozen candidate patch",
            data=b"fixture patch\n",
        )
        report_id = "art_api_report"
        self._register_bytes(
            artifact_id=report_id,
            job_id=job_id,
            run_id=run_id,
            kind="test_report",
            name="Frozen identity check report",
            data=b'{"passed":true}\n',
        )
        self.store.create_candidate(CandidateCreate(
            candidate_id=candidate_id,
            source_revision=base,
            tree_sha256=tree_sha,
            patch_sha256=patch_sha,
            job_id=job_id,
            run_id=run_id,
            base_revision=base,
            candidate_revision=base,
            manifest_artifact_id=manifest_id,
        ))
        self.store.attach_artifacts_to_candidate(candidate_id, [*source_artifact_ids.values(), diff_id, patch_id, report_id])
        self.store.finalize_job(job_id, "verifying", "Fixture identity check passed.")
        log_id = "art_api_log"
        self._register_bytes(
            artifact_id=log_id,
            job_id=job_id,
            run_id=run_id,
            kind="log",
            name="Fixture log",
            data=b"\x1b[31m<script>hostile</script>\x1b[0m\n",
        )
        self.store.append_run_event(job_id, run_id, "output", "\x1b[31m<script>log</script>\x1b[0m")
        return job_id, run_id, candidate_id, manifest_id, diff_id, file_ids

    async def test_auth_capabilities_and_paged_job_summary(self) -> None:
        unauthorized = await self.http.get("/v1/snapshot")
        self.assertEqual(unauthorized.status_code, 403)
        self.assertEqual((await self.http.get("/health")).json()["service"], "sidequest-runtime")
        caps = (await self.http.get("/v1/capabilities", headers=self.auth)).json()
        self.assertTrue(caps["features"]["local_git_inspection"])
        self.assertFalse(caps["worker_model"]["verified"])
        self.assertFalse(caps["features"]["coding"])
        summary = await self.http.get(f"/v1/jobs/{self.job_id}/artifacts?limit=2", headers=self.auth)
        self.assertEqual(summary.status_code, 200)
        page = summary.json()
        self.assertEqual([item["kind"] for item in page["items"]], ["file_manifest", "diff"])
        self.assertTrue(page["next_cursor"])
        next_page = await self.http.get(
            f"/v1/jobs/{self.job_id}/artifacts?limit=2&cursor={page['next_cursor']}", headers=self.auth
        )
        self.assertEqual(next_page.status_code, 200)
        self.assertEqual([item["kind"] for item in next_page.json()["items"]], ["patch", "test_report"])
        hostile = await self.http.get("/v1/artifacts/art_api_log", headers=self.auth)
        self.assertEqual(hostile.status_code, 200)
        preview = hostile.json()["preview_text"]
        self.assertNotIn("\x1b", preview)
        self.assertIn("<script>hostile</script>", preview)

    async def test_manifest_text_diff_and_cursor_scope(self) -> None:
        response = await self.http.get(f"/v1/artifacts/{self.manifest_id}/files?limit=2", headers=self.auth)
        self.assertEqual(response.status_code, 200)
        page = response.json()
        self.assertEqual([item["file_id"] for item in page["files"]], ["f_alpha", "f_binary"])
        self.assertTrue(page["files"][0]["artifact_id"])
        self.assertTrue(page["next_cursor"])
        second = await self.http.get(
            f"/v1/artifacts/{self.manifest_id}/files?limit=2&cursor={page['next_cursor']}", headers=self.auth
        )
        self.assertEqual([item["file_id"] for item in second.json()["files"]], ["f_zeta"])
        bad = await self.http.get(
            f"/v1/artifacts/{self.manifest_id}/files?cursor=not-a-signed-cursor", headers=self.auth
        )
        self.assertEqual(bad.status_code, 400)
        forged_cursor = ("A" if page["next_cursor"][0] != "A" else "B") + page["next_cursor"][1:]
        cross_scope = await self.http.get(
            f"/v1/artifacts/{self.manifest_id}/files?cursor={forged_cursor}", headers=self.auth
        )
        self.assertEqual(cross_scope.status_code, 400)

        text = await self.http.get(
            f"/v1/artifacts/{self.manifest_id}/text?file_id=f_alpha&start_line=1&limit=1", headers=self.auth
        )
        self.assertEqual(text.status_code, 200)
        self.assertEqual(text.json()["lines"][0]["number"], 1)
        self.assertEqual(text.json()["next_line"], 2)
        self.assertNotIn("\x1b", text.json()["lines"][0]["text"])
        traversal = await self.http.get(
            f"/v1/artifacts/{self.manifest_id}/text?file_id=../../etc/passwd", headers=self.auth
        )
        self.assertNotEqual(traversal.status_code, 200)
        binary_text = await self.http.get(
            f"/v1/artifacts/{self.manifest_id}/text?file_id=f_binary", headers=self.auth
        )
        self.assertEqual(binary_text.status_code, 400)

        diff = await self.http.get(
            f"/v1/artifacts/{self.diff_id}/diff?file_id=f_alpha&limit=4", headers=self.auth
        )
        self.assertEqual(diff.status_code, 200)
        diff_page = diff.json()
        self.assertEqual(len(diff_page["rows"]), 4)
        self.assertTrue(diff_page["next_cursor"])
        diff_next = await self.http.get(
            f"/v1/artifacts/{self.diff_id}/diff?file_id=f_alpha&limit=4&cursor={diff_page['next_cursor']}", headers=self.auth
        )
        self.assertEqual(diff_next.status_code, 200)
        self.assertEqual(diff_next.json()["rows"][0]["kind"], "hunk_header")
        binary_diff = await self.http.get(
            f"/v1/artifacts/{self.diff_id}/diff?file_id=f_binary", headers=self.auth
        )
        self.assertEqual(binary_diff.status_code, 200)
        self.assertIn("binary", [item["kind"] for item in binary_diff.json()["rows"]])

    async def test_content_is_exact_attachment_and_job_run_events_are_scoped(self) -> None:
        file_id = (await self.http.get(f"/v1/artifacts/{self.manifest_id}/files", headers=self.auth)).json()["files"][1]
        content_id = file_id["artifact_id"]
        content = await self.http.get(f"/v1/artifacts/{content_id}/content", headers=self.auth)
        self.assertEqual(content.status_code, 200)
        self.assertEqual(content.content, b"\x00\xff\x10")
        self.assertEqual(content.headers["content-type"], "application/octet-stream")
        self.assertEqual(content.headers["x-content-type-options"], "nosniff")
        self.assertEqual(content.headers["etag"], f'"{hashlib.sha256(content.content).hexdigest()}"')
        run = await self.http.get(f"/v1/runs/{self.run_id}", headers=self.auth)
        self.assertEqual(run.status_code, 200)
        self.assertIsNone(run.json()["run"]["usage"]["input_tokens"])
        events = await self.http.get(f"/v1/runs/{self.run_id}/events?limit=200", headers=self.auth)
        self.assertEqual(events.status_code, 200)
        self.assertIn("<script>log</script>", events.json()["items"][-1]["message"])
        self.assertNotIn("\x1b", events.json()["items"][-1]["message"])

    async def test_only_zero_budget_inspection_can_run(self) -> None:
        payload = {
            "project_id": self.project_id,
            "title": "API read-only inspection",
            "source": {"kind": "typed", "uri": "sidequest:local-git-inspection", "text": "Inspect committed files."},
            "checks": ["candidate.frozen_identity"],
            "budget_usd": 0,
            "allowed_actions": ["read_repo", "run_checks"],
        }
        created = await self.http.post("/v1/commands", headers=self.auth, json={
            "v": 1, "command_id": str(uuid4()), "type": "job.create", "expected_revision": self.store.revision, "payload": payload,
        })
        self.assertEqual(created.status_code, 202)
        job_id = created.json()["result"]["job_id"]
        stored_job = (await self.http.get(f"/v1/jobs/{job_id}", headers=self.auth)).json()["job"]
        self.assertEqual(stored_job["execution_profile"], "local_git_inspection")
        run = await self.http.post("/v1/commands", headers=self.auth, json={
            "v": 1, "command_id": str(uuid4()), "type": "job.run", "expected_revision": created.json()["revision"], "payload": {"job_id": job_id},
        })
        self.assertEqual(run.status_code, 202)
        self.assertEqual(self.scheduler.enqueued, [job_id])

        bad_zero = {**payload, "title": "Zero budget coding attempt", "checks": ["unit-tests"], "allowed_actions": ["propose_patch"]}
        invalid = await self.http.post("/v1/commands", headers=self.auth, json={
            "v": 1, "command_id": str(uuid4()), "type": "job.create", "expected_revision": self.store.revision, "payload": bad_zero,
        })
        self.assertEqual(invalid.status_code, 400)

        coding = {**bad_zero, "title": "Blocked coding attempt", "budget_usd": "1.000000"}
        coding_created = await self.http.post("/v1/commands", headers=self.auth, json={
            "v": 1, "command_id": str(uuid4()), "type": "job.create", "expected_revision": self.store.revision, "payload": coding,
        })
        self.assertEqual(coding_created.status_code, 202)
        coding_id = coding_created.json()["result"]["job_id"]
        denied = await self.http.post("/v1/commands", headers=self.auth, json={
            "v": 1, "command_id": str(uuid4()), "type": "job.run", "expected_revision": coding_created.json()["revision"], "payload": {"job_id": coding_id},
        })
        self.assertEqual(denied.status_code, 403)
        self.assertEqual(self.scheduler.enqueued, [job_id])

    async def test_serialized_text_diff_and_manifest_pages_stay_within_byte_limit(self) -> None:
        special_line = ('"\\\t雪' * 50_000) + "\nTAIL\n"
        special_bytes = special_line.encode("utf-8")
        special_sha = hashlib.sha256(special_bytes).hexdigest()
        original_manifest = json.loads(self.artifacts.read_artifact(self.store.get_artifact(self.manifest_id)))
        candidate = original_manifest["candidate"]

        hostile_entry = {
            "file_id": "f_hostile",
            "path": "hostile.txt",
            "old_path": None,
            "status": "modified",
            "media_type": "text/plain",
            "size_bytes": len(special_bytes),
            "sha256": special_sha,
            "added_lines": 1,
            "deleted_lines": 0,
            "binary": False,
        }
        manifest_entries = [hostile_entry]
        for index in range(100):
            path = f"dir_{index}/" + ("a" * 2500) + f"_{index}.txt"
            manifest_entries.append({
                "file_id": f"f_path_{index}",
                "path": path,
                "old_path": None,
                "status": "unchanged",
                "media_type": "text/plain",
                "size_bytes": 0,
                "sha256": hashlib.sha256(b"").hexdigest(),
                "added_lines": 0,
                "deleted_lines": 0,
                "binary": False,
            })
        large_manifest = (canonical_json({"v": 1, "candidate": candidate, "files": manifest_entries}) + "\n").encode("utf-8")
        large_manifest_id = self._register_bytes(
            artifact_id="art_api_large_manifest",
            job_id=self.job_id,
            run_id=self.run_id,
            kind="file_manifest",
            name="Large fixture manifest",
            data=large_manifest,
            candidate_id=self.candidate_id,
        )
        self._register_bytes(
            artifact_id="art_api_hostile_source",
            job_id=self.job_id,
            run_id=self.run_id,
            kind="source_file",
            name="hostile.txt",
            data=special_bytes,
            candidate_id=self.candidate_id,
        )

        text_response = await self.http.get(
            f"/v1/artifacts/{large_manifest_id}/text?file_id=f_hostile&limit=1", headers=self.auth
        )
        self.assertEqual(text_response.status_code, 200, text_response.text[:200])
        self.assertLessEqual(len(text_response.content), 256 * 1024)
        text_page = text_response.json()
        self.assertTrue(text_page["lines"][0]["clipped"])
        self.assertLess(len(text_page["lines"][0]["text"]), len(special_line.splitlines()[0]))
        self.assertEqual(text_page["next_line"], 2)
        second_line = await self.http.get(
            f"/v1/artifacts/{large_manifest_id}/text?file_id=f_hostile&start_line={text_page['next_line']}&limit=1",
            headers=self.auth,
        )
        self.assertEqual(second_line.status_code, 200)
        self.assertLessEqual(len(second_line.content), 256 * 1024)
        self.assertEqual(second_line.json()["lines"][0]["text"], "TAIL")

        long_diff = (
            b"diff --git a/alpha.txt b/alpha.txt\nindex 1111111..2222222 100644\n"
            b"--- a/alpha.txt\n+++ b/alpha.txt\n@@ -1 +1 @@\n+"
            + (('"\\\t雪' * 50_000) + "\n").encode("utf-8")
        )
        diff_id = self._register_bytes(
            artifact_id="art_api_large_diff",
            job_id=self.job_id,
            run_id=self.run_id,
            kind="diff",
            name="Large fixture diff",
            data=long_diff,
            candidate_id=self.candidate_id,
        )
        diff_head = await self.http.get(f"/v1/artifacts/{diff_id}/diff?file_id=f_alpha&limit=200", headers=self.auth)
        self.assertEqual(diff_head.status_code, 200, diff_head.text[:200])
        self.assertLessEqual(len(diff_head.content), 256 * 1024)
        self.assertTrue(diff_head.json()["next_cursor"])
        diff_tail = await self.http.get(
            f"/v1/artifacts/{diff_id}/diff?file_id=f_alpha&limit=200&cursor={diff_head.json()['next_cursor']}",
            headers=self.auth,
        )
        self.assertEqual(diff_tail.status_code, 200, diff_tail.text[:200])
        self.assertLessEqual(len(diff_tail.content), 256 * 1024)
        self.assertTrue(diff_tail.json()["rows"][0]["clipped"])
        self.assertIsNone(diff_tail.json()["next_cursor"])

        file_page = await self.http.get(f"/v1/artifacts/{large_manifest_id}/files?limit=100", headers=self.auth)
        self.assertEqual(file_page.status_code, 200, file_page.text[:200])
        self.assertLessEqual(len(file_page.content), 256 * 1024)
        page_data = file_page.json()
        self.assertLess(len(page_data["files"]), 100)
        self.assertTrue(page_data["next_cursor"])
        count = len(page_data["files"])
        following = await self.http.get(
            f"/v1/artifacts/{large_manifest_id}/files?limit=100&cursor={page_data['next_cursor']}", headers=self.auth
        )
        self.assertEqual(following.status_code, 200, following.text[:200])
        self.assertLessEqual(len(following.content), 256 * 1024)
        self.assertEqual(following.json()["files"][0]["file_id"], manifest_entries[count]["file_id"])


if __name__ == "__main__":
    unittest.main()
