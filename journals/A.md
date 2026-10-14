# Lane A journal

## A1 — persistent project/job/task state

Status: ready for coordinator review; no known blockers. Implemented the fixed SQLite migration, XDG config, Pydantic models, policy checks, serialized transactional store, project root/revision registration through local Git, command replay, candidate/approval identity, task claims, reservations and unknown usage handling. Runtime/API work beyond A1 remains unstarted.

Changed paths: `services/runtime/` and `journals/A.md`; detailed evidence is in `evidence/A/A1.json`.

Validation: `python3 -m unittest discover -s services/runtime/tests -p 'test_*.py' -v` — 10 passed, 0 failed. Tests use temporary Git repositories and SQLite databases. Python 3.12.14 was available; source targets Python 3.11 compatibility. No product jobs or model/provider calls were run.

Next action: coordinator fresh review of the A1 candidate before integration work.
