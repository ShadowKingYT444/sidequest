# Lane A journal

## Runtime status

A1 passed fresh review at `5f1de2613e3f8f0840e670a34bd1d7d8c8158f35`. A2's repaired inspection API passed fresh review at `5c628b522a77817ee34b589f5896df4d2cc0f23d`. The authenticated local runtime retains its deterministic zero-budget Git inspection path and adds an optional host-gated Codex session lifecycle under `services/runtime/`.

The new `system.codex.refresh` command is the only runtime readiness probe; status reads make no provider calls. Codex jobs require cached verified readiness, host consent, a canonical stored profile, current source identity, and positive budget reservation. Provider session IDs are persisted privately, interruptions become ambiguous, and explicit resume uses the same attempt/thread. Unknown USD cost stays null and the reservation remains held. The complete pipeline test uses fake adapters only.

Validation passed: runtime suite (36 tests), B/tools suite (39 tests), runtime compile, `python3 -m services.runtime.main --help`, and `git diff --check`. Fake cancellation tests confirm pause leaves an uncertain, resumable attempt without automatic retry. No live capability probe or provider turn ran. Native app-server readiness remains blocked before initialize because the host Codex state is read-only; model/account verification remains unavailable. The app-server does not enforce a verified USD spend ceiling. Evidence: `evidence/A/A1.json`, `evidence/A/A1-final-review.json`, `evidence/A/A2.json`, `evidence/A/A2-repair-review.json`, and `evidence/A/A3.json`.
