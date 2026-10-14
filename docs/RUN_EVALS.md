# Run local evaluations

These checks use local Git/SQLite fixtures, deterministic checks and browser automation. They do not start Codex jobs, contact a model provider, spend money or restart the cancelled Cooki evaluations. Run from the repository root unless a block says otherwise.

## Install dependencies

Python 3.12, Git and Node 24 are required. Use an isolated Python environment and the committed dependency locks:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r services/runtime/requirements.lock
.venv/bin/python -m pip install -r services/workshops/requirements.lock
npm_config_cache=/tmp/sidequest-npm npm --prefix desktop ci
```

Browser checks require Chromium. This VM has `/usr/bin/chromium`. On another host, set `CHROMIUM_PATH` for the desktop browser suite or install the Playwright Chromium runtime separately. Native Electron also requires a desktop session and a working OS sandbox.

## Component and security evaluations

```sh
.venv/bin/python -m unittest discover -s services/runtime/tests -p 'test_*.py' -v
.venv/bin/python -m unittest discover -s services/tools/tests -p 'test_*.py' -v
.venv/bin/python -m unittest discover -s services/workshops/tests -p 'test_*.py' -v
.venv/bin/python -m unittest discover -s dev -p 'test_*.py' -q
npm --prefix desktop test
npm --prefix desktop run typecheck
npm --prefix desktop run build
```

Every command must exit zero. The development-controller tests use model transport doubles; their printed goal passes are not product, live-agent or provider acceptance. Trusted check code is protected by `services/workshops/trust.lock.json`; do not change the lock merely to hide an unexpected mismatch.

## Deterministic browser red/green evaluation

```sh
.venv/bin/python tests/e2e/run_d1.py
```

Expected: the deliberately bad signup fixture fails `SIGNUP_DESTINATION_MISMATCH`; the known-good fixture passes `SIGNUP_JOURNEY_PASSED`; the unit suite passes. The runner copies fixtures to temporary read-only snapshots and leaves checkout originals untouched. It writes real screenshots, reports, hashes and a summary to `evidence/D/`. A failed negative fixture is the expected red control, not a command failure.

## Viewer interaction and accessibility evaluation

The original runtime assets in `desktop/public/office/` are tracked and required for these interaction tests. The configured repository must contain a long committed text change (over 120 added lines so scroll restoration is meaningfully tested) between its base and HEAD. For this feature branch, `SIDEQUEST_BASE=69bf066` includes the real `dev/luna.py` change; `HEAD~1` may be too small for this scroll test:

```sh
cd desktop
SIDEQUEST_REPO=/absolute/path/to/repository SIDEQUEST_BASE=69bf066 \
CHROMIUM_PATH=/usr/bin/chromium CI=1 npm run test:browser
```

Expected: six viewer and two revised T3 Code settings tests pass; the three live inspection/session tests skip unless explicitly enabled below. The suite reads genuine local committed Git data, verifies one lazy editor, Expand/Escape selection and scroll retention, hostile text, origin restrictions, reduced motion, responsive layouts and automated accessibility checks. Real screenshots go to `evidence/desktop/`. The tests wait for all 26 original staged figures before interaction. The slim footer selector is the keyboard alternative to the scene objects. Original assets are mandatory for office acceptance. The rejected temporary office has been removed from the default experience; its prior captures are historical only. The settings tests cover automatic CLI metadata, provider selection, Cost/Tokens/Limits, unknown telemetry, modal ownership and accessibility at 1440/390px. They fill a test-only prompt, scope and budget, verify Submit remains disabled, and assert that setup refresh sends no grant, coding submission or coding launch request. They also open the truthful disconnected figure view. Use these current captures for visual review; the rejected warm version is historical only.

## Original asset and scene evaluations

With the development server already running, execute the existing probes from the repository root:

```sh
node evidence/desktop/original-office/validate-assets.mjs
node evidence/desktop/original-office/capture-browser.mjs
node evidence/desktop/original-office/check-browser-bindings.mjs
node evidence/desktop/original-office/check-browser-actors.mjs
```

The deterministic validator compares all 24 measured monitor surfaces and verifies every copied image/actor hash and local path. The integrated capture verifies 26 loaded figures, successful local asset responses, a selected real Git editor and Expand/Escape. The bindings probe physically clicks a visible original monitor, actor, workstation pick bounds and board; it records the actual selected station where scene geometry overlaps, verifies the compact cards and captures screenshots. Four additional monitor focus poses are checked through keyboard navigation. Actor clips are retained compatibility evidence; sampled typing poses are staged artwork, never a live agent. Browser captures use software WebGL on this VM and do not establish owner-device performance or native Electron acceptance.

## Native Electron smoke evaluation

```sh
cd desktop
npm run install:electron
npm run build
SIDEQUEST_REPO=/absolute/path/to/repository SIDEQUEST_BASE=HEAD~1 npm run test:electron
```

Expected on a supported host: a native window opens and the smoke check exits zero. Exit 2 means the native check is blocked; read `evidence/desktop/electron-smoke.json`. Preserve the sandbox. This VM currently lacks a usable sandbox, so a browser pass must not be reported as an Electron pass.

## Integrated job acceptance

This opt-in evaluation submits and runs a genuine **deterministic local Git inspection** through the UI, authenticated runtime and Git/check adapters. It creates local project/job records and result artifacts. It never starts a coding model or delivers source changes.

Use a clean clone as the approved source: browser captures write evidence into the Sidequest checkout, which must not make the inspected repository dirty. Choose an unused destination, or substitute another trusted clean repository:

```sh
git clone --no-local /absolute/path/to/sidequest /tmp/sidequest-eval-source
```

In terminal 1, from the Sidequest checkout root, start the host with dedicated directories outside Git. Codex is explicitly disabled:

```sh
SIDEQUEST_CODEX_ENABLED=false .venv/bin/python -m services.runtime.main \
  --allowed-root /tmp/sidequest-eval-source \
  --data-dir /tmp/sidequest-eval-data \
  --config-dir /tmp/sidequest-eval-config \
  --runtime-dir /tmp/sidequest-eval-runtime
