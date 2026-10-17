from __future__ import annotations

import tempfile
import subprocess
import unittest
from pathlib import Path
from uuid import uuid4

from pydantic import ValidationError

from services.runtime.models import ApprovalCreate, CandidateCreate, CandidateIdentity, TaskPlan, TaskSpec
from services.runtime.policy import ErrorCode, RuntimeFault
from services.runtime.store import RuntimeStore
from services.runtime.tests.test_support import make_job, open_fixture


class PolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.store, self.config, self.project_id = open_fixture(self.root)

    def tearDown(self) -> None:
        self.store.close()
        self.temporary.cleanup()

    def _candidate(self) -> tuple[str, str, CandidateIdentity]:
        base_revision = self.store.get_project(self.project_id)["base_revision"]
        job_response = self.store.create_job(str(uuid4()), None, make_job(self.project_id))
        job_id = job_response["result"]["job_id"]
        worker_id = self.store.create_worker("builder")
        claim = self.store.claim_ready_task(worker_id, 20)
        self.store.settle_attempt(claim["attempt_id"], cost_micro=5)
        artifact_id = self.store.create_artifact(
            job_id=job_id,
            run_id=claim["attempt_id"],
            kind="file_manifest",
            media_type="application/json",
            display_name="manifest",
            sha256="a" * 64,
            size_bytes=0,
            storage_key="artifacts/fixture/manifest.json",
        )
        candidate_id = str(uuid4())
        identity = CandidateIdentity(
            candidate_id=candidate_id,
            source_revision=base_revision,
            tree_sha256="b" * 64,
            patch_sha256="c" * 64,
        )
        self.store.create_candidate(
            CandidateCreate(
                **identity.model_dump(),
                job_id=job_id,
                run_id=claim["attempt_id"],
                base_revision=base_revision,
                candidate_revision="fixture-candidate-revision-1",
                manifest_artifact_id=artifact_id,
            )
        )
        return job_id, candidate_id, identity

    def _advance_project_git(self) -> str:
        project_root = self.store.get_project(self.project_id)["canonical_root"]
        Path(project_root, "README.md").write_text("Updated trusted temporary fixture.\n", encoding="utf-8")
        subprocess.run(["git", "-C", project_root, "add", "README.md"], check=True, shell=False)
        subprocess.run(
            [
                "git",
                "-C",
                project_root,
                "-c",
                "user.name=Sidequest Fixture",
                "-c",
                "user.email=fixture@example.invalid",
                "commit",
                "-q",
                "-m",
                "fixture update",
            ],
            check=True,
            shell=False,
        )
        return subprocess.check_output(
            ["git", "-C", project_root, "rev-parse", "HEAD"], text=True, shell=False
        ).strip()

    def test_rejects_stale_approval_identity(self) -> None:
        job_id, candidate_id, identity = self._candidate()
        response = self.store.request_approval(
            str(uuid4()),
            self.store.revision,
            ApprovalCreate(
                **identity.model_dump(),
                job_id=job_id,
                action="local_deliver",
                destination="local:test-target",
            ),
        )
        approval_id = response["result"]["approval_id"]
        new_revision = self._advance_project_git()
        self.assertEqual(self.store.refresh_project_revision(self.project_id), new_revision)
        with self.assertRaises(RuntimeFault) as caught:
            self.store.decide_approval(str(uuid4()), self.store.revision, approval_id, True, identity)
        self.assertEqual(caught.exception.code, ErrorCode.VERSION_CONFLICT)
        with self.store.read_connection() as connection:
            state = connection.execute("SELECT state FROM approvals WHERE id = ?", (approval_id,)).fetchone()[0]
        self.assertEqual(state, "stale")

    def test_approval_decision_detects_unrefreshed_git_source_change(self) -> None:
        job_id, _, identity = self._candidate()
        response = self.store.request_approval(
            str(uuid4()),
            self.store.revision,
            ApprovalCreate(
                **identity.model_dump(),
                job_id=job_id,
                action="local_deliver",
                destination="local:test-target",
            ),
        )
        approval_id = response["result"]["approval_id"]
        self.assertNotEqual(self._advance_project_git(), identity.source_revision)
        with self.assertRaises(RuntimeFault) as caught:
            self.store.decide_approval(str(uuid4()), self.store.revision, approval_id, True, identity)
        self.assertEqual(caught.exception.code, ErrorCode.VERSION_CONFLICT)
        with self.store.read_connection() as connection:
            state = connection.execute("SELECT state FROM approvals WHERE id = ?", (approval_id,)).fetchone()[0]
        self.assertEqual(state, "stale")

    def test_rejects_differing_body_duplicate_command_but_replays_identical_body(self) -> None:
        command_id = str(uuid4())
        current = self.store.revision
        executions = []

        def operation(connection):
            executions.append("called")
            return {"marker": "first-result"}

        first = self.store.execute_command(command_id, "job.create", {"value": 1}, current, operation)
        self.store.create_worker("researcher")
        replay = self.store.execute_command(command_id, "job.create", {"value": 1}, current, operation)
        self.assertEqual(replay, first)
        self.assertEqual(executions, ["called"])
        with self.assertRaises(RuntimeFault) as caught:
            self.store.execute_command(command_id, "job.create", {"value": 2}, current, operation)
        self.assertEqual(caught.exception.code, ErrorCode.VERSION_CONFLICT)

    def test_new_command_rejects_a_stale_global_revision(self) -> None:
        stale_revision = self.store.revision
        self.store.create_worker("researcher")
        with self.assertRaises(RuntimeFault) as caught:
            self.store.execute_command(
                str(uuid4()),
                "project.select",
                {"project_id": self.project_id},
                stale_revision,
                lambda connection: {"selected": True},
            )
        self.assertEqual(caught.exception.code, ErrorCode.VERSION_CONFLICT)

    def test_rejects_project_root_outside_the_approved_roots(self) -> None:
        outside = self.root / "outside-project"
        outside.mkdir()
        with self.assertRaises(RuntimeFault) as caught:
            self.store.register_project(
                str(uuid4()),
                self.store.revision,
                {
                    "name": "Outside project",
                    "repo_path": str(outside),
                    "base_ref": "HEAD",
                },
            )
        self.assertEqual(caught.exception.code, ErrorCode.POLICY_DENIED)

    def test_rejects_denied_action_and_missing_project(self) -> None:
        with self.assertRaises(RuntimeFault) as denied:
            self.store.create_job(
                str(uuid4()),
                None,
                make_job(self.project_id, allowed_actions=["github_pr"]),
            )
        self.assertEqual(denied.exception.code, ErrorCode.POLICY_DENIED)
        with self.assertRaises(RuntimeFault) as missing:
            self.store.create_job(str(uuid4()), None, make_job(str(uuid4())))
        self.assertEqual(missing.exception.code, ErrorCode.NOT_FOUND)

    def test_rejects_cycles_and_unsafe_scopes(self) -> None:
        with self.assertRaises(ValidationError):
            TaskPlan(
                tasks=[
                    TaskSpec(id="first", objective="first", depends_on=["second"]),
                    TaskSpec(id="second", objective="second", depends_on=["first"]),
                ]
            )
        with self.assertRaises(ValidationError):
            TaskSpec(id="unsafe", objective="unsafe", write_paths=["../outside"])
