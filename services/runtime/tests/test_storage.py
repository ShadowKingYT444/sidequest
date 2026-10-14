from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path
from uuid import uuid4

from services.runtime.models import CandidateCreate
from services.runtime.policy import ErrorCode, RuntimeFault
from services.runtime.store import RuntimeStore
from services.runtime.tests.test_support import make_job, open_fixture


class StorageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.store, self.config, self.project_id = open_fixture(self.root)

    def tearDown(self) -> None:
        self.store.close()
        self.temporary.cleanup()

    def _create_candidate(self) -> tuple[str, str, str, str]:
        base_revision = self.store.get_project(self.project_id)["base_revision"]
        response = self.store.create_job(str(uuid4()), None, make_job(self.project_id, dependency=True, task_count=2))
        job_id = response["result"]["job_id"]
        tasks = self.store.list_tasks(job_id)
        worker_id = self.store.create_worker("builder")
        claim = self.store.claim_ready_task(worker_id, 50)
        self.assertIsNotNone(claim)
        self.store.settle_attempt(
            claim["attempt_id"],
            cost_micro=7,
            input_tokens=13,
            cached_input_tokens=None,
            output_tokens=5,
            total_tokens=None,
        )
        artifact_id = self.store.create_artifact(
            job_id=job_id,
            run_id=claim["attempt_id"],
            kind="file_manifest",
            media_type="application/json",
            display_name="candidate manifest",
            sha256="a" * 64,
            size_bytes=20,
            storage_key="artifacts/fixture/manifest.json",
        )
        candidate_id = str(uuid4())
        self.store.create_candidate(
            CandidateCreate(
                candidate_id=candidate_id,
                source_revision=base_revision,
                tree_sha256="b" * 64,
                patch_sha256="c" * 64,
                job_id=job_id,
                run_id=claim["attempt_id"],
                base_revision=base_revision,
                candidate_revision="fixture-candidate-revision-1",
                manifest_artifact_id=artifact_id,
            )
        )
        return job_id, tasks[0]["id"], candidate_id, artifact_id

    def test_initial_migration_reload_source_task_metadata_and_candidate_linkage(self) -> None:
        project = self.store.get_project(self.project_id)
        self.assertEqual(Path(project["canonical_root"]), self.root / "projects" / "sample-project")
        self.assertRegex(project["base_revision"], r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
        job_id, first_task_id, candidate_id, artifact_id = self._create_candidate()
        task = self.store.list_tasks(job_id)[0]
        self.assertEqual(task["id"], first_task_id)
        self.assertEqual(task["objective"], "Fixture objective 1")
        self.assertEqual(task["check_ids"], ["unit-tests"])
        self.assertEqual(task["write_paths"], ["src"])
        with self.store.read_connection() as connection:
            migration = connection.execute("SELECT version FROM schema_migrations ORDER BY version DESC").fetchone()[0]
            candidate = connection.execute("SELECT * FROM candidates WHERE id = ?", (candidate_id,)).fetchone()
            artifact = connection.execute("SELECT candidate_id FROM artifacts WHERE id = ?", (artifact_id,)).fetchone()
            self.assertEqual(connection.execute("PRAGMA foreign_keys").fetchone()[0], 1)
            self.assertEqual(connection.execute("PRAGMA journal_mode").fetchone()[0].lower(), "wal")
        self.assertEqual(migration, 2)
        self.assertEqual(candidate["tree_sha256"], "b" * 64)
        self.assertEqual(artifact["candidate_id"], candidate_id)
        with self.assertRaises(sqlite3.IntegrityError):
            with self.store.transaction() as connection:
                connection.execute("UPDATE candidates SET tree_sha256 = ? WHERE id = ?", ("d" * 64, candidate_id))
        with self.assertRaises(sqlite3.IntegrityError):
            with self.store.transaction() as connection:
                connection.execute("UPDATE artifacts SET candidate_id = NULL WHERE id = ?", (artifact_id,))

        self.store.close()
        self.store = RuntimeStore(self.config)
        restored = self.store.get_job(job_id)
        self.assertEqual(restored["source"]["text"], "Fixture source text")
        self.assertEqual(restored["outcome"], "Fixture source text")
        self.assertEqual(restored["candidate_id"], candidate_id)
        self.assertEqual(restored["tasks"][0]["state"], "completed")
        self.assertEqual(restored["tasks"][1]["depends_on"], [first_task_id])

    def test_unknown_usage_remains_null_and_keeps_budget_reservation(self) -> None:
        job = self.store.create_job(
            str(uuid4()), None, make_job(self.project_id, budget="0.000100", scopes=("src/a", "src/b"), task_count=2)
        )
        job_id = job["result"]["job_id"]
        worker = self.store.create_worker("builder")
        claim = self.store.claim_ready_task(worker, 60)
        self.assertIsNotNone(claim)
        self.store.settle_attempt(
            claim["attempt_id"],
            cost_micro=None,
            input_tokens=None,
            cached_input_tokens=None,
            output_tokens=None,
            total_tokens=None,
        )
        attempt = self.store.get_attempt(claim["attempt_id"])
        budget = self.store.get_budget(job_id)
        self.assertIsNone(attempt["cost_micro"])
        self.assertIsNone(attempt["input_tokens"])
        self.assertEqual(attempt["usage_uncertain"], 1)
        self.assertIsNone(budget["spent_micro"])
        self.assertEqual(budget["reserved_micro"], 60)
        self.assertEqual(budget["uncertain"], 1)
        with self.assertRaises(RuntimeFault) as caught:
            self.store.claim_ready_task(worker, 50)
        self.assertEqual(caught.exception.code, ErrorCode.BUDGET_LIMIT)

    def test_zero_reservation_is_limited_to_trusted_deterministic_verify_work(self) -> None:
        response = self.store.create_job(
            str(uuid4()), None, make_job(self.project_id, budget="0.000001", scopes=("src/check",))
        )
        job_id = response["result"]["job_id"]
        task_id = self.store.list_tasks(job_id)[0]["id"]
        builder = self.store.create_worker("builder")
        with self.assertRaises(RuntimeFault) as caught:
            self.store.claim_ready_task(builder, 0)
        self.assertEqual(caught.exception.code, ErrorCode.BUDGET_LIMIT)
        self.assertEqual(self.store.list_tasks(job_id)[0]["state"], "queued")
        with self.store.transaction() as connection:
            connection.execute("UPDATE tasks SET kind = 'verify' WHERE id = ?", (task_id,))
        verifier = self.store.create_worker("verifier")
        with self.assertRaises(RuntimeFault) as caught:
            self.store.claim_ready_task(verifier, 0)
        self.assertEqual(caught.exception.code, ErrorCode.BUDGET_LIMIT)
        self.assertEqual(self.store.list_tasks(job_id)[0]["state"], "queued")
        trusted_verifier = self.store.create_worker("verifier", trusted_deterministic_internal=True)
        claim = self.store.claim_ready_task(trusted_verifier, 0)
        self.assertIsNotNone(claim)
        self.assertEqual(claim["reserved_micro"], 0)
