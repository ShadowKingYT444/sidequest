# Desktop follow-up and durable drafts checkpoint

Isolated branch `repair/desktop-transport`, starting at `1a5d1be`. The monitor keeps the existing compact composition and original office assets. Native startup and live provider acceptance are not established by these tests.

The trace composer now uses validated follow-up message/attachment/status bridge methods. Explicit Send stages files with local UUID keys, persists opaque stage IDs and a run-bound message command UUID/prompt/attachment list/expected revision, then submits. New sends remain locked after uncertain responses. Check send status reads the exact command; a not-found retry repeats the identical envelope. Definite rejections retain the draft for explicit review. Follow-up run rebinding preserves the job conversation draft.

Draft text, attachment Blob/File bytes, original local UUIDs and keyboard selection persist in IndexedDB. Image previews receive fresh object URLs after reload. URLs, filesystem paths and credentials are never stored in the message record. Corrupt pending storage stays blocked and cannot be silently overwritten by editing. Concurrent text edits are preserved when the earlier send is accepted.

Production readiness remains enforced by renderer explanations, validated IPC client and runtime authorization: current completed coding run, verifying/accepted job, current task attempt if exposed, known positive remaining approved budget, fresh coding/catalog/consent and enforced USD limit. UTF-8 text/raster provider attachments are bounded to 1 MiB combined content per message; PDFs and larger files remain local. No model call, provider startup, spending, authentication, credential or sandbox change occurred.

Validation:

- `unit-suite-current-gate.log`: 65 desktop tests, zero failures/skips. Includes protocol-fake storage/send, guard, client and native IPC fault-envelope tests.
- `build-final.log`: TypeScript check and production build passed.
- `browser-transport-current-gate.log`: 3/3 passed, retries 0, 9.7s. Real Chromium IndexedDB/File reload, image preview recreation, actual keyboard selection restoration, lost response reconciliation with exactly one stage/send, next draft retention, narrow 390px reflow and disabled unknown USD execution. The runtime is explicitly fake and screenshots are labeled.
- `red-durable-send.log`, `red-runtime-transport.log`, `red-corrupt-pending.log`, `red-native-ipc-error.log`, `red-current-session-gate.log`: preserved failing evidence. Corresponding green logs establish implementation and targeted repairs. Early browser fixture refresh/import errors and its synthetic-selection failure are retained separately; the final test uses actual keyboard selection and normal product CSS.
- `verification.json`: touched source hashes and unchanged tracked public-asset hashes. No protected asset path changed.

Captures are `captures/durable-composer.png`, `captures/pending-composer.png` and `captures/reconciled-composer-mobile.png`. They show the actual composer with protocol-fake data, not a native/live result. Full integrated office/browser regression validation belongs to the integrator after backend and notification changes land.

## Accepted receipt rejected before start

A command receipt acknowledges queue acceptance. If the matching message status is `rejected`, the provider did not start: reconciliation retains text, attachments and any concurrent next thought, persists a rejected pending state, and exposes the existing explicit Review retained draft action. It never creates another UUID or resends automatically. The message ID must match the command UUID; invalid states/run IDs and contradictory later metadata fail closed. The unchanged successful receipt path remains covered.

`red-rejected-receipt.log` reproduces both unsafe clearing failures; `green-rejected-receipt.log` passes 12 store regressions. `unit-suite-rejected-receipt-final.log` passes 68 desktop tests; `build-rejected-receipt-final.log` passes TypeScript/build. The four protocol-fake browser tests passed with retries 0 in 16.6s on separate port 5175 (`browser-rejected-before-start-isolated.log`), including reload, file/next-thought retention, explicit review and exactly one stage/send/status sequence. The initial port-5173 collision stopped before tests and is retained; no root sources or native/live workflows were touched. Captures from this checkpoint are in `rejected-receipt-captures/`; the prior checkpoint captures remain unchanged.

Reproduce the isolated checks from `desktop/`: `SIDEQUEST_TRANSPORT_EVIDENCE_RUN=rejected-receipt-captures CHROMIUM_PATH=/usr/bin/chromium CI=1 npm run test:browser -- --config ../evidence/desktop/transport/playwright-isolated.config.mts --grep 'protocol fake:' --retries=0`.

The committed isolated configuration is `.mts` so its `import.meta` remains an ES module outside the desktop package. The initial `.ts` reproduction failed at config loading (log retained); `browser-rejected-before-start-reproducible-mts.log` verifies the exact committed config and new rejected-state test, 1/1 pass, retries 0, 4.2s. No product test assertion or timeout was changed to resolve the config issue.
