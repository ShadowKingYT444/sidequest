# Integrated runtime session transport — protocol-fake checkpoint

Implemented from `1a5d1be` and integrated with isolated desktop/provider/notification commits. Tests below are deterministic local/protocol fakes and make **zero live model calls**.

Authenticated local staging persists File bytes under opaque run-bound IDs, validates canonical encoding/type/hash/size, rejects symlinks/hardlinks and cross-run use, and makes the original local UUID an idempotent key. Local staging accepts up to 10 files, 10 MiB each and 25 MiB total. Provider sends accept UTF-8 text and PNG/JPEG/GIF/WebP, at most 1 MiB combined; PDF sending remains unsupported and retains the local file.

`session.message` persists the exact command UUID, payload and expected revision before one queue action. `GET /v1/commands/{id}` reconciles acceptance without dispatch. An exact replay returns the original receipt even after state/readiness changes. The store preserves the original goal, write scope, checks and recorded worker, and claims a new run under the existing job. Station reassignment uses the existing immutable identity checks. Prior frozen edits are hash-checked and materialized into a fresh original-base clone. The provider independently verifies the exact initial tree/scope and terminal previous turn, retains cumulative goal tokens and never infers quota authority from usage percentages.

Completed text-only follow-ups record trace without inventing Git candidates. New edits retain frozen-candidate/artifact/check validation. Interrupted dispatches become uncertain; startup resumes only accepted queued intents that never reached dispatch and only with fresh execution gates. Legacy Resume cannot repeat an uncertain follow-up. Unknown usage keeps its USD reservation and prevents a fresh turn. The existing production Codex USD/consent/model/repository guards remain intact.

Snapshot `jobs` remains latest 20. `office_jobs` adds all assigned jobs (up to 24) and up to 100 other active jobs across projects. Assigned runs remain complete when active coverage overflows; the boolean overflow marker is visible in the notification tray. Supplemental records still undergo full ownership and duplicate validation.

TDD evidence: `red.log` establishes missing staging/message/receipt/claim paths; `red-supplemental.log` proves the older-job omission; `red-mime.log` catches empty image MIME/code type mismatch; `red-worker-identity.log` catches worker switching; `red-uncertain-resume.log` proves the unsafe legacy Resume acceptance. Final root runtime suite passes **63/63** in `runtime-final-reconciled.log`; desktop **72/72** in `desktop-integrated.log`; tools **56/56** in `tools-final.log`; typecheck/build passes in `build-integrated.log`. `candidate-and-pipeline.log` verifies authenticated staging → durable intent → scheduler → exact fake provider inputs → trace → receipt, prior candidate bytes, symlink refusal and overflow. All earlier/intermediate failures are preserved; the first fixture setup error and schema-version expectation update are explicitly historical, not product regressions.

Commands:

```sh
.venv/bin/python -m unittest discover -s services/runtime/tests -p 'test_*.py' -v
.venv/bin/python -m unittest discover -s services/tools/tests -p 'test_*.py' -v
npm --prefix desktop test
npm --prefix desktop run build
python3 -m py_compile services/runtime/sessions.py services/runtime/api.py services/runtime/scheduler.py services/runtime/store.py services/runtime/artifacts.py
git diff --check
```

Subscription-backed usage is represented separately as nullable `subscription_quota` and numeric `subscription_reserve`; these are fresh read-only observations, not an enforceable spend/reserve authorization. The installed schema supplies no proven guarantee against purchased-credit fallback or crossing the requested 10% reserve during a turn. Consequently the existing USD spending gate stays closed. Actual quota remains unverifiable on this host.

Native Electron sandbox/display and Codex protected-state EROFS remain the preserved host blockers. No failed native startup was repeated for this implementation. No live/model turn, paid spending, new authentication, credential copying, sandbox/security change, merge, deployment or force push occurred. Original art and earlier logs/captures are retained. Full integrated browser verification follows this code checkpoint; native/live acceptance is still unverified.
