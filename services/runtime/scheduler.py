"""Deterministic A2 scheduler and the zero-cost local Git inspection pipeline."""

from __future__ import annotations

import asyncio
import json
import re
import os
import shutil
import stat
from pathlib import Path
from typing import Any

from .adapters import AdapterRunner
from .artifacts import ArtifactStore
from .config import RuntimeConfig
from .models import CandidateCreate
from .policy import ErrorCode, RuntimeFault
from .store import RuntimeStore

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
        self._closed = False

    def start(self) -> None:
        if self._closed:
            self._closed = False
        workers = self.store.list_workers()
        self._workers = [
            worker["id"]
            for worker in workers
            if worker["role"] == "verifier"
            and worker["configuration"].get("trusted_deterministic_internal") is True
        ]
        while len(self._workers) < self.config.max_parallel:
            self._workers.append(self.store.create_worker("verifier", trusted_deterministic_internal=True))

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
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)

    async def cancel_job(self, job_id: str) -> None:
        await self.pause_job(job_id)

    async def stop(self) -> None:
        self._closed = True
        tasks = list(self._tasks.values())
        for task in tasks:
            if not task.done():
                task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        self._tasks.clear()

    def _get_profile(self, job_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
        job = self.store.get_job(job_id)
        project = self.store.get_project(job["project_id"])
        profile = {
            "source": job["source"],
            "checks": job["checks"],
            "allowed_actions": job["allowed_actions"],
            "budget_micro": job["budget_micro"],
            "plan": None if len(job["tasks"]) == 1 and job["tasks"][0]["kind"] == "verify" else job["tasks"],
        }
        if not is_local_git_inspection_from_stored(profile):
            raise RuntimeFault(ErrorCode.POLICY_DENIED, "no verified coding worker is configured")
        return job, project

    async def _run_job(self, job_id: str) -> None:
        attempt_id: str | None = None
        claimed: dict[str, Any] | None = None
        try:
            while True:
                if self.store.get_setting("stopped", False) is True:
                    return
                job, project = self._get_profile(job_id)
                if job["state"] != "running":
                    return
                if not any(task["state"] == "queued" for task in job["tasks"]):
                    return
                self.store.refresh_project_revision(project["id"])
                project = self.store.get_project(project["id"])
                workers = {item["id"]: item for item in self.store.list_workers()}
                claimed = None
                assigned_here = [
                    worker_id
                    for worker_id in self._workers
                    if workers.get(worker_id, {}).get("configuration", {}).get("assigned_job_id") == job_id
                ]
                worker_ids = assigned_here or [
                    worker_id
                    for worker_id in self._workers
                    if workers.get(worker_id, {}).get("configuration", {}).get("assigned_job_id") is None
                ]
                for worker_id in worker_ids:
                    worker = workers.get(worker_id)
                    if not worker or worker["state"] != "idle":
                        continue
                    claimed = self.store.claim_ready_task(
                        worker_id,
                        0,
                        max_parallel=self.config.max_parallel,
                        job_id=job_id,
                    )
                    if claimed is not None:
                        break
                if claimed is None:
                    await asyncio.sleep(0.1)
                    continue
                attempt_id = claimed["attempt_id"]
                self.store.append_run_event(job_id, attempt_id, "status", "Starting local Git inspection.")
                await self._inspect(job, project, claimed)
                return
        except asyncio.CancelledError:
            if claimed and attempt_id:
                try:
                    self.store.settle_attempt(attempt_id, cost_micro=0, uncertain=False, state="cancelled")
                except RuntimeFault:
                    pass
            raise
        except RuntimeFault as error:
            if claimed and attempt_id:
                try:
                    self.store.settle_attempt(attempt_id, cost_micro=0, uncertain=False, state="failed")
                except RuntimeFault:
                    pass
            try:
                current_job = self.store.get_job(job_id)
                if current_job["state"] not in {"cancelled", "paused"}:
                    blocked = error.code in {ErrorCode.POLICY_DENIED, ErrorCode.INVALID_INPUT, ErrorCode.VERSION_CONFLICT}
                    self.store.finalize_job(
                        job_id,
                        "blocked" if blocked else "failed",
                        "Local inspection could not complete safely.",
                        blocked_reason=error.message[:1024] if blocked else None,
                    )
            except RuntimeFault:
                pass
        except Exception:
            if claimed and attempt_id:
                try:
                    self.store.settle_attempt(attempt_id, cost_micro=0, uncertain=False, state="failed")
                except RuntimeFault:
                    pass
            try:
                current_job = self.store.get_job(job_id)
                if current_job["state"] not in {"cancelled", "paused"}:
                    self.store.finalize_job(job_id, "failed", "Local inspection failed safely.")
            except RuntimeFault:
                pass
        finally:
            for path in (
                self.config.workspaces_dir / f"inspection-{attempt_id}" if attempt_id else None,
                self.config.adapter_output_dir / f"b-{attempt_id}" if attempt_id else None,
                self.config.adapter_output_dir / f"d-{attempt_id}" if attempt_id else None,
            ):
                if path is not None:
                    try:
                        self._remove_tree(path)
                    except (OSError, RuntimeFault):
                        pass

    async def _progress(self, job_id: str, attempt_id: str, record: dict[str, Any]) -> None:
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
