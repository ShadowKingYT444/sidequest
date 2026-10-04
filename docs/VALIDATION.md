# Fresh validation contract

A builder's native goal can complete while the product requirement remains false. Treat that event as a request for review, not a release gate.

The controller commits only allowed paths. The validator works in a detached worktree at that exact SHA. It has no builder chat history. Its prompt identifies the goal, required checks, frozen specification, and candidate. It may inspect the committed journal as claims to verify; it must not use journal prose as proof.

Run the acceptance commands again, inspect artifacts, and try at least one relevant negative case. For C, open actual rendered screenshots and exercise the built interface or the editor at the validation path. For I1, use real subprocesses rather than the mock HTTP server. Verify that mock mode is visibly identified and no success derives only from a scripted event playback.

Write `.sidequest/verdict.json`:

```json
{
  "verdict": "PASS",
  "candidate": "exact 40-character commit SHA",
  "goal": "A1",
  "checks": [
    {"id": "A1-1", "result": "PASS", "evidence": "exact command and result, plus artifact path"}
  ],
  "findings": []
}
```

Every required check ID must occur exactly once. Values are PASS, FAIL, or BLOCKED. PASS requires all check results to be PASS, a matching candidate, no findings, and no tracked or unignored source changes by the reviewer. A report without an executed check is invalid. A file path alone is not execution evidence; state the command and result.

FAIL means a requirement was tested and failed. BLOCKED means a necessary check could not be performed. Missing credentials, Unity editor access, actual screenshots, or a browser never become PASS. Stop for credentials or environment repair; do not silently substitute a fake service.

Reviewers may run tests that create ignored caches, build outputs, and `.sidequest/` evidence. They must not change tracked tests or code. Add exploratory tests under `.sidequest/` when necessary. The controller copies the verdict out before proceeding. A new candidate requires new validation. It cannot reuse an older PASS, even for a small edit.

Component PASS does not mean the whole application is accepted. I1 verifies the complete product and the exact merged commit. There is no automatic push to main in the development loop.

## Evidence policy

Record commit, tool versions, commands, exit results, and paths. For visual evidence include resolution, scene name, camera pose, selected job, and mock/live mode. Capture only the fixture application, never unrelated desktop windows. Report frame timing as a measured sample with hardware, not a universal performance claim.

Model-based review is fallible. Host checks enforce structure, ownership, report completeness, and commit identity; they cannot prove a screenshot is attractive or a reviewer interpreted every test correctly. Owner review and the executable final scenario remain important.
