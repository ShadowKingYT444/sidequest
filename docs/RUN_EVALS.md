# Run local evaluations

These checks use local Git/SQLite fixtures, deterministic checks and browser automation. They do not start Codex jobs, contact a model provider, spend money or restart the cancelled Cooki evaluations. Run from the repository root unless a block says otherwise.

## Install dependencies

Python 3.12, Git and Node 24 are required. Use an isolated Python environment and the committed dependency locks:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r services/runtime/requirements.lock
.venv/bin/python -m pip install -r services/workshops/requirements.lock
npm --prefix desktop ci
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

The configured repository must contain at least one meaningful committed text change between its base and HEAD:

```sh
cd desktop
SIDEQUEST_REPO=/absolute/path/to/repository SIDEQUEST_BASE=HEAD~1 \
CHROMIUM_PATH=/usr/bin/chromium CI=1 npm run test:browser
```

Expected: all browser tests pass. The suite reads genuine local committed Git data, verifies one lazy editor, Expand/Escape selection and scroll retention, hostile text, origin restrictions, reduced motion, responsive layouts and automated accessibility checks. Real screenshots go to `evidence/desktop/`. It does not establish actual office rendering or native Electron acceptance.

## Native Electron smoke evaluation

```sh
cd desktop
npm run install:electron
npm run build
SIDEQUEST_REPO=/absolute/path/to/repository SIDEQUEST_BASE=HEAD~1 npm run test:electron
```

Expected on a supported host: a native window opens and the smoke check exits zero. Exit 2 means the native check is blocked; read `evidence/desktop/electron-smoke.json`. Preserve the sandbox. This VM currently lacks a usable sandbox, so a browser pass must not be reported as an Electron pass.

## Integrated job acceptance

Live HTTP/UI inspection acceptance is in progress. Do not count component fixtures as proof of a user job. The final acceptance record must name the registered repository revision, command/job/run IDs, frozen candidate and artifact hashes, check result, real screenshot paths, zero model calls and zero spending. Follow [MVP_ACCEPTANCE.md](MVP_ACCEPTANCE.md) for the current state and remaining blockers.
