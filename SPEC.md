# Sidequest — implementation baseline 0.3

Decision date: 2026-10-07. Status: specified, not implemented. The owner reports that the office assets are complete. Preserve them; build behavior around them. The inspected main branch contains the launch kit, not the asset project. No Unity editor version or prefab identifier has been invented.

## Product

A calm Unity office for organizing real agent work. Accept a job, assign workers, observe progress, inspect their files and diffs on an in-game computer, verify the result, and approve delivery. Turn a successful procedure into a tested reusable workshop. The office is the control and observation surface, not an extra autonomous planner.

The main worker's computer is a real product surface. It shows all project work and can open a worker-specific view. Individual worker computers open their own runs. Files, diffs, logs, screenshots, test results, and approvals are rendered inside Unity. Viewing them never calls a model. No permanent wall of text over the office.

## Fixed decisions

| Concern | Decision |
|---|---|
| Presentation | Existing Unity office; C#; uGUI world-space computer screen; TextMeshPro; focus camera and large-view mode |
| Local service | Python 3.11+, FastAPI, Uvicorn, Pydantic 2; one process and one SQLite writer |
| Execution | Existing Codex app-server, not a new agent reasoning framework |
| Default worker | `gpt-6-luna`, `max`, only when advertised by the installed account's model catalog |
| Manager | Deterministic scheduling. No continuous Sol orchestrator. Sol is explicit, bounded escalation only |
| Transport | Loopback HTTP; snapshot polling; paginated artifacts/logs; subprocess adapters |
| Source control | Local Git isolation; immutable candidates; user-approved delivery; no automatic main push |
| Verification | Trusted Playwright Python browser checks plus native Unity tests; optional bounded semantic review |
| Monitoring | Structured events first; opt-in selected-screen capture with local inference; no continuous cloud vision |
| Reuse | Versioned JSON workshop recipe, supported cases, immutable checks, activation approval |
| Scope | Single user on one Linux machine first. Multiple projects supported, distributed execution deferred |

## Authoritative documents

[Architecture](docs/ARCHITECTURE.md) fixes components and control flow. [Computer UI](docs/COMPUTER_UI.md) fixes all in-game viewing behavior. [Execution and monitoring](docs/EXECUTION.md) fixes workers, lookouts and verification. [Protocol](contracts/PROTOCOL.md) fixes shared interfaces, with [v1.1 additions](contracts/EXTENSIONS.md). [Feature matrix](docs/FEATURE_MATRIX.md) maps every capability to an owner and acceptance test.

[Agent execution](docs/LOW_TOKEN_EXECUTION.md), [parallel ownership](docs/PARALLEL_PLAN.md), and the four goal documents define development. [Asset binding](docs/ASSET_BINDING.md) prevents asset regeneration. [Research](docs/RESEARCH.md) contains exact upstream links, reuse decisions and limitations.

These documents supersede the initial proposed architecture and visual factory-station interpretation. The [0.2 specification](docs/archive/SPEC-0.2.md) is retained for historical context, not routine agent input. Its AC-01 through AC-14 acceptance requirements remain required and are mapped in the feature matrix. Its statement that Unity versions, backend stack and provider choice remain open no longer applies. The existing wire envelope remains `v:1`; additions are contract revision 1.1, not a silent breaking API replacement.

## Release demonstration

Start from the owner's completed office. Connect a disposable club-site Git repository. A local lookout detects the seeded signup failure. Two compatible tasks may run concurrently, in isolated working copies. The main computer shows their actual status and outputs. Open the changed file, scroll its diff, inspect before/after browser evidence and the test result, then approve that exact candidate for local delivery. Package the accepted process, test additional supported and unsupported cases, activate it, and handle a second supported failure without replanning. Restart the service and reconnect the office without duplicate delivery.

Show a clearly labeled fixture mode separately. A successful recording or animation is never evidence of a live action. No savings or success-rate claims have been measured yet. A specification reduces avoidable decisions; it does not guarantee a one-attempt implementation.
