from __future__ import annotations

import subprocess
from pathlib import Path
from uuid import uuid4

from services.runtime.config import RuntimeConfig
from services.runtime.models import (
    JobCreate,
    ProjectPolicy,
    ProjectRegistration,
    Source,
    TaskPlan,
    TaskSpec,
)
from services.runtime.store import RuntimeStore


def open_fixture(root: Path, *, max_parallel: int = 2) -> tuple[RuntimeStore, RuntimeConfig, str]:
    root.mkdir(parents=True, exist_ok=True)
    data_dir = root / "data"
    allowed_root = root / "projects"
    allowed_root.mkdir(parents=True, exist_ok=True)
    project_root = allowed_root / "sample-project"
    project_root.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", str(project_root)], check=True, shell=False)
    (project_root / "README.md").write_text("Trusted temporary fixture.\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(project_root), "add", "README.md"], check=True, shell=False)
    subprocess.run(
        [
            "git",
            "-C",
            str(project_root),
            "-c",
            "user.name=Sidequest Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-q",
            "-m",
            "fixture base",
        ],
        check=True,
        shell=False,
    )
    config = RuntimeConfig(data_dir=data_dir, allowed_roots=(allowed_root,), max_parallel=max_parallel)
    store = RuntimeStore(config)
    response = store.register_project(
        str(uuid4()),
        store.revision,
        ProjectRegistration(
            name="Fixture project",
            repo_path=str(project_root),
            base_ref="HEAD",
            policy=ProjectPolicy(allowed_actions=["read_repo", "propose_patch", "run_checks", "local_deliver"]),
        ),
    )
    return store, config, response["result"]["project_id"]


def make_job(
    project_id: str,
    *,
    title: str = "Fixture task",
    budget: str = "0.001000",
    scopes: tuple[str, ...] = ("src",),
    task_count: int = 1,
    dependency: bool = False,
    allowed_actions: list[str] | None = None,
) -> JobCreate:
    specs = []
    for index in range(task_count):
        task_id = f"task-{index + 1}"
        specs.append(
            TaskSpec(
                id=task_id,
                objective=f"Fixture objective {index + 1}",
                depends_on=[f"task-{index}"] if dependency and index == 1 else [],
                write_paths=[scopes[index % len(scopes)]],
                check_ids=["unit-tests"],
            )
        )
    return JobCreate(
        title=title,
        source=Source(kind="typed", uri="local:fixture", text="Fixture source text"),
        checks=["unit-tests"],
        budget_usd=budget,
        allowed_actions=allowed_actions or ["propose_patch", "local_deliver"],
        project_id=project_id,
        plan=TaskPlan(tasks=specs),
    )
