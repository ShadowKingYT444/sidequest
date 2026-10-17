# Verification evidence

Historical full-suite functional source: `8e39baba943c32da1c09944313e47286c69672ee`; published verification checkpoint: `bdf2fdd51196634293588ac38a9845e02894dab0`. [Feature-by-feature acceptance](../docs/ACCEPTANCE.md) distinguishes real runs, injected fixtures and unverified behavior.

| Evidence | Scope |
| --- | --- |
| [Actual-launcher walkthrough](desktop/proof-20261017/README.md) | Real browser video, uncut original and ten screenshots; no mocks or provider turns |
| [Browser acceptance](desktop/startup-browser-20261017/README.md) | Full 25/25 suite, zero retries; exact source hashes, 37 screenshots and explicit mock boundaries |
| [Fresh setup and native probes](desktop/startup-20261017/README.md) | Dependency/build installation, actual launcher, real Git inspection, unit/integration logs, native failures and source-transfer manifest |
| [Separate VM native smoke](desktop/native-vm-20261017/README.md) | Sandbox-preserving shell/IPC and Git/Jobs passes, seven native UI screenshots, WebGL2 office failure and auth/transport limits |
| [Graphics recovery](desktop/native-graphics-20261017/README.md) | Independent VM: two sandbox-enabled browser cases, actual native recovery and precise graphics limits |
| [Compact interface](desktop/compact-ui-20261017/README.md) | T3 source review, unit/build logs; new native/browser validation pending |
| [Billing capability review](desktop/billing-review-20261017/README.md) | Offline installed-protocol inspection; no provider login or model turn |

## Historical records

Older `desktop/` directories retain earlier successful and failed runs, diagnostics, receipt regressions and original asset recovery. `A/`, `B/`, `C/`, `D/` and integration records retain the original managed development evidence. Their dates and commit IDs are part of the record; an old successful test does not establish current native/live acceptance.

Failed test logs, error contexts, CPU profiles and original art are deliberately preserved. Disposable Playwright `.last-run.json` pointers are excluded; their outcomes remain in the full reports, terminal logs and verification manifests. No dependency tree, private runtime database, credential file or build output belongs here.
