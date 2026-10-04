# Sidequest contract v1 — frozen for the four lanes

These are requirements and fixtures, not an implemented API. Do not change this contract inside a lane. Report an ambiguity in its journal; request a coordinator revision before changing a shared shape. Additive fields must not be required by a consumer. Reject unsupported `v` values.

## Ownership and deployment

A runs `services/runtime/main.py` with Python 3.11+, owns SQLite and the loopback HTTP service, and starts B/D as subprocesses. B implements `services/tools/main.py`. D implements `services/workshops/main.py`. Each service owns its own dependency file and tests. C owns the complete Unity project. No service imports another lane's implementation. All three service entry points accept `--help`; B/D additionally support the JSON-lines mode below.

Use one isolated Python environment per service. Runtime config supplies an explicit argv array for each adapter, including that environment's Python interpreter. Never use `shell=True`. Workspaces, artifact roots, allowed repositories, provider settings, and credentials are configured locally, not embedded in a Unity build. Linux desktop is the initial acceptance target. C records the actual installed Unity 6 version and package lock before building; a version number in prose is not an installed editor.

## HTTP: Unity ↔ runtime

Bind `127.0.0.1`, default port 4317. Require `Authorization: Bearer <local-session-token>` except `/health`; token lives in user settings, not committed assets. Reject external bind by default. Disable CORS unless an explicit local origin is configured. No credentials in responses.

- `GET /health` → `{ "v":1, "service":"sidequest-runtime", "mode":"live" }`. Development mock says `mode:"fixture"`.
- `GET /v1/snapshot` → the object in `snapshot.json`. Integer `revision` increases on every state change. Poll twice per second initially. Avoid another event-stream dependency for v1.
- `GET /v1/jobs/{id}` → `{ "v":1, "job": Job }`.
- `POST /v1/commands` → Command below. Return HTTP 202 with `{ "v":1, "command_id":"...", "accepted":true, "revision":12 }` only after durable acceptance. It means queued, not completed.
- `GET /v1/artifacts/{id}` → `{ "v":1, "artifact":Artifact, "preview_text":"..." }`. Only serve known allowlisted artifacts. No caller-supplied filesystem paths. Large/binary files use an explicit allowlisted download endpoint added by A without altering the existing shape.

Errors use `{ "v":1, "error":{ "code":"POLICY_DENIED", "message":"...", "retryable":false } }`. Codes: `INVALID_INPUT`, `NOT_FOUND`, `VERSION_CONFLICT`, `POLICY_DENIED`, `BUDGET_LIMIT`, `DEPENDENCY_FAILED`, `UNAVAILABLE`, `INTERNAL`. Use 400/404/409/403/429/424/503/500 respectively. Error messages must not expose tokens or full environment variables.

Command: `{ "v":1, "command_id":"uuid", "type":"job.create", "expected_revision":10, "payload":{} }`. Retries with the same ID and same body return the recorded outcome; same ID with a different body is rejected. Check `expected_revision` before new mutations; null is allowed only for `job.create` and `system.stop`. Unknown commands are rejected.

| Type | Required payload | Meaning |
|---|---|---|
| `job.create` | `title`, `source:{kind,uri,text}`, `checks:[id]`, `budget_usd`, `allowed_actions:[string]` | Create a job; source kind is `typed`, `issue`, or `lookout`. |
| `job.run` | `job_id` | Start within policy; not permission to publish. |
| `job.pause`, `job.cancel` | `job_id` | Prevent new dispatch, request in-flight cancellation. |
| `job.assign` | `job_id`, `worker_id` | Assign queued work; reject mid-write reassignment. |
| `approval.decide` | `approval_id`, `approve:bool`, `artifact_sha256`, `action`, `destination` | Approve only the exact tested artifact and action. |
| `workshop.propose` | `job_id` | Draft a package from an accepted job. |
| `workshop.test` | `workshop_id`, `version`, `case_ids:[string]` | Run trusted scope and negative cases. |
| `workshop.activate` | `workshop_id`, `version` | Requires passing activation evidence and human authorization. |
| `workshop.pause` | `workshop_id` | Stop new matching jobs. |
| `layout.save` | `nodes:[{id,kind,x,y}]`, `edges:[{from,to}]` | Save a versioned acyclic workflow; never change an active run's version. |
| `system.stop` | none | Global dispatch stop, not rollback. |

## Domain objects

Snapshot fields: `v`, `revision`, `mode`, `jobs`, `workers`, `workshops`, `approvals`, `layout`, `budget`, `stopped`. Arrays may be empty. IDs are opaque strings. Costs are nonnegative decimal USD; store internally as integer micro-dollars, never binary floats for accounting. Unknown cost is null, not zero. UTC timestamps use ISO 8601. UI must handle unknown future display states safely as unavailable, not completed.

