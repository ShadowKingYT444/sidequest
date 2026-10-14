# Sidequest desktop slice

Electron hosts React/TypeScript. React Three Fiber/Drei binds the supplied office GLB, and a selected computer opens one lazy read-only Monaco diff editor. Expand moves that selection into a flat reading panel; Escape returns to the office and retains the selected file, cursor/selection and editor scroll state. Non-selected monitors use small previews. The office renders on demand and stops rendering while hidden; decorative animation is not started.

**Current scope:** the original office and all 26 staged reference figures are imported, with 24 measured monitors. Materials, local textures, original geometry and authored transforms are preserved. The original 131 MB embedded environment was made Git-compatible by relocating its 90 image payloads byte-for-byte into local files; no art was replaced or recompressed. Seven human GLBs retain all 28 original clips, and 20 staged caps use the supplied fit/identity resources. Reference poses are sampled once and explicitly remain disconnected artwork.

The office uses the camera and lighting preset supplied after the parent reviewed the owner's reference pixels, with slim bars and one contextual card beside the selected object. Click a monitor for committed Git/files/results, the actual board for a compact task detail, a figure for its truthful session view, or the original workstation pick bounds for the detected-provider/prompt layer. Open task expands the board detail into the existing Jobs panel. The footer selector is a keyboard alternative. Settings follow pinned T3 Code source and remain a transient screen. Provider discovery checks metadata only; launch is restricted to installed Codex because that is the implemented runtime adapter. Submit and Launch remain distinct, explicit, backend-gated actions; no demonstration coding job is launched.

The browser has performed a genuine local Git inspection/check job and read its immutable files/report/activity through the existing Python/SQLite runtime. That profile has zero model calls and no source delivery. Native Codex lifecycle tests use a fake transport. **Native Electron remains blocked by the VM OS sandbox, and native Codex by protected runtime-state operations plus unverified USD enforcement.** Browser captures establish browser rendering and interactions only. Original office compatibility is recorded separately from native acceptance in `../evidence/desktop/original-office/`.

## Run in a browser

Requires Node 24.x and installed Git. From the repository root:

```sh
cd desktop
npm ci
# Configure a trusted local Git worktree root. Both revisions must be commits.
SIDEQUEST_REPO=/absolute/path/to/repository SIDEQUEST_BASE=HEAD~1 npm run dev
```

Open `http://127.0.0.1:5173`. The development adapter binds only that loopback address/port and rejects other origins. Git endpoints support GET reads only; the separate runtime proxy accepts only fixed JSON methods from the local origin. With no `SIDEQUEST_REPO`, browser development reads the Sidequest checkout one level above `desktop/`. The initial viewer evidence inspected base `69bf06696a93c9f58eee2d088e84404d4f6563d6` and candidate `674f1477efb7327fe46fbe3aa6f5d622766c1723`; later verification records identify the exact revisions used.

The host pins `SIDEQUEST_BASE` and `HEAD` when it starts. Refresh re-reads that pinned manifest/diff; it does not switch candidates mid-review. Restart the host to inspect a newly committed candidate. Dirty working files are not displayed. An initial repository without a parent commit needs an explicit valid base commit. Empty, binary, withheld, oversized and unavailable reads have explicit states.

When assets are absent, an explicit original-office-pending state offers **Inspect local Git diff** and the existing Jobs panel. A repository viewer can display actual selected results while original desk bindings are pending. No fallback geometry is presented. Settings offers six provider views plus focused Cost/Tokens/Limits screens; selection and refresh are functional, paths are read-only, and no provider process or model turn is launched. Installed means only executable metadata was found; authentication and service reachability are shown separately as unknown. The detector checks bounded PATH and documented install locations, including current Cursor `agent` and Antigravity `agy`, without scanning directories or reading config/credentials/sessions. If automatic discovery fails, an operator can supply `SIDEQUEST_CODEX_EXECUTABLE`, `SIDEQUEST_CLAUDE_EXECUTABLE`, `SIDEQUEST_CURSOR_EXECUTABLE`, `SIDEQUEST_GROK_EXECUTABLE`, `SIDEQUEST_OPENCODE_EXECUTABLE` or `SIDEQUEST_ANTIGRAVITY_EXECUTABLE` as an absolute executable locator when starting the host. This fallback validates metadata only and grants no execution or account permission. The independent tank component represents fraction USED; T3-style quota rows represent REMAINING. Missing telemetry shows unknown, with no fabricated fill or chart. The tank is not mounted into a substitute office.