```

In terminal 2, stop your existing Vite development server so the test can own port 5173, then run:

```sh
cd desktop
SIDEQUEST_REPO=/tmp/sidequest-eval-source SIDEQUEST_BASE=69bf066 \
SIDEQUEST_RUNTIME_URL=http://127.0.0.1:4317 \
SIDEQUEST_API_TOKEN_FILE=/tmp/sidequest-eval-config/session.token \
SIDEQUEST_TEST_INSPECTION=1 CHROMIUM_PATH=/usr/bin/chromium CI=1 \
npm run test:browser -- tests/browser/jobs-live.spec.ts
```

Expected: three tests pass. It explicitly registers the configured repository, submits an inspection, clicks Run, reads real frozen files and the identity-check report, verifies zero inference calls in that report, checks cached readiness refresh, reflows at 960/390px, and returns with Escape while preserving artifact selection. A second test checks repeated submissions, clearing stale notices, controlled read disconnection/recovery, read-only result assignment and 180px scroll restoration through Expand, Settings, Escape and reopening. Its extra submitted inspection remains queued and makes no model call. The tests write `evidence/desktop/job-*.png`, `job-browser.json` and `job-accessibility.json`. The inspection clones the registered revision unchanged, so its candidate diff is empty; the separate viewer suite proves a nonempty committed Git diff. The backend retains `verifying` because delivery/acceptance is disabled; the UI separately reports ready results after completed tasks and passed checks.

To run the complete extended **11-test suite**, use the same terminal 1 host and terminal 2 environment above, removing the final file filter:

```sh
SIDEQUEST_REPO=/tmp/sidequest-eval-source SIDEQUEST_BASE=69bf066 \
SIDEQUEST_RUNTIME_URL=http://127.0.0.1:4317 \
SIDEQUEST_API_TOKEN_FILE=/tmp/sidequest-eval-config/session.token \
SIDEQUEST_TEST_INSPECTION=1 CHROMIUM_PATH=/usr/bin/chromium CI=1 \
npm run test:browser
```

Run one browser suite/probe at a time on software WebGL hosts. The prior office suite passed 10/10 in 7.3 minutes; the extended suite adds persistent session ownership and contextual events. Stop terminal 1 with Ctrl-C when finished.

Codex lifecycle tests use a fake app-server process only. Native startup in this VM is blocked before initialization by read-only protected runtime state, and the installed protocol has no verified enforceable USD ceiling. Native execution is denied before thread/turn creation. These tests establish neither a live agent run nor subscription/model readiness. Follow [MVP_ACCEPTANCE.md](MVP_ACCEPTANCE.md) for the acceptance limits.

The third integrated test assigns an actual recorded run to Computer 19, verifies stored worker/project/run identity, opens real events and usage, reads the same job results, restores ownership after reload, follows the board task link, rejects a test-only wrong-worker response and explicitly detaches. It records session-browser.json and real recorded-session screenshots. It issues no coding submission, permission grant or model request.
