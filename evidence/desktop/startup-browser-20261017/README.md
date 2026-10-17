# Browser acceptance — 2026-10-17

**25/25 browser tests passed in 12.9 minutes, with zero retries, skips, flaky cases or page errors**, at frozen source `8e39baba943c32da1c09944313e47286c69672ee`. The run used fresh runtime state, a genuine trusted Git project, coding disabled, and process-only ephemeral API credentials. No token files were created. All **252 source/test/asset hashes** matched before and after the run. The runtime shut down gracefully and ports 5173/44317 were released.

See [final verification](final-full/verification.json), [Playwright report](final-full/playwright-report.json), [terminal log](final-full/browser.log), and [exact source hashes](final-full/run-context.json).

## What is real and what is mocked

The application, imported office assets, browser, Git viewer, local authenticated runtime, SQLite records, isolated inspection, trusted frozen-identity checks, and immutable artifacts are real. Both executed inspections passed with zero recorded cost; the extra deliberately unexecuted queued inspection retains unknown cost. No model/provider turn ran. Session ownership, physical monitor navigation, workboard linking, local file/image handling, expanded views, Escape/reopen, scroll retention, responsive layouts and automated WCAG checks passed.

Five composer cases use real React/Chromium/IndexedDB/File behavior with **explicitly mocked delivery, receipt and capability responses**. Notification completion/attention statuses, selected error responses and hostile source content are explicit browser fixtures. The notification fixture uses genuine inspection record identities and does not persist fabricated statuses. Clipboard paste is a synthetic browser event, not proof of operating-system clipboard integration. [Scope details](final-full/mock-real-matrix.json).

This browser pass does **not** establish native Electron, live coding-provider execution, verified authentication/usage enforcement, or hardware GPU performance. Those have separate acceptance requirements.

## Performance repair and preserved failures

An earlier unchanged full attempt hit the existing 90/120-second limits on two long journeys. CPU profiling found 80.31 of 90.19 seconds in native `(program)` and only 0.356 seconds in sampled JavaScript intersection stacks; it did not support changing actor hit geometry. A separate [renderer probe](gpu-details.json) confirmed ANGLE/SwiftShader software WebGL.

The software-renderer camera change uses the existing instant camera path while preserving the approved art, lights, shadows and framing. The exact previously failing results case then passed in **46.8 seconds** under its unchanged 90-second timeout, and five related regressions passed. In the final full run that results case passed again in **45.0 seconds**. Native software-rendering stalls still occur, so this is functional acceptance rather than a claim of smooth hardware performance.

All prior evidence remains intact:

- `fixture-setup-failure/`: the runtime correctly rejected a shared Git clone's alternate object store; the setup was corrected to an independent clone.
- `interrupted-full/`: 2 passes, 2 time-budget failures, 1 interruption and 20 unrun cases, preserved before the camera repair.
- `profile/`: reproduced timeout and raw CPU profile before repair.
- `software-camera-focus/` and `software-camera-regressions/`: unchanged focused checks after repair.
- `mocked-composer/`: separate five-case pass against the fresh-launcher artifact at `6a6b8a3`.
- `final-full/`: complete passing run at the frozen source.

Assertions and timeouts were not changed. The harness now honors `SIDEQUEST_EVIDENCE_DIR` for every screenshot/diagnostic; optional `SIDEQUEST_CPU_PROFILE=1` records CPU diagnostics and was disabled for the final run.

## Reproduction

The trusted inspected project is an independent `git clone --no-local --no-checkout` of Sidequest, checked out at `8a9fb11c3b01a404c4dd305b71458377082697c1`; the viewer compares base `69bf06696a93c9f58eee2d088e84404d4f6563d6`. The renderer/runtime under test use the frozen current checkout. Runtime/config/work directories stay outside Git.

The runner starts `.venv/bin/python -m services.runtime.main --allowed-root <independent-clone> --data-dir <temporary-state>/data --config-dir <temporary-state>/config --runtime-dir <temporary-state>/runtime --port 44317` with coding disabled. A fresh random token is shared only through the runtime/Vite process environments. It runs `npm run test:browser -- --retries=0 --reporter=list,json --output <evidence>/playwright-results` with `SIDEQUEST_TEST_INSPECTION=1`, `CHROMIUM_PATH=/usr/bin/chromium`, `CI=1`, the configured source/runtime URLs and isolated `SIDEQUEST_EVIDENCE_DIR`. Exact argv, timestamps and shutdown results are in [run-summary.json](final-full/run-summary.json).

## Selected final screenshots

- [Original office overview](final-full/setup-desktop.png)
- [Real immutable inspection results](final-full/job-result.png)
- [Frozen-identity check report](final-full/job-check-report.png)
- [Real committed Git diff](final-full/git-diff.png)
- [Recorded session at the physical monitor](final-full/monitor-pov.png)
- [Local attachment composer on mobile](final-full/monitor-local-draft-390.png)
- [Detected provider settings](final-full/provider-settings.png)
- [Compact provider picker](final-full/provider-selector.png)
- [Explicit notification display fixture](final-full/notifications-badges-fixture.png)

The final verification lists all **37 screenshots**.
