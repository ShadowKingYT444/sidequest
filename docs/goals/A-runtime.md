# Lane A — Runtime and policy

Own only: `services/runtime/`, `journals/A.md`, `evidence/A/`. Read AGENTS.md and contracts/PROTOCOL.md. Three goals; finish and validate one before the next. Shared files are read-only.

## A1: Build durable job and policy state

/goal Complete A1 from docs/goals/A-runtime.md. Meet all A1 checks. Keep journals/A.md. Do not start the next goal.

Create SQLite job, event, approval, workshop and reservation storage with migrations and unit tests. No HTTP or other lane imports required.

Enforce state transitions, exact-artifact approvals, budget reservation, concurrency and global stop. Tests include duplicate request and invalid transition.

Acceptance evidence:

- **A1-1** — Run storage tests on an empty database and after restart; histories and revisions persist.
- **A1-2** — Negative tests reject changed artifact approval, denied action, exhausted budget and duplicate-body mismatch.
- **A1-3** — Concurrent reservations cannot oversubscribe configured capacity; journal lists commands and limitations.

## A2: Expose the contract and schedule isolated adapters

/goal Complete A2 from docs/goals/A-runtime.md. Meet all A2 checks. Keep journals/A.md. Do not start the next goal.

Implement HTTP endpoints and JSON-lines subprocess dispatcher from the frozen contract. Use fake B/D processes for independent tests.

Use bearer authentication, path-safe artifact serving, command IDs, dependency order, bounded retries and explicit cancellation. Document local configuration and --help.

Acceptance evidence:

- **A2-1** — HTTP tests cover snapshot, typed job, run, inspect evidence, approve and pause with exact shapes.
- **A2-2** — Fake-adapter tests cover malformed JSON, wrong ID, timeout, cancellation, digest mismatch and dependency ordering.
- **A2-3** — Unauthorized HTTP, path traversal and duplicate external-write requests cannot dispatch actions.

## A3: Make recovery and workshop activation reliable

/goal Complete A3 from docs/goals/A-runtime.md. Meet all A3 checks. Keep journals/A.md. Do not start the next goal.

Connect D operations through the contract, not imports. Persist package version, validation and activation state. Use fake D for lane tests.

Reconcile interrupted work on service restart. Do not repeat ambiguous external writes. Closing the presentation client must not affect service ownership.

Acceptance evidence:

- **A3-1** — Crash/restart tests preserve approved artifacts and stop ambiguous delivery; no duplicate write.
- **A3-2** — Workshop proposal, test, activation, match and pause are exercised with fake responses; untested version cannot activate.
- **A3-3** — Run all runtime tests and document exact start/config commands and actual dependency versions.
