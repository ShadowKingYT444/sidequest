# Lane B journal

## B1 — isolated Git and immutable artifacts

Built a strict JSON-line adapter, shell-free Git inspection, independent `--no-hardlinks` clones, mode-aware candidate artifacts and approval-gated local delivery. Freeze rejects hardlinked Git metadata and uses rooted no-follow writes. The path-aware scanner rejects plaintext credentials in config while preserving ordinary docs, environment lookups and interpolation. Credential fixtures are assembled at runtime.

## B2 — Codex app-server adapter

Implemented host-disabled `agent.execute` and read-only `agent.capabilities` over app-server stdio. Fake lifecycle tests cover catalog/account gates, resume, limits, interruption, output filtering, freeze and session recovery. Initialization now validates installed `codexHome`, `platformFamily`, `platformOs` and `userAgent`; marker-free JSON-RPC replies are accepted, wrong markers and boolean IDs fail closed. Thread-goal APIs are not marked experimental, so no experimental capability is requested.

Capabilities read ChatGPT quota only after account verification and return strict nullable `ordinary_usage_allowed` and `purchased_credits_available` booleans. They omit balances and account IDs, never refresh auth, and create no thread/turn. `usd_cost_enforced:false`; `max_cost_usd` does not cap spend, so production execute rejects before provider startup. Cost remains unknown (`null`, uncertain).

The prior native startup failed with EROFS on CODEX_HOME runtime files despite `sqlite_home` and `log_dir` under `/tmp`. No Codex daemon socket was found for the supported proxy path; `--code-mode-host` is not an existing-login route. No retry, auth change, permission change or provider turn occurred. Validation: 42 service tests, compile, help and diff checks pass. Evidence: `evidence/B/B2-readiness.json`, `evidence/B/native-setup-diagnosis.json` and `evidence/B/source-filter-repair.json`.
