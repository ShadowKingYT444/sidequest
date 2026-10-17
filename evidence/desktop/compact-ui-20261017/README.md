# Compact interface — 17 October 2026

Settings now leads with executable/authentication/reachability status and folds paths/model diagnostics into Advanced. Unreported usage is one line. Task results keep a concise outcome, with IDs, checks and hashes in Details. Redundant headers, explanations and unavailable paging controls are removed; the original physical office art and renderer are unchanged. The [reference review](reference-review.json) records the actual T3 Code source and design contract.

[90 desktop tests](unit.log) and [final production build](build-final.log) pass. Three new browser cases cover 1440/960/390px, keyboard access to Advanced, honest empty usage, refresh, Escape/focus return, overflow, accessibility and no provider writes. Existing job tests still assert the backend verifying state and passing checks through Details. The independent VM now passes all five compact settings/recovery cases and actual native Jobs/Details, immutable viewing, recorded trace and draft reload. [Unmodified VM report](vm/RESULTS.txt) · [import hashes](vm/manifest.json) · [browser log](vm/compact-retest.log). Its archive plus exact transfers has 88 available desktop unit tests, all passing; it is not a complete checkout of the 90-test repository.

All Playwright launches now retain Chromium sandbox and remove the automatic unsafe SwiftShader opt-in. The coding container cannot start this supported configuration. The separate VM passes the new five-case suite with these settings. Its initial attempt omitted SIDEQUEST_REPO for an archive without .git and correctly disabled the Git action; supplying a disposable Git project made all five pass without source changes.

On the sandbox-capable VM, apply the source transfer, build, and run from `desktop/` with a fresh absolute evidence directory and the configured trusted Git repository:

```sh
npm run build
SIDEQUEST_EVIDENCE_DIR=/absolute/path/to/compact-ui npx playwright test tests/browser/compact-ui.spec.ts tests/browser/office-failure.spec.ts --reporter=line --output=/absolute/path/to/compact-ui/playwright-results
```

Native Jobs/Details, recorded trace, local draft retention and close/reopen result selection now pass. Full window reload starts Jobs at its default file; results, assigned computers, recorded ownership and drafts persist. Existing selection/scroll promises cover same-session close/reopen and Expand/Escape, not persistent file selection. No new persistence was introduced. The three settings cases can run even when the host cannot render WebGL2. The full office-dependent browser suite needs actual WebGL2 and the local inspection runtime; do not disable the sandbox or GPU blocklist to manufacture acceptance. No live provider turn or authentication change is part of these checks.

## Current captures

[Desktop settings](vm/compact-providers-1440.png) · [960px settings](vm/compact-providers-960.png) · [390px settings](vm/compact-providers-390.png) · [empty usage](vm/compact-usage-960.png) · [native immutable result](vm/native-compact-jobs.png) · [native trace and retained draft after reload](vm/native-compact-reload.png).

The implementation owner inspected desktop/intermediate/mobile screenshots and native captures. The office remains the original physical scene; this VM cannot render it. Neither these images nor the earlier software-rendered office prove live coding or production GPU compatibility. The workshop CI diagnostic is [documented separately](../../D/ci-20261017/README.md).
