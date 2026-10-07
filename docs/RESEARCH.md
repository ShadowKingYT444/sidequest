# Source audit and reuse decisions — 2026-10-07

These are explicit reference links and adoption decisions, not a shopping list for implementation agents. Do not load every upstream README per goal. Use the fixed architecture unless a reproducible incompatibility requires a recorded change. No upstream code or asset has been vendored by this specification update.

## Original inspiration set

The owner's [agent-build-ideas collection](https://shadowkingyt444.github.io/agent-build-ideas/) and its [source list](https://github.com/ShadowKingYT444/agent-build-ideas/blob/main/ideas.json) were inspected. Earlier personal research also named clodfarm, cubefarm, Observer, ClosePaw, Bountora and reusable factories. The relevant mechanisms are selected below; unrelated trending projects are not mandatory dependencies.

| Project and exact source | Borrow | Do not import into Sidequest |
|---|---|---|
| [clodfarm](https://github.com/matank001/clodfarm), [governor](https://github.com/matank001/clodfarm/blob/main/clodfarm/governor.py), [budget notes](https://github.com/matank001/clodfarm/blob/main/docs/budget.md) | Deterministic capacity governor, durable worker status, explicit limits | AWS/Dynamo deployment, account-rotation behavior, or provider-specific quota assumptions. Codex capacity comes from its own account. |
| [cubefarm](https://github.com/leonvanzyl/cubefarm), [how it works](https://github.com/leonvanzyl/cubefarm/blob/main/docs/how-it-works.md) | Office as observation/control surface, real agent desks, inspectable QA and Git work | Whole Three.js frontend, its art or a second backend. Existing Unity assets remain authoritative. |
| [Observer](https://github.com/Roy3838/Observer), [README](https://github.com/Roy3838/Observer/blob/main/README.md) | Narrow selected sensor → local model → condition event; watch changes without a full planner polling | Its full app, arbitrary generated notification/click code, or an invented stable SDK. Original local lookout code implements the narrow mechanism. |
| [TesterArmy e2e](https://github.com/tester-army/e2e), [official introduction](https://tester.army/blog/introducing-e2e) | Mix deterministic tests with bounded agent exploration; reuse successful checks | A mandatory second TypeScript runtime or the claim that browser/mobile tests validate Unity desktop. APIs are still evolving. |
| [Playwright MCP](https://github.com/microsoft/playwright-mcp) | Structured browser operations when interactive QA is needed | Loading a large browser tool schema into every coding call. Its README recommends CLI/skills for many coding-agent workflows. |
| [Impeccable](https://github.com/pbakaus/impeccable) | Progressive disclosure, clear visual hierarchy, brief/critique discipline and deterministic checks where applicable | Rebuilding completed art or claiming web/DOM detectors validate Unity scenes. Use explicit Unity screenshots and native checks instead. |
| [ZOB harness](https://github.com/cgarrot/zob-harness) | Promote proven procedures into reusable factories/packages | Its Pi/tmux runtime or a second agent-management system. The recipe manifest is original and narrowly scoped. |
| [Bountora original post](https://www.reddit.com/r/SideProject/comments/1wjkdn4/bountora_a_job_board_where_ai_agents_bid_on/) | Job descriptions with objective acceptance conditions | Financial escrow, bidding, crypto payments or a dependency without a reviewed implementation. This is an inspiration reference, not a verified SDK. |
| [ClosePaw](https://github.com/imoonkey/closepaw) | Future mobile-worker boundary and visible pause/takeover | Android/virtual-display implementation in the initial Linux desktop release. It stays deferred. |

License observations from inspected upstream files: clodfarm's [license](https://github.com/matank001/clodfarm/blob/main/LICENSE) is MIT; Observer's [license](https://github.com/Roy3838/Observer/blob/main/LICENSE) is AGPL-3.0; Impeccable's [license](https://github.com/pbakaus/impeccable/blob/main/LICENSE) is Apache-2.0. No blanket license claim is made for the whole inspiration list. Before copying code, pin its exact revision, inspect all relevant notices and record attribution. Choosing a process boundary does not automatically remove license obligations. Prefer a small original adapter over copying an entire product.

## Platform decisions backed by primary documentation

| Primary documentation | Decision |
|---|---|
| [GPT-6 Sol and Luna](https://openai.com/index/introducing-gpt-6-sol-and-luna/) | Luna is the requested economical worker family. Account availability and effort support still require runtime discovery. No subscription cost is inferred from advertised API rates. |
| [Codex app-server](https://developers.openai.com/codex/app-server) | Reuse Codex's real editing/tool loop and persistent goals. model/list advertises supported efforts; config/read resolves effective settings; turn/start supports explicit model and effort. |
| [Codex configuration](https://developers.openai.com/codex/config-reference) | Store the preference in .codex/config.toml, then verify it was honored. max is model/client-dependent, not a universally accepted value. |
| [Codex Goals guide](https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex) | Persistent bounded objective rather than repeated “continue” prompts. A goal completing still requires external validation. |
| [Git worktrees](https://git-scm.com/docs/git-worktree), [Git diff](https://git-scm.com/docs/git-diff) | Separate development worktrees; Git-generated diffs and immutable revisions. Runtime task clones avoid shared writable Git refs. |
| [Unity world-space UI](https://docs.unity3d.com/Packages/com.unity.ugui@2.0/manual/HOWTO-UIWorldSpace.html), [Canvas render modes](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/Canvas-renderMode.html) | Render native controls on the existing monitor; reuse the same state for enlarged screen-space viewing. No embedded browser is necessary for text/diff/image views. |
| [TextMeshPro](https://docs.unity3d.com/Packages/com.unity.textmeshpro@4.0/manual/index.html) | Native text rendering; disable rich text for untrusted source/logs. Use the package compatible with the supplied Unity project, not the version embedded in a documentation URL. |
| [Playwright Python contexts](https://playwright.dev/python/docs/browser-contexts) | Isolate browser test state per run and collect concrete evidence. |
| [FastAPI async tests](https://fastapi.tiangolo.com/advanced/async-tests/) | Async HTTP contract tests without a separate frontend stack. |
| [XDG ScreenCast portal](https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.ScreenCast.html) | Linux user-mediated selected-source capture via portal/PipeWire, not a hidden global screenshot loop. |

## Deliberate omissions

No Hindsight/Chroma/graph memory server is necessary for short implementation jobs: immutable artifacts, task records and small journals provide continuity. No new framework must decide task order when dependency and scope checks can do it. No browser engine belongs inside the game merely to display a diff. No computer-use model is necessary to observe a process exit code. Sol is a bounded escalation option, not a fixed tax on every worker response.

This audit used direct source inspection. No research subagents or product agents were launched in this chat environment. Model identifiers and source descriptions were checked, but live Codex, Unity builds, portal capture and the owner's asset project were not run here. Their acceptance evidence remains a development requirement.
