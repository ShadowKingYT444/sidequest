# Lane A journal

## A1 and A2 — runtime

Status: A1 passed fresh review at `5f1de2613e3f8f0840e670a34bd1d7d8c8158f35`; A2 implementation and validation are ready for coordinator review. SQLite persistence, policy, serialized claims and reservations, authenticated loopback API, host-owned startup configuration, B/D subprocess adapters, scheduler, immutable artifact import, and bounded artifact/status paging are implemented under `services/runtime/`.

The only runnable profile is `local_git_inspection`: a zero-budget, deterministic read-only Git snapshot and frozen-identity check using B and D. Capabilities explicitly report model verification and coding unavailable. Provider calls, delivery, workshops, capture, and Codex execution were not run or enabled.

Validation: `python3 -m services.runtime.main --help`, `python3 -m py_compile services/runtime/*.py`, and `python3 -m unittest discover -s services/runtime/tests -p 'test_*.py' -v` all passed; 21 tests passed. Coverage includes API auth and paging, cursor tampering, startup-token protections, concurrency and budget guards, plus fake-adapter and actual B/D pipelines against temporary Git fixtures. Python 3.12.14 was available; code targets 3.11+. No known A2 blocker. Evidence: `evidence/A/A1.json`, `evidence/A/A1-final-review.json`, and `evidence/A/A2.json`.
