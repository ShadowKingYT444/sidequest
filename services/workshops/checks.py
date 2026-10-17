"""Trusted D1 checks. Candidate-supplied checks and destinations are never loaded."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from . import browser_checks
from .config import MAX_REPORT_BYTES, TRUSTED_CHECKS_PATH, TRUST_LOCK_PATH
from .identity import (
    IdentityError,
    assigned_directory,
    verify_artifact_manifest,
    verify_candidate_tree,
    verify_host_artifact_inputs,
)
from .reports import build_report, canonical_json, create_run_directory, write_artifact

_SAFE_REVISION = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
_SAFE_TRUSTED_FILES = {
    "__init__.py",
    "browser_checks.py",
    "checks.py",
    "config.py",
    "identity.py",
    "main.py",
    "reports.py",
    "requirements.lock",
    "trusted_checks.json",
}


class CheckError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def verify_trusted_integrity(package_dir: Path | None = None) -> None:
    directory = package_dir or Path(__file__).parent
    lock_path = directory / "trust.lock.json"
    try:
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CheckError("TRUSTED_HARNESS_INVALID", "Trusted check integrity metadata is unavailable.") from exc
    if not isinstance(lock, dict) or lock.get("v") != 1 or not isinstance(lock.get("files"), dict):
        raise CheckError("TRUSTED_HARNESS_INVALID", "Trusted check integrity metadata is invalid.")
    hashes = lock["files"]
    if set(hashes) != _SAFE_TRUSTED_FILES:
        raise CheckError("TRUSTED_HARNESS_INVALID", "Trusted check integrity file set is invalid.")
    for name, expected in hashes.items():
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
            raise CheckError("TRUSTED_HARNESS_INVALID", "Trusted check integrity digest is invalid.")
        path = directory / name
        try:
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError as exc:
            raise CheckError("TRUSTED_HARNESS_INVALID", "A trusted check component is unavailable.") from exc
        if actual != expected:
            raise CheckError("TRUSTED_HARNESS_CHANGED", "A trusted check component changed after its integrity lock was created.")


def load_trusted_checks(package_dir: Path | None = None) -> dict[str, dict[str, Any]]:
    directory = package_dir or Path(__file__).parent
    try:
        raw = json.loads((directory / TRUSTED_CHECKS_PATH.name).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CheckError("TRUSTED_CHECKS_INVALID", "Trusted check definitions are unavailable.") from exc
    if not isinstance(raw, dict) or raw.get("v") != 1 or not isinstance(raw.get("checks"), list):
        raise CheckError("TRUSTED_CHECKS_INVALID", "Trusted check definitions have an invalid shape.")
    checks: dict[str, dict[str, Any]] = {}
    for definition in raw["checks"]:
        if not isinstance(definition, dict):
            raise CheckError("TRUSTED_CHECKS_INVALID", "Trusted check definition is invalid.")
        check_id = definition.get("id")
        kind = definition.get("kind")
        if not isinstance(check_id, str) or not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,100}", check_id):
            raise CheckError("TRUSTED_CHECKS_INVALID", "Trusted check identifier is invalid.")
        if check_id in checks or kind not in {"browser_signup", "candidate_identity"}:
            raise CheckError("TRUSTED_CHECKS_INVALID", "Trusted check definition is duplicated or unsupported.")
        if kind == "browser_signup":
            if (
                definition.get("entry_path") != "/"
                or not isinstance(definition.get("expected_path"), str)
                or not definition["expected_path"].startswith("/")
                or ".." in definition["expected_path"].split("/")
                or not isinstance(definition.get("link_name"), str)
                or not isinstance(definition.get("success_selector"), str)
                or not isinstance(definition.get("success_text"), str)
            ):
                raise CheckError("TRUSTED_CHECKS_INVALID", "Trusted browser destination is invalid.")
        checks[check_id] = definition
    return checks


def _is_contained(parent: Path, child: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def run_checks(request: dict[str, Any]) -> dict[str, Any]:
    """Run named checks against only host-assigned, frozen candidate inputs."""
    verify_trusted_integrity()
    request_id = request.get("request_id")
    payload = request.get("payload")
    context = request.get("context")
    if not isinstance(payload, dict) or not isinstance(context, dict):
        raise CheckError("INVALID_INPUT", "Check request payload or host context is missing.")
    check_ids = payload.get("check_ids")
    source_revision = payload.get("source_revision")
    context_revision = context.get("source_revision")
    if (
        not isinstance(check_ids, list)
        or not check_ids
        or len(check_ids) > 20
        or any(not isinstance(check_id, str) for check_id in check_ids)
        or len(set(check_ids)) != len(check_ids)
    ):
        raise CheckError("INVALID_INPUT", "Check identifiers are missing, duplicated, or invalid.")
    if not isinstance(source_revision, str) or not _SAFE_REVISION.fullmatch(source_revision):
        raise CheckError("INVALID_INPUT", "A valid source revision is required.")
    if context_revision is not None and context_revision != source_revision:
        raise CheckError("INVALID_INPUT", "Payload and host context source revisions do not match.")

    definitions = load_trusted_checks()
    if any(check_id not in definitions for check_id in check_ids):
        raise CheckError("INVALID_INPUT", "A requested check is not in the trusted check registry.")

    try:
        candidate_root = assigned_directory(request.get("workspace"), name="candidate workspace")
        output_root = assigned_directory(context.get("output_root"), name="output root")
        if _is_contained(candidate_root, output_root) or _is_contained(output_root, candidate_root):
            raise IdentityError("Candidate and output roots must be separate.")
        verified_inputs = verify_host_artifact_inputs(context.get("artifact_inputs"))
        candidate, manifest_files, manifest_artifact = verify_artifact_manifest(verified_inputs)
        candidate_revision = candidate.get("candidate_revision")
        if candidate_revision is not None and candidate_revision != source_revision:
            raise IdentityError("Candidate revision does not match the assigned source revision.")
        tree_hash, _ = verify_candidate_tree(candidate_root, manifest_files, require_read_only=True)
        if tree_hash != candidate.get("tree_sha256"):
            raise IdentityError("Candidate workspace does not match the manifest tree digest.")
    except IdentityError as exc:
        raise CheckError("INVALID_CANDIDATE", str(exc)) from exc

    try:
        run_dir = create_run_directory(output_root, request_id)
    except (OSError, ValueError) as exc:
        raise CheckError("OUTPUT_FAILED", "Host-assigned output directory could not be prepared.") from exc

    results: list[dict[str, Any]] = []
    artifacts: list[dict[str, Any]] = []
    browser_version: str | None = None
    registered_origin: str | None = None
    for check_id in check_ids:
        definition = definitions[check_id]
        if definition["kind"] == "candidate_identity":
            results.append({
                "id": check_id,
                "state": "pass",
                "evidence_artifact_id": manifest_artifact["id"],
                "message": "The read-only candidate matches its host-staged file manifest.",
            })
            continue

        journey = browser_checks.run_browser_journey(candidate_root, definition)
        browser_version = journey.browser_version
        registered_origin = journey.origin or None
        named_files: list[tuple[str, bytes, str, str]] = []
        if journey.before_png is not None:
            named_files.append(("before.png", journey.before_png, "screenshot", "image/png"))
        if journey.after_png is not None:
            named_files.append(("after.png", journey.after_png, "screenshot", "image/png"))
        log_bytes = browser_checks.serialize_log(journey.log)
        named_files.append(("browser.log.json", log_bytes, "log", "application/json"))
        for name, data, kind, media_type in named_files:
            artifacts.append(write_artifact(run_dir, name, data, kind=kind, media_type=media_type))
        evidence_id = next(
            (item["id"] for item in artifacts if item["relative_path"].endswith("after.png")),
            next((item["id"] for item in artifacts if item["relative_path"].endswith("browser.log.json")), None),
        )
        results.append({
            "id": check_id,
            "state": journey.state,
            "evidence_artifact_id": evidence_id,
            "message": journey.message,
            "code": journey.code,
        })

    try:
        after_hash, _ = verify_candidate_tree(candidate_root, manifest_files, require_read_only=True)
    except IdentityError as exc:
        after_hash = ""
        identity_error = str(exc)
    else:
        identity_error = ""
    if after_hash != tree_hash:
        for result in results:
            result["state"] = "blocked"
            result["code"] = "CANDIDATE_CHANGED"
            result["message"] = "The frozen candidate identity changed during verification."
        if identity_error:
            results.append({
                "id": "candidate.frozen_identity",
                "state": "blocked",
                "evidence_artifact_id": manifest_artifact["id"],
                "message": "The frozen candidate identity changed during verification.",
                "code": "CANDIDATE_CHANGED",
            })

    identity_requested = "candidate.frozen_identity" in check_ids
    if identity_requested and after_hash == tree_hash:
        # Keep the identity assertion adjacent to the actual browser result in output.
        pass

    report = build_report(
        request_id=request_id,
        source_revision=source_revision,
        candidate_id=candidate["id"],
        tree_sha256=tree_hash,
        manifest_artifact_id=manifest_artifact["id"],
        results=results,
        browser_version=browser_version,
        origin=registered_origin,
        inference_calls=0,
    )
    report_bytes = canonical_json(report)
    if len(report_bytes) > MAX_REPORT_BYTES:
        raise CheckError("OUTPUT_FAILED", "Check report exceeds the size limit.")
    artifacts.append(write_artifact(
        run_dir,
        "check-report.json",
        report_bytes,
        kind="test_report",
        media_type="application/json",
    ))
    passed = all(result["state"] == "pass" for result in results) and bool(results)
    return {
        "passed": passed,
        "results": results,
        "candidate": {
            "id": candidate["id"],
            "tree_sha256": tree_hash,
            "source_revision": source_revision,
        },
        "artifacts": artifacts,
        "inference_calls": 0,
    }
