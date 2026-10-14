# Sidequest desktop slice

Electron hosts React/TypeScript. React Three Fiber/Drei binds the supplied office GLB, and a selected computer opens one lazy read-only Monaco diff editor. Expand moves that selection into a flat reading panel; Escape returns to the office and retains the selected file, cursor/selection and editor scroll state. Non-selected monitors use small previews. The office renders on demand and stops rendering while hidden; decorative animation is not started.

**Current verified state:** the browser can inspect real committed Git changes, expand, scroll, return and reopen. The persistent runtime, authenticated artifact API, independent Git clones and trusted frozen-candidate checks are implemented. The jobs board has completed a genuine UI/HTTP/Git/check inspection and displayed its immutable files and check report. That fixed profile makes zero model calls, spends zero provider dollars and performs no source delivery. The Codex app-server adapter and persisted task/session lifecycle are implemented and tested with a fake transport; native coding execution remains blocked. The repository originally contained specifications and development tooling only; these services implement the specified boundaries.

**Unverified:** the actual office assets are located in the owner's Drive archive but have not transferred into this VM. Its proxy returns 403 for authenticated transfer URLs. No real office render, texture/material match, animation playback or monitor alignment has passed. Native Electron startup is blocked by the VM's unusable Linux sandbox helper/user namespace support. The browser screenshots are actual browser captures of Git data, not office mockups or desktop runtime proof.

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

When assets are absent, the setup screen offers **Inspect local Git diff**. This is an accessible fallback for testing the viewer, not a substitute office or a working worker session.

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

## Bind the actual office

Protected source: [the owner's October 7 art kit](https://drive.google.com/drive/folders/1J69rRCIT03-AFo9A0WqwEc7CQswM4rlY). Eight archive parts concatenate, in numerical order, to 535,951,540 bytes. Expected archive SHA-256:

```text
f7159fbda50771486d65e1a5bd2a42d265120a422d88a686471a9bbb6fb60a95
```

Retain the archive and `scene/Sidequest_Office_Master.blend` outside Git. Do not run bundled scripts automatically. The runtime GLB is `scene/Sidequest_Runtime_Environment_Batched.glb`; copy only a validated runtime export and its required local resources into `desktop/public/office/`. These local art inputs and built `dist/` are ignored by Git. Preserve the asset bytes and record source/copy hashes.

```sh
cd desktop
python3 scripts/install-office.py --parts-directory /absolute/path/to/parts
npm run inspect:office
```

The safe installer checks archive identity and paths before copying art. The inspector reports the actual SHA, material/texture metadata, clips, local resources and transformed bounds. This metadata is not proof of visual compatibility. Draco loading is disabled to prevent the default decoder CDN request; if the inspected GLB requires Draco, bundle and validate a local decoder before enabling it.

Create `public/office/bindings.json` using measured anchors from the real scene, with this shape (the strings/vectors below describe fields, not a runnable or fabricated layout):

```text
modelUrl: /office/office.glb
overview: { position: [x,y,z], target: [x,y,z] }
stations: [{ id, label, workerId?, anchor: [x,y,z], rotation: [x,y,z],
             screenSize: [width,height], focus: { position, target } }]
board?: { anchor, rotation, size }
```

IDs must be stable and unique; camera/anchor vectors finite; screen sizes positive. Bind roles to existing monitor surfaces; do not add desks or rebuild the room. Computers currently expose the host-configured committed repository and state that agent execution is unavailable. A worker label alone must never imply a live assignment. The bound board opens the existing jobs panel. Rebuild after installing assets for Electron, then verify actual object selection, focus-camera movement, in-world diff readability, board targeting and the expanded view. Worker-specific run resolution and additional artifact tabs remain future work.

## Run the local jobs board

Install the Python runtime/check locks and start the host as described in [RUN_EVALS.md](../docs/RUN_EVALS.md#integrated-job-acceptance). Use a clean, trusted source repository and dedicated state directories outside Git. In another terminal:

```sh
cd desktop
SIDEQUEST_REPO=/absolute/path/to/clean/repository SIDEQUEST_BASE=HEAD~1 \
SIDEQUEST_RUNTIME_URL=http://127.0.0.1:4317 \
SIDEQUEST_API_TOKEN_FILE=/absolute/path/to/private-config/session.token npm run dev
```

For Electron, pass the same host variables to `npm start` after building. The private app-session token stays in the host process; the renderer receives no token or arbitrary path access. Open **Jobs**, register the configured repository, submit an inspection, review the queued job, and explicitly click **Run inspection**. The panel reads status, immutable files, diff rows, reports and recent events. Artifact/file/text/diff pages have explicit navigation. JSON reports are formatted and all source/log text stays literal. Escape closes the board and preserves the selected artifact. Polling stops while the panel or window is hidden.

The deterministic inspection clones the registered commit unchanged, so its candidate diff is empty. The computer viewer separately compares the configured committed base and HEAD. Completed checks make inspection results ready, while the backend keeps `verifying` with source delivery disabled. This is a genuine local job pipeline, not a coding-agent demonstration.

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

The Electron smoke script deliberately starts the native executable directly; Playwright's convenience Electron launcher adds a sandbox-disabling flag and is not valid evidence for this boundary. Screenshots and machine-readable results are under `../evidence/desktop/`.

Monaco's diff engine and Three.js remain sizeable dependencies: approximately 695 kB and 271 kB compressed in separate lazy chunks, respectively, on the recorded build. They are not loaded as independent editors for every desk. No owner-device frame-rate or memory claim has been measured.

## Security and remaining integration

The renderer is sandboxed with context isolation and Node integration disabled. Its preload exposes fixed Git reads and a narrow runtime capability object. IPC validates the current window/main frame, origin, method, argument count and values. Repository registration uses the host-configured path; submission constructs the fixed inspection profile. No renderer-supplied filesystem path, shell command, API credential or arbitrary IPC channel is accepted. Execution additionally requires the runtime's explicit local-inspection capability and backend policy. App files are allowlisted beneath `dist`, with realpath containment; navigation, popups, downloads, webviews and capture permissions are denied. Capture remains an explicit future permission flow. Source text is rendered literally, and hyperlinks in Monaco are disabled.

Git uses argv with `shell: false`, disabled external diff/textconv/hooks/fsmonitor, scrubbed inherited Git environment variables, pinned immutable blob IDs, output/time/file/concurrency limits, and generic errors. Filename and common credential-material filters are heuristic, not a full secret scanner. Configure a trusted repository that has been checked for secrets; unknown secret formats may still be present in ordinary source files. Likely sensitive content is withheld with an explicit reason rather than mislabeled as binary.

Codex host setup, readiness refresh and persisted task lifecycle are described in [services/runtime/README.md](../services/runtime/README.md). Status refresh reads cached state and launches no model process or turn. The installed CLI reports an existing ChatGPT login, but its native app-server fails before initialization because protected runtime state is read-only; no catalog/model/effort or account response has been verified. Its protocol also lacks a verified enforceable USD ceiling, so production coding execution is blocked before thread/turn creation. Synthetic lifecycle tests are explicitly fixture evidence.

Next steps are: obtain the actual art through an authorized working transfer route, inspect original/copy hashes and visually bind monitors/camera/materials; run Electron on a sandbox-capable host; resolve native Codex runtime-state and enforceable budget readiness before seeking authorization for a tiny real turn; then resolve desks to actual runs and add screenshots/workshops/capture and exact delivery approval flows. No merge or deployment is requested.
