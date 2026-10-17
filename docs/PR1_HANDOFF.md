# Current follow-up — 2026-10-17

The earlier handoff below is historical. The active repair adds a single `sidequest.py setup/run/doctor` entry point, supervised runtime + office launch, process-only local API authentication, one-commit Git support, actionable Electron startup failure handling, safe provider startup diagnostics and fresh/stale readiness handling. The application suites and build now run in CI. Browser evidence can be redirected without overwriting prior captures.

Start with the [quick start](../README.md) and [new verification record](../evidence/desktop/startup-20261017/README.md). **Native Electron and live coding acceptance remain blocked; PR #1 stays draft.** No sandbox, spending or permission gate was weakened. No credentials were copied or persisted, and no model turn, merge, deployment or release was performed.

---

# PR #1 handoff

Branch: `feat/electron-office-diff`. PR: <https://github.com/ShadowKingYT444/sidequest/pull/1>. Keep the PR draft until native/live acceptance is established. This handoff changes documentation only and proposes future work without implementing it.

## Implemented and verified scope

- Electron/React/TypeScript with React Three Fiber/Drei binds the original office assets. Close office framing, slim bars, compact ready-provider logo/name picker, task notifications and primary-figure badges preserve the approved design. Executable discovery alone never means connected or ready.
- Physical monitor selection approaches its measured screen and shows recorded trace/output plus a thin composer. Files shows genuine committed Git or immutable job artifacts in one lazy read-only Monaco editor. Expand/Escape preserve camera, file/editor selection, drafts, local attachments and scroll.
- Python/FastAPI/SQLite owns projects, jobs, recorded runs, immutable candidates, checks, command receipts and permission/budget gates. Local Git inspection is real and makes zero inference calls.
- Guarded follow-up transport stages supported bytes under opaque run-bound IDs, persists exact command UUID/payload/revision, retains the original goal/scope/checks/worker and anchored provider thread, restores prior frozen edits safely, and records trace-only completion without invented Git candidates. Interrupted dispatch is uncertain and cannot replay through legacy Resume.
- A successful queue acknowledgement now preserves its receipt and original sent text/File snapshot until a verified outcome. Rejection before dispatch survives reload; explicit review/restore retains the newer draft separately. Corrupt or incomplete recovery records fail closed. The successful-reply regression verifies one send only.
- Assigned jobs remain available beyond the latest-20 history, and bounded active-job overflow is disclosed. Subscription quota/reserve observations remain separate from USD authority and cannot authorize dispatch.

These facts establish browser/local-Git/protocol behavior. They do not establish native Electron or live provider acceptance.

## Verified checkpoints and evidence

| Check | Exact result | Evidence |
| --- | --- | --- |
| Latest functional source | `af4420cf1993ab6a0ede1fcb180b8a2ce2ebb25f` | [Frozen run/source hashes](../evidence/desktop/acknowledged-rejection/full-run.json) |
| Published repair/evidence checkpoint before handoff | `cf5fda740c7827a95efd305c8c582396241560f7` | [Verification](../evidence/desktop/acknowledged-rejection/verification.json) |
| Full browser suite | 25 passed, 0 failed/skipped, retries 0, exit 0, 11.3 minutes; all 318 frozen file hashes unchanged | [Full log](../evidence/desktop/acknowledged-rejection/full-browser.log) |
| Desktop/store | 82 desktop tests including 19 store regressions pass | [Desktop log](../evidence/desktop/acknowledged-rejection/desktop-unit.log), [store log](../evidence/desktop/acknowledged-rejection/green-store-final.log) |
| Runtime | 65 tests pass | [Runtime log](../evidence/desktop/acknowledged-rejection/runtime-unit.log) |
| Provider/tools | Inherited 56-test pass; provider source unchanged and not rerun for the renderer repair | [Provider log](../evidence/A/session-transport/tools-final.log) |
| TypeScript/production build | Pass | [Build log](../evidence/desktop/acknowledged-rejection/build.log) |
| Preservation | All 126 protected asset hashes and prior failed/passed logs unchanged | [Preservation](../evidence/desktop/acknowledged-rejection/preservation-after.json) |
| Current CI scope | `Launch kit checks` runs offline development-controller tests and `dev/check.py --setup`; it does not run the desktop/browser/native/live suites | [Workflow](../.github/workflows/launch-kit.yml) |

The browser suite includes 20 office/editor/inspection/accessibility cases and five explicitly protocol-fake composer cases. Image recovery at 390px passes automated WCAG A/AA checks. The real Git tests inspect the pinned small project within unchanged repository/output guards; the asset-heavy full PR checkout exceeds those original guards.

