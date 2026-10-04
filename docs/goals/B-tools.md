# Lane B — Tools and execution

Own only: `services/tools/`, `journals/B.md`, `evidence/B/`. Read AGENTS.md and contracts/PROTOCOL.md. Three goals; finish and validate one before the next. Shared files are read-only.

## B1: Build isolated repository and adapter operations

/goal Complete B1 from docs/goals/B-tools.md. Meet all B1 checks. Keep journals/B.md. Do not start the next goal.

Implement the JSON-lines entry point, local repo inspection/preparation, safe artifact creation and local test-destination delivery.

Use temporary fixture repositories in tests. Never use this source repository as an agent repair target.

Acceptance evidence:

- **B1-1** — Tests prepare independent workspaces from one source without editing it; dirty source and unsafe paths rejected.
- **B1-2** — Local delivery checks digest, revision and exact approval, and retry ID cannot apply twice.
- **B1-3** — Entry point satisfies request/response envelope including errors and stderr-only diagnostics.

## B2: Connect a real coding worker and optional GitHub delivery

/goal Complete B2 from docs/goals/B-tools.md. Meet all B2 checks. Keep journals/B.md. Do not start the next goal.

Add a configurable coding provider adapter with bounded subprocess/model use. Test with a fake transport, then run one real provider repair on a disposable fixture. No claim of live success without credentials and a completed run.

Add optional GitHub PR creation behind explicit test-repository and user approval. Network writes are not required for lane PASS: negative/mock transport tests plus clearly documented disabled-by-default mode suffice. The real local provider repair is required.

Acceptance evidence:

- **B2-1** — A real configured coding provider creates a patch in a disposable repository; record redacted invocation and artifact digest.
- **B2-2** — Malformed provider output, timeout and missing credentials fail safely; no pretend fallback success.
- **B2-3** — PR adapter tests cover permission denial, stale approval and idempotent retry with mocked network; no unapproved live write.

## B3: Add narrow lookouts and operational limits

/goal Complete B3 from docs/goals/B-tools.md. Meet all B3 checks. Keep journals/B.md. Do not start the next goal.

Implement source-scoped file or build-event lookout polling, stable cursor and event IDs. No always-on screen capture or social scraping.

Provide repeatable tool tests, isolated environment setup and compatibility notes for runtime integration.

Acceptance evidence:

- **B3-1** — Polling unchanged input emits no duplicate job event; changed supported condition emits one stable event.
- **B3-2** — Cancellation, symlink escape, secrets redaction and repeated poll after restart are tested.
- **B3-3** — Run all tool tests and show fixture-mode versus real-provider evidence with exact configuration.
