# Native host status — 2026-10-14

No available runtime path in this VM resolves the native blockers within the current restrictions. This is a read-only follow-up to the recorded failures, not another Electron launch or Codex initialization. The browser, renderer security tests and deterministic adapter tests remain useful evidence, but do not certify native startup or live agent execution.

| Gate | Current evidence | Supported next setup | Available here? |
| --- | --- | --- | --- |
| Electron OS sandbox | Electron 44.7.1 exited with SIGTRAP before a window. Its `chrome-sandbox` is uid 1000, mode 0755; the fatal error requires a root-owned mode 4755 helper. | A managed host/environment already configured with a usable Electron sandbox and desktop session, followed by the existing direct native smoke command. | No supported configuration was found. No permissions or sandbox settings were changed. |
| Codex runtime state | Prior stdio initialization failed before its response with EROFS in original `CODEX_HOME` runtime paths. That directory remains non-writable. | A host-provided writable runtime layout that retains the original supported authentication state without copying credentials, or an existing authenticated host-owned app-server endpoint. | Neither is provisioned. Redirecting SQLite/logs was already tried and did not relocate the failing non-SQLite paths. |
| Codex USD ceiling | The native adapter reports `usd_cost_enforced:false`; production `execute_agent` rejects before process/thread/turn startup. | Independently verified enforcement of the existing positive USD budget contract, plus all existing consent/model/project/permission gates. | No installed native protocol or adapter enforcement was verified. Host startup repair would not clear this product gate. |

The system Chromium sandbox helper is mode 4755 but uid 65534, so it is not the root-owned helper required by the recorded Electron failure. The kernel's `user/max_user_namespaces` is positive; that value alone does not prove namespace creation is permitted or that Chromium's sandbox works. Earlier acceptance evidence reports no usable namespace alternative. This review did not attempt namespace creation, point Electron at another helper, use Playwright's Electron launcher, or pass any sandbox-disabling flag.

The installed Codex CLI advertises `app-server proxy --sock SOCKET_PATH` and `--listen unix://` / `unix://PATH`. This is a supported transport to an **already-running** app-server, not a way to create authenticated state in a temporary directory. The default control socket is absent. All seven visible Unix-socket entries with “codex” in their path belong to containerd/container networking services; none identifies an app-server. No socket was connected to. Sidequest's current adapter starts private stdio directly; a host-provided proxy endpoint would also need explicit adapter integration and validation before it could establish readiness. `--code-mode-host` selects a Code Mode host and does not establish an existing authenticated app-server route.

Installed `ThreadStartParams` and `TurnStartParams` schemas have no top-level dollar-budget or spend-ceiling field. Token usage and account rate limits describe telemetry/quota, not independently enforced USD cost. This limited schema inspection is not a claim about every possible future provider capability. The existing adapter's explicit execution refusal is the decisive current product boundary; time/token limits, subscription login, nullable quota booleans and a client-side budget reservation do not replace it.

Read-only commands executed during this follow-up:

```bash
/opt/codex/bin/codex app-server --help
/opt/codex/bin/codex app-server proxy --help
git rev-parse HEAD
```

Both help commands exited zero and emitted the existing PATH-alias EROFS warning. They did not start app-server transport or a provider job. Python metadata reads checked helper uid/mode, kernel settings, directory writability, default socket existence and `/proc/net/unix`; generated local JSON schemas and adapter source were read. No credential contents, account/catalog endpoint, native initialization or model turn were accessed.

If the host later supplies materially new supported setup, run the existing `npm run test:electron` from `desktop/` with the sandbox preserved. Codex readiness remains an explicit authenticated runtime action; it must not run automatically from UI status reads. Successful initialize/catalog/account checks would still leave production execution blocked until the independent USD contract is verified. No change to spending guards is proposed here.

Exact prior outcomes and current source/schema hashes are recorded in [native-supported-paths.json](../evidence/desktop/native-supported-paths.json), [electron-smoke.json](../evidence/desktop/electron-smoke.json), [B2-readiness.json](../evidence/B/B2-readiness.json) and [native-setup-diagnosis.json](../evidence/B/native-setup-diagnosis.json). Worker ownership, conversation rendering and task-specific board associations are separate product work; this host report does not mark them complete or make them contingent on a model demonstration.
