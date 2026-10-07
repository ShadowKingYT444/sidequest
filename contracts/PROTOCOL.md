# Shared protocol — wire v1, contract revision 1.1

Frozen implementation interface. Read [EXTENSIONS.md](EXTENSIONS.md) for projects, task plans, paginated files/diffs, run events, capture and exact candidate approval. That document is required for the first complete release, not an optional wishlist. [snapshot.json](snapshot.json) remains an explicitly labeled legacy fixture. It cannot authorize live delivery.

## Processes and transport

A runs services/runtime/main.py, owns SQLite and loopback HTTP, and dispatches B at services/tools/main.py and D at services/workshops/main.py. Use configured argv arrays with each service's environment, shell disabled. No cross-lane Python imports. C uses only HTTP. All three entry points provide --help. B/D accept one JSON-line request on stdin, return one JSON-line response on stdout, log to stderr and exit. Maximum input/final output is 4 MiB. Progress uses the assigned file described in EXTENSIONS.md. A enforces deadlines and cancels process groups.

HTTP binds 127.0.0.1:4317 by default. Require Authorization: Bearer <local-session-token> except /health. Credentials remain outside committed Unity assets, job text, artifacts and logs. Disable CORS by default. The first release is a single-user local app, not a multi-tenant service.

GET /health → {v:1,service:"sidequest-runtime",mode:"live"|"fixture"}.
GET /v1/snapshot → {v,revision,mode,jobs,workers,workshops,approvals,layout,budget,stopped}, with additive projects field.
GET /v1/jobs/{id} → {v,job}.
GET /v1/artifacts/{id} → {v,artifact,preview_text}; only authorized registered artifacts, no arbitrary read path.
POST /v1/commands → durable queued command response, not job completion.

## Commands

Request: {v:1,command_id:"uuid",type:"job.create",expected_revision:12,payload:{...}}. Response HTTP 202: {v:1,command_id,accepted:true,revision}. A checks version and schema, then transactionally enforces idempotency and policy. Same ID/same canonical body returns the recorded outcome; same ID/different body is rejected. For a new mutation, an outdated revision returns VERSION_CONFLICT. expected_revision may be null only for job.create and system.stop. The client must explicitly re-review after a stale approval; no automatic retry with a new revision.

| Command | Required payload |
|---|---|
| job.create | title,source:{kind,uri,text},checks:[id],budget_usd,allowed_actions:[string]; project_id and optional bounded plan in extensions |
| job.run, job.pause, job.cancel | job_id |
| job.assign | job_id,worker_id; reject mid-write reassignment |
| approval.decide | approval_id,approve:boolean,artifact_sha256,action,destination; v1.1 candidate identity required in extensions |
| workshop.propose | job_id |
| workshop.test | workshop_id,version,case_ids:[string] |
| workshop.activate | workshop_id,version; tested digest and human authorization required |
| workshop.pause | workshop_id |
| layout.save | nodes:[{id,kind,x,y}],edges:[{from,to}]; versioned acyclic workflow only |
| system.stop | empty payload; stop new dispatch, request cancellation, not rollback |

Resume, project and watcher commands are defined in extensions. Reject unknown commands; do not interpret them as natural-language instructions. Permissions are stable strings: read_repo, propose_patch, run_checks, local_deliver, github_pr. Each consequential action needs both project policy and a current exact approval. Model calls also require configured provider/budget consent.

Errors: {v:1,error:{code,message,retryable}}. INVALID_INPUT=400, NOT_FOUND=404, VERSION_CONFLICT=409, POLICY_DENIED=403, BUDGET_LIMIT=429, DEPENDENCY_FAILED=424, UNAVAILABLE=503, INTERNAL=500. Messages are short, actionable and redacted. A timeout cannot be represented as success.

## Base objects

IDs are opaque strings; timestamps UTC ISO8601. Integer snapshot revision increases on state mutations, not on reads. Persist money as integer micro-dollars; JSON USD decimals are presentation values. Unknown measured usage is null, not zero. Old history is paginated instead of appended without limit to every snapshot.

Job: id,title,source,state,checks,allowed_actions,budget_usd,spent_usd,worker_id,artifact_ids,events,blocked_reason,workflow_version. source.kind is typed,issue or lookout. state is queued,running,verifying,needs_approval,accepted,blocked,failed,paused or cancelled. checks:[{id,state,evidence_artifact_id}] where state is pending,pass,fail or blocked. events:[{id,at,type,message,artifact_id}]. C handles unknown display values as unavailable, never accepted.

Worker: {id,role,state,job_id}; role builder,researcher or verifier; state idle,working,blocked or paused. Roles are tool/policy capabilities, not simulated intelligence. An avatar does not determine actual capacity.

Artifact: {id,kind,sha256,job_id,source_revision,relative_path}. Base kind patch,log,test_report,screenshot or workshop; extensions add file/diff metadata. Verify regular-file containment and digest before registering or reading. relative_path is metadata, not authorization.

Approval: {id,job_id,artifact_id,artifact_sha256,action,destination,state}; state pending,approved,denied or stale. Changes to source revision, candidate, action or destination invalidate it. A owns approval records; a worker-created JSON file cannot grant permission.

Workshop: {id,name,version,state,supported_case_ids,validation_artifact_ids,last_job_id}; state draft,testing,ready,active,paused or blocked. D owns its recipe contents, A owns activation and policy. An updated version must pass new testing.

layout:{version,nodes,edges}; node kind lookout,board,workstation,test_lab,approval or workshop; x/y integers0..15 are logical workflow coordinates, not required physical furniture. Office placement is separate presentation state. budget:{limit_usd,reserved_usd,spent_usd,uncertain}. Reservations are reconciled, not billed twice.

## Adapter envelope

Request: {v:1,request_id,op,job_id,workspace,payload,context?}. workspace and all context paths are host-assigned and allowlisted. Response: {v:1,request_id,ok:true,data:{...},artifacts:[],usage:{cost_usd:null,uncertain:true}}. Failure uses ok:false,data:{},artifacts:[], plus error:{code,message,retryable}. Each returned Artifact has a verified digest. Nonzero exit, malformed/extra final output, wrong ID/version or wrong digest is failure. No implicit retry of an external write.

| B operation | Payload → data |
|---|---|
| repo.inspect | {repo_path,revision} → {revision,clean,files:[string]} |
| repo.prepare | {repo_path,revision} → {workspace,revision} |
| agent.execute | {objective,check_ids,limits:{max_seconds,max_cost_usd}} → {status:"candidate"|"blocked",summary,patch_artifact_id}; bounded token/model settings from trusted config |
| repo.deliver | {patch_artifact_id,artifact_sha256,source_revision,destination,approval} → {status,delivery_id}; privileged host channel and action_id in extensions |
| lookout.poll | {source_id,cursor} → {cursor,events:[{id,source_uri,condition,text}]} |

| D operation | Payload → data |
|---|---|
| check.run | {check_ids,source_revision} → {passed,results:[{id,state,evidence_artifact_id}]} |
| workshop.propose | {accepted_job,artifact_ids} → {workshop,package_artifact_id} |
| workshop.test | {package_artifact_id,case_ids} → {passed,results,validation_artifact_ids} |
| workshop.match | {package_artifact_id,event} → {supported,reason,objective,check_ids}; proposal only, never execution permission |

All input artifact IDs are resolved by host-staged context.artifact_inputs, not arbitrary filesystem search. B provides artifacts.freeze and preview.capture in extensions. Trusted D checks remain outside writable candidate roots. A independently verifies all returned artifact bytes and enforces project scope.
