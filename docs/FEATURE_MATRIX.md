# Feature and acceptance map

This map prevents a narrow happy-path prototype from being called the complete app. Included means required implementation, not completed work. Versioned extensions are explicit, not silently added dependencies.

| Feature | Required release behavior | Owner / goal |
|---|---|---|
| Existing office | Bind supplied art; no regeneration or replacement room | C1 |
| Main computer | Project-wide selection and real Files/Diff/Runs/Preview/Checks inside Unity | C2, C3; A2/B1 |
| Worker computers | Same viewer scoped to stable worker/run identity | C2 |
| Jobs | Typed prompt, registered GitHub issue, pasted external link and local event | A1, A2; B2 |
| Swarm division | At most four tasks, fixed scopes/dependencies, safe parallelism and integration | A2, B1 |
| Worker provider | Luna/max capability checked; bounded real Codex execution, no replacement harness | B2 |
| State visibility | Real progress events, errors, assignment, pause/resume/cancel | A2, C2 |
| Files and diffs | Immutable candidate manifest, added/deleted/renamed/binary entries, paginated native viewer | B1, A2, C2 |
| QA | Trusted red-before-green browser tests plus native Unity tests | D1, C3 |
| Delivery | Exact candidate/action/destination approval; local target and optional approved GitHub PR | A3, B2, C2 |
| Structured lookouts | File/process/GitHub condition events with restart-safe de-duplication | B3, A3 |
| Selected-screen lookout | Opt-in Linux source, masks, local inference, cooldown, no cloud fallback | B3, A3, C2 settings |
| Reusable workshop | Propose, scope-test, activate, match, pause and version with evidence | D2, A3, C2 |
| Project browsing | Multiple registered local projects; open repo metadata/files through computer | A1/A2, B1, C2 |
| Social sources | User-selected links or pasted X/Reddit content attached to a job | A1, C2 |
| Low-cost management | Idle world and viewing do not invoke a model; bounded planning is explicit | A2, B2, D3 |
| Restart | Preserve records, invalidate stale approval, reconcile ambiguous actions | A3, B2 |
| Calm interaction | Sparse overview, details on selection, expanded computer mode and reduced motion | C3 |

## Original acceptance requirements retained

| ID | Integration assertion / evidence | Owner |
|---|---|---|
| AC-01 | Job source, outcome, checks, actions, budget and history survive reload | A |
| AC-02 | One source event causes one proposed job across polls/restart | A+B |
| AC-03 | Disjoint tasks overlap in time; dependent/conflicting work waits; clones stay separate | A+B |
| AC-04 | Scene reflects snapshots; pausing animations does not pause/complete backend work | C |
| AC-05 | Seeded signup failure produces red evidence, exact frozen fix produces green evidence | D |
| AC-06 | Candidate attempt to alter a mandatory check/expected destination is rejected | B+D |
| AC-07 | Failed check and stale candidate cannot authorize delivery | A+B+D |
| AC-08 | Recipe includes scope, tests, permissions, limits, escalation and immutable version | D |
| AC-09 | Original + two additional supported cases pass; unsupported case abstains | D |
| AC-10 | Activated workshop handles a second supported failure without a new planning chat | A+B+D |
| AC-11 | Permission, retry, time, token and concurrency limits plus global stop work | A+B |
| AC-12 | Unity reopen preserves visibility; service restart does not repeat uncertain delivery | A+B+C |
| AC-13 | Main computer opens actual diff, log and screenshots; fixtures/recordings labeled | A+B+C+D |
| AC-14 | Cosmetic rewards never change policy or conceal measured/unknown cost | A+C |

## New release assertions

UI-01: Open an added, modified, renamed, deleted and binary file from the main computer. UI-02: Scroll a large diff/log without freezing; stale replies cannot replace a newly selected file. UI-03: Hostile TMP markup/ANSI is literal or sanitized. UI-04: Focus/Expand/Escape preserve the selection and working agents. UI-05: No external-browser-only substitute for native text, diff and image viewing.

MON-01: No inference calls for unchanged structured input. MON-02: Consent revocation stops screen capture. MON-03: Only selected/masked frames reach the configured local endpoint. MON-04: Cooldown and de-duplication prevent storms. MON-05: Missing portal/model capability is explicit and does not trigger cloud fallback. A full screen-watch claim requires an actual selected-source capture plus local-model test on the owner's machine; fixtures alone are not enough.

COST-01: Thirty seconds of idle office interaction and artifact browsing makes zero model requests. COST-02: One test failure produces at most the configured repair count. COST-03: Usage-unknown is shown as unknown, not free. COST-04: No automatic Sol promotion or hidden manager conversation. COST-05: Existing account limitations stop/defer work rather than rotating credentials.

## Explicit exclusions

Android/ClosePaw control, macOS/Windows screen capture, autonomous X/Reddit scraping/posting, distributed/cloud workers, shared multiplayer, paid bounty settlement, auto-merge/deployment, general-purpose desktop clicking, native PDF/DOCX/video editors, and public workflow marketplaces are deferred. Their source links and future integration boundaries remain in RESEARCH.md; a worker must not add them to “complete everything.”

A normal local-code release may run with selected-screen monitoring disabled on an unsupported machine, but it must label that capability unavailable. The complete monitoring-enabled acceptance profile remains BLOCKED until MON-01..05 run with the required environment. This is a platform capability distinction, not permission to report an untested feature as done.
