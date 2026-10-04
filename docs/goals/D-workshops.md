# Lane D — Verification and workshop reuse

Own only: `services/workshops/`, `demo/`, `tests/e2e/`, `journals/D.md`, `evidence/D/`. Read AGENTS.md and contracts/PROTOCOL.md. Three goals; finish and validate one before the next. Shared files are read-only.

## D1: Create trustworthy acceptance checks and a demo target

/goal Complete D1 from docs/goals/D-workshops.md. Meet all D1 checks. Keep journals/D.md. Do not start the next goal.

Build a disposable club signup site fixture with trusted expected destinations outside the writable repair tree. Create red/green browser journey checks and evidence artifacts.

Implement check.run JSON-lines operation. Include wrong-path, missing-href and unsupported-destination cases. Never trust an agent saying tests passed.

Acceptance evidence:

- **D1-1** — Actual browser test fails on seeded bug, passes on known-good control, and records screenshot plus results.
- **D1-2** — Candidate attempts to replace a check or change the trusted expected destination cannot make it pass.
- **D1-3** — Protocol tests cover check result IDs, failure details, artifact digests and malformed request.

## D2: Package and gate reusable workshops

/goal Complete D2 from docs/goals/D-workshops.md. Meet all D2 checks. Keep journals/D.md. Do not start the next goal.

Implement propose, test and match operations. A package contains supported scope, trigger, code/instructions, checks, limits and escalation. No self-activation.

Run original regression, two additional supported examples and at least one unsupported input. Scope changes create a new version.

Acceptance evidence:

- **D2-1** — Package validates all required fields, pins check IDs and records a reproducible digest/version.
- **D2-2** — Actual checker passes supported cases and stops/asks on unsupported case; a failed or missing case prevents ready status.
- **D2-3** — Match tests never execute actions, grant permissions or silently broaden scope.

## D3: Prepare the final integration acceptance rig

/goal Complete D3 from docs/goals/D-workshops.md. Meet all D3 checks. Keep journals/D.md. Do not start the next goal.

Write a reusable end-to-end rig and demo instructions that substitute real A/B services after merge. While this lane is isolated, test the rig with clearly labeled fakes.

Cover the entire SPEC acceptance table, including service restart, duplicate lookout, stale approval and second failure handled without a new planning conversation. Do not claim full product validation before I1.

Acceptance evidence:

- **D3-1** — Rig tests distinguish fixture runs from real-service runs and fail missing services rather than skip.
- **D3-2** — Every SPEC AC-01..AC-14 maps to a named integration assertion/evidence step, including negative cases.
- **D3-3** — Demo instructions and all workshop tests run locally; actual end-to-end product run remains assigned to I1.