The original 19:54 UTC deadline on October 14, 2026 was missed. Earlier incomplete checkpoints and failed logs are preserved as historical evidence, not current acceptance claims. The last source repair adds the successful-202 path that the earlier lost-reply regression missed; its red unit and Chromium evidence remains in [the repair directory](../evidence/desktop/acknowledged-rejection/README.md).

Screenshots: [office overview](../evidence/desktop/acknowledged-rejection/full-captures/setup-desktop.png), [monitor/local composer](../evidence/desktop/acknowledged-rejection/full-captures/monitor-pov-local-draft.png), [original and newer draft recovery](../evidence/desktop/acknowledged-rejection/full-composer-captures/acknowledged-rejection-restored.png). The recovery image is explicitly protocol-fake. The monitor shows a zero-model Git inspection and unavailable sending. No screenshot proves live model execution.

## Current issues and acceptance gaps

| Priority | Issue or boundary | Present outcome | Required acceptance |
| --- | --- | --- | --- |
| P0 | Native Electron sandbox/display | Preserved startup SIGTRAP (-5); helper uid 1000/mode 0755 and absent display. Startup was not repeated in this handoff. | A supported managed desktop host starts Electron with its sandbox intact; isolated IPC, clipboard, office/monitor, Files/Trace and Escape flows pass in a native window. |
| P0 | Codex protected runtime state | Preserved read-only initialization EROFS (os error 30), zero responses. Existing CLI login is not proof of app-server reachability. | Supported writable runtime layout or existing authorized endpoint initializes using the original account locator; no credential copying or permission bypass. |
| P0 | USD/quota authority | No verified enforceable USD ceiling; real quota and hard 10% subscription reserve remain unknown. Production dispatch is denied before provider process/thread/turn creation. | Fresh authoritative account/catalog/consent/source checks plus enforceable USD and reserve controls prevent exceeding the approved limits or falling back to purchased credits. Unknown inputs stay blocked. |
| P0 | Native/live end-to-end orchestration | No successful native coding run, live follow-up/attachment, reconnect, or full delivery acceptance has been demonstrated. Protocol fakes are labeled. | After prerequisites and explicit authorization, verify one bounded disposable job, anchored follow-up with supported bytes, restart/receipt reconciliation, candidate/check identity and exact approved delivery. Prove no duplicate turn or unapproved write. |
| P1 | Provider support | Only Codex has a dispatch adapter; other provider views are metadata/settings surfaces. | Keep unsupported choices unavailable; any later adapter needs its own proven identity, scope, spending, consent and recovery contract. |
| P1 | Attachment and repository limits | Local staging: 10 files, 10 MiB each, 25 MiB/run. Provider input: UTF-8 text and PNG/JPEG/GIF/WebP, at most 1 MiB combined. PDF/oversized provider inputs remain local. Full PR art/evidence exceeds unchanged inspection guards. | Preserve explicit unavailable states and existing guards. Use a trusted project within the caps for baseline validation; any proposed expansion needs separate limits and tests. |

Exact preserved host actions and failures: [host verification](../evidence/desktop/full-product-20261014/verification.json), [native record](../evidence/desktop/full-product-20261014/native-startup.json), [Codex initialization record](../evidence/desktop/full-product-20261014/codex-initialize.json). That older verification's “transport unimplemented” entry is historical; transport is now implemented and protocol-tested, with live acceptance still blocked.

## Reproducible offline and browser checks

Use Python 3.12, Node 24, Git, committed dependency locks and Chromium. Install into local ignored dependency directories using [RUN_EVALS.md](RUN_EVALS.md). From the repository root:

```sh
npm --prefix desktop test
npm --prefix desktop run build
.venv/bin/python -m unittest discover -s services/runtime/tests -p 'test_*.py' -v
.venv/bin/python -m unittest discover -s services/tools/tests -p 'test_*.py' -v
python3 -m unittest discover -s dev -p 'test_*.py' -v
python3 dev/check.py --setup
```

For a focused receipt/recovery check:

```sh
node --test desktop/tests/session-drafts.test.mjs
cd desktop
CHROMIUM_PATH=/usr/bin/chromium CI=1 npm run test:browser -- transport.spec.ts --retries=0
```

The full integrated suite requires a clean trusted Git project with a committed long diff and an authenticated local runtime. Choose unused temporary directories and preserve existing ones. The previously tested project is real revision `8a9fb11c3b01a404c4dd305b71458377082697c1`, with base `69bf066`:

```sh
git clone --no-local /absolute/path/to/sidequest /tmp/sidequest-handoff-source
git -C /tmp/sidequest-handoff-source switch --detach 8a9fb11c3b01a404c4dd305b71458377082697c1
```

