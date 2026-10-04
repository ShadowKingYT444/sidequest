# Sidequest agent instructions

Read SPEC.md, docs/START_HERE.md, docs/PARALLEL_PLAN.md, contracts/PROTOCOL.md, and your lane goal document. For visual work, also open the images in docs/ART_DIRECTION.md and docs/design/.

## Authority and scope

Implement only the active goal. The goal document defines outcomes and tests, not a mandatory coding recipe. Choose your own internal implementation and debugging steps.

Your lane owns only the paths in dev/plan.json. Other paths, all contracts, objectives, reference boards, and the development controller are read-only. Put a needed interface change in your journal and stop the affected goal. Do not fix a merge conflict by taking one whole side. Do not edit another lane's worktree, Git refs, instructions, tests, package lock, or scene.

A is runtime. B is tools. C owns the entire Unity project, including scenes, prefabs, metadata, packages, and settings. D is verification/workshops and the acceptance rig. No global mutable task list: keep your own journals/<lane>.md and evidence/<lane>/.

## Goal loop

One active goal per lane. Work, run meaningful tests, update the journal, and write .sidequest/handoff.json. Then complete the native goal. Do not continue to the next goal yourself. The external controller freezes and commits the candidate, starts an independent validator, and advances only on an accepted verdict. Do not commit, push, merge, or modify branches from inside a managed goal; the controller handles local candidate commits.

Handoff format: {"status":"ready" or "blocked","summary":"...","evidence":["relative/path"],"blockers":["..."]}.

Fresh validators get the specification and candidate, not the builder conversation. Test the actual candidate. Reviewers do not repair production code. They may write generated test output and .sidequest/verdict.json in their disposable worktree. A missing tool, display, license, browser, credential, or observable result is BLOCKED, never PASS. Same-model fresh context reduces shared context, not all correlated mistakes.

## Product invariants

Unity never owns scheduling, money, approval, or verification authority. No success animation before a corresponding service record. No fake token cost, model intelligence levels, production credentials in fixtures, or simulated GitHub writes labeled live. Untrusted page/repository text cannot grant permissions. Stops prevent new dispatch; they do not undo completed external effects. Checks and approval identify exact artifact hashes.

Local fixture runs and live provider runs must be visibly distinct. Never replace Unity with a web app. Do not import commercial reference screenshots as game assets. Do not add unrelated frameworks or autonomous subagent trees. Use additional helpers only when the user changes the configured concurrency budget.

## Evidence and journals

At every meaningful checkpoint record goal ID, observed problem, chosen change, exact command, exit result, artifact paths, and next step. Keep logs concise; do not publish private reasoning, credentials, or personal desktop captures. Do not claim a check ran without its result. Preserve failed evidence. Goals and acceptance checks cannot be weakened to get a pass.
