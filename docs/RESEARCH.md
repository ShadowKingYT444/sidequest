# Research decisions — 2026-10-04

Only primary documentation and original projects inform the technical decisions below. Links are references, not a claim that any dependency has been installed.

| Source | Decision |
| --- | --- |
| [OpenAI: Goals](https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex) | Each objective has explicit checks, a budget, a journal, and a blocked stop. Persist a goal rather than relying on repeated “continue” messages. |
| [OpenAI: App Server](https://developers.openai.com/codex/app-server) | Use `thread/start`, `thread/goal/set`, and `turn/start`. Goal set uses the same persisted state as `/goal`. Never claim a fork is a clean reviewer. The client must remain connected. |
| [OpenAI: non-interactive mode](https://developers.openai.com/codex/noninteractive) | Do not treat a slash command string passed to `codex exec` as a supported interactive command. Keep permissions explicit and records machine-readable. |
| [OpenAI: worktrees](https://developers.openai.com/codex/app/worktrees) | Give each lane a permanent worktree and each validator a frozen checkout. Worktrees separate files, not shared external resources. |
| [OpenAI: config reference](https://developers.openai.com/codex/config-reference) | Enable Goals explicitly for this controller. Preserve the user's selected model. Disable nested multi-agent fan-out in managed runs to bound concurrent sessions. |
| [Geoffrey Huntley: Ralph](https://ghuntley.com/ralph/) | Keep task continuity in repository artifacts; use tests and bounded iteration. We adopt the repeated objective/check pattern, not an infinite loop. |
| [Unity: scene and prefab version control](https://unity.com/blog/author-scenes-and-prefabs-with-verson-control) | One Unity asset owner; commit asset metadata with its source. Use text serialization and preserve GUIDs. A YAML merge is not proof that a scene still works. |
| [Git: worktree](https://git-scm.com/docs/git-worktree) | Use named lane branches and detached candidate worktrees. Never reset or force-update a user's branch to repair setup. |
| [Playwright: test assertions](https://playwright.dev/docs/test-assertions) | Browser acceptance must exercise the actual signup path and check visible results, not just a 200 response. D selects and pins the package in its own directory. |

## Product and art precedents

[Little Big Workshop](https://store.steampowered.com/app/574720/Little_Big_Workshop/) informs readable miniature workspaces and tangible job artifacts. [Good Company](https://store.steampowered.com/app/911430/Good_Company/) informs build-mode previews and production connections. See the actual images and the per-image “borrow/avoid” notes in ART_DIRECTION.md.

[Kenney's Isometric Miniature Prototype](https://kenney.nl/assets/isometric-miniature-prototype) is a CC0 **2D** reference, not an imported 3D Unity kit. Do not mistake its category or license for permission to use unrelated commercial screenshots.

The original [agent-build-ideas collection](https://shadowkingyt444.github.io/agent-build-ideas/) remains the inspiration source. This setup does not silently vendor those projects. B owns a narrow original adapter rather than coupling the application to every prototype on that site.

## Claims we do not make

This design does not establish that Ralph beats other workflows, that four agents beat one on every task, that a fresh same-model reviewer is unbiased, or that this project can win every hackathon. The purpose of fixed boundaries is to remove predictable coordination conflicts. The final test still measures whether the application works.

The controller is checked using a fake local protocol server and temporary Git repositories. Its live integration requires the installed Codex build and account. Unsupported methods, missing credentials, and missing Unity access are explicit blockers rather than silent fallbacks.
