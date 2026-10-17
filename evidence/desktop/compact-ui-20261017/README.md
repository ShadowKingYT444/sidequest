# Compact interface — 17 October 2026

Settings now leads with executable/authentication/reachability status and folds paths/model diagnostics into Advanced. Unreported usage is one line. Task results keep a concise outcome, with IDs, checks and hashes in Details. Redundant headers, explanations and unavailable paging controls are removed; the original physical office art and renderer are unchanged. The [reference review](reference-review.json) records the actual T3 Code source and design contract.

[90 desktop tests](unit.log) and [final production build](build-final.log) pass. Three new browser cases cover 1440/960/390px, keyboard access to Advanced, honest empty usage, refresh, Escape/focus return, overflow, accessibility and no provider writes. Existing job tests still assert the backend verifying state and passing checks through Details. Native visual verification of this candidate is pending; earlier screenshots show the earlier interface.

All Playwright launches now retain Chromium sandbox and remove the automatic unsafe SwiftShader opt-in. The coding container cannot start this supported configuration. The separate VM already passed the prior [two graphics recovery cases](../native-graphics-20261017/vm/GRAPHICS-VERIFICATION.txt) with these settings; that is separate from the new compact UI checks.

On the sandbox-capable VM, apply the source transfer, build, and run from `desktop/` with a fresh absolute evidence directory and the configured trusted Git repository:

```sh
npm run build
SIDEQUEST_EVIDENCE_DIR=/absolute/path/to/compact-ui npx playwright test tests/browser/compact-ui.spec.ts tests/browser/office-failure.spec.ts --reporter=line --output=/absolute/path/to/compact-ui/playwright-results
```

Manually verify native Jobs/Details, recorded trace, local draft retention and result selection. The three settings cases can run even when the host cannot render WebGL2. The full office-dependent browser suite needs actual WebGL2 and the local inspection runtime; do not disable the sandbox or GPU blocklist to manufacture acceptance. No live provider turn or authentication change is part of these checks.
