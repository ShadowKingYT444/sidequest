# Browser acceptance and performance diagnosis — 2026-10-17

The software-renderer camera fix passes the exact previously failing results journey in **46.8 seconds** under its unchanged 90-second limit. Five related session/navigation/rendering regressions also pass with zero retries, including the previously failing 120-second session case. The five explicitly mocked composer tests separately pass in 10.3 seconds. The final complete 25-case run awaits the source checkpoint; no full-suite pass is claimed yet.

The earlier full attempt and follow-up CPU profile remain preserved: 2 passes, 2 timeout failures, 1 interruption and 20 unrun cases. The live UI had already completed a real deterministic Git inspection and a physical monitor/camera interaction.

All new evidence is isolated here. Prior repository evidence remains untouched. Test assertions and timeouts were not changed. The harness now honors `SIDEQUEST_EVIDENCE_DIR`; optional `SIDEQUEST_CPU_PROFILE=1` records a Chromium CPU profile without changing product code.

## Environment and commands

The application ran from the working Sidequest branch. `interrupted-full/run-context.json` records exact application source hashes. The trusted inspected project was an independent local clone checked out at `8a9fb11c3b01a404c4dd305b71458377082697c1`; the Git viewer compared base `69bf06696a93c9f58eee2d088e84404d4f6563d6`. The runtime used fresh private directories outside Git, port 44317, and `SIDEQUEST_CODEX_ENABLED=false`. A random token existed only in the runtime/Vite process environments; no token file was generated. Logs and JSON summaries contain no credential values.

The runner started `.venv/bin/python -m services.runtime.main --allowed-root <independent-clone> --data-dir <temporary-state>/data --config-dir <temporary-state>/config --runtime-dir <temporary-state>/runtime --port 44317`. It then ran `npm run test:browser -- --retries=0 --reporter=list,json --output <evidence>/playwright-results` with `SIDEQUEST_TEST_INSPECTION=1`, `CHROMIUM_PATH=/usr/bin/chromium`, `CI=1`, and the configured source/runtime URLs. Exact argv and results are in each `run-summary.json`.

## Results and scope

- `interrupted-full/job-browser.json`: real project registration, submission, run, immutable files, check report and activity through UI/HTTP/adapters; zero inference calls and zero recorded spending. The candidate remains unchanged, so its inspection diff is empty.
- `interrupted-full/monitor-camera-browser.json`: actual original Computer19 monitor was clicked; recorded trace identity and normal/interrupted camera return were checked. No coding submissions or uploads occurred.
- `interrupted-full/playwright-results/`: original failures at the final result reopen and late recorded-session board link; each exhausted its existing overall timeout. These are retained failures, not suppressed or retried to green.
- `profile/`: the unchanged results test was run again solely to collect diagnostics. Of its 90.19-second CPU profile, 80.31 seconds were in native `(program)` and only 0.356 seconds in sampled JavaScript intersection stacks. This does **not** support changing actor hit geometry as the primary fix. The exact native stall cause remains unproven.
- `gpu-details.json`: a separate blank-page probe using identical Chromium launch options confirms ANGLE/SwiftShader software WebGL. No hardware GPU performance is claimed.
- `fixture-setup-failure/`: preserved initial setup error. A shared Git clone was correctly rejected for alternate object storage; an independent clone and new database corrected the test setup without weakening safety checks.

This establishes neither native Electron nor live coding-provider acceptance. Composer delivery uses explicitly mocked protocol responses in its dedicated tests and cannot establish live provider dispatch. The five composer cases passed separately in 10.3 seconds with zero retries against the fresh launcher artifact at `6a6b8a3`; see [mocked-composer/browser.log](mocked-composer/browser.log). This verifies real browser persistence and UI behavior with fake receipts, not live dispatch.

## Software camera fix verification

[The focused results report](software-camera-focus/playwright-report.json) and [five related regression results](software-camera-regressions/playwright-report.json) use unchanged assertions and timeouts, zero retries and no profiling overhead. The camera fix preserves the approved art and uses the existing instant camera path on detected software renderers. It reduces expensive frames; 3–7 second native stalls still occur on this SwiftShader host, so smooth hardware performance is not established.

## Screenshots

- [Real inspection results](interrupted-full/job-result.png)
- [Actual check report](interrupted-full/job-check-report.png)
- [Responsive results at390px](interrupted-full/job-390.png)
- [Reopened assigned result after fix](software-camera-focus/assigned-result.png)
- [Recorded session after fix](software-camera-regressions/recorded-session.png)
- [Original physical monitor view](interrupted-full/monitor-pov.png)

See [verification.json](verification.json), [CPU summary](profile/cpu-summary.json), and [full-attempt log](interrupted-full/browser.log).
