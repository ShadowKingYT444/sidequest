# Lane A journal

## A1 — persistent project/job/task state

Status: ready for coordinator review after validator repair; no known blockers. Implemented the fixed SQLite migration, XDG config, Pydantic models, policy checks, serialized transactional store, Git-backed project revisions, command replay, candidate/approval identity, and atomic task claims/reservations. Build/research claims require positive budget, per-call capacity cannot exceed config, approval decisions refresh Git identity, and candidate links are NULL-safe immutable. Runtime/API work beyond A1 remains unstarted.

Changed paths: `services/runtime/` and `journals/A.md`; detailed evidence is in `evidence/A/A1.json`.

Validation: `python3 -m unittest discover -s services/runtime/tests -p 'test_*.py' -v` — 13 passed, 0 failed, including regression tests for all four validator findings. Tests use temporary Git repositories and SQLite databases. Python 3.12.14 was available; source targets Python 3.11 compatibility. No product jobs or model/provider calls were run.

Next action: coordinator fresh review of the A1 candidate before integration work.
