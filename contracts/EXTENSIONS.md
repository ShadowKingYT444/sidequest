# Contract revision 1.1 — artifacts, projects, runs and lookouts

This adds explicit first-release features to the wire-v1 base protocol. Read with PROTOCOL.md. All examples retain v:1. Consumers tolerate extra response fields. Servers reject unknown mutation fields/types instead of guessing. No caller-controlled filesystem read path is accepted.

## Deterministic local inspection profile

The MVP exposes additive `features.local_git_inspection:true` only when its host-configured deterministic Git/check pipeline is available. It must keep coding-model verification false until a real coding adapter is proven. A job additionally exposes host-derived `execution_profile:"local_git_inspection"` only when its persisted canonical profile is the fixed zero-budget, read_repo/run_checks inspection with candidate.frozen_identity and no custom plan; other jobs expose null or unavailable. This field is display/dispatch metadata, never accepted from user mutation input. The desktop re-reads the selected job and requires that profile, queued state and zero budget before sending job.run. A independently revalidates persisted policy/profile and current revision at dispatch. Reads and UI status refresh make zero model calls.

## Capability and project setup

GET /v1/capabilities returns {v,contract_revision:"1.1",features:{computer_artifacts:true,screen_watch:"available"|"unavailable"|"permission_required",github_delivery:boolean},worker_model:{id,effort,verified:boolean},limits:{max_parallel,max_tasks_per_plan},reasons:[string]}.

Register a project through command project.register with {name,repo_path,base_ref}. This is a deliberate local-user action: canonicalize the supplied path, confirm it against configured allowed roots, reject symlink escapes, inspect Git and persist the resolved revision. Untrusted issue text cannot invoke registration. Response state later appears in snapshot.projects:[{id,name,base_revision,status}]. Existing jobs without project_id resolve only to the explicitly configured default project; otherwise block setup.

Add commands project.select {project_id}, job.resume {job_id}, system.resume {}, watcher.create {project_id,kind,source_id,condition,rule,expires_at}, watcher.enable {watcher_id,enabled}, and watcher.ack {watcher_id,event_id}. All require expected_revision. Resume rechecks capability, dependencies, stop state and budget; it is not a blind repeat of an ambiguous action. A system stop never clears approval requirements.

job.create additionally accepts project_id and optional plan:{tasks:[{id,objective,depends_on:[id],write_paths:[relative_prefix],check_ids:[id]}]}. At most four tasks, unique IDs, acyclic dependencies, no unsafe path. Missing plan uses the fixed single-ticket pipeline. Overlapping write scopes serialize even if the user claims independence. An AI-proposed plan uses the same schema and requires user approval before job.run. Source material is data, never authorization.

## Domain extensions

Job additionally exposes project_id, run_ids:[id], tasks:[{id,state,depends_on,worker_id,attempt_id}], candidate_id and delivery_state. Run: {id,job_id,task_id,worker_id,attempt,state,model,effort,started_at,ended_at,usage:{input_tokens,cached_input_tokens,output_tokens,total_tokens,cost_usd,uncertain}}. Missing provider measures are null; do not add overlapping usage categories twice. Provider thread IDs are local diagnostics, not credentials or user-visible content.

Artifact additionally exposes run_id, media_type, size_bytes, candidate_id, immutable and display_name. Existing fields id,kind,sha256,job_id,source_revision,relative_path remain. relative_path is safe metadata only, never a read capability. New kinds text, file_manifest, diff and image supplement patch/log/test_report/screenshot/workshop. Candidate: {id,project_id,base_revision,candidate_revision,tree_sha256,patch_sha256,manifest_artifact_id,verified_check_ids}.

Approval additionally binds candidate_id, candidate_tree_sha256 and source_revision. These come from host-verified records. approval.decide must include them for a v1.1 candidate. Clients must read capabilities and use this revision; a missing identity is rejected, not filled from an unrelated current selection. Existing fixture-only v1 records can be displayed but cannot authorize live v1.1 delivery.

## Read endpoints

Every response is authenticated and project/job scoped. The local service token authenticates this single-user application, not a multi-tenant SaaS. Enforce ownership links even on local requests.

| Endpoint | Response fields after v |
|---|---|
| GET /v1/jobs/{job}/artifacts?cursor=&limit=100 | job_id, items:[Artifact], next_cursor |
| GET /v1/runs/{run} | run:Run |
| GET /v1/runs/{run}/events?after_seq=0&limit=200 | run_id, items:[RunEvent], next_after_seq, has_more |
| GET /v1/artifacts/{artifact}/files?cursor=&limit=100 | artifact_id, candidate_id, files:[FileEntry], next_cursor |
| GET /v1/artifacts/{artifact}/text?file_id=&start_line=1&limit=200 | artifact_id,file_id,sha256,start_line,lines:[{number,text,clipped}],next_line,encoding,immutable |
| GET /v1/artifacts/{artifact}/diff?file_id=&cursor=&limit=200 | artifact_id,candidate_id,base_revision,candidate_revision,rows:[DiffRow],next_cursor |
| GET /v1/artifacts/{artifact}/content | Exact verified bytes; Content-Type, Content-Length, ETag=digest; no active HTML |
| GET /v1/watchers | items:[{id,project_id,kind,state,source_label,last_event_at,reason}] |

FileEntry: {file_id,path,old_path,status,media_type,size_bytes,sha256,added_lines,deleted_lines,binary}. status is added, modified, deleted, renamed or unchanged; old_path is null except rename; deleted sha256 is null. file_id is an opaque manifest-local identifier, not a path encoding. Server resolves it only within the requested authorized artifact. Base-file viewing uses a separate base manifest, never arbitrary Git object requests.

