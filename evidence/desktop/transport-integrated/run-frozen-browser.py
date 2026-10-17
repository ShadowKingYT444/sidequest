"""One full zero-retry browser run; keep exact source, log and capture evidence."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import sys

root = Path(__file__).resolve().parents[3]
evidence = Path(__file__).resolve().parent
def git(*args):
    return subprocess.check_output(["git", *args], cwd=root).decode().strip()
def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
paths = [p for p in git("ls-files", "-z").split("\0") if p and not p.startswith("evidence/")]
before = {p: digest(root / p) for p in paths}
env_values = {
    "SIDEQUEST_REPO": "/tmp/sidequest-eval-source",
    "SIDEQUEST_BASE": "69bf066",
    "SIDEQUEST_RUNTIME_URL": "http://127.0.0.1:4317",
    "SIDEQUEST_API_TOKEN_FILE": "/tmp/sidequest-eval-config-2/session.token",
    "SIDEQUEST_TEST_INSPECTION": "1",
    "SIDEQUEST_EVIDENCE_RUN": "transport-full-timings",
    "CHROMIUM_PATH": "/usr/bin/chromium",
    "CI": "1",
}
command = ["npm", "run", "test:browser", "--", "--retries=0"]
record = {
    "startedAt": now(), "sourceCommit": git("rev-parse", "HEAD"),
    "sourceFileCount": len(paths), "sourceHashesBefore": before,
    "command": command, "environment": env_values, "expectedTests": 23,
    "retries": 0, "nativeAttempts": 0, "codingModelAttempts": 0, "protocolFakeComposerTests": 3,
    "inspectedProject": subprocess.check_output(["git", "-C", env_values["SIDEQUEST_REPO"], "rev-parse", "HEAD"]).decode().strip(),
}
record_path = evidence / "full-run.json"
record_path.write_text(json.dumps(record, indent=2) + "\n")
print(f"Frozen {len(paths)} files at {record['sourceCommit']}; 23 tests, retries 0.", flush=True)
with (evidence / "full-browser.log").open("w") as log:
    result = subprocess.run(command, cwd=root / "desktop", env={**os.environ, **env_values}, stdout=log, stderr=subprocess.STDOUT)
after = {p: digest(root / p) if (root / p).is_file() else None for p in paths}
record.update(endedAt=now(), exitCode=result.returncode, sourceHashesAfter=after,
              sourceUnchanged=before == after, logSha256=digest(evidence / "full-browser.log"))
# Restore previous published evidence only after preserving every new capture.
captures = [p for p in git("diff", "--name-only", "-z", "--", "evidence/desktop").split("\0") if p and not p.startswith(str(evidence.relative_to(root)))]
for p in captures:
    destination = evidence / "full-captures" / Path(p).relative_to("evidence/desktop")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(root / p, destination)
if captures:
    subprocess.run(["git", "restore", "--", *captures], cwd=root, check=True)
if (root / "desktop/test-results").is_dir():
    shutil.copytree(root / "desktop/test-results", evidence / "full-test-results", dirs_exist_ok=True)
record["preservedCaptures"] = captures
record_path.write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps({k: record[k] for k in ["exitCode", "sourceCommit", "sourceFileCount", "sourceUnchanged", "logSha256"]}), flush=True)
sys.exit(result.returncode or (0 if record["sourceUnchanged"] else 1))