## Run Electron

```sh
cd desktop
npm ci
npm run install:electron
npm run build
SIDEQUEST_REPO=/absolute/path/to/repository SIDEQUEST_BASE=HEAD~1 npm start
```

Current Electron installs its runtime through `install-electron`; merely installing the npm package is not sufficient. The default startup loads the built local `app://sidequest/index.html`, not Vite. To test the Electron shell against Vite, start `npm run dev` separately, then:

```sh
SIDEQUEST_REPO=/absolute/path/to/repository \
SIDEQUEST_DEV_SERVER_URL=http://127.0.0.1:5173 npm start
```

For this VM's writable cache and proxy configuration, the runtime installation succeeded with:

```sh
NODE_USE_ENV_PROXY=1 electron_config_cache=/tmp/sidequest-electron npm run install:electron
```

A desktop session and supported OS sandbox are required. This VM's direct native launch aborted because `chrome-sandbox` is not root-owned mode 4755 and unprivileged namespaces do not provide a usable alternative. Do not disable the sandbox to make the smoke check pass. No root ownership, system permissions or account configuration was changed.

## Original office provenance and bindings

The approved October 7 Drive archive was recovered in the separate authorized asset environment. All eight parts reconstruct **535,951,540 bytes**, SHA-256 `f7159fbda50771486d65e1a5bd2a42d265120a422d88a686471a9bbb6fb60a95`. Originals, native `Sidequest_Office_Master.blend` and the original embedded runtime export remain outside Git in that environment. No bundled archive scripts ran. The imported runtime assets are tracked in `public/office/` and copied to `dist/office/` during build.

See [original-office evidence](../evidence/desktop/original-office/README.md) and `public/office/provenance.json` for archive/source/output hashes. All 24 monitor surfaces match the original runtime geometry within 0.00000154 metres. `bindings.json` retains stable `parent_001`–`parent_024` IDs, measured screen dimensions/focus cameras and the actual board surface. The overview uses camera `[11.5, 8.5, 12]`, target `[1, -0.3, -3.8]`, FOV 40 and ACES exposure 1.2. Six original glass meshes are excluded from opaque shadow casting; their materials and geometry stay intact. Desk focus poses remain unchanged. Desk picking uses the original `PickBounds` metadata, not replacement furniture.

Both Draco and Meshopt loading are disabled: the imported assets require neither decoder. Embedded actor/cap images use Three TextureLoader under the existing `img-src blob:` permission; CSP is unchanged. Only UI previews are drawn onto small monitor textures. The original room materials/textures are intact, no blur/postprocessing is used, and only the selected work mounts a full editor. Actors and status refresh never imply working agents. Assigning a job as a result display stores station/job/project IDs only, without assigning an actual worker or starting a model.

For a future manual asset recovery, `scripts/install-office.py` and `scripts/inspect-assets.mjs` remain available. Do not overwrite the tracked measured imports with a new unverified export or fabricate anchors.

## Run the local jobs board

