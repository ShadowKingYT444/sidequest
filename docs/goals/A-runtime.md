# A — runtime, state and artifact service

Own services/runtime/, journals/A.md and evidence/A/. No Unity, tool-adapter, checker or shared-contract edits. Stack is fixed; use FastAPI/Uvicorn/Pydantic 2/stdlib SQLite, not another framework. Create the component files named in ARCHITECTURE.md. Unit tests use unittest (IsolatedAsyncioTestCase when needed) and HTTPX ASGITransport for HTTP; dependencies are lane-local and pinned once.

## A1 — persistent project/job/task state

/goal Complete A1 only. Read AGENTS.md, ARCHITECTURE.md sections 1–4, [STORAGE.md](../../contracts/STORAGE.md), and the object/command definitions in contracts/PROTOCOL.md and contracts/EXTENSIONS.md.

Implement config.py, models.py, store.py, policy.py and initial SQL migrations from STORAGE.md's table and transaction contract. Register approved project roots/revisions; persist jobs/tasks/attempts, events, candidate identity, approvals, command outcomes and budget reservations. Use UUIDs, integer micro-dollar accounting and null for unknown usage. SQLite has one serialized writer; claim/reserve/intent are transactional. Invalid scopes, cycles, stale revision and action-policy failures have typed errors. Implement the specified columns/indexes in the migration, not a second architecture proposal.

- **A1-1**: Storage tests cover initial migration, reload, source/task metadata and immutable candidate linkage.
- **A1-2**: Policy tests reject stale approval, differing-body duplicate command, denied action, missing project and exhausted reservation.
- **A1-3**: Concurrent claim/reservation tests cannot oversubscribe configured worker/budget limits; unknown usage stays unknown.

Run: python3 -m unittest discover -s services/runtime/tests -p 'test_*.py' -v. Save concise output/evidence and handoff; do not start A2.

## A2 — scheduler and complete computer API

/goal Complete A2 only. Read A1's code, ARCHITECTURE.md sections 4–5, contracts/EXTENSIONS.md, and COMPUTER_UI.md endpoint/paging requirements.

Implement api.py, scheduler.py, adapters.py and artifacts.py. Expose base and extension endpoints exactly, including project selection, task state, artifact manifest/text/diff/content and paginated runs. Implement fixed task pipeline, scope-aware ready queue, dependency order, cancellations and versioned layout. Tail validated bounded progress records. Use fake B/D subprocesses for this lane. Deterministically plan simple jobs; no implicit AI manager. Text/media reads are authenticated and path-safe, with no model calls.

- **A2-1**: HTTP tests exercise computer endpoints, paging, unauthorized scope, malformed cursor, binary content, traversal and hostile log text; fixtures match the shared example.
- **A2-2**: Scheduler tests show disjoint tasks overlap, dependent/overlapping tasks wait, malformed/timeout/duplicate adapter results fail safely, and cancelled work cannot schedule successors.
- **A2-3**: Interaction/idle tests count zero model dispatches for snapshots/file/diff viewing. Delivery is never triggered by a progress event or UI animation.

Run the complete runtime suite. Document main.py --help and service startup/config. Do not start A3 before independent review.

## A3 — recovery, approval, watchers and workshop activation

/goal Complete A3 only. Read ARCHITECTURE.md sections 6–7, EXECUTION.md sections 4–6 and the corresponding extension commands.

Persist approval identity and confirmed/ambiguous delivery state. Reconcile interrupted attempts rather than repeat external actions. Add workshop propose/test/activate/match/pause through D's protocol, watcher cursor de-duplication/coalescing and capability reporting. Verify required checks before activation/delivery. Resume always rechecks state, budget and permissions. A fake adapter can test all branches without importing B/D code.

- **A3-1**: Kill/restart tests retain state, block unknown deliveries and reject source/candidate changes; no duplicate write or automatic new paid attempt.
- **A3-2**: Workshop and watcher tests cover activation gates, new versions, duplicate event across restart, screen capability unavailable and system stop/resume.
- **A3-3**: Full runtime suite passes with real HTTP and fake subprocesses; every fake is labeled and startup/health/capabilities are documented.
