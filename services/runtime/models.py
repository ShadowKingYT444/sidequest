"""Validated A1 domain and command models.

HTTP routing is introduced in A2. These models are shared by the persistence
and policy layer so invalid state cannot be stored through internal callers.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from decimal import Decimal, InvalidOperation
from pathlib import PurePosixPath
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


MAX_TITLE_LENGTH = 200
MAX_SOURCE_TEXT_LENGTH = 16_000
MAX_TASK_OBJECTIVE_LENGTH = 4_000
MAX_USER_TASKS = 4
MAX_TASK_ID_LENGTH = 80
MAX_CHECK_ID_LENGTH = 120
MAX_ACTION_LENGTH = 80
MAX_BUDGET_MICRO = 1_000_000_000_000
ALLOWED_ACTIONS = frozenset({"read_repo", "propose_patch", "run_checks", "local_deliver", "github_pr"})
HEX_256_RE = re.compile(r"^[0-9a-f]{64}$")
SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,119}$")


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Source(StrictModel):
    kind: Literal["typed", "issue", "lookout"]
    uri: str = Field(min_length=1, max_length=2048)
    text: str = Field(max_length=MAX_SOURCE_TEXT_LENGTH)

    @field_validator("uri")
    @classmethod
    def uri_has_no_controls(cls, value: str) -> str:
        if any(ord(char) < 32 for char in value):
            raise ValueError("source URI contains control characters")
        return value


def _validate_relative_scope(scope: str) -> str:
    if not scope or len(scope) > 1024:
        raise ValueError("write path must contain 1 to 1024 characters")
    if "\\" in scope or any(ord(char) < 32 for char in scope):
        raise ValueError("write path must be a safe POSIX relative path")
    path = PurePosixPath(scope)
    if path.is_absolute() or scope.startswith("~") or any(part in {"", ".", ".."} for part in scope.split("/")):
        raise ValueError("write path must be a safe POSIX relative path")
    if path.as_posix() != scope:
        raise ValueError("write path must be normalized")
    return scope


class TaskSpec(StrictModel):
    id: str = Field(min_length=1, max_length=MAX_TASK_ID_LENGTH)
    objective: str = Field(min_length=1, max_length=MAX_TASK_OBJECTIVE_LENGTH)
    depends_on: list[str] = Field(default_factory=list, max_length=MAX_USER_TASKS)
    write_paths: list[str] = Field(default_factory=list, max_length=64)
    check_ids: list[str] = Field(default_factory=list, max_length=64)

    @field_validator("id")
    @classmethod
    def task_id_is_safe(cls, value: str) -> str:
        if not SAFE_ID_RE.fullmatch(value):
            raise ValueError("task id contains unsupported characters")
        return value

    @field_validator("objective")
    @classmethod
    def objective_is_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("task objective cannot be blank")
        return value

    @field_validator("depends_on")
    @classmethod
    def dependencies_are_unique(cls, value: list[str]) -> list[str]:
        if len(value) != len(set(value)):
            raise ValueError("task dependencies must be unique")
        return value

    @field_validator("write_paths")
    @classmethod
    def scopes_are_safe(cls, value: list[str]) -> list[str]:
        if len(value) != len(set(value)):
            raise ValueError("write paths must be unique")
        return [_validate_relative_scope(item) for item in value]

    @field_validator("check_ids")
    @classmethod
    def checks_are_valid(cls, value: list[str]) -> list[str]:
        if len(value) != len(set(value)):
            raise ValueError("check ids must be unique")
        for check_id in value:
            if not SAFE_ID_RE.fullmatch(check_id) or len(check_id) > MAX_CHECK_ID_LENGTH:
                raise ValueError("check id contains unsupported characters")
        return value


class TaskPlan(StrictModel):
    tasks: list[TaskSpec] = Field(min_length=1, max_length=MAX_USER_TASKS)

    @model_validator(mode="after")
    def valid_dependency_graph(self) -> "TaskPlan":
        by_id = {task.id: task for task in self.tasks}
        if len(by_id) != len(self.tasks):
            raise ValueError("task ids must be unique")
        for task in self.tasks:
            if task.id in task.depends_on:
                raise ValueError("a task cannot depend on itself")
            missing = set(task.depends_on) - set(by_id)
            if missing:
                raise ValueError("task dependency references an unknown task")
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(task_id: str) -> None:
            if task_id in visiting:
                raise ValueError("task dependencies must be acyclic")
            if task_id in visited:
                return
            visiting.add(task_id)
            for dependency in by_id[task_id].depends_on:
                visit(dependency)
            visiting.remove(task_id)
            visited.add(task_id)

        for task_id in by_id:
            visit(task_id)
        return self


class ProjectPolicy(StrictModel):
    allowed_actions: list[str] = Field(default_factory=lambda: ["read_repo"])

    @field_validator("allowed_actions")
    @classmethod
    def policy_actions_are_known(cls, value: list[str]) -> list[str]:
        if len(value) != len(set(value)):
            raise ValueError("policy actions must be unique")
        unknown = set(value) - ALLOWED_ACTIONS
        if unknown:
            raise ValueError("policy contains an unknown action")
        return value


class ProjectRegistration(StrictModel):
    name: str = Field(min_length=1, max_length=200)
    repo_path: str = Field(min_length=1, max_length=4096)
    base_ref: str = Field(min_length=1, max_length=255)
    policy: ProjectPolicy = Field(default_factory=ProjectPolicy)

    @field_validator("name", "base_ref")
    @classmethod
    def no_control_characters(cls, value: str) -> str:
        if not value.strip() or any(ord(char) < 32 for char in value):
            raise ValueError("value contains control characters")
        return value


class JobCreate(StrictModel):
    title: str = Field(min_length=1, max_length=MAX_TITLE_LENGTH)
    source: Source
    checks: list[str] = Field(default_factory=list, max_length=64)
    budget_usd: Decimal = Field(ge=Decimal("0"), max_digits=18, decimal_places=6)
    allowed_actions: list[str] = Field(default_factory=list)
    project_id: str
    plan: TaskPlan | None = None
    outcome: str | None = Field(default=None, max_length=MAX_SOURCE_TEXT_LENGTH)

    @field_validator("title")
    @classmethod
    def title_is_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("title cannot be blank")
        return value

    @field_validator("checks")
    @classmethod
    def checks_are_unique(cls, value: list[str]) -> list[str]:
        if len(value) != len(set(value)):
            raise ValueError("check ids must be unique")
        for item in value:
            if not SAFE_ID_RE.fullmatch(item) or len(item) > MAX_CHECK_ID_LENGTH:
                raise ValueError("check id contains unsupported characters")
        return value

    @field_validator("allowed_actions")
    @classmethod
    def requested_actions_are_known(cls, value: list[str]) -> list[str]:
        if len(value) != len(set(value)):
            raise ValueError("allowed actions must be unique")
        if set(value) - ALLOWED_ACTIONS:
            raise ValueError("allowed actions contains an unknown action")
        return value

    @field_validator("budget_usd", mode="before")
    @classmethod
    def budget_is_exact_decimal(cls, value: Any) -> Any:
        if isinstance(value, float):
            if not math.isfinite(value):
                raise ValueError("budget must be a finite decimal")
            return Decimal(str(value))
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError):
            raise ValueError("budget must be a decimal") from None

    @model_validator(mode="after")
    def zero_budget_is_only_for_local_inspection(self) -> "JobCreate":
        if self.budget_usd == 0 and not is_local_git_inspection(self):
            raise ValueError("zero budget is allowed only for deterministic local Git inspection")
        return self


class CandidateIdentity(StrictModel):
    candidate_id: str = Field(min_length=1, max_length=80)
    source_revision: str = Field(min_length=1, max_length=255)
    tree_sha256: str
    patch_sha256: str

    @field_validator("tree_sha256", "patch_sha256")
    @classmethod
    def hashes_are_sha256(cls, value: str) -> str:
        if not HEX_256_RE.fullmatch(value):
            raise ValueError("candidate digest must be lowercase SHA-256 hex")
        return value


class CandidateCreate(CandidateIdentity):
    job_id: str
    run_id: str
    base_revision: str = Field(min_length=1, max_length=255)
    candidate_revision: str = Field(min_length=1, max_length=255)
    manifest_artifact_id: str


class ApprovalCreate(CandidateIdentity):
    job_id: str
    action: str = Field(min_length=1, max_length=MAX_ACTION_LENGTH)
    destination: str = Field(min_length=1, max_length=2048)

    @field_validator("action")
    @classmethod
    def action_is_known(cls, value: str) -> str:
        if value not in ALLOWED_ACTIONS:
            raise ValueError("unknown action")
        return value

    @field_validator("destination")
    @classmethod
    def destination_has_no_controls(cls, value: str) -> str:
        if any(ord(char) < 32 for char in value):
            raise ValueError("destination contains control characters")
        return value


class CommandRequest(StrictModel):
    v: Literal[1] = 1
    command_id: UUID
    type: str = Field(min_length=1, max_length=80)
    expected_revision: int | None
    payload: dict[str, Any]


def is_local_git_inspection(job: JobCreate) -> bool:
    return (
        job.budget_usd == 0
        and job.source.kind == "typed"
        and set(job.allowed_actions) == {"read_repo", "run_checks"}
        and job.checks == ["candidate.frozen_identity"]
        and job.plan is None
    )


def is_codex_job_from_stored(profile: dict[str, Any], tasks: list[dict[str, Any]]) -> bool:
    """Recognize the deliberately narrow, host-dispatched build profile from persisted data."""
    actions = profile.get("allowed_actions")
    if (
        not isinstance(profile.get("source"), dict)
        or profile["source"].get("kind") != "typed"
        or not isinstance(actions, list)
        or set(actions) != {"read_repo", "propose_patch", "run_checks"}
        or profile.get("checks") != ["candidate.frozen_identity"]
        or not isinstance(profile.get("budget_micro"), int)
        or isinstance(profile.get("budget_micro"), bool)
        or profile["budget_micro"] <= 0
        or not isinstance(tasks, list)
        or len(tasks) != 1
    ):
        return False
    task = tasks[0]
    return (
        task.get("kind") == "build"
        and bool(task.get("write_paths"))
        and task.get("check_ids") == ["candidate.frozen_identity"]
        and task.get("depends_on") == []
        and task.get("check_ids") == profile.get("checks")
    )


def budget_to_micro(value: Decimal | str | int | float, *, allow_zero: bool = False) -> int:
    """Convert USD into integer micro-dollars without binary rounding."""
    try:
        decimal = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError("budget must be a decimal") from None
    if not decimal.is_finite() or decimal < 0 or (decimal == 0 and not allow_zero) or decimal.as_tuple().exponent < -6:
        raise ValueError("budget must be positive with at most six decimal places")
    micro = decimal * 1_000_000
    if micro != micro.to_integral_value() or micro > MAX_BUDGET_MICRO:
        raise ValueError("budget is outside the supported range")
    return int(micro)


def canonical_json(value: Any) -> str:
    """Serialize deterministic JSON with exact decimal values represented as strings."""
    def normalize(item: Any) -> Any:
        if isinstance(item, BaseModel):
            return normalize(item.model_dump(mode="python"))
        if isinstance(item, Decimal):
            if not item.is_finite():
                raise ValueError("non-finite decimal is not valid JSON")
            return format(item, "f")
        if isinstance(item, float):
            if not math.isfinite(item):
                raise ValueError("non-finite float is not valid JSON")
            # JSON callers may supply USD values as numbers. Convert through
            # the shortest decimal spelling; never persist a binary float.
            return format(Decimal(str(item)), "f")
        if isinstance(item, UUID):
            return str(item)
        if isinstance(item, dict):
            if not all(isinstance(key, str) for key in item):
                raise ValueError("JSON object keys must be strings")
            return {key: normalize(item[key]) for key in sorted(item)}
        if isinstance(item, (list, tuple)):
            return [normalize(child) for child in item]
        if item is None or isinstance(item, (str, int, bool)):
            return item
        raise ValueError("value cannot be represented as canonical JSON")

    return json.dumps(normalize(value), ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False)


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()
