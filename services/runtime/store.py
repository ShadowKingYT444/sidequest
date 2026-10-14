"""SQLite persistence for the A1 project, job, task and approval state."""

from __future__ import annotations

import contextlib
import json
import os
import re
import sqlite3
import subprocess
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterator
from uuid import UUID, uuid4

from .config import RuntimeConfig, codex_execution_enabled
from .models import (
    ApprovalCreate,
    CandidateCreate,
    CandidateIdentity,
    JobCreate,
    ProjectRegistration,
    TaskSpec,
    budget_to_micro,
    canonical_json,
    canonical_sha256,
    is_local_git_inspection,
    is_codex_job_from_stored,
)
from .policy import ErrorCode, PolicyEngine, RuntimeFault


_MIGRATIONS_DIR = Path(__file__).parent / "migrations"
_MAX_EVENT_LENGTH = 4096
_GIT_OBJECT_ID_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
_OPAQUE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:_-]{0,199}$")
_PROVIDER_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,511}$")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _require_uuid(value: str, label: str) -> str:
    try:
        return str(UUID(str(value)))
    except (ValueError, TypeError, AttributeError):
        raise RuntimeFault(ErrorCode.INVALID_INPUT, f"{label} must be a UUID") from None


def _require_opaque_id(value: str, label: str) -> str:
    if not isinstance(value, str) or not _OPAQUE_ID_RE.fullmatch(value):
        raise RuntimeFault(ErrorCode.INVALID_INPUT, f"{label} must be a bounded opaque identifier")
    return value


def _json_load(value: str) -> Any:
    return json.loads(value)


