# Specification and launch-tool verification

## Original launch kit

The original 69bf066 baseline had 15 offline controller tests and a successful GitHub Actions run. Those tests validate the worktree/goal-controller behavior under local test doubles, not a working Sidequest game or a live Codex integration.

## October 7 specification revision

Added fixed architecture and in-computer artifact/diff interfaces, existing-asset protection, local monitoring/QA decisions, source audit, revised goal packets, lower default budgets and a Luna/max preflight launcher. The original loop lifecycle is retained; the launcher explicitly pins model/effort on every app-server invocation and validates effective config plus account-advertised support. The preference is also recorded in .codex/config.toml for manual app use.

New tests cover account/model/effort failure, visual modality requirements, catalog pagination/cursor errors, absence of inference in the preflight, injected command restoration, goal/read-list consistency, budget/config agreement, feature coverage and labeled artifact fixtures. They are offline tests; they do not make paid model calls.

Required verification commands, run by the existing GitHub workflow after publication:

```bash
python3 -m unittest discover -s dev -p 'test_*.py' -v
python3 dev/check.py --setup
```

Consult the Actions result for the exact published commit. This document does not predeclare that an unrun CI job passed. Markdown code-fence and link checks are structural only; they do not prove Mermaid renderer compatibility or product behavior.

Not executed in this preparation environment: research subagents, real development agents, installed Codex model inference, Unity editor/build, the owner's actual asset project, selected-source Linux capture, local vision inference or live GitHub delivery. Each remains explicit acceptance evidence or an environment preflight step. No assets were regenerated and no product feature is marked implemented.
