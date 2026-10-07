# Candidate validation

A completed native goal requests review. It does not prove the feature works. The controller freezes the candidate SHA and starts a new validator in a detached worktree. Read AGENTS.md, the active goal and its Read list, then inspect/run the named checks. Do not load the entire builder conversation or research archive. Journal claims are leads, not evidence.

Required report at .sidequest/verdict.json:

```json
{
  "goal": "A1",
  "candidate": "exact candidate commit SHA",
  "verdict": "PASS",
  "checks": [{"id":"A1-1","result":"PASS","evidence":"Executed command, exit result, artifact path"}],
  "findings": []
}
```

Include every required check ID exactly once. Result/verdict values are PASS, FAIL or BLOCKED. PASS requires all checks pass, no unresolved findings, exact goal/SHA and no tracked or unignored reviewer source changes. Actual report must contain all three checks for a component goal; the example shows one only to illustrate shape.

Run cheap deterministic checks first. Reviewer reruns relevant tests and at least one negative case rather than relying on builder screenshots/log prose. UI review requires actual rendered Unity evidence at both specified resolutions and interaction with the computer. A screenshot of a drawing cannot pass it. Native file/diff/image viewing is required; a link that opens GitHub alone fails.

A missing asset, local model, credential, display, Unity license or observed result means BLOCKED. Report exactly what is unavailable. Do not mark it passed because source code looks plausible. Test doubles validate the component contract only; I1 must use real services, real coding-provider output and a built Unity client. A local demo repository is allowed and must be labeled as a fixture target.

Reviewers do not repair production code or edit tests. Generated logs, experimental check scripts and outputs go under .sidequest/ or existing ignored build directories. No credentials/private desktop captures in evidence. Record versions, commands, exit results, candidate identity and screenshot resolutions. Never publish private chain-of-thought.

Model review remains fallible; report shape checks do not prove correctness. Deterministic tests and final integrated execution are separate gates. The controller stops after the configured attempts. An operator must resolve a BLOCKED environment before re-running; do not spend tokens repeatedly asking models to overcome unavailable tools.