class RuntimeStore:
    """One SQLite connection and one serialized writer per runtime process.

    The process lock protects the shared connection. BEGIN IMMEDIATE also
    serializes writers across independently opened RuntimeStore instances.
    No callback passed to a transaction may perform I/O or wait for a worker.
    """

    def __init__(self, database: str | Path | RuntimeConfig, *, config: RuntimeConfig | None = None):
        if isinstance(database, RuntimeConfig):
            config = database
            db_path = config.database_path
        else:
            db_path = Path(database)
        self.config = config or RuntimeConfig(data_dir=db_path.parent)
        if str(db_path) != ":memory:":
            db_path.parent.mkdir(parents=True, exist_ok=True)
        self.database_path = db_path
        self._lock = threading.RLock()
        self._connection = sqlite3.connect(
            str(db_path),
            timeout=self.config.sqlite_busy_timeout_ms / 1000,
            isolation_level=None,
            check_same_thread=False,
        )
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._connection.execute(f"PRAGMA busy_timeout = {int(self.config.sqlite_busy_timeout_ms)}")
        self._connection.execute("PRAGMA journal_mode = WAL")
        self._apply_migrations()
        self._seed_settings()

    def close(self) -> None:
        with self._lock:
            self._connection.close()

    def __enter__(self) -> "RuntimeStore":
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.close()

    @contextlib.contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        with self._lock:
            try:
                self._connection.execute("BEGIN IMMEDIATE")
                yield self._connection
                self._connection.execute("COMMIT")
            except Exception:
                if self._connection.in_transaction:
                    self._connection.execute("ROLLBACK")
                raise

    @contextlib.contextmanager
    def read_connection(self) -> Iterator[sqlite3.Connection]:
        with self._lock:
            yield self._connection

    def _apply_migrations(self) -> None:
        with self._lock:
            self._connection.execute(
                "CREATE TABLE IF NOT EXISTS schema_migrations (version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL)"
            )
            for migration_path in sorted(_MIGRATIONS_DIR.glob("[0-9][0-9][0-9]_*.sql")):
                version = int(migration_path.name.split("_", 1)[0])
                sql = migration_path.read_text(encoding="utf-8")
                self._connection.execute("BEGIN IMMEDIATE")
                try:
                    already_applied = self._connection.execute(
                        "SELECT 1 FROM schema_migrations WHERE version = ?", (version,)
                    ).fetchone()
                    if already_applied:
                        self._connection.execute("COMMIT")
                        continue
                    statement = ""
                    for line in sql.splitlines(keepends=True):
                        statement += line
                        if sqlite3.complete_statement(statement):
                            if statement.strip():
                                self._connection.execute(statement)
                            statement = ""
                    if statement.strip():
                        raise RuntimeFault(ErrorCode.INTERNAL, "migration contains an incomplete SQL statement")
                    self._connection.execute(
                        "INSERT INTO schema_migrations(version, applied_at) VALUES (?, ?)",
                        (version, utc_now()),
                    )
                    self._connection.execute("COMMIT")
                except Exception:
                    if self._connection.in_transaction:
                        self._connection.execute("ROLLBACK")
                    raise

    def _seed_settings(self) -> None:
        defaults = {
            "revision": 0,
            "stopped": False,
            "selected_project_id": None,
            "max_parallel": self.config.max_parallel,
        }
        with self.transaction() as connection:
            for key, value in defaults.items():
                connection.execute(
                    "INSERT OR IGNORE INTO settings(key, value_json) VALUES (?, ?)",
                    (key, canonical_json(value)),
                )

    @staticmethod
    def _revision(connection: sqlite3.Connection) -> int:
        row = connection.execute("SELECT value_json FROM settings WHERE key = 'revision'").fetchone()
        return int(_json_load(row[0])) if row else 0

    @classmethod
    def _bump_revision(cls, connection: sqlite3.Connection) -> int:
        revision = cls._revision(connection) + 1
        connection.execute(
            "INSERT INTO settings(key, value_json) VALUES ('revision', ?) "
            "ON CONFLICT(key) DO UPDATE SET value_json = excluded.value_json",
            (canonical_json(revision),),
        )
        return revision

    @property
    def revision(self) -> int:
        with self.read_connection() as connection:
            return self._revision(connection)

    def execute_command(
        self,
        command_id: str | UUID,
        command_type: str,
        payload: dict[str, Any],
        expected_revision: int | None,
        operation: Callable[[sqlite3.Connection], dict[str, Any]],
    ) -> dict[str, Any]:
        """Apply one idempotent command and persist its exact accepted response."""
        normalized_id = _require_uuid(str(command_id), "command_id")
        if not command_type or len(command_type) > 80:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "command type is invalid")
        if expected_revision is None and command_type not in {"job.create", "system.stop"}:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "expected_revision is required for this command")
        if expected_revision is not None and (
            not isinstance(expected_revision, int) or isinstance(expected_revision, bool) or expected_revision < 0
        ):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "expected_revision must be a non-negative integer")
        request_sha = self._command_request_sha(command_type, payload, expected_revision)
        replay = self._read_command_result(normalized_id, request_sha)
        if replay is not None:
            return replay
        with self.transaction() as connection:
            prior = connection.execute(
                "SELECT request_sha256, response_json FROM command_results WHERE command_id = ?",
                (normalized_id,),
            ).fetchone()
            if prior:
                if prior["request_sha256"] != request_sha:
                    raise RuntimeFault(ErrorCode.VERSION_CONFLICT, "command_id was already used with a different request")
                return _json_load(prior["response_json"])

            current_revision = self._revision(connection)
            if expected_revision is not None and expected_revision != current_revision:
                raise RuntimeFault(ErrorCode.VERSION_CONFLICT, "state changed; review the current project state")
            try:
                result = operation(connection)
            except sqlite3.IntegrityError as error:
                raise RuntimeFault(ErrorCode.VERSION_CONFLICT, "request conflicts with saved state") from error
            accepted_revision = self._bump_revision(connection)
            response = {
                "v": 1,
                "command_id": normalized_id,
                "accepted": True,
                "revision": accepted_revision,
            }
            if result:
                response["result"] = result
            connection.execute(
                "INSERT INTO command_results(command_id, request_sha256, type, accepted_revision, response_json, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    normalized_id,
                    request_sha,
                    command_type,
                    accepted_revision,
                    canonical_json(response),
                    utc_now(),
                ),
            )
            return response

    @staticmethod
    def _command_request_sha(command_type: str, payload: dict[str, Any], expected_revision: int | None) -> str:
        try:
            request_json = canonical_json(
                {"type": command_type, "expected_revision": expected_revision, "payload": payload}
            )
        except (TypeError, ValueError):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "command payload is not valid JSON") from None
        if len(request_json.encode("utf-8")) > 4 * 1024 * 1024:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "command payload exceeds 4 MiB")
        return canonical_sha256(
            {"type": command_type, "expected_revision": expected_revision, "payload": payload}
        )

    def _read_command_result(self, command_id: str, request_sha: str) -> dict[str, Any] | None:
        with self.read_connection() as connection:
            prior = connection.execute(
                "SELECT request_sha256, response_json FROM command_results WHERE command_id = ?",
                (command_id,),
            ).fetchone()
            if not prior:
                return None
            if prior["request_sha256"] != request_sha:
                raise RuntimeFault(ErrorCode.VERSION_CONFLICT, "command_id was already used with a different request")
            return _json_load(prior["response_json"])

    def lookup_command_result(
        self,
        command_id: str | UUID,
        command_type: str,
        payload: dict[str, Any],
        expected_revision: int | None,
    ) -> dict[str, Any] | None:
        normalized_id = _require_uuid(str(command_id), "command_id")
        request_sha = self._command_request_sha(command_type, payload, expected_revision)
        return self._read_command_result(normalized_id, request_sha)

    def get_codex_readiness(self) -> dict[str, Any] | None:
        return self.get_setting("codex_readiness")

    def record_codex_readiness(
        self,
        command_id: str | UUID,
        expected_revision: int,
        *,
        config_sha256: str,
        capability: dict[str, Any],
        refreshed_at: str,
    ) -> dict[str, Any]:
        record = {
            "config_sha256": config_sha256,
            "capability": capability,
            "refreshed_at": refreshed_at,
        }

        def write(connection: sqlite3.Connection) -> dict[str, Any]:
            connection.execute(
                "INSERT INTO settings(key, value_json) VALUES ('codex_readiness', ?) "
                "ON CONFLICT(key) DO UPDATE SET value_json = excluded.value_json",
                (canonical_json(record),),
            )
            return {"capability": capability, "refreshed_at": refreshed_at}

        return self.execute_command(command_id, "system.codex.refresh", {}, expected_revision, write)

    def reconcile_interrupted_attempts(self) -> int:
        """Block persisted live attempts on startup; never auto-repeat inference."""
        with self.transaction() as connection:
            rows = connection.execute(
                "SELECT a.id, a.task_id, a.worker_id, t.job_id FROM attempts a "
                "JOIN tasks t ON t.id = a.task_id WHERE a.state = 'running'"
            ).fetchall()
            if not rows:
                return 0
            now = utc_now()
            for row in rows:
                connection.execute(
                    "UPDATE attempts SET state = 'ambiguous', ended_at = ?, cost_micro = NULL, usage_uncertain = 1 "
                    "WHERE id = ? AND state = 'running'",
                    (now, row["id"]),
                )
                connection.execute(
                    "UPDATE budget_reservations SET settled_micro = NULL, state = 'uncertain' WHERE attempt_id = ?",
                    (row["id"],),
                )
                connection.execute(
                    "UPDATE tasks SET state = 'blocked', worker_id = NULL, resume_requested = 0 WHERE id = ?",
                    (row["task_id"],),
                )
                if row["worker_id"]:
                    connection.execute(
                        "UPDATE workers SET state = 'idle', current_task_id = NULL WHERE id = ?",
                        (row["worker_id"],),
                    )
                connection.execute(
                    "UPDATE jobs SET state = 'blocked', blocked_reason = ?, updated_at = ? WHERE id = ? "
                    "AND state IN ('running', 'queued', 'paused')",
                    ("An interrupted attempt is ambiguous; explicitly resume its saved Codex session or create a new job.", now, row["job_id"]),
                )
                next_seq = connection.execute(
                    "SELECT COALESCE(MAX(run_seq), 0) + 1 FROM events WHERE run_id = ?", (row["id"],)
                ).fetchone()[0]
                self._insert_event(
                    connection,
                    row["job_id"],
                    row["id"],
                    next_seq,
                    "warning",
                    "Runtime restarted during an attempt; usage and provider completion are uncertain. No automatic retry was scheduled.",
                    None,
                )
            self._bump_revision(connection)
            return len(rows)

    def register_project(
        self,
        command_id: str | UUID,
        expected_revision: int,
        registration: ProjectRegistration,
    ) -> dict[str, Any]:
        if not isinstance(registration, ProjectRegistration):
            registration = ProjectRegistration.model_validate(registration)
        normalized_command_id = _require_uuid(str(command_id), "command_id")
        if (
            not isinstance(expected_revision, int)
            or isinstance(expected_revision, bool)
            or expected_revision < 0
        ):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "expected_revision must be a non-negative integer")
        payload = registration.model_dump(mode="python")
        request_sha = self._command_request_sha("project.register", payload, expected_revision)
        replay = self._read_command_result(normalized_command_id, request_sha)
        if replay is not None:
            return replay
        with self.read_connection() as connection:
            current_revision = self._revision(connection)
        if expected_revision != current_revision:
            raise RuntimeFault(ErrorCode.VERSION_CONFLICT, "state changed; review the current project state")
        canonical_root = PolicyEngine.canonical_project_root(registration.repo_path, self.config.allowed_roots)
        base_revision = self._resolve_project_revision(canonical_root, registration.base_ref)
        policy_json = canonical_json(registration.policy.model_dump(mode="python"))
        project_id = str(uuid4())

        def write(connection: sqlite3.Connection) -> dict[str, Any]:
            connection.execute(
                "INSERT INTO projects(id, name, canonical_root, base_ref, base_revision, policy_json, status, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, 'active', ?)",
                (
                    project_id,
                    registration.name,
                    str(canonical_root),
                    registration.base_ref,
                    base_revision,
                    policy_json,
                    utc_now(),
                ),
            )
            return {"project_id": project_id}

        return self.execute_command(
            normalized_command_id,
            "project.register",
            payload,
            expected_revision,
            write,
        )

    def enable_project_coding(
        self,
        command_id: str | UUID,
        expected_revision: int,
        project_id: str,
    ) -> dict[str, Any]:
        """Grant only proposal permission after current host readiness is proven."""
        project_id = _require_uuid(project_id, "project_id")
        payload = {"project_id": project_id}

        def write(connection: sqlite3.Connection) -> dict[str, Any]:
            stopped_row = connection.execute(
                "SELECT value_json FROM settings WHERE key = 'stopped'"
            ).fetchone()
            if stopped_row and bool(_json_load(stopped_row[0])):
                raise RuntimeFault(ErrorCode.POLICY_DENIED, "runtime dispatch is stopped")
            readiness_row = connection.execute(
                "SELECT value_json FROM settings WHERE key = 'codex_readiness'"
            ).fetchone()
            readiness = _json_load(readiness_row[0]) if readiness_row else None
            if not codex_execution_enabled(self.config, readiness):
                raise RuntimeFault(ErrorCode.POLICY_DENIED, "fresh host Codex execution readiness and consent are required")
            row = connection.execute(
                "SELECT policy_json, status FROM projects WHERE id = ?", (project_id,)
            ).fetchone()
            if not row:
                raise RuntimeFault(ErrorCode.NOT_FOUND, "project was not found")
            if row["status"] != "active":
                raise RuntimeFault(ErrorCode.POLICY_DENIED, "project is not active")
            policy = _json_load(row["policy_json"])
            if not isinstance(policy, dict) or not isinstance(policy.get("allowed_actions"), list):
                raise RuntimeFault(ErrorCode.INTERNAL, "stored project policy is invalid")
            actions = policy["allowed_actions"]
            if any(not isinstance(action, str) for action in actions):
                raise RuntimeFault(ErrorCode.INTERNAL, "stored project policy is invalid")
            if "propose_patch" not in actions:
                policy["allowed_actions"] = [*actions, "propose_patch"]
                connection.execute(
                    "UPDATE projects SET policy_json = ? WHERE id = ?",
                    (canonical_json(policy), project_id),
                )
            return {"project_id": project_id, "allowed_actions": policy["allowed_actions"]}

        return self.execute_command(
            command_id,
            "project.enable_coding",
            payload,
            expected_revision,
            write,
        )

    @staticmethod
    def _run_git(project_root: Path, *arguments: str) -> str:
        environment = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
        try:
            result = subprocess.run(
                ["git", "-C", str(project_root), *arguments],
                check=False,
                capture_output=True,
                text=True,
                timeout=5,
                shell=False,
                env=environment,
            )
        except FileNotFoundError:
            raise RuntimeFault(ErrorCode.UNAVAILABLE, "Git is not available") from None
        except subprocess.TimeoutExpired:
            raise RuntimeFault(ErrorCode.UNAVAILABLE, "Git repository inspection timed out", retryable=True) from None
        if result.returncode != 0:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "project repository or base_ref could not be resolved")
        return result.stdout.strip()

    def refresh_project_revision(self, project_id: str) -> str:
        project_id = _require_uuid(project_id, "project_id")
        with self.read_connection() as connection:
            project = connection.execute(
                "SELECT canonical_root, base_ref, base_revision FROM projects WHERE id = ?", (project_id,)
            ).fetchone()
            if not project:
                raise RuntimeFault(ErrorCode.NOT_FOUND, "project was not found")
            project_root = project["canonical_root"]
            base_ref = project["base_ref"]
            previous_revision = project["base_revision"]
        canonical_root = PolicyEngine.canonical_project_root(project_root, self.config.allowed_roots)
        if str(canonical_root) != project_root:
            raise RuntimeFault(ErrorCode.VERSION_CONFLICT, "registered project path changed")
        base_revision = self._resolve_project_revision(canonical_root, base_ref)
        if base_revision == previous_revision:
            return base_revision
        with self.transaction() as connection:
            current = connection.execute(
                "SELECT canonical_root, base_ref, base_revision FROM projects WHERE id = ?", (project_id,)
            ).fetchone()
            if not current:
                raise RuntimeFault(ErrorCode.NOT_FOUND, "project was not found")
            if current["canonical_root"] != project_root or current["base_ref"] != base_ref:
                raise RuntimeFault(ErrorCode.VERSION_CONFLICT, "project registration changed during Git inspection")
            if current["base_revision"] != previous_revision:
                raise RuntimeFault(ErrorCode.VERSION_CONFLICT, "project revision changed during Git inspection")
            if base_revision == current["base_revision"]:
                return base_revision
            connection.execute(
                "UPDATE projects SET base_revision = ? WHERE id = ?",
                (base_revision, project_id),
            )
            connection.execute(
                "UPDATE approvals SET state = 'stale' WHERE state IN ('pending', 'approved') AND job_id IN "
                "(SELECT id FROM jobs WHERE project_id = ?) AND source_revision != ?",
                (project_id, base_revision),
            )
            self._bump_revision(connection)
            return base_revision

    @classmethod
    def _resolve_project_revision(cls, canonical_root: Path, base_ref: str) -> str:
        top_level = cls._run_git(canonical_root, "rev-parse", "--show-toplevel")
        if Path(top_level).resolve(strict=True) != canonical_root:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "project path must be the Git repository root")
        base_revision = cls._run_git(
            canonical_root,
            "rev-parse",
            "--verify",
            "--end-of-options",
            f"{base_ref}^{{commit}}",
        )
        if not _GIT_OBJECT_ID_RE.fullmatch(base_revision):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "base_ref did not resolve to a Git commit")
        return base_revision

    def create_job(self, command_id: str | UUID, expected_revision: int | None, job: JobCreate) -> dict[str, Any]:
        if not isinstance(job, JobCreate):
            job = JobCreate.model_validate(job)
        if job.plan is not None and len(job.plan.tasks) > self.config.max_tasks_per_plan:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "task plan exceeds the configured task limit")
        project_id = _require_uuid(job.project_id, "project_id")
        local_inspection = is_local_git_inspection(job)
        job_id = str(uuid4())
        now = utc_now()
        source_json = canonical_json(job.source.model_dump(mode="python"))
        checks_json = canonical_json(job.checks)
        actions_json = canonical_json(job.allowed_actions)
        try:
            budget_micro = budget_to_micro(job.budget_usd, allow_zero=local_inspection)
        except ValueError as error:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, str(error)) from None
        outcome = job.outcome if job.outcome is not None else job.source.text
        if job.plan is None:
            default_spec = TaskSpec(
                id="task-1",
                objective=job.source.text.strip() or job.title,
                check_ids=job.checks,
            )
            task_specs = [default_spec]
        else:
            task_specs = list(job.plan.tasks)
        task_ids = {spec.id: str(uuid4()) for spec in task_specs}
        task_rows = [
            (
                task_ids[spec.id],
                spec,
                [task_ids[dependency] for dependency in spec.depends_on],
                sort_order,
            )
            for sort_order, spec in enumerate(task_specs)
        ]
        payload = job.model_dump(mode="python")

        def write(connection: sqlite3.Connection) -> dict[str, Any]:
            project = connection.execute(
                "SELECT policy_json FROM projects WHERE id = ? AND status = 'active'", (project_id,)
            ).fetchone()
            if not project:
                raise RuntimeFault(ErrorCode.NOT_FOUND, "project was not found or is inactive")
            project_policy = _json_load(project["policy_json"])
            denied = set(job.allowed_actions) - set(project_policy.get("allowed_actions", []))
            if denied:
                raise RuntimeFault(ErrorCode.POLICY_DENIED, "job requests an action denied by project policy")
            connection.execute(
                "INSERT INTO jobs(id, project_id, title, source_json, outcome, state, checks_json, allowed_actions_json, "
                "budget_micro, spent_micro, workflow_version, candidate_id, blocked_reason, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, 'queued', ?, ?, ?, NULL, 1, NULL, NULL, ?, ?)",
                (
                    job_id,
                    project_id,
                    job.title,
                    source_json,
                    outcome,
                    checks_json,
                    actions_json,
                    budget_micro,
                    now,
                    now,
                ),
            )
            task_kind = "verify" if local_inspection else ("research" if job.source.kind == "lookout" else "build")
            for task_id, spec, dependencies, sort_order in task_rows:
                connection.execute(
                    "INSERT INTO tasks(id, job_id, kind, objective, depends_on_json, write_paths_json, check_ids_json, "
                    "state, worker_id, current_attempt_id, sort_order) VALUES (?, ?, ?, ?, ?, ?, ?, 'queued', NULL, NULL, ?)",
                    (
                        task_id,
                        job_id,
                        task_kind,
                        spec.objective,
                        canonical_json(dependencies),
                        canonical_json(spec.write_paths),
                        canonical_json(spec.check_ids),
                        sort_order,
                    ),
                )
            self._insert_event(connection, job_id, None, None, "job_created", "Job created.", None)
            return {"job_id": job_id, "task_ids": [task_id for task_id, _, _, _ in task_rows]}

        return self.execute_command(command_id, "job.create", payload, expected_revision, write)

    def create_worker(
        self,
        role: str,
        *,
        worker_id: str | UUID | None = None,
        configuration: dict[str, Any] | None = None,
        trusted_deterministic_internal: bool = False,
    ) -> str:
        if role not in {"builder", "researcher", "verifier"}:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "worker role is invalid")
        if not isinstance(trusted_deterministic_internal, bool) or (
            trusted_deterministic_internal and role != "verifier"
        ):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "only verifier workers can be trusted for deterministic internal work")
        worker_id = _require_uuid(str(worker_id or uuid4()), "worker_id")
        worker_configuration = dict(configuration or {})
        worker_configuration["trusted_deterministic_internal"] = trusted_deterministic_internal
        configuration_json = canonical_json(worker_configuration)
        with self.transaction() as connection:
            connection.execute(
                "INSERT INTO workers(id, role, state, current_task_id, configuration_json) VALUES (?, ?, 'idle', NULL, ?)",
                (worker_id, role, configuration_json),
            )
            self._bump_revision(connection)
        return worker_id

    def create_artifact(
        self,
        *,
        job_id: str,
        kind: str,
        media_type: str,
        display_name: str,
        sha256: str,
        size_bytes: int,
        storage_key: str,
        run_id: str | None = None,
        immutable: bool = True,
        artifact_id: str | UUID | None = None,
    ) -> str:
        artifact_id = _require_opaque_id(str(artifact_id or uuid4()), "artifact_id")
        job_id = _require_uuid(job_id, "job_id")
        if run_id is not None:
            run_id = _require_uuid(run_id, "run_id")
        if not isinstance(sha256, str) or len(sha256) != 64 or any(char not in "0123456789abcdef" for char in sha256):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "artifact digest must be lowercase SHA-256 hex")
        if (
            not isinstance(kind, str)
            or not isinstance(media_type, str)
            or not isinstance(display_name, str)
            or not kind
            or not media_type
            or not display_name
            or not isinstance(size_bytes, int)
            or isinstance(size_bytes, bool)
            or size_bytes < 0
            or not isinstance(immutable, bool)
            or len(display_name) > 4096
            or len(media_type) > 255
            or len(kind) > 80
        ):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "artifact metadata is invalid")
        if (
            not storage_key
            or len(storage_key) > 4096
            or "\\" in storage_key
            or storage_key.startswith("/")
            or any(part in {"", ".", ".."} for part in storage_key.split("/"))
        ):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "artifact storage key must be relative")
        with self.transaction() as connection:
            row = connection.execute("SELECT id FROM jobs WHERE id = ?", (job_id,)).fetchone()
            if not row:
                raise RuntimeFault(ErrorCode.NOT_FOUND, "job was not found")
            if run_id:
                attempt = connection.execute(
                    "SELECT t.job_id FROM attempts a JOIN tasks t ON t.id = a.task_id WHERE a.id = ?", (run_id,)
                ).fetchone()
                if not attempt or attempt["job_id"] != job_id:
                    raise RuntimeFault(ErrorCode.POLICY_DENIED, "artifact attempt is outside this job")
            connection.execute(
                "INSERT INTO artifacts(id, job_id, run_id, candidate_id, kind, media_type, display_name, sha256, "
                "size_bytes, storage_key, immutable, created_at) VALUES (?, ?, ?, NULL, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    artifact_id,
                    job_id,
                    run_id,
                    kind,
                    media_type,
                    display_name,
                    sha256,
                    size_bytes,
                    storage_key,
                    1 if immutable else 0,
                    utc_now(),
                ),
            )
            self._bump_revision(connection)
        return artifact_id

    def create_candidate(self, candidate: CandidateCreate) -> str:
        if not isinstance(candidate, CandidateCreate):
            candidate = CandidateCreate.model_validate(candidate)
        candidate_id = _require_opaque_id(candidate.candidate_id, "candidate_id")
        job_id = _require_uuid(candidate.job_id, "job_id")
        run_id = _require_uuid(candidate.run_id, "run_id")
        manifest_id = _require_opaque_id(candidate.manifest_artifact_id, "manifest_artifact_id")
        if candidate.source_revision != candidate.base_revision:
            raise RuntimeFault(ErrorCode.VERSION_CONFLICT, "candidate source revision does not match its base revision")
        with self.transaction() as connection:
            row = connection.execute(
                "SELECT j.project_id, j.candidate_id, p.base_revision, a.state AS attempt_state, t.job_id AS attempt_job "
                "FROM jobs j JOIN projects p ON p.id = j.project_id "
                "JOIN tasks t ON t.job_id = j.id JOIN attempts a ON a.task_id = t.id "
                "WHERE j.id = ? AND a.id = ?",
                (job_id, run_id),
            ).fetchone()
            if not row:
                raise RuntimeFault(ErrorCode.NOT_FOUND, "candidate job or attempt was not found")
            if row["attempt_state"] != "completed" or row["attempt_job"] != job_id:
                raise RuntimeFault(ErrorCode.POLICY_DENIED, "candidate must link to a completed attempt in this job")
            if row["base_revision"] != candidate.base_revision:
                raise RuntimeFault(ErrorCode.VERSION_CONFLICT, "project revision changed before candidate registration")
            artifact = connection.execute(
                "SELECT job_id, run_id, kind, immutable, candidate_id FROM artifacts WHERE id = ?",
                (manifest_id,),
            ).fetchone()
            if (
                not artifact
                or artifact["job_id"] != job_id
                or artifact["run_id"] != run_id
                or artifact["kind"] != "file_manifest"
                or not artifact["immutable"]
                or artifact["candidate_id"] is not None
            ):
                raise RuntimeFault(ErrorCode.POLICY_DENIED, "candidate manifest is not an immutable artifact from this attempt")
            connection.execute(
                "INSERT INTO candidates(id, job_id, run_id, base_revision, candidate_revision, tree_sha256, patch_sha256, "
                "manifest_artifact_id, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    candidate_id,
                    job_id,
                    run_id,
                    candidate.base_revision,
                    candidate.candidate_revision,
                    candidate.tree_sha256,
                    candidate.patch_sha256,
                    manifest_id,
                    utc_now(),
                ),
            )
            connection.execute("UPDATE artifacts SET candidate_id = ? WHERE id = ?", (candidate_id, manifest_id))
            connection.execute("UPDATE jobs SET candidate_id = ?, updated_at = ? WHERE id = ?", (candidate_id, utc_now(), job_id))
            connection.execute(
                "UPDATE approvals SET state = 'stale' WHERE state IN ('pending', 'approved') AND job_id = ? AND candidate_id != ?",
                (job_id, candidate_id),
            )
            self._insert_event(connection, job_id, run_id, None, "candidate_registered", "Candidate recorded.", manifest_id)
            self._bump_revision(connection)
        return candidate_id

    def request_approval(self, command_id: str | UUID, expected_revision: int, request: ApprovalCreate) -> dict[str, Any]:
        if not isinstance(request, ApprovalCreate):
            request = ApprovalCreate.model_validate(request)
        approval_id = str(uuid4())
        job_id = _require_uuid(request.job_id, "job_id")
        candidate_id = _require_uuid(request.candidate_id, "candidate_id")
        payload = request.model_dump(mode="python")

        def write(connection: sqlite3.Connection) -> dict[str, Any]:
            row = connection.execute(
                "SELECT j.candidate_id, j.allowed_actions_json, c.base_revision, c.tree_sha256, c.patch_sha256, "
                "p.base_revision AS project_revision, p.policy_json "
                "FROM jobs j JOIN projects p ON p.id = j.project_id JOIN candidates c ON c.job_id = j.id "
                "WHERE j.id = ? AND c.id = ?",
                (job_id, candidate_id),
            ).fetchone()
            if not row:
                raise RuntimeFault(ErrorCode.NOT_FOUND, "job candidate was not found")
            PolicyEngine.assert_action_allowed(
                request.action,
                _json_load(row["policy_json"]),
                _json_load(row["allowed_actions_json"]),
            )
            PolicyEngine.assert_candidate_current(
                CandidateIdentity(
                    candidate_id=request.candidate_id,
                    source_revision=request.source_revision,
                    tree_sha256=request.tree_sha256,
                    patch_sha256=request.patch_sha256,
                ),
                expected_candidate_id=row["candidate_id"],
                project_revision=row["project_revision"],
                candidate_base_revision=row["base_revision"],
                candidate_tree_sha256=row["tree_sha256"],
                candidate_patch_sha256=row["patch_sha256"],
            )
            connection.execute(
                "INSERT INTO approvals(id, job_id, candidate_id, source_revision, tree_sha256, patch_sha256, action, "
                "destination, state, decision_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending', NULL)",
                (
                    approval_id,
                    job_id,
                    candidate_id,
                    request.source_revision,
                    request.tree_sha256,
                    request.patch_sha256,
                    request.action,
                    request.destination,
                ),
            )
            self._insert_event(connection, job_id, None, None, "approval_requested", "Approval requested.", None)
            return {"approval_id": approval_id}

        return self.execute_command(command_id, "approval.request", payload, expected_revision, write)

    def decide_approval(
        self,
        command_id: str | UUID,
        expected_revision: int,
        approval_id: str,
        approve: bool,
        identity: CandidateIdentity,
    ) -> dict[str, Any]:
        approval_id = _require_uuid(approval_id, "approval_id")
        if not isinstance(approve, bool):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "approval decision must be boolean")
        if not isinstance(identity, CandidateIdentity):
            identity = CandidateIdentity.model_validate(identity)
        payload = {"approval_id": approval_id, "approve": approve, "identity": identity.model_dump(mode="python")}
        normalized_command_id = _require_uuid(str(command_id), "command_id")
        if (
            not isinstance(expected_revision, int)
            or isinstance(expected_revision, bool)
            or expected_revision < 0
        ):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "expected_revision must be a non-negative integer")
        request_sha = self._command_request_sha("approval.decide", payload, expected_revision)
        replay = self._read_command_result(normalized_command_id, request_sha)
        if replay is not None:
            return replay
        with self.read_connection() as connection:
            target = connection.execute(
                "SELECT j.project_id FROM approvals ap JOIN jobs j ON j.id = ap.job_id WHERE ap.id = ?",
                (approval_id,),
            ).fetchone()
        if target:
            # A fresh local ref check invalidates approvals after an unobserved
            # Git change. A changed revision bumps global state, so the caller
            # must re-read and review before any approval can be accepted.
            self.refresh_project_revision(target["project_id"])

        def write(connection: sqlite3.Connection) -> dict[str, Any]:
            row = connection.execute(
                "SELECT ap.*, j.candidate_id AS current_candidate, p.base_revision AS project_revision, "
                "c.base_revision AS candidate_base_revision, c.tree_sha256 AS candidate_tree_sha256, "
                "c.patch_sha256 AS candidate_patch_sha256, j.allowed_actions_json, p.policy_json "
                "FROM approvals ap JOIN jobs j ON j.id = ap.job_id JOIN projects p ON p.id = j.project_id "
                "JOIN candidates c ON c.id = ap.candidate_id WHERE ap.id = ?",
                (approval_id,),
            ).fetchone()
            if not row:
                raise RuntimeFault(ErrorCode.NOT_FOUND, "approval was not found")
            if row["state"] != "pending":
                raise RuntimeFault(ErrorCode.VERSION_CONFLICT, "approval is no longer pending")
            if (
                identity.candidate_id != row["candidate_id"]
                or identity.source_revision != row["source_revision"]
                or identity.tree_sha256 != row["tree_sha256"]
                or identity.patch_sha256 != row["patch_sha256"]
            ):
                raise RuntimeFault(ErrorCode.VERSION_CONFLICT, "approval identity differs from the saved request")
            PolicyEngine.assert_candidate_current(
                identity,
                expected_candidate_id=row["current_candidate"],
                project_revision=row["project_revision"],
                candidate_base_revision=row["candidate_base_revision"],
                candidate_tree_sha256=row["candidate_tree_sha256"],
                candidate_patch_sha256=row["candidate_patch_sha256"],
            )
            if approve:
                PolicyEngine.assert_action_allowed(
                    row["action"],
                    _json_load(row["policy_json"]),
                    _json_load(row["allowed_actions_json"]),
                )
            state = "approved" if approve else "denied"
            connection.execute(
                "UPDATE approvals SET state = ?, decision_at = ? WHERE id = ?",
                (state, utc_now(), approval_id),
            )
            self._insert_event(
                connection,
                row["job_id"],
                None,
                None,
                "approval_decided",
                "Approval approved." if approve else "Approval denied.",
                None,
            )
            return {"approval_id": approval_id, "state": state}

        return self.execute_command(normalized_command_id, "approval.decide", payload, expected_revision, write)

    def claim_ready_task(
        self,
        worker_id: str,
        reservation_micro: int,
        *,
        max_parallel: int | None = None,
        job_id: str | None = None,
    ) -> dict[str, Any] | None:
        """Atomically claim one dependency-ready task and reserve its budget."""
        worker_id = _require_uuid(worker_id, "worker_id")
        if not isinstance(reservation_micro, int) or isinstance(reservation_micro, bool) or reservation_micro < 0:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "reservation must be a non-negative integer micro-dollar amount")
        if max_parallel is not None and (
            not isinstance(max_parallel, int) or isinstance(max_parallel, bool) or not 1 <= max_parallel <= 4
        ):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "worker capacity must be between 1 and 4")
        if job_id is not None:
            job_id = _require_uuid(job_id, "job_id")
        capacity = self.config.max_parallel if max_parallel is None else min(self.config.max_parallel, max_parallel)
        with self.transaction() as connection:
            worker = connection.execute("SELECT state, role, configuration_json FROM workers WHERE id = ?", (worker_id,)).fetchone()
            if not worker:
                raise RuntimeFault(ErrorCode.NOT_FOUND, "worker was not found")
            if worker["state"] != "idle":
                return None
            stopped = connection.execute("SELECT value_json FROM settings WHERE key = 'stopped'").fetchone()
            if stopped and _json_load(stopped[0]) is True:
                return None
            active = connection.execute(
                "SELECT COUNT(*) FROM budget_reservations WHERE state = 'active'"
            ).fetchone()[0]
            if active >= capacity:
                return None

            ready_sql = (
                "SELECT t.*, j.project_id, j.budget_micro, j.spent_micro, j.state AS job_state, "
                "p.base_revision, p.status AS project_status "
                "FROM tasks t JOIN jobs j ON j.id = t.job_id JOIN projects p ON p.id = j.project_id "
                "WHERE t.state = 'queued' AND j.state IN ('queued', 'running') "
            )
            if job_id is not None:
                ready_sql += "AND j.id = ? "
            ready_sql += "ORDER BY j.created_at, t.sort_order, t.id"
            ready_rows = connection.execute(ready_sql, (job_id,) if job_id is not None else ()).fetchall()
            has_ready = False
            budget_blocked = False
            for task in ready_rows:
                if task["project_status"] != "active":
                    continue
                deps = _json_load(task["depends_on_json"])
                if deps:
                    placeholders = ",".join("?" for _ in deps)
                    dep_rows = connection.execute(
                        f"SELECT id, state FROM tasks WHERE id IN ({placeholders})", deps
                    ).fetchall()
                    state_by_id = {row["id"]: row["state"] for row in dep_rows}
                    if any(state_by_id.get(dep) in {"failed", "blocked", "cancelled"} for dep in deps):
                        continue
                    if any(state_by_id.get(dep) != "completed" for dep in deps):
                        continue
                has_ready = True
                worker_configuration = _json_load(worker["configuration_json"])
                is_resume = task["resume_requested"] == 1
                if reservation_micro == 0 and not is_resume and not (
                    task["kind"] == "verify"
                    and worker["role"] == "verifier"
                    and worker_configuration.get("trusted_deterministic_internal") is True
                ):
                    budget_blocked = True
                    continue
                if reservation_micro > task["budget_micro"]:
                    budget_blocked = True
                    continue
                reserved = connection.execute(
                    "SELECT COALESCE(SUM(reserved_micro), 0) FROM budget_reservations "
                    "WHERE state IN ('active', 'uncertain') AND attempt_id IN "
                    "(SELECT a.id FROM attempts a JOIN tasks t2 ON t2.id = a.task_id WHERE t2.job_id = ?)",
                    (task["job_id"],),
                ).fetchone()[0]
                known_spent = connection.execute(
                    "SELECT COALESCE(SUM(a.cost_micro), 0) FROM attempts a "
                    "JOIN tasks t2 ON t2.id = a.task_id WHERE t2.job_id = ?",
                    (task["job_id"],),
                ).fetchone()[0]
                spent = known_spent
                if spent + reserved + reservation_micro > task["budget_micro"]:
                    budget_blocked = True
                    continue
                active_scopes = connection.execute(
                    "SELECT t.write_paths_json FROM tasks t JOIN jobs j ON j.id = t.job_id "
                    "WHERE t.state = 'running' AND j.project_id = ?",
                    (task["project_id"],),
                ).fetchall()
                task_scopes = _json_load(task["write_paths_json"])
                if any(PolicyEngine.scopes_overlap(task_scopes, _json_load(row[0])) for row in active_scopes):
                    continue

                if is_resume:
                    prior_id = task["current_attempt_id"]
                    prior = connection.execute(
                        "SELECT a.state, a.provider_thread_id, a.base_revision AS attempt_revision, "
                        "br.reserved_micro, br.state AS reservation_state "
                        "FROM attempts a JOIN budget_reservations br ON br.attempt_id = a.id "
                        "WHERE a.id = ? AND a.task_id = ?",
                        (prior_id, task["id"]),
                    ).fetchone()
                    if (
                        not prior
                        or prior["state"] != "ambiguous"
                        or not prior["provider_thread_id"]
                        or prior["reservation_state"] != "uncertain"
                        or not isinstance(prior["reserved_micro"], int)
                        or prior["reserved_micro"] <= 0
                        or prior["attempt_revision"] != task["base_revision"]
                    ):
                        raise RuntimeFault(ErrorCode.POLICY_DENIED, "explicit resume requires an ambiguous attempt with a persisted provider session and reservation")
                    now = utc_now()
                    connection.execute(
                        "UPDATE attempts SET state = 'running', ended_at = NULL, resume_count = resume_count + 1 "
                        "WHERE id = ?",
                        (prior_id,),
                    )
                    connection.execute(
                        "UPDATE budget_reservations SET state = 'active', settled_micro = NULL WHERE attempt_id = ?",
                        (prior_id,),
                    )
                    connection.execute(
                        "UPDATE tasks SET state = 'running', worker_id = ?, resume_requested = 0 WHERE id = ?",
                        (worker_id, task["id"]),
                    )
                    connection.execute(
                        "UPDATE workers SET state = 'working', current_task_id = ? WHERE id = ?",
                        (task["id"], worker_id),
                    )
                    connection.execute("UPDATE jobs SET state = 'running', blocked_reason = NULL, updated_at = ? WHERE id = ?", (now, task["job_id"]))
                    next_seq = connection.execute(
                        "SELECT COALESCE(MAX(run_seq), 0) + 1 FROM events WHERE run_id = ?", (prior_id,)
                    ).fetchone()[0]
                    self._insert_event(connection, task["job_id"], prior_id, next_seq, "status", "Explicit Codex session resume reserved.", None)
                    revision = self._bump_revision(connection)
                    return {
                        "task_id": task["id"],
                        "job_id": task["job_id"],
                        "worker_id": worker_id,
                        "attempt_id": prior_id,
                        "reservation_id": connection.execute("SELECT id FROM budget_reservations WHERE attempt_id = ?", (prior_id,)).fetchone()[0],
                        "reserved_micro": prior["reserved_micro"],
                        "provider_thread_id": prior["provider_thread_id"],
                        "resume": True,
                        "revision": revision,
                    }

                if task["current_attempt_id"]:
                    prior_state = connection.execute(
                        "SELECT state FROM attempts WHERE id = ?", (task["current_attempt_id"],)
                    ).fetchone()
                    if prior_state and prior_state["state"] == "ambiguous":
                        raise RuntimeFault(ErrorCode.POLICY_DENIED, "ambiguous provider work requires an explicit session resume")

                attempt_id = str(uuid4())
                reservation_id = str(uuid4())
                now = utc_now()
                attempt_number = connection.execute(
                    "SELECT COALESCE(MAX(number), 0) + 1 FROM attempts WHERE task_id = ?", (task["id"],)
                ).fetchone()[0]
                connection.execute(
                    "INSERT INTO attempts(id, task_id, number, state, base_revision, provider_thread_id, provider_turn_id, "
                    "model, effort, started_at, ended_at, input_tokens, cached_input_tokens, output_tokens, total_tokens, "
                    "cost_micro, usage_uncertain, worker_id) "
                    "VALUES (?, ?, ?, 'running', ?, NULL, NULL, NULL, NULL, ?, NULL, NULL, NULL, NULL, NULL, NULL, 1, ?)",
                    (attempt_id, task["id"], attempt_number, task["base_revision"], now, worker_id),
                )
                connection.execute(
                    "INSERT INTO budget_reservations(id, attempt_id, reserved_micro, settled_micro, state, created_at) "
                    "VALUES (?, ?, ?, NULL, 'active', ?)",
                    (reservation_id, attempt_id, reservation_micro, now),
                )
                connection.execute(
                    "UPDATE tasks SET state = 'running', worker_id = ?, current_attempt_id = ? WHERE id = ?",
                    (worker_id, attempt_id, task["id"]),
                )
                connection.execute("UPDATE workers SET state = 'working', current_task_id = ? WHERE id = ?", (task["id"], worker_id))
                connection.execute("UPDATE jobs SET state = 'running', updated_at = ? WHERE id = ?", (now, task["job_id"]))
                self._insert_event(connection, task["job_id"], attempt_id, 1, "dispatch_intent", "Task dispatch reserved.", None)
                revision = self._bump_revision(connection)
                return {
                    "task_id": task["id"],
                    "job_id": task["job_id"],
                    "worker_id": worker_id,
                    "attempt_id": attempt_id,
                    "reservation_id": reservation_id,
                    "reserved_micro": reservation_micro,
                    "provider_thread_id": None,
                    "resume": False,
                    "revision": revision,
                }
            if has_ready and budget_blocked:
                raise RuntimeFault(ErrorCode.BUDGET_LIMIT, "job budget cannot cover the requested reservation")
            return None

    def record_provider_session(
        self,
        attempt_id: str,
        *,
        provider_thread_id: str | None,
        provider_turn_id: str | None,
        model: str | None,
        effort: str | None,
    ) -> None:
        attempt_id = _require_uuid(attempt_id, "attempt_id")
        for label, value in (("provider thread id", provider_thread_id), ("provider turn id", provider_turn_id)):
            if value is not None and (
                not isinstance(value, str)
                or len(value) > 512
                or not _PROVIDER_ID_RE.fullmatch(value)
            ):
                raise RuntimeFault(ErrorCode.INVALID_INPUT, f"{label} is invalid")
        if model is not None and (not isinstance(model, str) or len(model) > 128 or not _OPAQUE_ID_RE.fullmatch(model)):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "provider model id is invalid")
        if effort is not None and (not isinstance(effort, str) or len(effort) > 32 or not _OPAQUE_ID_RE.fullmatch(effort)):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "provider effort is invalid")
        with self.transaction() as connection:
            row = connection.execute(
                "SELECT state, provider_thread_id, model, effort FROM attempts WHERE id = ?",
                (attempt_id,),
            ).fetchone()
            if not row:
                raise RuntimeFault(ErrorCode.NOT_FOUND, "attempt was not found")
            if row["state"] != "running":
                raise RuntimeFault(ErrorCode.VERSION_CONFLICT, "provider session belongs to a non-running attempt")
            if (
                row["provider_thread_id"] is not None
                and provider_thread_id is not None
                and row["provider_thread_id"] != provider_thread_id
            ):
                raise RuntimeFault(ErrorCode.VERSION_CONFLICT, "provider thread identity changed during this attempt")
            if row["model"] is not None and model is not None and row["model"] != model:
                raise RuntimeFault(ErrorCode.VERSION_CONFLICT, "provider model identity changed during this attempt")
            if row["effort"] is not None and effort is not None and row["effort"] != effort:
                raise RuntimeFault(ErrorCode.VERSION_CONFLICT, "provider effort identity changed during this attempt")
            connection.execute(
                "UPDATE attempts SET provider_thread_id = COALESCE(?, provider_thread_id), "
                "provider_turn_id = COALESCE(?, provider_turn_id), model = COALESCE(?, model), effort = COALESCE(?, effort) "
                "WHERE id = ?",
                (provider_thread_id, provider_turn_id, model, effort, attempt_id),
            )

    def settle_attempt(
        self,
        attempt_id: str,
        *,
        cost_micro: int | None,
        input_tokens: int | None = None,
        cached_input_tokens: int | None = None,
        output_tokens: int | None = None,
        total_tokens: int | None = None,
        uncertain: bool = False,
        state: str = "completed",
    ) -> None:
        attempt_id = _require_uuid(attempt_id, "attempt_id")
        if state not in {"completed", "failed", "cancelled", "ambiguous"}:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "attempt result state is invalid")
        values = (cost_micro, input_tokens, cached_input_tokens, output_tokens, total_tokens)
        if any(
            value is not None
            and (not isinstance(value, int) or isinstance(value, bool) or value < 0)
            for value in values
        ):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "usage values must be non-negative integers or null")
        if cost_micro is None:
            uncertain = True
        with self.transaction() as connection:
            row = connection.execute(
                "SELECT a.state, a.task_id, t.job_id, t.worker_id, t.current_attempt_id "
                "FROM attempts a JOIN tasks t ON t.id = a.task_id WHERE a.id = ?",
                (attempt_id,),
            ).fetchone()
            if not row:
                raise RuntimeFault(ErrorCode.NOT_FOUND, "attempt was not found")
            if row["state"] != "running" or row["current_attempt_id"] != attempt_id:
                raise RuntimeFault(ErrorCode.VERSION_CONFLICT, "attempt is no longer current")
            now = utc_now()
            connection.execute(
                "UPDATE attempts SET state = ?, ended_at = ?, input_tokens = ?, cached_input_tokens = ?, output_tokens = ?, "
                "total_tokens = ?, cost_micro = ?, usage_uncertain = ? WHERE id = ?",
                (
                    state,
                    now,
                    input_tokens,
                    cached_input_tokens,
                    output_tokens,
                    total_tokens,
                    cost_micro,
                    1 if uncertain else 0,
                    attempt_id,
                ),
            )
            reservation_state = "uncertain" if uncertain or cost_micro is None else "settled"
            connection.execute(
                "UPDATE budget_reservations SET settled_micro = ?, state = ? WHERE attempt_id = ?",
                (cost_micro, reservation_state, attempt_id),
            )
            if row["worker_id"]:
                connection.execute("UPDATE workers SET state = 'idle', current_task_id = NULL WHERE id = ?", (row["worker_id"],))
            task_state = "completed" if state == "completed" else (
                "cancelled" if state == "cancelled" else ("blocked" if state == "ambiguous" else "failed")
            )
            connection.execute(
                "UPDATE tasks SET state = ?, worker_id = NULL WHERE id = ?",
                (task_state, row["task_id"]),
            )
            connection.execute("UPDATE tasks SET resume_requested = 0 WHERE id = ?", (row["task_id"],))
            cost_rows = connection.execute(
                "SELECT cost_micro, state FROM attempts WHERE task_id IN (SELECT id FROM tasks WHERE job_id = ?)",
                (row["job_id"],),
            ).fetchall()
            if cost_rows and all(item["cost_micro"] is not None for item in cost_rows):
                spent_micro = sum(item["cost_micro"] for item in cost_rows)
            else:
                spent_micro = None
            connection.execute("UPDATE jobs SET spent_micro = ?, updated_at = ? WHERE id = ?", (spent_micro, now, row["job_id"]))
            next_seq = connection.execute(
                "SELECT COALESCE(MAX(run_seq), 0) + 1 FROM events WHERE run_id = ?", (attempt_id,)
            ).fetchone()[0]
            self._insert_event(connection, row["job_id"], attempt_id, next_seq, "attempt_finished", "Attempt result recorded.", None)
            self._bump_revision(connection)

    def get_budget(self, job_id: str) -> dict[str, Any]:
        job_id = _require_uuid(job_id, "job_id")
        with self.read_connection() as connection:
            row = connection.execute(
                "SELECT j.budget_micro, j.spent_micro, "
                "COALESCE((SELECT SUM(br.reserved_micro) FROM budget_reservations br JOIN attempts a ON a.id = br.attempt_id "
                "JOIN tasks t ON t.id = a.task_id WHERE t.job_id = j.id AND br.state IN ('active', 'uncertain')), 0) AS reserved_micro, "
                "EXISTS(SELECT 1 FROM attempts a JOIN tasks t ON t.id = a.task_id WHERE t.job_id = j.id AND a.usage_uncertain = 1) AS uncertain "
                "FROM jobs j WHERE j.id = ?",
                (job_id,),
            ).fetchone()
            if not row:
                raise RuntimeFault(ErrorCode.NOT_FOUND, "job was not found")
            return dict(row)

    def block_unclaimed_tasks(self, job_id: str) -> int:
        """Prevent a failed dispatch gate from leaving queued work under a blocked job."""
        job_id = _require_uuid(job_id, "job_id")
        with self.transaction() as connection:
            changed = connection.execute(
                "UPDATE tasks SET state = 'blocked', resume_requested = 0 "
                "WHERE job_id = ? AND state = 'queued'",
                (job_id,),
            ).rowcount
            if changed:
                self._bump_revision(connection)
            return changed

    def list_projects(self) -> list[dict[str, Any]]:
        with self.read_connection() as connection:
            rows = connection.execute(
                "SELECT id, name, base_revision, status, policy_json, created_at FROM projects ORDER BY name, id"
            ).fetchall()
            return [
                {
                    **dict(row),
                    "policy": _json_load(row["policy_json"]),
                }
                for row in rows
            ]

    def list_jobs(self, project_id: str | None = None, *, limit: int = 100) -> list[dict[str, Any]]:
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 500:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "job list limit must be between 1 and 500")
        with self.read_connection() as connection:
            if project_id is None:
                rows = connection.execute(
                    "SELECT id, project_id, title, source_json, outcome, state, checks_json, allowed_actions_json, "
                    "budget_micro, spent_micro, workflow_version, candidate_id, blocked_reason, created_at, updated_at "
                    "FROM jobs ORDER BY created_at DESC, id DESC LIMIT ?",
                    (limit,),
                ).fetchall()
            else:
                project_id = _require_uuid(project_id, "project_id")
                rows = connection.execute(
                    "SELECT id, project_id, title, source_json, outcome, state, checks_json, allowed_actions_json, "
                    "budget_micro, spent_micro, workflow_version, candidate_id, blocked_reason, created_at, updated_at "
                    "FROM jobs WHERE project_id = ? ORDER BY created_at DESC, id DESC LIMIT ?",
                    (project_id, limit),
                ).fetchall()
            return [
                {
                    **dict(row),
                    "source": _json_load(row["source_json"]),
                    "checks": _json_load(row["checks_json"]),
                    "allowed_actions": _json_load(row["allowed_actions_json"]),
                }
                for row in rows
            ]

    def list_workers(self) -> list[dict[str, Any]]:
        with self.read_connection() as connection:
            rows = connection.execute(
                "SELECT w.*, t.job_id AS current_job_id FROM workers w "
                "LEFT JOIN tasks t ON t.id = w.current_task_id ORDER BY w.role, w.id"
            ).fetchall()
            output = []
            for row in rows:
                item = dict(row)
                item["configuration"] = _json_load(item.pop("configuration_json"))
                if item.get("current_job_id") is None:
                    item["current_job_id"] = item["configuration"].get("assigned_job_id")
                output.append(item)
            return output

    def list_approvals(self) -> list[dict[str, Any]]:
        with self.read_connection() as connection:
            rows = connection.execute(
                "SELECT id, job_id, candidate_id, source_revision, tree_sha256, patch_sha256, action, destination, state, decision_at "
                "FROM approvals ORDER BY rowid DESC LIMIT 100"
            ).fetchall()
            return [dict(row) for row in rows]

    def list_job_artifacts(self, job_id: str, *, limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        job_id = _require_uuid(job_id, "job_id")
        if not 1 <= limit <= 101 or offset < 0:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "artifact page bounds are invalid")
        with self.read_connection() as connection:
            return [
                dict(row)
                for row in connection.execute(
                    "SELECT * FROM artifacts WHERE job_id = ? "
                    "ORDER BY CASE kind WHEN 'file_manifest' THEN 0 WHEN 'diff' THEN 1 WHEN 'patch' THEN 2 "
                    "WHEN 'test_report' THEN 3 WHEN 'log' THEN 4 ELSE 5 END, created_at, id LIMIT ? OFFSET ?",
                    (job_id, limit, offset),
                ).fetchall()
            ]

    def list_candidate_artifacts(
        self,
        candidate_id: str,
        *,
        display_names: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        candidate_id = _require_opaque_id(candidate_id, "candidate_id")
        if display_names is not None and (
            not isinstance(display_names, list)
            or len(display_names) > 100
            or any(not isinstance(item, str) or len(item) > 4096 for item in display_names)
        ):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "candidate artifact path filter is invalid")
        with self.read_connection() as connection:
            if not connection.execute("SELECT 1 FROM candidates WHERE id = ?", (candidate_id,)).fetchone():
                raise RuntimeFault(ErrorCode.NOT_FOUND, "candidate was not found")
            if display_names is not None:
                if not display_names:
                    return []
                placeholders = ",".join("?" for _ in display_names)
                rows = connection.execute(
                    f"SELECT * FROM artifacts WHERE candidate_id = ? AND kind = 'source_file' "
                    f"AND display_name IN ({placeholders}) ORDER BY display_name, id",
                    (candidate_id, *display_names),
                ).fetchall()
                return [dict(row) for row in rows]
            return [
                dict(row)
                for row in connection.execute(
                    "SELECT * FROM artifacts WHERE candidate_id = ? ORDER BY created_at, id",
                    (candidate_id,),
                ).fetchall()
            ]

    def list_job_runs(self, job_id: str) -> list[dict[str, Any]]:
        job_id = _require_uuid(job_id, "job_id")
        with self.read_connection() as connection:
            rows = connection.execute(
                "SELECT a.*, t.job_id, t.id AS task_id FROM attempts a "
                "JOIN tasks t ON t.id = a.task_id WHERE t.job_id = ? "
                "ORDER BY a.started_at, a.id",
                (job_id,),
            ).fetchall()
            return [dict(row) for row in rows]

    def get_run(self, run_id: str) -> dict[str, Any]:
        run_id = _require_uuid(run_id, "run_id")
        with self.read_connection() as connection:
            row = connection.execute(
                "SELECT a.*, t.job_id, t.id AS task_id FROM attempts a "
                "JOIN tasks t ON t.id = a.task_id WHERE a.id = ?",
                (run_id,),
            ).fetchone()
            if not row:
                raise RuntimeFault(ErrorCode.NOT_FOUND, "run was not found")
            return dict(row)

    def list_run_events(self, run_id: str, *, after_seq: int = 0, limit: int = 200) -> list[dict[str, Any]]:
        run_id = _require_uuid(run_id, "run_id")
        if (
            not isinstance(after_seq, int) or isinstance(after_seq, bool) or after_seq < 0
            or not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 200
        ):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "run event page bounds are invalid")
        with self.read_connection() as connection:
            rows = connection.execute(
                "SELECT run_seq AS seq, at, type, message, artifact_id, job_id FROM events "
                "WHERE run_id = ? AND run_seq > ? ORDER BY run_seq LIMIT ?",
                (run_id, after_seq, limit + 1),
            ).fetchall()
            return [dict(row) for row in rows]

    def append_run_event(
        self,
        job_id: str,
        run_id: str,
        event_type: str,
        message: str,
        artifact_id: str | None = None,
    ) -> int:
        job_id = _require_uuid(job_id, "job_id")
        run_id = _require_uuid(run_id, "run_id")
        with self.transaction() as connection:
            seq = self._insert_event(connection, job_id, run_id, None, event_type, message, artifact_id)
            self._bump_revision(connection)
            return seq

    def finalize_job(self, job_id: str, state: str, outcome: str, *, blocked_reason: str | None = None) -> None:
        job_id = _require_uuid(job_id, "job_id")
        if state not in {"verifying", "failed", "blocked", "cancelled"}:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "final job state is invalid")
        if len(outcome) > 16000 or (blocked_reason is not None and len(blocked_reason) > 4096):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "job outcome exceeds the configured limit")
        with self.transaction() as connection:
            row = connection.execute("SELECT id FROM jobs WHERE id = ?", (job_id,)).fetchone()
            if not row:
                raise RuntimeFault(ErrorCode.NOT_FOUND, "job was not found")
            connection.execute(
                "UPDATE jobs SET state = ?, outcome = ?, blocked_reason = ?, updated_at = ? WHERE id = ?",
                (state, outcome, blocked_reason, utc_now(), job_id),
            )
            self._insert_event(connection, job_id, None, None, "status", outcome[:_MAX_EVENT_LENGTH], None)
            self._bump_revision(connection)

    def set_job_command(
        self,
        command_id: str | UUID,
        expected_revision: int,
        command_type: str,
        job_id: str,
        *,
        codex_ready: bool = False,
    ) -> dict[str, Any]:
        if command_type not in {"job.run", "job.resume", "job.pause", "job.cancel"}:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "job command is unsupported")
        job_id = _require_uuid(job_id, "job_id")
        payload = {"job_id": job_id}

        def write(connection: sqlite3.Connection) -> dict[str, Any]:
            row = connection.execute(
                "SELECT state, source_json, checks_json, allowed_actions_json, budget_micro, project_id FROM jobs WHERE id = ?",
                (job_id,),
            ).fetchone()
            if not row:
                raise RuntimeFault(ErrorCode.NOT_FOUND, "job was not found")
            state = row["state"]
            if command_type == "job.run":
                create_data = {
                    "source": _json_load(row["source_json"]),
                    "checks": _json_load(row["checks_json"]),
                    "allowed_actions": _json_load(row["allowed_actions_json"]),
                    "budget_micro": row["budget_micro"],
                }
                safe_run = (
                    create_data["source"].get("kind") == "typed"
                    and set(create_data["allowed_actions"]) == {"read_repo", "run_checks"}
                    and create_data["checks"] == ["candidate.frozen_identity"]
                    and create_data["budget_micro"] == 0
                )
                task_rows = connection.execute("SELECT * FROM tasks WHERE job_id = ? ORDER BY sort_order, id", (job_id,)).fetchall()
                tasks = []
                for task in task_rows:
                    item = dict(task)
                    item["depends_on"] = _json_load(item["depends_on_json"])
                    item["write_paths"] = _json_load(item["write_paths_json"])
                    item["check_ids"] = _json_load(item["check_ids_json"])
                    tasks.append(item)
                codex_profile = codex_ready and is_codex_job_from_stored(
                    {
                        **create_data,
                        "checks": create_data["checks"],
                        "budget_micro": create_data["budget_micro"],
                    },
                    tasks,
                )
                if not safe_run and not codex_profile:
                    raise RuntimeFault(ErrorCode.POLICY_DENIED, "no verified coding worker is configured")
                if state not in {"queued", "paused"}:
                    raise RuntimeFault(ErrorCode.VERSION_CONFLICT, "job is not ready to run")
                if codex_profile and connection.execute(
                    "SELECT 1 FROM tasks t JOIN attempts a ON a.id = t.current_attempt_id "
                    "WHERE t.job_id = ? AND a.state = 'ambiguous'",
                    (job_id,),
                ).fetchone():
                    raise RuntimeFault(ErrorCode.POLICY_DENIED, "ambiguous Codex work requires the explicit job.resume command")
                connection.execute(
                    "UPDATE jobs SET state = 'running', blocked_reason = NULL, updated_at = ? WHERE id = ?",
                    (utc_now(), job_id),
                )
                connection.execute(
                    "UPDATE tasks SET state = 'queued' WHERE job_id = ? AND state IN ('paused', 'cancelled')",
                    (job_id,),
                )
                self._insert_event(
                    connection,
                    job_id,
                    None,
                    None,
                    "status",
                    "Host-authorized Codex task queued." if codex_profile else "Read-only inspection queued.",
                    None,
                )
                return {"job_id": job_id, "state": "running"}
            if command_type == "job.resume":
                if not codex_ready:
                    raise RuntimeFault(ErrorCode.POLICY_DENIED, "a fresh verified Codex capability and host consent are required to resume")
                task_rows = connection.execute(
                    "SELECT t.*, a.state AS attempt_state, a.provider_thread_id, a.base_revision AS attempt_revision, "
                    "br.state AS reservation_state, br.reserved_micro, p.base_revision AS project_revision "
                    "FROM tasks t JOIN projects p ON p.id = ? "
                    "LEFT JOIN attempts a ON a.id = t.current_attempt_id "
                    "LEFT JOIN budget_reservations br ON br.attempt_id = a.id "
                    "WHERE t.job_id = ? AND t.state = 'blocked' ORDER BY t.sort_order, t.id",
                    (row["project_id"], job_id),
                ).fetchall()
                resume_task = next((item for item in task_rows if item["attempt_state"] == "ambiguous"), None)
                profile_tasks = []
                all_tasks = connection.execute("SELECT * FROM tasks WHERE job_id = ? ORDER BY sort_order, id", (job_id,)).fetchall()
                for task in all_tasks:
                    item = dict(task)
                    item["depends_on"] = _json_load(item["depends_on_json"])
                    item["write_paths"] = _json_load(item["write_paths_json"])
                    item["check_ids"] = _json_load(item["check_ids_json"])
                    profile_tasks.append(item)
                profile = {
                    "source": _json_load(row["source_json"]),
                    "checks": _json_load(row["checks_json"]),
                    "allowed_actions": _json_load(row["allowed_actions_json"]),
                    "budget_micro": row["budget_micro"],
                }
                if state not in {"paused", "blocked"} or not is_codex_job_from_stored(profile, profile_tasks):
                    raise RuntimeFault(ErrorCode.POLICY_DENIED, "job is not an eligible Codex session to resume")
                if (
                    not resume_task
                    or not resume_task["provider_thread_id"]
                    or resume_task["reservation_state"] != "uncertain"
                    or not resume_task["reserved_micro"]
                    or resume_task["attempt_revision"] != resume_task["project_revision"]
                ):
                    raise RuntimeFault(ErrorCode.POLICY_DENIED, "explicit resume requires a saved session, uncertain reservation and current source revision")
                connection.execute(
                    "UPDATE tasks SET state = 'queued', resume_requested = 1 WHERE id = ?",
                    (resume_task["id"],),
                )
                connection.execute(
                    "UPDATE jobs SET state = 'running', blocked_reason = NULL, updated_at = ? WHERE id = ?",
                    (utc_now(), job_id),
                )
                self._insert_event(connection, job_id, resume_task["current_attempt_id"], None, "status", "Explicit Codex session resume requested.", None)
                return {"job_id": job_id, "task_id": resume_task["id"], "state": "running", "resumed": True}
            if command_type == "job.pause":
                if state not in {"queued", "running"}:
                    raise RuntimeFault(ErrorCode.VERSION_CONFLICT, "job cannot be paused in its current state")
                connection.execute(
                    "UPDATE jobs SET state = 'paused', updated_at = ? WHERE id = ?", (utc_now(), job_id)
                )
                connection.execute("UPDATE tasks SET state = 'paused' WHERE job_id = ? AND state = 'queued'", (job_id,))
                self._insert_event(connection, job_id, None, None, "status", "Job paused.", None)
                return {"job_id": job_id, "state": "paused"}
            if state in {"accepted", "cancelled"}:
                raise RuntimeFault(ErrorCode.VERSION_CONFLICT, "job cannot be cancelled in its current state")
            connection.execute(
                "UPDATE jobs SET state = 'cancelled', updated_at = ? WHERE id = ?", (utc_now(), job_id)
            )
            connection.execute(
                "UPDATE tasks SET state = 'cancelled' WHERE job_id = ? AND state IN ('queued', 'paused')", (job_id,)
            )
            self._insert_event(connection, job_id, None, None, "status", "Job cancellation requested.", None)
            return {"job_id": job_id, "state": "cancelled"}

        return self.execute_command(command_id, command_type, payload, expected_revision, write)

    def select_project(self, command_id: str | UUID, expected_revision: int, project_id: str) -> dict[str, Any]:
        project_id = _require_uuid(project_id, "project_id")

        def write(connection: sqlite3.Connection) -> dict[str, Any]:
            row = connection.execute("SELECT id FROM projects WHERE id = ? AND status = 'active'", (project_id,)).fetchone()
            if not row:
                raise RuntimeFault(ErrorCode.NOT_FOUND, "active project was not found")
            connection.execute(
                "INSERT INTO settings(key, value_json) VALUES ('selected_project_id', ?) "
                "ON CONFLICT(key) DO UPDATE SET value_json = excluded.value_json",
                (canonical_json(project_id),),
            )
            return {"project_id": project_id}

        return self.execute_command(command_id, "project.select", {"project_id": project_id}, expected_revision, write)

    def assign_worker(
        self,
        command_id: str | UUID,
        expected_revision: int,
        job_id: str,
        worker_id: str,
    ) -> dict[str, Any]:
        job_id = _require_uuid(job_id, "job_id")
        worker_id = _require_uuid(worker_id, "worker_id")
        payload = {"job_id": job_id, "worker_id": worker_id}

        def write(connection: sqlite3.Connection) -> dict[str, Any]:
            if not connection.execute("SELECT 1 FROM jobs WHERE id = ?", (job_id,)).fetchone():
                raise RuntimeFault(ErrorCode.NOT_FOUND, "job was not found")
            worker = connection.execute(
                "SELECT state, role, configuration_json FROM workers WHERE id = ?", (worker_id,)
            ).fetchone()
            if not worker:
                raise RuntimeFault(ErrorCode.NOT_FOUND, "worker was not found")
            if worker["state"] != "idle":
                raise RuntimeFault(ErrorCode.VERSION_CONFLICT, "a working worker cannot be reassigned")
            worker_configuration = _json_load(worker["configuration_json"])
            if worker["role"] != "verifier" or worker_configuration.get("trusted_deterministic_internal") is not True:
                raise RuntimeFault(ErrorCode.POLICY_DENIED, "only a trusted deterministic verifier is available in this runtime profile")
            if connection.execute("SELECT 1 FROM tasks WHERE job_id = ? AND state = 'running'", (job_id,)).fetchone():
                raise RuntimeFault(ErrorCode.VERSION_CONFLICT, "a running job cannot be reassigned")
            worker_configuration["assigned_job_id"] = job_id
            connection.execute(
                "UPDATE workers SET configuration_json = ? WHERE id = ?",
                (canonical_json(worker_configuration), worker_id),
            )
            return {"job_id": job_id, "worker_id": worker_id}

        return self.execute_command(command_id, "job.assign", payload, expected_revision, write)

    def system_stop(self, command_id: str | UUID, expected_revision: int | None, stopped: bool) -> dict[str, Any]:
        command_type = "system.stop" if stopped else "system.resume"

        def write(connection: sqlite3.Connection) -> dict[str, Any]:
            connection.execute(
                "INSERT INTO settings(key, value_json) VALUES ('stopped', ?) "
                "ON CONFLICT(key) DO UPDATE SET value_json = excluded.value_json",
                (canonical_json(stopped),),
            )
            if stopped:
                connection.execute("UPDATE tasks SET state = 'paused' WHERE state = 'queued'")
                connection.execute("UPDATE jobs SET state = 'paused', updated_at = ? WHERE state IN ('queued', 'running')", (utc_now(),))
            return {"stopped": stopped}

        return self.execute_command(command_id, command_type, {}, expected_revision, write)

    def save_layout(self, command_id: str | UUID, expected_revision: int, layout: dict[str, Any]) -> dict[str, Any]:
        def write(connection: sqlite3.Connection) -> dict[str, Any]:
            current = connection.execute("SELECT value_json FROM settings WHERE key = 'layout'").fetchone()
            version = (_json_load(current[0])["version"] if current else 0) + 1
            stored = {"version": version, "nodes": layout["nodes"], "edges": layout["edges"]}
            connection.execute(
                "INSERT INTO settings(key, value_json) VALUES ('layout', ?) "
                "ON CONFLICT(key) DO UPDATE SET value_json = excluded.value_json",
                (canonical_json(stored),),
            )
            return stored

        return self.execute_command(command_id, "layout.save", layout, expected_revision, write)

    def get_setting(self, key: str, default: Any = None) -> Any:
        with self.read_connection() as connection:
            row = connection.execute("SELECT value_json FROM settings WHERE key = ?", (key,)).fetchone()
            return _json_load(row[0]) if row else default

    def get_project(self, project_id: str) -> dict[str, Any]:
        project_id = _require_uuid(project_id, "project_id")
        with self.read_connection() as connection:
            row = connection.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
            if not row:
                raise RuntimeFault(ErrorCode.NOT_FOUND, "project was not found")
            result = dict(row)
            result["policy"] = _json_load(result.pop("policy_json"))
            return result

    def get_job(self, job_id: str) -> dict[str, Any]:
        job_id = _require_uuid(job_id, "job_id")
        with self.read_connection() as connection:
            row = connection.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
            if not row:
                raise RuntimeFault(ErrorCode.NOT_FOUND, "job was not found")
            result = dict(row)
            for stored, exposed in (
                ("source_json", "source"),
                ("checks_json", "checks"),
                ("allowed_actions_json", "allowed_actions"),
            ):
                result[exposed] = _json_load(result.pop(stored))
            result["tasks"] = self.list_tasks(job_id)
            return result

    def list_tasks(self, job_id: str) -> list[dict[str, Any]]:
        job_id = _require_uuid(job_id, "job_id")
        with self.read_connection() as connection:
            rows = connection.execute(
                "SELECT * FROM tasks WHERE job_id = ? ORDER BY sort_order, id", (job_id,)
            ).fetchall()
            results = []
            for row in rows:
                item = dict(row)
                item["depends_on"] = _json_load(item.pop("depends_on_json"))
                item["write_paths"] = _json_load(item.pop("write_paths_json"))
                item["check_ids"] = _json_load(item.pop("check_ids_json"))
                results.append(item)
            return results

    def get_attempt(self, attempt_id: str) -> dict[str, Any]:
        attempt_id = _require_uuid(attempt_id, "attempt_id")
        with self.read_connection() as connection:
            row = connection.execute("SELECT * FROM attempts WHERE id = ?", (attempt_id,)).fetchone()
            if not row:
                raise RuntimeFault(ErrorCode.NOT_FOUND, "attempt was not found")
            return dict(row)

    def get_candidate(self, candidate_id: str) -> dict[str, Any]:
        candidate_id = _require_opaque_id(candidate_id, "candidate_id")
        with self.read_connection() as connection:
            row = connection.execute("SELECT * FROM candidates WHERE id = ?", (candidate_id,)).fetchone()
            if not row:
                raise RuntimeFault(ErrorCode.NOT_FOUND, "candidate was not found")
            return dict(row)

    def get_artifact(self, artifact_id: str) -> dict[str, Any]:
        artifact_id = _require_opaque_id(artifact_id, "artifact_id")
        with self.read_connection() as connection:
            row = connection.execute("SELECT * FROM artifacts WHERE id = ?", (artifact_id,)).fetchone()
            if not row:
                raise RuntimeFault(ErrorCode.NOT_FOUND, "artifact was not found")
            return dict(row)

    def attach_artifacts_to_candidate(self, candidate_id: str, artifact_ids: list[str]) -> None:
        candidate_id = _require_opaque_id(candidate_id, "candidate_id")
        ids = [_require_opaque_id(item, "artifact_id") for item in artifact_ids]
        with self.transaction() as connection:
            if not connection.execute("SELECT 1 FROM candidates WHERE id = ?", (candidate_id,)).fetchone():
                raise RuntimeFault(ErrorCode.NOT_FOUND, "candidate was not found")
            for artifact_id in ids:
                row = connection.execute(
                    "SELECT candidate_id FROM artifacts WHERE id = ?", (artifact_id,)
                ).fetchone()
                if not row:
                    raise RuntimeFault(ErrorCode.NOT_FOUND, "artifact was not found")
                if row["candidate_id"] not in (None, candidate_id):
                    raise RuntimeFault(ErrorCode.POLICY_DENIED, "artifact already belongs to another candidate")
                connection.execute(
                    "UPDATE artifacts SET candidate_id = ? WHERE id = ?", (candidate_id, artifact_id)
                )
            self._bump_revision(connection)

    def _insert_event(
        self,
        connection: sqlite3.Connection,
        job_id: str,
        run_id: str | None,
        run_seq: int | None,
        event_type: str,
        message: str,
        artifact_id: str | None,
    ) -> int:
        if len(message) > _MAX_EVENT_LENGTH:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "event message exceeds 4096 characters")
        if not event_type or len(event_type) > 80:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "event type is invalid")
        if run_id is not None and run_seq is None:
            run_seq = connection.execute(
                "SELECT COALESCE(MAX(run_seq), 0) + 1 FROM events WHERE run_id = ?", (run_id,)
            ).fetchone()[0]
        if run_seq is not None and run_seq < 1:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "run event sequence must be positive")
        if artifact_id is not None:
            artifact = connection.execute("SELECT job_id FROM artifacts WHERE id = ?", (artifact_id,)).fetchone()
            if not artifact or artifact["job_id"] != job_id:
                raise RuntimeFault(ErrorCode.POLICY_DENIED, "event artifact is outside this job")
        cursor = connection.execute(
            "INSERT INTO events(job_id, run_id, run_seq, at, type, message, artifact_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (job_id, run_id, run_seq, utc_now(), event_type, message, artifact_id),
        )
        return int(cursor.lastrowid)


__all__ = ["RuntimeStore"]
