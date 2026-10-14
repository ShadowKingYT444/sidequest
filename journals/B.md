# Lane B journal

## B1 — isolated Git and immutable artifacts

Implemented a strict JSON-line adapter, shell-free Git inspection, independent `--no-hardlinks` clones, immutable mode-aware candidate artifacts and approval-gated local delivery. Review repair 2 rejects hardlinked Git metadata and uses rooted no-follow writes; sentinel tests confirm outside bytes stay unchanged. Follow-up review 332e746 found unquoted credentials in ordinary config. A path-aware config scanner now rejects plaintext assignments while preserving docs, source environment lookups and interpolation references. Existing token, private-key, structured-secret, literal-assignment and path checks remain covered. Test samples are assembled at runtime.

## B2 — Codex app-server adapter

Implemented host-disabled `agent.execute` and read-only `agent.capabilities` over app-server stdio. The adapter verifies catalog/model/effort/account, resumes only host-supplied threads, bounds duration and tokens, interrupts on stop, filters output, freezes changed Git data, and emits typed thread/turn session progress for host recovery. Fake-transport tests pass; Python compilation, `main --help`, and all 39 service tests pass.

`max_cost_usd` is required and positive-validated but does not limit spend. The provider cost is unknown, so responses report `cost_usd:null` and `uncertain:true`; only time and token ceilings are enforced. API-key account mode is rejected before thread creation in deterministic coverage. No real provider turn is authorized or run.

Live readiness remains blocked: installed app-server 0.159.0-alpha.3 failed before initialize response because read-only CODEX_HOME denied writes to tmp/arg0, uid_map and installation_id. No live model/account read completed; gpt-6-luna/max remain unverified. Evidence: `evidence/B/B1.json`, `evidence/B/B2-readiness.json` and `evidence/B/source-filter-repair.json`.
