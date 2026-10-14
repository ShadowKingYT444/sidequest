from __future__ import annotations

import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from uuid import uuid4

from services.runtime.policy import ErrorCode, RuntimeFault
from services.runtime.store import RuntimeStore
from services.runtime.tests.test_support import make_job, open_fixture


class ClaimConcurrencyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.store, self.config, self.project_id = open_fixture(self.root, max_parallel=2)
        self.connections: list[RuntimeStore] = []

    def tearDown(self) -> None:
        for store in self.connections:
            store.close()
        self.store.close()
        self.temporary.cleanup()

    def _parallel_stores(self, count: int) -> list[RuntimeStore]:
        stores = [RuntimeStore(self.config) for _ in range(count)]
        self.connections.extend(stores)
        return stores

    def test_concurrent_claims_never_exceed_worker_capacity(self) -> None:
        for index in range(4):
            self.store.create_job(
                str(uuid4()),
                None,
                make_job(
                    self.project_id,
                    title=f"Parallel job {index}",
                    budget="0.010000",
                    scopes=(f"src/{index}",),
                ),
            )
        workers = [self.store.create_worker("builder") for _ in range(6)]
        stores = self._parallel_stores(len(workers))
        with ThreadPoolExecutor(max_workers=len(workers)) as pool:
            claims = list(
                pool.map(
                    lambda pair: pair[0].claim_ready_task(pair[1], 100, max_parallel=2),
                    zip(stores, workers),
                )
            )
        self.assertEqual(sum(claim is not None for claim in claims), 2)
        with self.store.read_connection() as connection:
            active = connection.execute("SELECT COUNT(*) FROM budget_reservations WHERE state = 'active'").fetchone()[0]
        self.assertEqual(active, 2)

    def test_concurrent_reservations_cannot_overspend_one_job(self) -> None:
        response = self.store.create_job(
            str(uuid4()),
            None,
            make_job(
                self.project_id,
                title="Shared budget",
                budget="0.000100",
                scopes=("src/one", "src/two"),
                task_count=2,
            ),
        )
        job_id = response["result"]["job_id"]
        workers = [self.store.create_worker("builder") for _ in range(2)]
        stores = self._parallel_stores(len(workers))

        def claim(pair):
            store, worker_id = pair
            try:
                return store.claim_ready_task(worker_id, 60, max_parallel=2)
            except RuntimeFault as error:
                return error

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(claim, zip(stores, workers)))
        claimed = [result for result in results if isinstance(result, dict)]
        failures = [result for result in results if isinstance(result, RuntimeFault)]
        self.assertEqual(len(claimed), 1)
        self.assertEqual(len(failures), 1)
        self.assertEqual(failures[0].code, ErrorCode.BUDGET_LIMIT)
        budget = self.store.get_budget(job_id)
        self.assertEqual(budget["reserved_micro"], 60)
        self.assertLessEqual(budget["reserved_micro"], budget["budget_micro"])

    def test_call_cannot_raise_capacity_above_runtime_configuration(self) -> None:
        single_root = self.root / "single-capacity"
        store, config, project_id = open_fixture(single_root, max_parallel=1)
        extra_stores: list[RuntimeStore] = []
        try:
            for index in range(3):
                store.create_job(
                    str(uuid4()),
                    None,
                    make_job(project_id, title=f"Capacity {index}", scopes=(f"src/{index}",)),
                )
            workers = [store.create_worker("builder") for _ in range(3)]
            extra_stores = [RuntimeStore(config) for _ in workers]
            with ThreadPoolExecutor(max_workers=3) as pool:
                results = list(
                    pool.map(
                        lambda pair: pair[0].claim_ready_task(pair[1], 10, max_parallel=4),
                        zip(extra_stores, workers),
                    )
                )
            self.assertEqual(sum(result is not None for result in results), 1)
            with store.read_connection() as connection:
                active = connection.execute(
                    "SELECT COUNT(*) FROM budget_reservations WHERE state = 'active'"
                ).fetchone()[0]
            self.assertEqual(active, 1)
        finally:
            for extra in extra_stores:
                extra.close()
            store.close()
