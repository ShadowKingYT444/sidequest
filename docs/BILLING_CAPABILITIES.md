# Subscription and spending capability review

**The current gate blocks every production Codex turn, including ordinary ChatGPT subscription use. Its USD-only explanation is too broad, but a safe subscription-only execution path has not been implemented or demonstrated.** This review does not enable execution or change the native tester’s source checkpoint.

## What the code does

| Layer | Current behavior |
| --- | --- |
| [Provider bridge](../services/tools/codex_bridge.py) | `probe_capabilities` always reports `usd_cost_enforced=false`. Public `execute_agent` rejects before starting an app-server. The internal `_test_only_allow_unmetered` argument is only for protocol tests and is not a runtime setting. |
| [Runtime readiness](../services/runtime/config.py) and [normalization](../services/runtime/api.py) | A fresh account/model/effort check, consent and `usd_cost_enforced=true` are all required. Subscription quota/reserve observations do not grant execution. |
| [Scheduler](../services/runtime/scheduler.py) and [storage](../services/runtime/store.py) | A coding claim must reserve positive micro-dollars; zero reservations are restricted to trusted deterministic inspection. Provider cost remains unknown, so the reservation stays held. |
| [Follow-ups](../services/runtime/sessions.py) | Unknown spending cannot authorize another turn. Exact session/receipt/source identity and project permissions are also required. |
| [Provider picker](../desktop/src/provider-readiness.ts) and [task form](../desktop/src/StationLauncher.tsx) | Readiness requires USD enforcement and the form requires a positive USD limit. The convenience launcher deliberately disables coding. |

[Five focused existing regressions](../evidence/desktop/billing-review-20261017/existing-gate-tests.log) pass and reproduce these gates using protocol/local fixtures. This is more than a single incorrect condition: bypassing the bridge guard would still leave the accounting, follow-up and UI contract wrong for subscription-only use.

## What can actually be established

The [installed offline protocol record](../evidence/desktop/billing-review-20261017/installed-protocol.json) comes from Codex `0.159.0-alpha.3`; no account or inference call was made.

- `account/read` distinguishes ChatGPT, API-key and Bedrock authentication. ChatGPT sign-in alone does not establish an included-only billing route; plans can include credit-based usage.
- `account/rateLimits/read` can return authoritative nullable `ordinaryUsageAllowed`, percentage windows and credit flags. Its installed schema explicitly disallows inferring included-usage permission from percentages or reset times when permission is unknown.
- The inspected thread/start, thread/settings/update, turn/start and thread/goal/set schemas provide no explicit included-only billing or hard reserve setting. Arbitrary configuration keys are possible, but no documented/verified key was found that enforces these constraints.
- A token ceiling and a percentage snapshot do not establish how much of an account-wide quota a turn may consume. Other clients can use the same account concurrently; stopping after telemetry arrives cannot guarantee the retained 10% reserve.

Official guidance distinguishes included usage from API prices and says available credits can fund continued usage after included limits. Thus `hasCredits=false` at one instant is not a durable prohibition on credit use or reloads. [Pricing](https://learn.chatgpt.com/docs/pricing), [credit behavior](https://help.openai.com/en/articles/12642688-using-credits-for-flexible-usage-in-chatgpt-personal-plans), [app-server rate-limit fields](https://learn.chatgpt.com/docs/app-server).

`forced_login_method=chatgpt` restricts authentication, not credit fallback. It cannot substitute for billing enforcement. [Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference).

## Minimal safe enabling change — proposed, not implemented

1. Separate verified execution authority into **included subscription**, **metered**, and **unknown** modes. Account names, plans, UI flags and quota snapshots must never mint authority. Included mode needs a supported provider/account guarantee that rejects paid/API/credit fallback, plus enforceable quota reservation/limits sufficient for the retained reserve policy. Bind that guarantee to the current account, model, configuration, thread and expiry; recheck it before each initial or follow-up turn.
2. Keep metered mode blocked without explicit spending permission and a provider-enforced ceiling. Keep unknown mode blocked. Preserve all source-scope, project approval, host consent, sandbox, model selection and exact receipt/recovery checks.
3. For genuinely verified included-only mode, record subscription capacity separately and allow a coding claim without a fabricated positive dollar budget. Do not translate token counts or percentages into invented USD cost. Change scheduler/store/usage settlement, follow-ups and the task form together; a UI-only bypass is insufficient.
4. Explain the actual missing guarantee in Settings. A provider with no supported no-credit-fallback/reserve mechanism remains unavailable, even if ordinary usage currently appears available.

Required regression matrix: included-only authority with zero additional charges; API-key/credit/unknown routes denied; absent/stale/mismatched account or authority denied; reserve at/below 10% denied; concurrent claims and mid-turn authority loss; initial and follow-up accounting without invented dollars; unchanged consent/scope/sandbox/receipt protections. Positive fixtures prove policy logic only. Live acceptance additionally requires a supported authenticated host and explicit authorization for a bounded included-only test.

## Present blocker and next decision

A provider-side included-only guarantee and enforceable reserve mechanism have not been established. The current installed schema does not supply them through the inspected methods. A supported alternative or a deliberate change to the product’s reserve policy would need separate evidence/authorization; this task does not relax either requirement. No paid API turn, credit purchase, credential copy, model fallback or live coding turn was attempted.
