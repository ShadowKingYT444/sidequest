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