Install the Python runtime/check locks and start the host as described in [RUN_EVALS.md](../docs/RUN_EVALS.md#integrated-job-acceptance). Use a clean, trusted source repository and dedicated state directories outside Git. In another terminal:

```sh
cd desktop
SIDEQUEST_REPO=/absolute/path/to/clean/repository SIDEQUEST_BASE=HEAD~1 \
SIDEQUEST_RUNTIME_URL=http://127.0.0.1:4317 \
SIDEQUEST_API_TOKEN_FILE=/absolute/path/to/private-config/session.token npm run dev
```

For Electron, pass the same host variables to `npm start` after building. The private app-session token stays in the host process; the renderer receives no token or arbitrary path access. Open **Jobs**, register the configured repository, submit an inspection, review the queued job, and explicitly click **Run inspection**. The panel reads status, immutable files, diff rows, reports and recent events. Use **Assign result display** to read the selected job at a computer, with Expand/Escape continuity. The coding form has separate submit/run and explicit project proposal permission, but stays disabled without verified host/catalog/model/effort/consent and an enforced USD ceiling. Artifact/file/text/diff pages have explicit navigation. JSON reports are formatted and all source/log text stays literal. Escape closes the board and preserves the selected artifact. Polling stops while the panel or window is hidden.

The deterministic inspection clones the registered commit unchanged, so its candidate diff is empty. The computer viewer separately compares the configured committed base and HEAD. Completed checks make inspection results ready, while the backend keeps `verifying` with source delivery disabled. This is a genuine local job pipeline, not a coding-agent demonstration.

## Recorded session ownership and conversation

Click a figure, open **Attach recorded session**, select an actual task/run and click **Assign session**. SQLite stores the station, job, run, worker and project relationship. One recorded worker/run can occupy one station; occupied stations and conflicting identities are rejected. **Detach session** clears only this presentation relationship. Neither action starts, moves, resumes or cancels execution, changes project permissions or grants spending. Result display assignment stays separate.

The figure shows its persisted task/worker/run identity and **Conversation & events**. Expanding it reads the existing bounded run-event adapter; the original task request and event/output text remain literal. Recorded usage shows actual nullable token/cost fields, keeping unknown and uncertain values explicit. The run is pinned to its saved worker; a changed worker identity is rejected and previous data is labeled last known. Reads pause when hidden/collapsed; completed runs stop polling. **Open results** opens the same job's immutable artifacts. The selected board task links to its recorded station/session.

The existing browser harness uses a real completed zero-model inspection to verify ownership across reload, contextual events, same-job results, board navigation, narrow accessibility and explicit detach. A wrong-worker response is labeled as a test fixture and never changes persisted data. This proves recorded ownership and a read-only conversation/event view. Sending conversational turns and native orchestration remain incomplete. Provider quota/reset telemetry remains unknown; per-run recorded usage is available.

[Native host status](../docs/NATIVE_HOST_STATUS.md) documents the read-only supported-path investigation. No existing authenticated daemon or supported sandbox/runtime-state setup was found; the independent USD gate remains enforced.

## Verification

```sh
cd desktop
npm test
npm run typecheck
npm run build
# Requires a Chromium binary; set CHROMIUM_PATH if it is not /usr/bin/chromium.
npm run test:browser
# Requires a working desktop session and OS sandbox; returns 2 when blocked.
SIDEQUEST_REPO=/absolute/path/to/repository npm run test:electron
```

Unit tests use temporary Git repositories and clearly synthetic GLB/archive fixtures. Browser tests inspect genuine committed Sidequest Git data and verify single lazy editor mounting, selection/scroll continuity, Escape/focus return, reduced motion, 1440/960/390px layout and same-origin/read-only API restrictions. Security tests cover sensitive files, symlinks, hostile names, inherited Git environment/config commands, opaque IDs, IPC sender validation and safe app protocol serving.

The previous complete office slice passed all 10 browser tests (six viewer, two settings/blocked-launcher/session, two genuine local inspections), 28 desktop component/security tests, 42 runtime tests and 42 tools tests. The physical scene probe separately clicked an original monitor, actor, workstation and board with no page/console errors. The result scroll regression preserves 180px after Expand, Settings, Escape and reopening; restoration waits for the actual body instead of a loading placeholder. These results and current source hashes are in [verification.json](../evidence/desktop/verification.json). Use [RUN_EVALS.md](../docs/RUN_EVALS.md) for dependency setup, the long Git revision range and the opt-in 10-test command.

The Electron smoke script deliberately starts the native executable directly; Playwright's convenience Electron launcher adds a sandbox-disabling flag and is not valid evidence for this boundary. Screenshots and machine-readable results are under `../evidence/desktop/`.

Monaco's diff engine and Three.js remain sizeable dependencies: approximately 696 kB and 273 kB compressed in separate lazy chunks, respectively, on the recorded build. They are not loaded as independent editors for every desk. No owner-device frame-rate or memory claim has been measured.

## Security and remaining integration

The renderer is sandboxed with context isolation and Node integration disabled. Its preload exposes fixed Git reads and a narrow runtime capability object. IPC validates the current window/main frame, origin, method, argument count and values. Repository registration uses the host-configured path; submission constructs the fixed inspection profile. No renderer-supplied filesystem path, shell command, API credential or arbitrary IPC channel is accepted. Execution additionally requires the runtime's explicit local-inspection capability and backend policy. App files are allowlisted beneath `dist`, with realpath containment; navigation, popups, downloads, webviews and capture permissions are denied. Capture remains an explicit future permission flow. Source text is rendered literally, and hyperlinks in Monaco are disabled.

Git uses argv with `shell: false`, disabled external diff/textconv/hooks/fsmonitor, scrubbed inherited Git environment variables, pinned immutable blob IDs, output/time/file/concurrency limits, and generic errors. Filename and common credential-material filters are heuristic, not a full secret scanner. Configure a trusted repository that has been checked for secrets; unknown secret formats may still be present in ordinary source files. Likely sensitive content is withheld with an explicit reason rather than mislabeled as binary.

Codex host setup, readiness refresh and persisted task lifecycle are described in [services/runtime/README.md](../services/runtime/README.md). Status refresh reads cached state and launches no model process or turn. The installed CLI reports an existing ChatGPT login, but its native app-server fails before initialization because protected runtime state is read-only; no catalog/model/effort or account response has been verified. Its protocol also lacks a verified enforceable USD ceiling, so production coding execution is blocked before thread/turn creation. Synthetic lifecycle tests are explicitly fixture evidence.

Next steps are: run Electron on a sandbox-capable host; resolve native Codex runtime-state and enforceable budget readiness before seeking authorization for a tiny real turn; then connect actual worker/session ownership and usage telemetry, and add screenshots/workshops/capture and exact delivery approval flows. No merge or deployment is requested.

The session continuation passes 30 desktop and 48 runtime tests with a current production build. The extended browser run passed the existing 10 tests and exposed one mobile disclosure target-size failure in the new session test. The target was enlarged without weakening the check; session-browser.log and verification.json record the focused repaired rerun separately.

## Final complete browser run — 10:13 UTC

Ran the full 11-test suite exactly once on repaired source `cc9d70a71825d5434ad0d7c8a2330395c08a1da5`, with retries disabled and all 94 source hashes unchanged before/after. Terminal result: **exit 1; 10 passed, 1 failed in 8.9 minutes**. The recorded-session ownership test and mobile accessibility pass. The viewer test fails at `viewer.spec.ts:39`: after Escape/reopening Computer 19, the expected Monaco `diff-editor` is absent at 15 seconds; the page snapshot contains original/modified read-only fallback textboxes. Cause remains unconfirmed. No fix, retry, model/native run or feature change was performed.

Exact command, source identity, terminal counts, failure context and log hashes are in `evidence/desktop/final-11-run.json`; full output is `final-11-browser.log`; assertion snapshot is `final-11-viewer-error-context.md`. Previous target-size failure and focused repair proof remain separate. This result leaves full-suite acceptance unresolved; it does not certify native orchestration.

## Monaco reopen repair

The lifecycle defect is reproduced: on reopening, the previous diff renders immediately, then the visibility-dependent read effect clears it and fetches the same pinned data, destroying that editor and constructing a second. The targeted regression fails on unrepaired code with two mounts and passes after the fix with one mount, saved scroll and a fresh read on explicit Refresh. The last successful read is paired with refresh generation, both pinned revisions and file ID; mismatched reads never render. Cache retention is bounded to one diff.

The captured read-only textboxes are also part of Monaco's normal accessibility DOM; they alone did not prove a fallback. The diagnostic run recorded no Monaco exception. DiffEditor.tsx, read-only/accessibility behavior and the original assertions/timeouts are unchanged. The original viewer test and the new regression pass; typecheck/build and 30 desktop tests pass. Full 12-test verification on published repair f6b8a19 is running. Evidence: monaco-reopen-repair.json, the red/green logs and DOM traces. No backend, asset, model/native or feature changes were made.

## Final Monaco repair verification — 11:00 UTC

**Full suite passed: 12/12, exit 0, retries disabled, 9.9 minutes**, on published repair `f6b8a1921e3000de82268b1878a090fd900b0560`. All 94 code/configuration hashes match before/after. The new regression reproduces two editor mounts on unrepaired code and verifies one after repair, saved scroll and fresh Git reading on explicit Refresh. The original viewer assertions and timeouts remain unchanged; its previously failing Escape/reopen flow passes in the full suite. Read-only/accessibility behavior is unchanged. Typecheck/build and 30 desktop tests pass.

Cause and scoped fix are established; the earlier textbox snapshot was insufficient evidence of fallback, because normal Monaco exposes those accessibility textboxes. Prior full-run failures, the red regression and diagnostic trace remain preserved. Current terminal record/log: `repaired-12-run.json` and `repaired-12-browser.log`; cause/fix record: `monaco-reopen-repair.json`. No model calls, native attempts, backend/asset changes or new product features. Native host/USD gates and interactive orchestration remain incomplete.
