# Guarded provider transport checkpoint

Baseline: `1a5d1be12314b0e314740cec7a9083e1ae470387`. This is provider implementation and **protocol-fake evidence**, not a verified live Codex turn or native desktop workflow. The public adapter still rejects execution before provider startup because enforceable USD spending authority is unavailable.

`agent.execute` retains its original objective/checks/limits. An optional `followup:{message_id,prompt}` resumes the host's exact `context.provider_thread_id` and terminal `context.provider_turn_id`. Before starting another turn, the adapter checks the latest persisted turn, original goal identity, known remaining cumulative tokens, and preservation of that token counter when reactivating the goal. A changed/active/unavailable anchor, unknown goal state, exhausted budget, or reset counter blocks another send. Message deduplication and crash reconciliation remain runtime-owned; the provider protocol has no verified message-id idempotency parameter.

Host-resolved `context.attachments` entries contain `attachment_id,name,media_type,size_bytes,sha256,path`. Files are read through rooted no-follow descriptors, must be single-link regular files beneath configured artifact roots outside the worker clone, and must match recorded size/digest. Ten inputs and 1 MiB combined decoded bytes are the maximum. UTF-8 plain text, Markdown, CSV and JSON become explicitly untrusted text; PNG/JPEG/GIF/WebP become bounded image data URLs. Image signatures are checked; actual provider image decoding remains unverified. Paths, arbitrary URLs, file IDs, PDF and unsupported binary inputs are not sent. Encoded input is checked against the 2 MiB RPC bound before startup, and credential-like text is rejected.

For a host-materialized prior candidate, `context.initial_tree_sha256` is a `tree_digest` of every actual path/mode/size/byte digest. A dirty initial clone is allowed only for follow-up with that exact identity, original base HEAD, original scope and no project-local `.codex` configuration. The resulting candidate is still frozen against the original source and write scope.

TDD and validation:

- `baseline.log`: 44 existing tools tests pass.
- `red-confirmed-contract.log`: omitted attachments and rejected follow-up reproduced; 8 tests, 13 failing subcases and 6 errors. `red.log` preserves the earlier proposal run.
- `green.log` preserves the initial incomplete repair: one attachment secret-filter failure.
- `red-hardening.log`: unquoted credential text, unknown goal state and uncommitted project configuration reproduced; 9 tests, 3 failures.
- `green-hardened.log`: all 9 transport tests pass in 3.367 seconds.
- `full-tools.log`: all 53 tools tests pass in 11.758 seconds.
- `py_compile`, CLI `--help` and `git diff --check` pass.

The installed schema was generated offline; the relevant input and quota descriptions/hashes are preserved in `installed-schema.json`. `ordinaryUsageAllowed` is backend permission for included usage; null is unknown and cannot be recovered from percentages or reset times. Included-usage permission, a 10% reserve snapshot, purchased-credit availability and USD spending enforcement are separate authorities. The schema does not prove a no-credit-fallback policy or enforceable 10% stop. No spending guard was relaxed. No real account/quota read, model turn, auth grant, credential copy, permission/sandbox change, protected asset change, merge, push or deployment occurred in this lane.

## Terminal follow-up without a new tree change

The second checkpoint returns explicit `status:"completed"` for a terminal follow-up whose checked final tree matches the initial tree. For a clean original clone, the final worktree must remain clean; for a restored candidate, its final mode/path/size/byte digest must equal `initial_tree_sha256`. The response contains the durable message ID, provider thread/turn, verified model/effort, safe summary and unchanged unknown-USD usage. It records completion in the progress trace and returns no candidate or artifacts. Runtime retains the prior candidate. An original task that makes no Git change remains blocked.

- `no-change-red.log`: 12 transport tests, exactly two failures; clean follow-up was blocked and unchanged restored candidate was redundantly frozen.
- `no-change-green.log`: all 12 transport tests pass in 4.466 seconds.
- `no-change-full-tools.log`: all 56 tools tests pass in 21.793 seconds, including the stronger recorded-trace assertion.
- Compile and diff checks pass. This remains protocol-fake evidence; the production USD guard is unchanged.