DiffRow: {kind,old_line,new_line,text}. kind is file_header, hunk_header, context, add, remove, no_newline or binary. Non-applicable line numbers are null. Generate rows with Git; do not ask a model. Preserve escaped filenames and no-newline markers. Binary rows state that no textual diff is available. Text page limits are hard capped at 200 rows/256 KiB; clip and mark a single overlong line. Cursor contains an opaque server-validated offset tied to artifact hash and file_id. A bad or mismatched cursor returns INVALID_INPUT; a stale mutable stream cursor returns VERSION_CONFLICT.

RunEvent: {seq,at,type,message,artifact_id,task_id}. seq is monotonically increasing per run; at is UTC ISO8601. Allowed types status, tool_started, tool_finished, output, warning and usage. message is redacted plain text, at most 4 KiB. No private reasoning or authentication payloads. Text and image details are fetched only when viewed. All returned images are bounded previews under COMPUTER_UI.md; invalid media receives INVALID_INPUT, not a browser redirect.

## Adapter additions without changing stdout

Input may include context:{project_id,run_id,attempt_id,source_revision,write_paths,artifact_inputs:[{id,sha256,staged_path}],output_root,progress_path}. These are all assigned by A. B/D verify that staged files are contained, regular and hash-matched before reading. An artifact ID supplied only by user text cannot resolve a local file. A supplies read-only candidate roots to checks and separate writable report roots. A validates output artifacts against output_root, not arbitrary response paths.

Adapters append optional progress records to progress_path as newline JSON: {v,request_id,seq,type,message,artifact_id}. At most ten records per second and 4 KiB per record, maximum 10 MiB per attempt. Partial final records are ignored until complete. A rejects mismatched request IDs and repeated/non-monotonic sequence numbers. An adapter can report activity but cannot mark checks passed or approve writes through a progress record. stdout remains exactly one final response so old protocol transport tests retain meaning.

Add B op artifacts.freeze with {base_revision,write_paths} → {candidate,manifest_artifact_id,diff_artifact_id,patch_artifact_id}. Add B op preview.capture with {candidate_id,origin_ref} → {screenshot_artifact_id,captured_at}; origin_ref resolves only from host-registered preview settings. A does not fetch arbitrary URLs supplied by repository content. preview.capture is a convenience screenshot, not trusted QA.

For repo.deliver, A passes a delivery_id/action_id and a signed-or-host-owned approval record through the privileged delivery adapter channel, never a worker-authored JSON approval. B recomputes candidate/patch hashes and rechecks base revision/destination immediately before acting. Repeated ID returns the reconciled receipt. Mismatched hash/action/destination or uncertain prior write blocks.

## Watcher event boundary

WatcherEvent: {v,watcher_id,event_id,project_id,observed_at,source_kind,source_label,condition_id,source_revision,evidence_artifact_id}. source_kind is file, process, github or selected_screen. Revision and evidence can be null. For file/process events derive event_id from source_id + condition_id + observed source revision/transition. Screen events receive a UUID on a persisted rising edge; the same edge cannot emit again until reset plus cooldown. Confidence, when supplied, is metadata rather than authorization.

Selected-screen watchers are armed only after OS consent, source/mask configuration and a local vision endpoint are available. raw frame paths, tokens and arbitrary URLs never enter the public event. A maps condition_id to an existing approved rule, creates/coalesces a job and persists the event/cursor in one transaction. Unsupported or unknown conditions produce no job. No polling or office-rendering request may call the planner implicitly.

## Layout clarification

layout.save remains a versioned workflow topology command from the explicit workflow editor. It is not the same as moving desks. Ordinary office placement lives in C's local presentation settings and has zero effect on task permissions or currently running dependencies. A validates workflow edges before activation. Older grid examples are logical coordinates, not instructions to remodel the owner's office.

## Coordinator implementation clarifications — 2026-10-14

The frozen file-manifest artifact is JSON `{v:1,candidate,files:[FileEntry]}`. Each entry additionally records `mode` as a Git regular-file mode string (100644 or 100755). It contains all safe current candidate files, including unchanged entries, and deleted entries with null sha256. A frozen workspace contains exactly the non-deleted entries; no symlinks, special files or extra candidate files are allowed.

`candidate.tree_sha256` hashes canonical UTF-8 JSON `{v:1,files:[{path,mode,size_bytes,sha256}]}` over non-deleted entries sorted by path. Object keys are sorted, separators are compact, and Unicode is emitted directly (`ensure_ascii=false`). B freezes this identity; A rechecks before registering; D verifies exact bytes and modes before and after checks. Artifact SHA is still the hash of raw artifact bytes. For `check.run`, payload and context source_revision refer to the frozen candidate_revision; B execution requests use the registered base revision.

Privileged `repo.deliver` uses context.delivery_id and context.action_id; they must match in this release. The existing payload.approval carries identity metadata only. Context additionally supplies `approval_record:{id,sha256,staged_path}` for a host-staged approved record outside the worker workspace and under a configured host-owned approval root. B verifies regular-file containment, digest, approved state, exact source/candidate/tree/patch/action/destination and matching ID against that record. An arbitrary payload approval cannot grant permission. Manifest/patch artifacts resolve only through hash-checked context.artifact_inputs. Persist intent before action and reconcile repeated or uncertain IDs; do not blindly retry an external write.

These additive encodings resolve previously unspecified implementation placement. They do not grant a new action, change wire v1, weaken required checks or authorize a demonstration provider/delivery call.
