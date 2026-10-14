"""Deterministic A2 scheduler and the zero-cost local Git inspection pipeline."""

from __future__ import annotations

import asyncio
import json
import re
import os
import shutil
import stat
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from .adapters import AdapterRunner
from .artifacts import ArtifactStore
from .config import RuntimeConfig, codex_execution_enabled
from .models import CandidateCreate, budget_to_micro, is_codex_job_from_stored
from .policy import ErrorCode, RuntimeFault
from .store import RuntimeStore
from .sessions import AttachmentStore

_HEX_OBJECT = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_READ_ONLY_WRITE_SCOPE = ["__sidequest_read_only_inspection__"]


class Scheduler:
    """Runs bounded deterministic verification jobs; model/coding adapters stay disabled."""

    def __init__(self, store: RuntimeStore, config: RuntimeConfig, adapters: AdapterRunner, artifacts: ArtifactStore):
        self.store = store
        self.config = config
        self.adapters = adapters
        self.artifacts = artifacts
        self._tasks: dict[str, asyncio.Task[None]] = {}
        self._workers: list[str] = []
        self._builder_workers: list[str] = []
        self._cancel_events: dict[str, asyncio.Event] = {}
        self._closed = False

    def start(self) -> None:
        if self._closed:
            self._closed = False
        self.store.reconcile_interrupted_attempts()
        self.store.reconcile_interrupted_messages()
        workers = self.store.list_workers()
        self._workers = [
            worker["id"]
            for worker in workers
            if worker["role"] == "verifier"
            and worker["configuration"].get("trusted_deterministic_internal") is True
        ]
        while len(self._workers) < self.config.max_parallel:
            self._workers.append(self.store.create_worker("verifier", trusted_deterministic_internal=True))
        self._builder_workers = [
            worker["id"] for worker in workers
            if worker["role"] == "builder" and worker["configuration"].get("host_codex") is True
        ]
        if self.config.codex_enabled and self.config.codex_consent and not self._builder_workers:
            self._builder_workers.append(self.store.create_worker("builder", configuration={"host_codex": True}))
        # Only saved intents that never reached provider dispatch may resume.
        # Interrupted dispatches were marked uncertain above and are excluded.
        if codex_execution_enabled(self.config, self.store.get_codex_readiness()):
            for job_id in self.store.queued_message_jobs():
                self.enqueue(job_id)

    def enqueue(self, job_id: str) -> None:
        if self._closed:
            return
        current = self._tasks.get(job_id)
        if current is not None and not current.done():
            return
        self._tasks[job_id] = asyncio.create_task(self._run_job(job_id), name=f"sidequest-job-{job_id}")

    async def pause_job(self, job_id: str) -> None:
        task = self._tasks.get(job_id)
        if task is not None and not task.done():
            event = self._cancel_events.get(job_id)
            if event is None:
                task.cancel()
            else:
                event.set()
                done, _ = await asyncio.wait({task}, timeout=7.0)
                if not done:
                    task.cancel()
            await asyncio.gather(task, return_exceptions=True)

    async def cancel_job(self, job_id: str) -> None:
        await self.pause_job(job_id)

    async def stop(self) -> None:
        self._closed = True
        tasks = list(self._tasks.values())
        for event in self._cancel_events.values():
            event.set()
        if tasks:
            done, pending = await asyncio.wait(set(tasks), timeout=7.0)
            for task in pending:
                task.cancel()
        for task in tasks:
            if not task.done():
                task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        self._tasks.clear()
        self._cancel_events.clear()

    def _get_profile(self, job_id: str) -> tuple[dict[str, Any], dict[str, Any], str]:
        job = self.store.get_job(job_id)
        project = self.store.get_project(job["project_id"])
        profile = {
            "source": job["source"],
            "checks": job["checks"],
            "allowed_actions": job["allowed_actions"],
            "budget_micro": job["budget_micro"],
            "plan": None if len(job["tasks"]) == 1 and job["tasks"][0]["kind"] == "verify" else job["tasks"],
        }
        if is_local_git_inspection_from_stored(profile):
            return job, project, "local_git_inspection"
        if is_codex_job_from_stored(profile, job["tasks"]) and codex_execution_enabled(self.config, self.store.get_codex_readiness()):
            return job, project, "codex_session"
        raise RuntimeFault(ErrorCode.POLICY_DENIED, "no verified coding worker is configured")

    async def _run_job(self, job_id: str) -> None:
        attempt_id: str | None = None
        claimed: dict[str, Any] | None = None
        try:
            while True:
                if self.store.get_setting("stopped", False) is True:
                    return
                job, project, execution_profile = self._get_profile(job_id)
                if job["state"] != "running":
                    return
                if not any(task["state"] == "queued" for task in job["tasks"]):
                    return
                self.store.refresh_project_revision(project["id"])
                project = self.store.get_project(project["id"])
                job, project, execution_profile = self._get_profile(job_id)
                pending_task = next(task for task in job["tasks"] if task["state"] == "queued")
                workers = {item["id"]: item for item in self.store.list_workers()}
                claimed = None
                assigned_here = [
                    worker_id
                    for worker_id in (self._builder_workers if execution_profile == "codex_session" else self._workers)
                    if workers.get(worker_id, {}).get("configuration", {}).get("assigned_job_id") == job_id
                ]
                worker_ids = assigned_here or [
                    worker_id
                    for worker_id in (self._builder_workers if execution_profile == "codex_session" else self._workers)
                    if workers.get(worker_id, {}).get("configuration", {}).get("assigned_job_id") is None
                ]
                message_worker = self.store.queued_message_worker(pending_task['id'])
                if message_worker is not None:
                    worker_ids = [worker for worker in worker_ids if worker == message_worker]
                if execution_profile == "codex_session":
                    budget = self.store.get_budget(job_id)
                    resume_requested = pending_task.get("resume_requested") == 1
                    if resume_requested:
                        reservation = 0
                    else:
                        if budget["spent_micro"] is None and budget["uncertain"]:
                            raise RuntimeFault(ErrorCode.BUDGET_LIMIT, "known budget availability is required before a Codex dispatch")
                        known_spent = budget["spent_micro"] if budget["spent_micro"] is not None else 0
                        reservation = max(0, budget["budget_micro"] - known_spent - budget["reserved_micro"])
                        if reservation <= 0:
                            raise RuntimeFault(ErrorCode.BUDGET_LIMIT, "job budget cannot cover a positive Codex reservation")
                else:
                    reservation = 0
                    resume_requested = False
                for worker_id in worker_ids:
                    worker = workers.get(worker_id)
                    if not worker or worker["state"] != "idle":
                        continue
                    claimed = self.store.claim_ready_task(
                        worker_id,
                        0 if resume_requested else reservation,
                        max_parallel=self.config.max_parallel,
                        job_id=job_id,
                    )
                    if claimed is not None:
                        claimed["execution_profile"] = execution_profile
                        break
                if claimed is None:
                    await asyncio.sleep(0.1)
                    continue
                attempt_id = claimed["attempt_id"]
                self.store.append_run_event(
                    job_id,
                    attempt_id,
                    "status",
                    "Starting local Git inspection." if execution_profile == "local_git_inspection" else "Starting host-authorized Codex session.",
                )
                if execution_profile == "local_git_inspection":
                    await self._inspect(job, project, claimed)
                else:
                    cancel_event = asyncio.Event()
                    self._cancel_events[job_id] = cancel_event
                    await self._codex(job, project, claimed, pending_task, cancel_event)
                return
        except asyncio.CancelledError:
            if claimed and attempt_id:
                try:
                    codex_attempt = claimed.get("execution_profile") == "codex_session"
                    self.store.settle_attempt(
                        attempt_id,
                        cost_micro=None if codex_attempt else 0,
                        uncertain=codex_attempt,
                        state="ambiguous" if codex_attempt else "cancelled",
                    )
                except RuntimeFault:
                    pass
            raise
        except RuntimeFault as error:
            if claimed and attempt_id:
                try:
                    codex_attempt = claimed.get("execution_profile") == "codex_session"
                    self.store.settle_attempt(
                        attempt_id,
                        cost_micro=None if codex_attempt else 0,
                        uncertain=codex_attempt,
                        state="ambiguous" if codex_attempt else "failed",
                    )
                except RuntimeFault:
                    pass
            elif not claimed:
                try:
                    self.store.block_unclaimed_tasks(job_id)
                except RuntimeFault:
                    pass
            try:
                current_job = self.store.get_job(job_id)
                if current_job["state"] not in {"cancelled", "paused"}:
                    blocked = claimed is not None and claimed.get("execution_profile") == "codex_session" or error.code in {ErrorCode.POLICY_DENIED, ErrorCode.INVALID_INPUT, ErrorCode.VERSION_CONFLICT}
                    outcome = (
                        "Codex dispatch could not continue safely; no automatic retry was scheduled."
                        if claimed is not None and claimed.get("execution_profile") == "codex_session"
                        else "Local inspection could not complete safely."
                    )
                    self.store.finalize_job(
                        job_id,
                        "blocked" if blocked else "failed",
                        outcome,
                        blocked_reason=error.message[:1024] if blocked else None,
                    )
            except RuntimeFault:
                pass
        except Exception:
            if claimed and attempt_id:
                try:
                    codex_attempt = claimed.get("execution_profile") == "codex_session"
                    self.store.settle_attempt(
                        attempt_id,
                        cost_micro=None if codex_attempt else 0,
                        uncertain=codex_attempt,
                        state="ambiguous" if codex_attempt else "failed",
                    )
                except RuntimeFault:
                    pass
            elif not claimed:
                try:
                    self.store.block_unclaimed_tasks(job_id)
                except RuntimeFault:
                    pass
            try:
                current_job = self.store.get_job(job_id)
                if current_job["state"] not in {"cancelled", "paused"}:
                    is_codex = claimed is not None and claimed.get("execution_profile") == "codex_session"
                    self.store.finalize_job(
                        job_id,
                        "blocked" if is_codex else "failed",
                        "Codex session did not complete safely; provider state and USD usage are uncertain."
                        if is_codex else "Local inspection failed safely.",
                        blocked_reason="Review the saved provider session before explicitly resuming it." if is_codex else None,
                    )
            except RuntimeFault:
                pass
        finally:
            if attempt_id:
                self.store.settle_session_message(attempt_id)
            else:
                self.store.reject_unstarted_messages(job_id)
            self._cancel_events.pop(job_id, None)
            for path in (
                self.config.workspaces_dir / f"inspection-{attempt_id}" if attempt_id else None,
                self.config.workspaces_dir / f"codex-{attempt_id}" if attempt_id else None,
                self.config.adapter_output_dir / f"b-{attempt_id}" if attempt_id else None,
                self.config.adapter_output_dir / f"d-{attempt_id}" if attempt_id else None,
            ):
                if path is not None:
                    try:
                        self._remove_tree(path)
                    except (OSError, RuntimeFault):
                        pass

    async def _progress(self, job_id: str, attempt_id: str, record: dict[str, Any]) -> None:
        if record.get("type") == "session":
            self.store.record_provider_session(
                attempt_id,
                provider_thread_id=record.get("provider_thread_id"),
                provider_turn_id=record.get("provider_turn_id"),
                model=None,
                effort=None,
            )
            await self._progress(job_id, attempt_id, {"type": "status", "message": "Codex session progress was saved."})
            return
        self.store.append_run_event(job_id, attempt_id, record["type"], record["message"])

    async def _inspect(self, job: dict[str, Any], project: dict[str, Any], claim: dict[str, Any]) -> None:
        job_id = job["id"]
        attempt_id = claim["attempt_id"]
        base_revision = project["base_revision"]
        workspace = self.config.workspaces_dir / f"inspection-{attempt_id}"
        b_output = self.config.adapter_output_dir / f"b-{attempt_id}"
        d_output = self.config.adapter_output_dir / f"d-{attempt_id}"
        if workspace.exists() or workspace.is_symlink() or b_output.exists() or b_output.is_symlink() or d_output.exists() or d_output.is_symlink():
            raise RuntimeFault(ErrorCode.VERSION_CONFLICT, "host-assigned inspection workspace already exists")

        inspect_result = await self.adapters.call(
            "B",
            op="repo.inspect",
            job_id=job_id,
            workspace=workspace,
            payload={"repo_path": project["canonical_root"], "revision": base_revision},
            context={"project_id": project["id"], "source_revision": base_revision},
            progress_callback=lambda record: self._progress(job_id, attempt_id, record),
        )
        inspect_data = inspect_result["data"]
        if (
            inspect_data.get("revision") != base_revision
            or not isinstance(inspect_data.get("clean"), bool)
            or not isinstance(inspect_data.get("files"), list)
            or any(not isinstance(item, str) for item in inspect_data["files"])
        ):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "B returned invalid repository inspection data")
        if not inspect_data["clean"]:
            raise RuntimeFault(ErrorCode.POLICY_DENIED, "registered Git worktree must be clean for frozen inspection")

        prepare_result = await self.adapters.call(
            "B",
            op="repo.prepare",
            job_id=job_id,
            workspace=workspace,
            payload={"repo_path": project["canonical_root"], "revision": base_revision},
            context={"project_id": project["id"], "source_revision": base_revision},
            progress_callback=lambda record: self._progress(job_id, attempt_id, record),
        )
        prepared = prepare_result["data"].get("workspace")
        if not isinstance(prepared, str) or Path(prepared).resolve(strict=True) != workspace.resolve(strict=True):
            raise RuntimeFault(ErrorCode.POLICY_DENIED, "B returned an unexpected repository workspace")

        b_output.mkdir(mode=0o700)
        freeze_result = await self.adapters.call(
            "B",
            op="artifacts.freeze",
            job_id=job_id,
            workspace=workspace,
            payload={"base_revision": base_revision, "write_paths": _READ_ONLY_WRITE_SCOPE},
            context={
                "project_id": project["id"],
                "run_id": attempt_id,
                "attempt_id": attempt_id,
                "source_revision": base_revision,
                "write_paths": _READ_ONLY_WRITE_SCOPE,
                "output_root": str(b_output),
            },
            progress_callback=lambda record: self._progress(job_id, attempt_id, record),
        )
        freeze_data = freeze_result["data"]
        candidate = freeze_data.get("candidate")
        if not isinstance(candidate, dict):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "B did not return a frozen candidate identity")
        candidate_id = candidate.get("id")
        candidate_revision = candidate.get("candidate_revision")
        manifest_id = freeze_data.get("manifest_artifact_id")
        if (
            not isinstance(candidate_id, str)
            or not isinstance(candidate_revision, str)
            or not _HEX_OBJECT.fullmatch(candidate_revision)
            or candidate.get("base_revision") != base_revision
            or candidate.get("project_id") != project["id"]
            or not isinstance(candidate.get("tree_sha256"), str)
            or not _SHA256.fullmatch(candidate["tree_sha256"])
            or not isinstance(candidate.get("patch_sha256"), str)
            or not _SHA256.fullmatch(candidate["patch_sha256"])
            or not isinstance(manifest_id, str)
        ):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "B candidate identity is malformed")
        b_artifact_ids = self.artifacts.import_adapter_records(
            b_output,
            freeze_result["artifacts"],
            job_id=job_id,
            run_id=attempt_id,
            candidate_id=candidate_id,
        )
        if manifest_id not in b_artifact_ids:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "B manifest artifact is missing")
        manifest_artifact = self.store.get_artifact(manifest_id)
        manifest = self.artifacts.read_manifest(manifest_artifact)
        if manifest.get("candidate") != candidate:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "B manifest candidate differs from the adapter identity")
        snapshot_root_raw = freeze_data.get("snapshot_root")
        if not isinstance(snapshot_root_raw, str):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "B did not return a candidate snapshot")
        snapshot_root = Path(snapshot_root_raw)
        try:
            snapshot_root.resolve(strict=True).relative_to(b_output.resolve(strict=True))
        except (OSError, ValueError):
            raise RuntimeFault(ErrorCode.POLICY_DENIED, "B candidate snapshot is outside its host output root") from None
        file_ids, file_paths, runtime_snapshot = self.artifacts.import_candidate_snapshot(
            manifest,
            snapshot_root,
            job_id=job_id,
            run_id=attempt_id,
            candidate_id=candidate_id,
        )
        staged_manifest = self.artifacts.stage_manifest(
            manifest_artifact,
            candidate_id=candidate_id,
            input_root=self.config.adapter_input_dir,
        )
        d_output.mkdir(mode=0o700)
        d_result = await self.adapters.call(
            "D",
            op="check.run",
            job_id=job_id,
            workspace=runtime_snapshot,
            payload={"check_ids": ["candidate.frozen_identity"], "source_revision": candidate_revision},
            context={
                "project_id": project["id"],
                "run_id": attempt_id,
                "attempt_id": attempt_id,
                "source_revision": candidate_revision,
                "output_root": str(d_output),
                "artifact_inputs": [{"id": manifest_id, "sha256": manifest_artifact["sha256"], "staged_path": str(staged_manifest)}],
            },
            progress_callback=lambda record: self._progress(job_id, attempt_id, record),
        )
        data = d_result["data"]
        usage = d_result.get("usage")
        if (
            data.get("passed") is not True
            or data.get("inference_calls") != 0
            or data.get("candidate") != {
                "id": candidate_id,
                "tree_sha256": candidate["tree_sha256"],
                "source_revision": candidate_revision,
            }
            or data.get("results") != [{
                "id": "candidate.frozen_identity",
                "state": "pass",
                "evidence_artifact_id": manifest_id,
                "message": "The read-only candidate matches its host-staged file manifest.",
            }]
            or not isinstance(usage, dict)
            or usage.get("cost_usd") != 0.0
            or usage.get("uncertain") is not False
        ):
            raise RuntimeFault(ErrorCode.DEPENDENCY_FAILED, "D did not confirm the frozen identity check")
        d_artifact_ids = self.artifacts.import_adapter_records(
            d_output,
            d_result["artifacts"],
            job_id=job_id,
            run_id=attempt_id,
        )
        report = next((self.store.get_artifact(item) for item in d_artifact_ids if self.store.get_artifact(item)["kind"] == "test_report"), None)
        if report is None:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "D check report artifact is missing")
        try:
            report_data = json.loads(self.artifacts.read_artifact(report).decode("utf-8", "strict"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "D check report is malformed") from None
        if (
            report_data.get("source_revision") != candidate_revision
            or report_data.get("candidate", {}).get("id") != candidate_id
            or report_data.get("candidate", {}).get("tree_sha256") != candidate["tree_sha256"]
            or report_data.get("inference_calls") != 0
            or report_data.get("results") != data["results"]
        ):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "D report does not match the check response")

        self.store.settle_attempt(
            attempt_id,
            cost_micro=0,
            input_tokens=None,
            cached_input_tokens=None,
            output_tokens=None,
            total_tokens=None,
            uncertain=False,
            state="completed",
        )
        self.store.create_candidate(
            CandidateCreate(
                candidate_id=candidate_id,
                source_revision=base_revision,
                tree_sha256=candidate["tree_sha256"],
                patch_sha256=candidate["patch_sha256"],
                job_id=job_id,
                run_id=attempt_id,
                base_revision=base_revision,
                candidate_revision=candidate_revision,
                manifest_artifact_id=manifest_id,
            )
        )
        linked = [item for item in [*b_artifact_ids, *file_ids, *d_artifact_ids] if item != manifest_id]
        self.store.attach_artifacts_to_candidate(candidate_id, linked)
        self.store.append_run_event(job_id, attempt_id, "tool_finished", "Frozen identity check passed.", report["id"])
        self.store.finalize_job(
            job_id,
            "verifying",
            "Local Git inspection completed; the frozen candidate identity check passed. No model inference or delivery ran.",
        )
        self._remove_tree(workspace)
        self._remove_tree(b_output)
        self._remove_tree(d_output)

    async def _codex(
        self,
        job: dict[str, Any],
        project: dict[str, Any],
        claim: dict[str, Any],
        task: dict[str, Any],
        cancel_event: asyncio.Event,
    ) -> None:
        """Run one explicitly authorized Codex session and verify its frozen identity."""
        job_id = job["id"]
        attempt_id = claim["attempt_id"]
        base_revision = project["base_revision"]
        write_paths = list(task["write_paths"])
        workspace = self.config.workspaces_dir / f"codex-{attempt_id}"
        b_output = self.config.adapter_output_dir / f"b-{attempt_id}"
        d_output = self.config.adapter_output_dir / f"d-{attempt_id}"
        self.config.workspaces_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.config.adapter_output_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        if self.config.workspaces_dir.is_symlink() or self.config.adapter_output_dir.is_symlink():
            raise RuntimeFault(ErrorCode.POLICY_DENIED, "runtime workspace roots cannot be symlinks")
        if any(path.exists() or path.is_symlink() for path in (workspace, b_output, d_output)):
            raise RuntimeFault(ErrorCode.VERSION_CONFLICT, "host-assigned Codex workspace already exists")

        inspect_result = await self.adapters.call(
            "B",
            op="repo.inspect",
            job_id=job_id,
            workspace=workspace,
            payload={"repo_path": project["canonical_root"], "revision": base_revision},
            context={"project_id": project["id"], "source_revision": base_revision},
            progress_callback=lambda record: self._progress(job_id, attempt_id, record),
        )
        inspect_data = inspect_result["data"]
        if (
            inspect_data.get("revision") != base_revision
            or inspect_data.get("clean") is not True
            or not isinstance(inspect_data.get("files"), list)
            or any(not isinstance(item, str) for item in inspect_data["files"])
        ):
            raise RuntimeFault(ErrorCode.POLICY_DENIED, "registered Git worktree must be clean for a Codex session")

        prepare_result = await self.adapters.call(
            "B",
            op="repo.prepare",
            job_id=job_id,
            workspace=workspace,
            payload={"repo_path": project["canonical_root"], "revision": base_revision},
            context={"project_id": project["id"], "source_revision": base_revision},
            progress_callback=lambda record: self._progress(job_id, attempt_id, record),
        )
        prepared = prepare_result["data"].get("workspace")
        if not isinstance(prepared, str) or Path(prepared).resolve(strict=True) != workspace.resolve(strict=True):
            raise RuntimeFault(ErrorCode.POLICY_DENIED, "B returned an unexpected Codex workspace")

        b_output.mkdir(mode=0o700)
        reservation_micro = claim.get("reserved_micro")
        if not isinstance(reservation_micro, int) or isinstance(reservation_micro, bool) or reservation_micro <= 0:
            raise RuntimeFault(ErrorCode.BUDGET_LIMIT, "Codex execution requires a positive host budget reservation")
        max_cost_usd = float(Decimal(reservation_micro) / Decimal(1_000_000))
        context: dict[str, Any] = {
            "project_id": project["id"],
            "run_id": attempt_id,
            "attempt_id": attempt_id,
            "source_revision": base_revision,
            "write_paths": write_paths,
            "output_root": str(b_output),
        }
        if claim.get("resume") is True:
            provider_thread_id = claim.get("provider_thread_id")
            if not isinstance(provider_thread_id, str) or not provider_thread_id:
                raise RuntimeFault(ErrorCode.POLICY_DENIED, "explicit Codex resume has no persisted provider thread")
            context["provider_thread_id"] = provider_thread_id
        if claim.get("followup"):
            context["provider_thread_id"] = claim["provider_thread_id"]
            context["provider_turn_id"] = claim["provider_turn_id"]
            context["attachments"] = AttachmentStore(self.config, self.store).resolve(
                claim["parent_run_id"], claim["attachment_ids"])
            previous_candidate = job.get("candidate_id")
            if previous_candidate:
                context["initial_tree_sha256"] = self.artifacts.restore_candidate_for_followup(
                    previous_candidate, claim["parent_run_id"], workspace, write_paths)
        response = await self.adapters.call(
            "B",
            op="agent.execute",
            job_id=job_id,
            workspace=workspace,
            payload={
                "objective": task["objective"],
                "check_ids": list(task["check_ids"]),
                "limits": {
                    "max_seconds": self.config.codex_max_seconds,
                    "max_cost_usd": max_cost_usd,
                },
                **({"followup": claim["followup"]} if claim.get("followup") else {}),
            },
            context=context,
            progress_callback=lambda record: self._progress(job_id, attempt_id, record),
            cancel_event=cancel_event,
        )
        data = response["data"]
        usage = response.get("usage")
        usage_fields = ("input_tokens", "cached_input_tokens", "output_tokens", "total_tokens")
        if (
            not isinstance(usage, dict)
            or usage.get("cost_usd") is not None
            or usage.get("uncertain") is not True
            or any(
                usage.get(name) is not None
                and (
                    not isinstance(usage.get(name), int)
                    or isinstance(usage.get(name), bool)
                    or usage[name] < 0
                )
                for name in usage_fields
            )
        ):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "Codex usage must preserve unknown USD cost and validated token counts")
        provider_thread_id = data.get("provider_thread_id")
        provider_turn_id = data.get("provider_turn_id")
        model = data.get("model")
        effort = data.get("effort")
        if model is not None and not isinstance(model, str):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "Codex model identity is invalid")
        if effort is not None and not isinstance(effort, str):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "Codex effort identity is invalid")
        if claim.get("followup") and (
            data.get("message_id") != claim["followup"]["message_id"]
            or provider_thread_id != claim["provider_thread_id"]
            or not provider_turn_id or provider_turn_id == claim["provider_turn_id"]
        ):
            raise RuntimeFault(ErrorCode.POLICY_DENIED, "Follow-up response differs from its saved message/thread/turn identity")
        self.store.record_provider_session(
            attempt_id,
            provider_thread_id=provider_thread_id,
            provider_turn_id=provider_turn_id,
            model=model,
            effort=effort,
        )

        if claim.get("followup") and data.get("status") == "completed":
            if (data.get("message_id") != claim["followup"]["message_id"]
                or provider_thread_id != claim["provider_thread_id"]
                or not provider_turn_id or data.get("model_verified") is not True
                or data.get("effort_verified") is not True or model != self.config.codex_model
                or effort != self.config.codex_effort or response.get("artifacts")
                or cancel_event.is_set() or response.get("_cancel_requested") is True):
                raise RuntimeFault(ErrorCode.INVALID_INPUT, "Follow-up completion identity is invalid")
            self.store.settle_attempt(attempt_id, cost_micro=None, uncertain=True, state="completed",
                **{name: usage.get(name) for name in usage_fields})
            self.store.finalize_job(job_id, "verifying", "Follow-up completed without new Git changes. Prior frozen artifacts remain available; USD usage stays unknown.")
            return

        if data.get("status") != "candidate" or response.get("_cancel_requested") is True or cancel_event.is_set():
            self.store.settle_attempt(
                attempt_id,
                cost_micro=None,
                input_tokens=usage.get("input_tokens"),
                cached_input_tokens=usage.get("cached_input_tokens"),
                output_tokens=usage.get("output_tokens"),
                total_tokens=usage.get("total_tokens"),
                uncertain=True,
                state="ambiguous",
            )
            current = self.store.get_job(job_id)
            if current["state"] not in {"paused", "cancelled"}:
                self.store.finalize_job(
                    job_id,
                    "blocked",
                    "Codex stopped without an accepted candidate. Provider completion and USD usage remain uncertain; no automatic retry or delivery ran.",
                    blocked_reason="The Codex attempt is ambiguous. Review the saved session before explicitly resuming it.",
                )
            return

        if (
            data.get("model_verified") is not True
            or data.get("effort_verified") is not True
            or not isinstance(model, str)
            or not model
            or not isinstance(effort, str)
            or not effort
            or model != self.config.codex_model
            or effort != self.config.codex_effort
            or data.get("check_ids") != task["check_ids"]
        ):
            raise RuntimeFault(ErrorCode.POLICY_DENIED, "Codex did not confirm the host-configured model, effort and checks")
        summary = data.get("summary")
        if not isinstance(summary, str) or len(summary.encode("utf-8")) > 8 * 1024:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "Codex candidate summary is malformed")

        candidate = data.get("candidate")
        if not isinstance(candidate, dict):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "Codex did not return a frozen candidate identity")
        candidate_id = candidate.get("id")
        candidate_revision = candidate.get("candidate_revision")
        manifest_id = data.get("manifest_artifact_id")
        tree_sha = candidate.get("tree_sha256")
        patch_sha = candidate.get("patch_sha256")
        if (
            not isinstance(candidate_id, str)
            or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:_-]{0,199}", candidate_id)
            or not isinstance(candidate_revision, str)
            or not _HEX_OBJECT.fullmatch(candidate_revision)
            or candidate.get("base_revision") != base_revision
            or candidate.get("project_id") != project["id"]
            or not isinstance(tree_sha, str)
            or not _SHA256.fullmatch(tree_sha)
            or not isinstance(patch_sha, str)
            or not _SHA256.fullmatch(patch_sha)
            or not isinstance(manifest_id, str)
        ):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "Codex candidate identity is malformed")
        b_artifact_ids = self.artifacts.import_adapter_records(
            b_output,
            response["artifacts"],
            job_id=job_id,
            run_id=attempt_id,
            candidate_id=candidate_id,
        )
        if manifest_id not in b_artifact_ids:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "Codex manifest artifact is missing")
        manifest_artifact = self.store.get_artifact(manifest_id)
        manifest = self.artifacts.read_manifest(manifest_artifact)
        if manifest.get("candidate") != candidate:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "Codex manifest candidate differs from its adapter identity")
        snapshot_root_raw = data.get("snapshot_root")
        if not isinstance(snapshot_root_raw, str):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "Codex did not return its frozen candidate snapshot")
        snapshot_root = Path(snapshot_root_raw)
        try:
            snapshot_root.resolve(strict=True).relative_to(b_output.resolve(strict=True))
        except (OSError, ValueError):
            raise RuntimeFault(ErrorCode.POLICY_DENIED, "Codex candidate snapshot is outside its host output root") from None
        file_ids, _file_paths, runtime_snapshot = self.artifacts.import_candidate_snapshot(
            manifest,
            snapshot_root,
            job_id=job_id,
            run_id=attempt_id,
            candidate_id=candidate_id,
        )
        staged_manifest = self.artifacts.stage_manifest(
            manifest_artifact,
            candidate_id=candidate_id,
            input_root=self.config.adapter_input_dir,
        )
        d_output.mkdir(mode=0o700)
        d_result = await self.adapters.call(
            "D",
            op="check.run",
            job_id=job_id,
            workspace=runtime_snapshot,
            payload={"check_ids": ["candidate.frozen_identity"], "source_revision": candidate_revision},
            context={
                "project_id": project["id"],
                "run_id": attempt_id,
                "attempt_id": attempt_id,
                "source_revision": candidate_revision,
                "output_root": str(d_output),
                "artifact_inputs": [{
                    "id": manifest_id,
                    "sha256": manifest_artifact["sha256"],
                    "staged_path": str(staged_manifest),
                }],
            },
            progress_callback=lambda record: self._progress(job_id, attempt_id, record),
        )
        check_data = d_result["data"]
        check_usage = d_result.get("usage")
        expected_result = [{
            "id": "candidate.frozen_identity",
            "state": "pass",
            "evidence_artifact_id": manifest_id,
            "message": "The read-only candidate matches its host-staged file manifest.",
        }]
        if (
            check_data.get("passed") is not True
            or check_data.get("inference_calls") != 0
            or check_data.get("candidate") != {"id": candidate_id, "tree_sha256": tree_sha, "source_revision": candidate_revision}
            or check_data.get("results") != expected_result
            or not isinstance(check_usage, dict)
            or check_usage.get("cost_usd") != 0.0
            or check_usage.get("uncertain") is not False
        ):
            raise RuntimeFault(ErrorCode.DEPENDENCY_FAILED, "D did not confirm the Codex frozen identity check")
        d_artifact_ids = self.artifacts.import_adapter_records(
            d_output,
            d_result["artifacts"],
            job_id=job_id,
            run_id=attempt_id,
        )
        reports = [self.store.get_artifact(item) for item in d_artifact_ids]
        report = next((item for item in reports if item["kind"] == "test_report"), None)
        if report is None:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "D frozen identity report artifact is missing")
        try:
            report_data = json.loads(self.artifacts.read_artifact(report).decode("utf-8", "strict"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "D frozen identity report is malformed") from None
        if (
            report_data.get("source_revision") != candidate_revision
            or report_data.get("candidate", {}).get("id") != candidate_id
            or report_data.get("candidate", {}).get("tree_sha256") != tree_sha
            or report_data.get("inference_calls") != 0
            or report_data.get("results") != check_data["results"]
        ):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "D frozen identity report does not match its response")

        # A model turn may outlive an unnoticed source ref movement. Refresh
        # the registered root immediately before candidate registration so a
        # stale candidate cannot enter review.
        self.store.refresh_project_revision(project["id"])
        self.store.settle_attempt(
            attempt_id,
            cost_micro=None,
            input_tokens=usage.get("input_tokens"),
            cached_input_tokens=usage.get("cached_input_tokens"),
            output_tokens=usage.get("output_tokens"),
            total_tokens=usage.get("total_tokens"),
            uncertain=True,
            state="completed",
        )
        self.store.create_candidate(
            CandidateCreate(
                candidate_id=candidate_id,
                source_revision=base_revision,
                tree_sha256=tree_sha,
                patch_sha256=patch_sha,
                job_id=job_id,
                run_id=attempt_id,
                base_revision=base_revision,
                candidate_revision=candidate_revision,
                manifest_artifact_id=manifest_id,
            )
        )
        linked = [item for item in [*b_artifact_ids, *file_ids, *d_artifact_ids] if item != manifest_id]
        self.store.attach_artifacts_to_candidate(candidate_id, linked)
        self.store.append_run_event(job_id, attempt_id, "tool_finished", "Codex candidate passed the frozen identity check.", report["id"])
        self.store.finalize_job(
            job_id,
            "verifying",
            "Codex produced a frozen candidate and its frozen identity check passed. Provider USD usage remains unknown and reserved; no delivery ran.",
        )
        self._remove_tree(workspace)
        self._remove_tree(b_output)
        self._remove_tree(d_output)

    @staticmethod
    def _remove_tree(path: Path) -> None:
        if path.is_symlink():
            raise RuntimeFault(ErrorCode.POLICY_DENIED, "runtime workspace cannot be a symlink")
        if path.exists():
            for item in sorted(path.rglob("*"), key=lambda value: len(value.parts), reverse=True):
                try:
                    mode = item.lstat().st_mode
                    if stat.S_ISLNK(mode):
                        continue
                    os.chmod(item, 0o700 if stat.S_ISDIR(mode) else 0o600, follow_symlinks=False)
                except OSError:
                    continue
            os.chmod(path, 0o700, follow_symlinks=False)
            shutil.rmtree(path)


def is_local_git_inspection_from_stored(profile: dict[str, Any]) -> bool:
    return (
        profile["source"].get("kind") == "typed"
        and profile["checks"] == ["candidate.frozen_identity"]
        and set(profile["allowed_actions"]) == {"read_repo", "run_checks"}
        and profile["budget_micro"] == 0
        and profile["plan"] is None
    )
