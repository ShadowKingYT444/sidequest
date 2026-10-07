# SQLite storage contract — A1

Use this table/field layout for the initial migration. It completes the high-level table summary in ARCHITECTURE.md. This is an implementation specification, not an installed database. Python sqlite3, WAL mode, foreign_keys=ON, busy_timeout=5000, one serialized writer. Never wait for an adapter/model inside a transaction. IDs are TEXT UUID unless stated; times are TEXT UTC ISO8601. JSON fields contain canonical JSON validated at the API boundary. Money uses INTEGER micro-dollars; unknown usage is NULL.

| Table | Columns and constraints |
|---|---|
| projects | id PK, name, canonical_root UNIQUE, base_ref, base_revision, policy_json, status, created_at |
| jobs | id PK, project_id FK, title, source_json, outcome, state, checks_json, allowed_actions_json, budget_micro, spent_micro NULL, workflow_version, candidate_id NULL, blocked_reason NULL, created_at, updated_at |
| tasks | id PK, job_id FK, kind, objective, depends_on_json, write_paths_json, check_ids_json, state, worker_id NULL FK, current_attempt_id NULL, sort_order |
| workers | id PK, role, state, current_task_id NULL, configuration_json |
| attempts | id PK, task_id FK, number, state, base_revision, provider_thread_id NULL, provider_turn_id NULL, model NULL, effort NULL, started_at, ended_at NULL, input_tokens NULL, cached_input_tokens NULL, output_tokens NULL, total_tokens NULL, cost_micro NULL, usage_uncertain INTEGER; UNIQUE(task_id,number) |
| candidates | id PK, job_id FK, run_id FK attempts, base_revision, candidate_revision, tree_sha256, patch_sha256, manifest_artifact_id, created_at |
| events | id INTEGER PRIMARY KEY AUTOINCREMENT, job_id FK, run_id NULL FK attempts, run_seq NULL, at, type, message, artifact_id NULL; UNIQUE(run_id,run_seq) for non-null run IDs |
| artifacts | id PK, job_id FK, run_id NULL FK attempts, candidate_id NULL, kind, media_type, display_name, sha256, size_bytes, storage_key, immutable INTEGER, created_at |
| approvals | id PK, job_id FK, candidate_id FK, source_revision, tree_sha256, patch_sha256, action, destination, state, decision_at NULL; identity is immutable |
| deliveries | id PK, approval_id FK, request_sha256, state, external_receipt NULL, started_at, reconciled_at NULL; one action ID per requested delivery |
| workshops | id, version INTEGER, name, package_artifact_id FK, package_sha256, state, validation_json, activation_json NULL; PRIMARY KEY(id,version) |
| watcher_cursors | watcher_id PK, project_id FK, config_json, cursor_json, state, last_event_at NULL |
| watcher_events | watcher_id FK, event_id, job_id NULL FK, payload_sha256, observed_at; PRIMARY KEY(watcher_id,event_id) |
| budget_reservations | id PK, attempt_id FK UNIQUE, reserved_micro, settled_micro NULL, state, created_at |
| command_results | command_id PK, request_sha256, type, accepted_revision, response_json, created_at |
| settings | key PK, value_json; global revision, stop flag, selected project and capacities |
| schema_migrations | version INTEGER PK, applied_at |

Public run_id maps to attempts.id; do not create duplicate accounting. A worker-visible task has kind build or research. The scheduler creates internal integration and verify tasks as needed; they do not count against the maximum four user-supplied tasks. An integration attempt normally has model/effort NULL and no inference charge. This explicitly links a combined candidate to the job without pretending it belongs to the last parallel worker. A repair is a separately authorized bounded build attempt.

Job outcome defaults to the typed source text or issue body supplied by the user; checks define executable completion. Do not make a model call solely to populate this field. Optional outcome text may be provided by the client as an additive job.create field. All candidate-artifact links are validated in the same completion transaction; nullable cross-links are filled before a candidate becomes visible for approval.

Indexes: jobs(project_id,state,created_at), tasks(job_id,state,sort_order), attempts(task_id,state), events(run_id,run_seq), artifacts(job_id,candidate_id), approvals(job_id,state), workshops(state). Content-addressed bytes may be shared, but artifact rows retain ownership. Knowing a hash never authorizes another project's artifact. Watcher configuration stores endpoint references, not embedded credentials.

## Atomic transitions

Command: BEGIN IMMEDIATE → check command_id/hash → validate revision/policy → mutate state → increment revision → store response → COMMIT. An identical duplicate returns its original response even after the global revision moves. A duplicate with a different body returns conflict.

Dispatch: BEGIN IMMEDIATE → check ready dependencies, scope locks, stop and capacity → reserve budget → create attempt/dispatch event → mark task running → COMMIT → spawn. Spawn failure releases ownership/reservation in a new transaction. Checking capacity without claiming it transactionally is invalid.

Result: stage/hash-check files outside transaction → BEGIN IMMEDIATE → confirm current attempt → register frozen artifacts/candidate → reconcile usage/reservation → set state/event → COMMIT. A late cancelled/replaced result is diagnostic evidence, not current accepted work.

Delivery: record intent and exact approval identity first; perform action outside the transaction; then record receipt. A crash after action but before receipt is AMBIGUOUS. Reconcile by action ID, not blind retry. Changed candidates cannot reuse approval.

Watcher: BEGIN IMMEDIATE → verify event idempotency → coalesce/create proposed job → persist cursor/event → increment revision → COMMIT. Duplicate ID with different payload is rejected.

## Input and retention bounds

Validate title <=200 characters, source text <=16,000, task objective <=4,000, watcher condition <=1,000 and at most four user tasks. Reject oversize mutations rather than silently changing meaning. Truncate only previews with an indicator. Snapshot contains bounded recent jobs/events; full history is paginated. Binary images and full transcripts are stored as artifacts, not embedded in SQLite JSON.
