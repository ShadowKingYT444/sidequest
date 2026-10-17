#!/usr/bin/env python3
"""Run the disposable D1 red/green browser journey and archive verified evidence."""

from __future__ import annotations

import datetime as dt
import hashlib
import importlib.metadata
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "evidence/D"
INPUTS = EVIDENCE / "inputs"
OUTPUTS = EVIDENCE / "outputs"
FIXTURES = ROOT / "demo/club-site"
CHECK_IDS = ["candidate.frozen_identity", "club.signup.popup_destination"]
RUN_ID = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dt%H%M%S%fZ").lower()


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def copy_frozen_fixture(source: Path, destination: Path) -> Path:
    if source.is_symlink() or not source.is_dir():
        raise RuntimeError(f"D1 fixture source is not a regular directory: {source}")
    shutil.copytree(source, destination, symlinks=True, copy_function=shutil.copy2)
    for path in sorted(destination.rglob("*"), reverse=True):
        if path.is_symlink():
            raise RuntimeError("D1 fixture unexpectedly contains a symlink")
        info = path.stat(follow_symlinks=False)
        if stat.S_ISDIR(info.st_mode):
            mode = stat.S_IMODE(info.st_mode) & ~0o222
        elif stat.S_ISREG(info.st_mode):
            mode = stat.S_IMODE(info.st_mode) & ~0o222
        else:
            raise RuntimeError("D1 fixture contains a special file")
        path.chmod(mode)
    destination.chmod(stat.S_IMODE(destination.stat().st_mode) & ~0o222)
    return destination


def build_manifest(root: Path, name: str) -> tuple[dict[str, Any], str]:
    records: list[dict[str, Any]] = []
    entries: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise RuntimeError("D1 fixture unexpectedly contains a symlink")
        if path.is_dir():
            continue
        if not path.is_file():
            raise RuntimeError("D1 fixture contains a special file")
        info = path.stat()
        if info.st_mode & 0o222:
            raise RuntimeError("D1 fixture must be frozen read-only before verification")
        content = path.read_bytes()
        rel = path.relative_to(root).as_posix()
        mode = "100755" if info.st_mode & 0o111 else "100644"
        record = {
            "path": rel,
            "mode": mode,
            "size_bytes": len(content),
            "sha256": sha256(content),
        }
        records.append(record)
        entries.append({**record, "status": "unchanged"})
    records.sort(key=lambda row: row["path"])
    tree_sha256 = sha256(canonical({"v": 1, "files": records}))
    candidate_id = f"d1-{name}-{tree_sha256[:12]}"
    source_revision = f"fixture:d1-{name}"
    manifest = {
        "v": 1,
        "candidate": {
            "id": candidate_id,
            "base_revision": "fixture:d1-base",
            "candidate_revision": source_revision,
            "tree_sha256": tree_sha256,
        },
        "files": entries,
    }
    return manifest, source_revision


