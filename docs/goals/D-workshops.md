# D — independent verification and tested reuse

Own services/workshops/, demo/, tests/e2e/, journals/D.md and evidence/D/. Use Playwright Python plus standard unittest, not a second agent framework. Read only the current goal's sources. D must never trust a builder's self-reported success.

## D1 — trusted checks and evidence

/goal Complete D1 only. Read AGENTS.md, EXECUTION.md section 3, ARCHITECTURE.md section 6 and the check/artifact contracts.

Implement the specified checker components and a disposable club-site demo. Trusted expected destinations/check definitions live outside writable candidate snapshots. Browser contexts are isolated and origins constrained. Produce named results, red-before-green evidence, screenshot/log artifacts and exact candidate identity. No model call is needed for the normal regression.

- **D1-1**: Real browser journey fails on seeded bug and passes a known-good frozen control; report screenshot and exact candidate hashes.
- **D1-2**: Candidate changes to scripts/check definitions/expected destination cannot turn a bad candidate green; bad artifact hash or unsafe path is rejected.
- **D1-3**: Protocol tests cover error/timeout/partial output, isolated browser state and bounded artifacts; repeat deterministic checks with zero inference calls.

Run python3 -m unittest discover -s services/workshops/tests -p 'test_*.py' -v. Pin dependencies in the lane and record the Chromium installation/version.

## D2 — recipe proposal, tests and matching

/goal Complete D2 only. Read EXECUTION.md section 6 and workshop definitions in contracts/PROTOCOL.md and contracts/EXTENSIONS.md.

Implement recipes.py/scope.py and propose/test/match operations. Fixed manifest fields, canonical hash excluding its hash field, referenced executable hashes, allowlisted typed steps and no self-activation. Test original regression, two additional supported cases and one unsupported case. Reuse a proven plan, not unbounded generated shell or an entire new agent harness.

- **D2-1**: Schema/hash/version tests bind checks, actions, budget limits, source candidate and escalation; invalid or changed manifests fail validation.
- **D2-2**: Real deterministic/browser tests cover original plus two supported cases and unsupported abstention. Any failed/missing required case prevents ready status.
- **D2-3**: Match produces a scoped job proposal only; cannot execute, expand permissions, self-activate or silently replace an active version.

## D3 — complete acceptance rig

/goal Complete D3 only. Read FEATURE_MATRIX.md, docs/goals/I1-integration.md and all public contract shapes needed by the rig. Do not redesign runtime internals.

Create tests/e2e/run_acceptance.py with explicit --mode fixture|live and output directory. Fixture mode is for lane-independent rig tests; live mode fails missing real services/provider/Unity evidence rather than skipping. It drives actual HTTP commands and checks registered artifacts/digests. Map every AC-01..14, UI-01..05, MON-01..05 and COST-01..05 to executable assertions or specified native/portal evidence steps. Do not call a screenshot-only check backend verification.

- **D3-1**: Rig self-tests detect fake/live mislabeling, missing endpoint/evidence, stale artifact identity and skipped required assertions.
- **D3-2**: Complete acceptance map covers parallel work, main-computer viewing, exact approval, reuse, monitoring, zero-call idle and restart/duplicate failure cases.
- **D3-3**: All workshop/rig fixture tests pass and demo instructions list actual service/build commands; live full-product acceptance remains I1, not a claimed D3 result.
