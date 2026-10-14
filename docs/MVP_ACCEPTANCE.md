# Four-hour MVP acceptance — 2026-10-14

Deadline: **2026-10-14 05:46:56 UTC** (October 13, 22:46:56 PDT). Scope: office navigation, job submission/status, readable real artifacts/diffs, and one genuine safe job-to-result path. Workshops, selected-screen capture and additional polish are deferred. A local Git inspection/check job must be identified as deterministic local work; it must never be presented as a live coding agent.

## Exclusive ownership

| Role | Writer | Paths | Current goal |
|---|---|---|---|
| A — runtime/state/scheduler | Luna/max A owner | services/runtime/, journals/A.md, evidence/A/ | A1/A2 repairs passed fresh review; A3 scoped lifecycle repair passed at f9476f9, native blocked |
| B — Git/Codex/tools | Luna/max B owner | services/tools/, journals/B.md, evidence/B/ | B1 repair passed fresh review; B2 scoped adapter repair passed at f9476f9, native blocked |
| C — Electron/R3F/computers | coordinator | desktop/, journals/C.md, evidence/C/, evidence/desktop/ | seven integrated browser tests passed; stale smoke assertion repaired/reviewed at d9e415c; actual office/native proof blocked |
| D — trusted checks | Luna/max D1 owner | services/workshops/, demo/, tests/e2e/, journals/D.md, evidence/D/ | D1 passed fresh review; standalone frozen-copy runner verified |

Writers share a checkout with nonoverlapping paths. The coordinator alone changes shared contracts/plan and integrates. Fresh validators use detached exact-commit worktrees under `/workspace/sidequest-reviews/`; they do not edit builder source. No duplicate owner or native development controller runs on these paths. This is coordinated manual execution, not a claim that the native goal runner's token accounting is active. Model/effort and original per-goal attempt limits remain the policy; stopped or failed goals are not reset.

## Acceptance matrix

| Capability | Implementation | Fixture/component evidence | Live application evidence |
|---|---|---|---|
| Real committed Git diff viewer | Implemented | 26 desktop tests including narrow runtime bridge | Browser verified, genuine Sidequest Git revisions |
| Single lazy editor, Expand/Escape selection/scroll/focus | Implemented | Browser regression | Browser verified at 1440/960/390px |
| Literal hostile text and safe error retry | Implemented | Controlled hostile transport test | Tested boundary; no live agent source implied |
| Keyboard/contrast/reduced-motion reading | Implemented | Six browser checks, 0 automated WCAG A/AA violations | Browser verified; manual screen-reader acceptance not claimed |
| Actual supplied office GLB, monitors and camera | Loader/bindings implemented | Synthetic parser/resource tests only | BLOCKED: authenticated asset-host CONNECT returns proxy403 before link evaluation; not link expiry |
| Native Electron isolation and interaction | Shell/protocol implemented | Security tests and production build | BLOCKED: native OS sandbox helper/user namespaces unavailable; sandbox preserved |
| Persistent projects/jobs/policy and budget | A1 passed exact-commit fresh review | Foundation tests and independent budget/approval/immutability probes | Genuine local project/job persisted; model spend enforcement remains unavailable |
| Independent Git clones/frozen artifact pipeline | B1 repair passed exact-commit fresh review | Hard-link sentinel/containment and credential-filter probes | Genuine Sidequest commit cloned/frozen/imported; trusted roots and quiescent workers required, adapter is not an OS sandbox |
| Trusted candidate/browser checks | D1 passed exact-commit fresh review | Seeded bad/red and known-good/green controls; 13 tests and real Chromium fixture journey; standalone runner freezes temporary copies | Trusted browser path verified on fixtures, not a live coding worker |
| Authenticated job submission/status and artifact API | A2 repair passed exact-commit fresh review; C bridge repair passed scoped review | Serialized page bounds, cursor identity, process-group cleanup; 26 desktop tests | Real loopback HTTP/UI registration, submission, explicit execution and artifact reading passed |
| Genuine safe local job-to-result path | Real local Git inspection + frozen identity check | Real B/D pipeline, not an agent fixture | Final browser acceptance passed against clean Sidequest commit 23f26d6; registered project, job/run/candidate IDs, hashes, zero inference calls and $0 spent recorded in job-browser.json |
| Codex session adapter and task lifecycle | Implemented; A3/B2 scoped deterministic repairs passed exact-commit fresh review | 39 runtime tests, 41 tools tests; fake app-server lifecycle only, installed native schemas checked | BLOCKED: existing CLI reports ChatGPT login, but protected CODEX_HOME state operations return EROFS before initialize; no catalog/account response or real model turn; USD ceiling unsupported, execution denied before startup |
| Workshops/capture | Deferred | Outside MVP | Outside MVP |

Detailed viewer/job evidence and exact transfer/native failures are in [evidence/desktop/README.md](../evidence/desktop/README.md). Run instructions are in [RUN_EVALS.md](RUN_EVALS.md). Lane evidence is separate from final integrated acceptance. The requested office-to-native-agent experience is incomplete while art, Electron sandbox and native Codex/budget gates are blocked; a green fixture test cannot make an unverified live capability green.
