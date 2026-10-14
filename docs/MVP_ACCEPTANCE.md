# Four-hour MVP acceptance — 2026-10-14

Deadline: **2026-10-14 05:46:56 UTC** (October 13, 22:46:56 PDT). Scope: office navigation, job submission/status, readable real artifacts/diffs, and one genuine safe job-to-result path. Workshops, selected-screen capture and additional polish are deferred. A local Git inspection/check job must be identified as deterministic local work; it must never be presented as a live coding agent.

## Exclusive ownership

| Role | Writer | Paths | Current goal |
|---|---|---|---|
| A — runtime/state/scheduler | Luna/max A owner | services/runtime/, journals/A.md, evidence/A/ | A1 passed; A2 inspection API frozen for fresh review; Codex lifecycle integration next |
| B — Git/Codex/tools | Luna/max B owner | services/tools/, journals/B.md, evidence/B/ | B1 repair passed fresh review; B2 actual Codex app-server adapter in progress |
| C — Electron/R3F/computers | coordinator | desktop/, journals/C.md, evidence/C/, evidence/desktop/ | viewer integration; actual office/native proof blocked |
| D — trusted checks | Luna/max D1 owner | services/workshops/, demo/, tests/e2e/, journals/D.md, evidence/D/ | D1 passed fresh review; standalone frozen-copy runner verified |

Writers share a checkout with nonoverlapping paths. The coordinator alone changes shared contracts/plan and integrates. Fresh validators use detached exact-commit worktrees under `/workspace/sidequest-reviews/`; they do not edit builder source. No duplicate owner or native development controller runs on these paths. This is coordinated manual execution, not a claim that the native goal runner's token accounting is active. Model/effort and original per-goal attempt limits remain the policy; stopped or failed goals are not reset.

## Acceptance matrix

| Capability | Implementation | Fixture/component evidence | Live application evidence |
|---|---|---|---|
| Real committed Git diff viewer | Implemented | 24 desktop tests including narrow runtime bridge | Browser verified, genuine Sidequest Git revisions |
| Single lazy editor, Expand/Escape selection/scroll/focus | Implemented | Browser regression | Browser verified at 1440/960/390px |
| Literal hostile text and safe error retry | Implemented | Controlled hostile transport test | Tested boundary; no live agent source implied |
| Keyboard/contrast/reduced-motion reading | Implemented | Six browser checks, 0 automated WCAG A/AA violations | Browser verified; manual screen-reader acceptance not claimed |
| Actual supplied office GLB, monitors and camera | Loader/bindings implemented | Synthetic parser/resource tests only | BLOCKED: authenticated asset-host CONNECT returns proxy403 before link evaluation; not link expiry |
| Native Electron isolation and interaction | Shell/protocol implemented | Security tests and production build | BLOCKED: native OS sandbox helper/user namespaces unavailable; sandbox preserved |
| Persistent projects/jobs/policy and budget | A1 passed exact-commit fresh review | 13 tests and independent budget/approval/immutability probes | No application job run yet |
| Independent Git clones/frozen artifact pipeline | B1 repair passed exact-commit fresh review | 19 tests plus hard-link sentinel/containment probes | Ready for integrated inspection; trusted roots and quiescent workers required, adapter is not an OS sandbox |
| Trusted candidate/browser checks | D1 passed exact-commit fresh review | Seeded bad/red and known-good/green controls; 13 tests and real Chromium fixture journey; standalone runner freezes temporary copies | Trusted browser path verified on fixtures, not a live coding worker |
| Authenticated job submission/status and artifact API | A2 frozen for fresh review; C repair in progress | 21 runtime tests, real B/D temporary-Git pipeline; 26 desktop tests | Authenticated real loopback read verified; UI job acceptance next |
| Genuine safe job-to-result path | Target: real local Git inspection + frozen identity check | Pending integration | Must be proved through actual HTTP/UI with honest worker type |
| Codex session adapter and task lifecycle | Required MVP scope; B2 app-server adapter in progress, A integration next | Installed CLI schemas available; deterministic tests planned | Existing CLI reports ChatGPT login; app-server catalog initialization hit read-only state, safe runtime-state alternative under investigation; no demonstration provider run authorized |
| Workshops/capture | Deferred | Outside MVP | Outside MVP |

Detailed viewer evidence and exact transfer/native failures are in [evidence/desktop/README.md](../evidence/desktop/README.md). Lane evidence is separate from final integrated acceptance. Update this table at real checkpoints; a green fixture test cannot make an unverified live capability green.
