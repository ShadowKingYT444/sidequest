# Lane B journal

## B1 — isolated Git and immutable artifacts

Implemented a strict JSON-line adapter, shell-free Git inspection, independent `--no-hardlinks` clones, immutable mode-aware candidate artifacts and approval-gated local delivery. Repair 2 rejects hardlinked Git metadata and uses rooted no-follow writes; sentinel tests confirm outside bytes stay unchanged. Follow-up review 332e746 found unquoted credentials in ordinary config. The path-aware scanner rejects plaintext assignments while preserving docs, source environment lookups and interpolation references. Existing credential guards remain tested; samples are assembled at runtime.

## B2 — Codex app-server adapter

Implemented host-disabled `agent.execute` and read-only `agent.capabilities` over app-server stdio. Internal fake lifecycle tests cover catalog/model/account verification, host-assigned resume, time/token limits, interruption, output filtering, Git freeze and typed session recovery. Installed schemas permit marker-free replies; explicit wrong versions and boolean IDs fail closed. Production `agent.execute` rejects before provider startup because USD metering is unavailable. Compilation, `main --help` and all 41 service tests pass.

`agent.capabilities` exposes `usd_cost_enforced:false`. `max_cost_usd` is required and positive-validated by the internal lifecycle helper but does not limit spend. The provider cost is unknown, so responses report `cost_usd:null` and `uncertain:true`; time and token ceilings do not establish a USD ceiling. API-key mode is rejected before thread creation in deterministic coverage. No real provider turn is authorized or run.

Live readiness remains blocked: installed app-server 0.159.0-alpha.3 failed before initialize response because read-only CODEX_HOME denied writes to tmp/arg0, uid_map and installation_id. No live model/account read completed; gpt-6-luna/max remain unverified. Evidence: `evidence/B/B1.json`, `evidence/B/B2-readiness.json` and `evidence/B/source-filter-repair.json`.