Terminal 1, repository root:

```sh
SIDEQUEST_CODEX_ENABLED=false .venv/bin/python -m services.runtime.main \
  --allowed-root /tmp/sidequest-handoff-source \
  --data-dir /tmp/sidequest-handoff-data \
  --config-dir /tmp/sidequest-handoff-config \
  --runtime-dir /tmp/sidequest-handoff-runtime
```

Terminal 2, `desktop/`:

```sh
SIDEQUEST_REPO=/tmp/sidequest-handoff-source SIDEQUEST_BASE=69bf066 \
SIDEQUEST_RUNTIME_URL=http://127.0.0.1:4317 \
SIDEQUEST_API_TOKEN_FILE=/tmp/sidequest-handoff-config/session.token \
SIDEQUEST_TEST_INSPECTION=1 CHROMIUM_PATH=/usr/bin/chromium CI=1 \
npm run test:browser -- --retries=0
```

This full suite submits only deterministic zero-budget Git inspections; composer provider responses are explicit fakes. Run one browser suite at a time. Capture source hashes before/after, retain every failure and label fixtures. The archived [frozen-run wrapper](../evidence/desktop/acknowledged-rejection/run-frozen-browser.py) documents the exact prior environment and preservation procedure; its hardcoded machine paths must not overwrite prior evidence. Native instructions in RUN_EVALS.md are for a later supported host, not a request to repeat blocked probes now.

## Next owner

1. Fetch the PR branch normally and verify its remote SHA. Read this handoff and the exact frozen verification. Treat later documentation-only commits separately from tested functional source.
2. Confirm all non-documentation source/config/test hashes still match the frozen manifest and original assets/logs remain intact. Rerun only checks justified by subsequent source changes or unresolved failures; passing offline CI does not certify native/live acceptance.
3. Resolve the P0 host and authority prerequisites through supported configuration. Keep all current gates closed while any requirement remains unknown; do not fix the host by weakening the sandbox, copying credentials, or changing protected permissions.
4. Obtain explicit authorization for any future bounded live validation. Record source, account/model/effort, quota/reserve authority, USD ceiling, exact intent/receipt/run/candidate/check identity and measured outcome. Do not automatically repeat an uncertain turn.
5. Keep PR1 draft until native and live acceptance criteria pass. Exact delivery, merge, deployment and release remain separate approval actions.

## Proposed future additions — not implemented by this handoff

These are prioritized proposals for later scoping, not bugs fixed here, accepted requirements, or permission to start more work.

| Priority | Proposal | Acceptance before claiming completion |
| --- | --- | --- |
| P1 | Extend offline CI to desktop/runtime/provider unit checks, production build and asset preservation, with a controlled browser job | Pinned environment; zero model calls; retries disabled; archived terminal/source evidence; blocked native/live gates remain distinct. |
| P1 | Session archive/search and user-controlled draft/attachment retention cleanup | Older assigned runs remain visible; bounded queries; explicit local cleanup; no silent loss of acknowledged or uncertain sends. |
| P2 | Exact-candidate preview and opt-in before/after screenshot evidence | Explicit capture consent; bounded local scope; timestamps/candidate identity; privacy filtering; no background cloud vision. |
| P2 | Complete reusable workshop recipe/activation UI around the existing trusted-check foundation | Supported and unsupported cases tested; exact immutable recipe/check identity; activation approval; no unbudgeted replanning or delivery. |
| P2 | Reproducible native packaging and release checks after native acceptance | Supported sandbox-preserving host; verified IPC/clipboard; provenance and update/release checks; publishing remains separately authorized. |
| P3 | Additional provider adapters and separately scoped attachment formats | Per-provider account/model/budget/reserve enforcement and reconnect/idempotency tests; no silent fallback, credential sharing or unsupported-file passthrough. |

## Repository cleanup and exclusions

Completed implementation, tests, logs and screenshots were already committed at the repair/evidence checkpoints. The main checkout and all five isolated worktrees were clean; their patches are already included or patch-equivalent on the PR branch. Keep originals and worktrees intact.

`.venv/`, `desktop/node_modules/`, `desktop/dist/`, `desktop/test-results/` and Python caches stay ignored. Saved test-result copies belong in evidence. `.sidequest/` remains ignored machine-local handoff and private runtime/SQLite/probe state; sanitized failure evidence is already committed. Do not publish raw account/runtime databases, credentials, local Library metadata or unrelated temporary helper files. [Worktree audit](../evidence/desktop/pr1-handoff/worktree-audit.json) records the completed-work check.