def run_adapter(name: str, fixture: Path) -> dict[str, Any]:
    manifest, source_revision = build_manifest(fixture, name)
    candidate_id = manifest["candidate"]["id"]
    manifest_path = INPUTS / f"{name}-manifest-{RUN_ID}.json"
    if manifest_path.exists():
        raise RuntimeError(f"Refusing to replace existing evidence input {manifest_path.name}")
    manifest_bytes = canonical(manifest)
    manifest_path.write_bytes(manifest_bytes)
    manifest_path.chmod(0o444)
    manifest_sha256 = sha256(manifest_bytes)
    output_root = OUTPUTS
    request_id = f"d1-{name}-{RUN_ID}-{manifest_sha256[:8]}"
    request = {
        "v": 1,
        "request_id": request_id,
        "op": "check.run",
        "job_id": f"d1-fixture-{name}",
        "workspace": str(fixture),
        "payload": {"check_ids": CHECK_IDS, "source_revision": source_revision},
        "context": {
            "source_revision": source_revision,
            "artifact_inputs": [{
                "id": f"manifest:{candidate_id}",
                "sha256": manifest_sha256,
                "staged_path": str(manifest_path),
            }],
            "output_root": str(output_root),
        },
    }
    command = [sys.executable, "-m", "services.workshops.main"]
    completed = subprocess.run(
        command,
        input=canonical(request) + b"\n",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=ROOT,
        timeout=40,
        check=False,
    )
    if completed.returncode != 0 or completed.stdout.count(b"\n") != 1:
        raise RuntimeError("Workshop adapter did not return exactly one response line")
    response = json.loads(completed.stdout.decode("utf-8"))
    if not response.get("ok") or response.get("request_id") != request_id:
        raise RuntimeError("Workshop adapter rejected the host-assigned D1 fixture request")
    artifact_records = []
    for artifact in response.get("artifacts", []):
        relative = Path(artifact["relative_path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise RuntimeError("Workshop adapter returned an unsafe evidence path")
        output_path = output_root / relative
        resolved = output_path.resolve(strict=True)
        resolved.relative_to(output_root.resolve(strict=True))
        content = resolved.read_bytes()
        actual = sha256(content)
        if actual != artifact.get("sha256"):
            raise RuntimeError("Workshop evidence artifact digest did not verify")
        artifact_records.append({
            "kind": artifact["kind"],
            "relative_path": relative.as_posix(),
            "sha256": actual,
            "size_bytes": len(content),
        })
    report = next((OUTPUTS / row["relative_path"] for row in artifact_records if row["relative_path"].endswith("check-report.json")), None)
    browser_report = json.loads(report.read_text(encoding="utf-8")) if report else {}
    return {
        "fixture": name,
        "command": command,
        "request_id": request_id,
        "source_revision": source_revision,
        "candidate_id": candidate_id,
        "candidate_tree_sha256": response["data"]["candidate"]["tree_sha256"],
        "manifest_sha256": manifest_sha256,
        "results": response["data"]["results"],
        "passed": response["data"]["passed"],
        "inference_calls": response["data"]["inference_calls"],
        "browser_version": browser_report.get("browser", {}).get("version"),
        "registered_origin": browser_report.get("browser", {}).get("registered_origin"),
        "artifacts": artifact_records,
        "stderr_bytes_discarded": len(completed.stderr),
    }


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    INPUTS.mkdir(mode=0o700, exist_ok=True)
    OUTPUTS.mkdir(mode=0o700, exist_ok=True)
    cases: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="sidequest-d1-fixtures-") as temp_root:
        temp_path = Path(temp_root)
        bad_fixture = copy_frozen_fixture(FIXTURES / "bad", temp_path / "bad")
        known_good_fixture = copy_frozen_fixture(FIXTURES / "known-good", temp_path / "known-good")
        cases.append(run_adapter("bad", bad_fixture))
        cases.append(run_adapter("known-good", known_good_fixture))

    expected = {
        "bad": (False, "SIGNUP_DESTINATION_MISMATCH"),
        "known-good": (True, "SIGNUP_JOURNEY_PASSED"),
    }
    for case in cases:
        passed, browser_code = expected[case["fixture"]]
        if case["passed"] != passed:
            raise RuntimeError(f"Unexpected overall result for disposable {case['fixture']} fixture")
        browser_result = next((row for row in case["results"] if row["id"] == "club.signup.popup_destination"), None)
        if not browser_result or browser_result.get("code") != browser_code:
            raise RuntimeError(f"Unexpected named browser result for disposable {case['fixture']} fixture")

    test_command = [
        "python3", "-m", "unittest", "discover", "-s", "services/workshops/tests",
        "-p", "test_*.py", "-v",
    ]
    tests = subprocess.run(test_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=ROOT, timeout=240, check=False)
    test_log = tests.stdout[:1024 * 1024]
    test_log_path = EVIDENCE / f"unittest-{RUN_ID}.log"
    test_log_path.write_bytes(test_log)
    test_record = {
        "command": test_command,
        "exit_code": tests.returncode,
        "log_path": test_log_path.relative_to(ROOT).as_posix(),
        "log_sha256": sha256(test_log),
        "log_size_bytes": len(test_log),
        "log_truncated": len(tests.stdout) > len(test_log),
    }
    evidence = {
        "goal": "D1",
        "recorded_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "scope": "trusted deterministic browser checks against disposable local fixtures",
        "environment": {
            "python": sys.version.split()[0],
            "playwright": importlib.metadata.version("playwright"),
            "chromium_path": os.environ.get("CHROMIUM_PATH", "/usr/bin/chromium"),
            "chromium_version": cases[1]["browser_version"],
            "dependencies": "services/workshops/requirements.lock",
        },
        "adapter_command": [sys.executable, "-m", "services.workshops.main"],
        "cases": cases,
        "unittest": test_record,
        "inference_calls": 0,
        "production_actions": 0,
        "live_agent_claims": 0,
    }
    primary_report = EVIDENCE / "D1.json"
    if primary_report.exists():
        previous_report = EVIDENCE / f"D1-previous-{RUN_ID}.json"
        shutil.copy2(primary_report, previous_report)
    primary_report.write_bytes(canonical(evidence) + b"\n")
    print(json.dumps({
        "bad_passed": cases[0]["passed"],
        "known_good_passed": cases[1]["passed"],
        "unittest_exit_code": tests.returncode,
        "evidence": "evidence/D/D1.json",
    }, sort_keys=True))
    return 0 if tests.returncode == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