**Job** fields: `id,title,source,state,checks,allowed_actions,budget_usd,spent_usd,worker_id,artifact_ids,events,blocked_reason,workflow_version`. State: `queued`, `running`, `verifying`, `needs_approval`, `accepted`, `blocked`, `failed`, `paused`, `cancelled`. `events` contain `{id,at,type,message,artifact_id}`. `checks` contain `{id,state,evidence_artifact_id}` with state `pending`, `pass`, `fail`, `blocked`.

**Worker**: `{id,role,state,job_id}`. Roles `builder`, `researcher`, `verifier`; states `idle`, `working`, `blocked`, `paused`. Real capacity, not fake concurrency animations.

**Artifact**: `{id,kind,sha256,job_id,source_revision,relative_path}`. Kinds `patch`, `log`, `test_report`, `screenshot`, `workshop`. A checks path containment, symlink escapes and digest before serving. An artifact ID never grants tool execution.

**Approval**: `{id,job_id,artifact_id,artifact_sha256,action,destination,state}`. States `pending`, `approved`, `denied`, `stale`. A binds approval to the verified source revision too. Changing the patch, target revision, action or destination invalidates approval.

**Workshop**: `{id,name,version,state,supported_case_ids,validation_artifact_ids,last_job_id}`. States `draft`, `testing`, `ready`, `active`, `paused`, `blocked`. D additionally owns the package format; it must contain trigger, support boundary, executable steps, immutable check IDs, permissions, limits and escalation policy. A stores its digest/version and activation record.

`layout` contains `version,nodes,edges`. Node kinds: `lookout`, `board`, `workstation`, `test_lab`, `approval`, `workshop`. Positions are integer grid coordinates in [0,15]. `budget`: `{limit_usd,reserved_usd,spent_usd,uncertain}`. Reservations and actual costs are reconciled, not billed twice. Unknown in-flight cost must be visible.

## JSON-lines: runtime ↔ adapters

One process per request initially: write one UTF-8 JSON object plus newline to stdin; process writes one response plus newline to stdout, diagnostic logs to stderr, then exits. Maximum request/response 4 MiB. Runtime enforces a timeout and kills the process group on cancellation. No implicit retry of external writes. Config supplies local request and artifact roots; workers cannot choose a host path.

Request: `{ "v":1, "request_id":"...", "op":"repo.inspect", "job_id":"...", "workspace":"/approved/path", "payload":{} }`.
Response: `{ "v":1, "request_id":"...", "ok":true, "data":{}, "artifacts":[], "usage":{"cost_usd":null,"uncertain":true} }`. On failure `ok:false`, `data:{}`, plus `error:{code,message,retryable}`. `artifacts` use the Artifact shape; adapters populate digests. A independently checks them. Nonzero exit, missing/malformed/extra output, mismatched ID/version or wrong digest is failure, not success.

### B operations

- `repo.inspect`: payload `{repo_path,revision}` → data `{revision,clean,files:[string]}`. Local allowlist only.
- `repo.prepare`: `{repo_path,revision}` → `{workspace,revision}`. Isolated checkout; reject dirty source and unsafe paths.
- `agent.execute`: `{objective,check_ids,limits:{max_seconds,max_cost_usd}}` → `{status:"candidate"|"blocked",summary,patch_artifact_id}`. Uses an explicitly configured coding provider; fake provider is visibly fixture-only. Never edit trusted checks.
- `repo.deliver`: `{patch_artifact_id,artifact_sha256,source_revision,destination,approval:{id,action,artifact_sha256,destination}}` → `{status,delivery_id}`. First release implements local test-destination delivery and optional approved GitHub PR creation. A validates approval; B rechecks digest/revision and allowlisted destination. No automatic merge.
- `lookout.poll`: `{source_id,cursor}` → `{cursor,events:[{id,source_uri,condition,text}]}`. Narrow file/build events only; stable IDs, duplicates removed by A. Screen AI is deferred.

### D operations

- `check.run`: `{check_ids,source_revision}` → `{passed,results:[{id,state,evidence_artifact_id}]}`. Trusted checker lives outside writable candidate and mounts/reads it with controlled access. Runs the fixture signup browser journey; no candidate-controlled npm script can replace the mandatory verifier.
- `workshop.propose`: `{accepted_job,artifact_ids}` → `{workshop,package_artifact_id}`. Proposal cannot self-activate.
- `workshop.test`: `{package_artifact_id,case_ids}` → `{passed,results,validation_artifact_ids}`. Tests at least two additional supported failures, original regression, and unsupported input.
- `workshop.match`: `{package_artifact_id,event}` → `{supported,reason,objective,check_ids}`. Unknown cases abstain; output is a new job proposal, not permission to execute.

## Independent development fixtures

`snapshot.json` is a recorded, labeled example for C and serialization tests, not a runtime. B and D test their JSON-lines entry points with local fixture requests. A uses fake subprocesses implementing the response envelope. D owns the runnable demo fixture and test rig. Do not copy implementation across lanes. Final I1 substitutes the real services and Unity build; unit tests alone cannot pass it.
