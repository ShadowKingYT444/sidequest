# Billing capability review — October 17, 2026

The current product gate prevents all production Codex turns, including ChatGPT-authenticated accounts. The USD-only explanation is incomplete: included subscription usage and API dollar billing differ. However, enabling turns from a healthy quota snapshot would bypass the retained no-new-spending and reserve policy.

[Installed protocol inspection](installed-protocol.json) was generated offline by Codex 0.159.0-alpha.3. No provider session, authentication operation or inference was performed. The exact inspected schema hashes and fields are recorded. [Review and minimal enabling proposal](../../../docs/BILLING_CAPABILITIES.md) links source locations and required tests. No dispatch authorization, budget value or provider permission was changed.

[Five existing gate regressions](existing-gate-tests.log) were rerun and passed: healthy subscription snapshots do not grant execution, public dispatch rejects before provider startup, and stale/missing authority remains blocked. These use protocol fakes and local runtime fixtures; they prove the current denial behavior, not live billing enforcement.
