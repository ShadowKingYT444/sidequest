# Start here

This repository prepares development. The application is not implemented yet. Use a local Linux or macOS checkout with Git, Python 3.11+, a signed-in Codex CLI, and sufficient disk space. The Unity lane also needs an installed Unity 6 editor and its desktop build module. Windows users can run the controller in WSL, but must validate their Unity bridge and path mapping before lane C; WSL compatibility is not pre-validated.

## 1. Check and prepare

```bash
git clone https://github.com/ShadowKingYT444/sidequest.git
cd sidequest
codex --version
codex app-server --help
python3 -m unittest discover -s dev -p 'test_*.py' -v
python3 dev/check.py --setup
python3 dev/loop.py prepare
```

`prepare` creates four sibling worktrees under `../sidequest-worktrees/`, all from the same commit. It records the base SHA and exact paths under the ignored `.sidequest/` directory in this checkout. It never resets an existing branch or overwrites a worktree. Use this main checkout for controller commands. Do not also start Codex writers manually in a managed worktree.

Inspect `dev/plan.json` before running. Default limits are three attempts per goal, a 60-minute timeout per thread, 80,000 goal tokens for a builder, and 32,000 for a validator. They are ceilings, not cost estimates or a spending authorization. Codex billing follows your own account and configuration. Reduce limits when appropriate. No model is hard-coded; your selected Codex model is used. Set `SIDEQUEST_MODEL` to an account-supported model ID to override it.

Before launching, inspect your Codex MCP/tool configuration and remove unrelated accounts or write-capable integrations. Worktrees and the workspace sandbox are coordination controls, not a security boundary against a hostile agent. Do not provide production secrets. The example `--allow-network` flag permits dependency downloads, localhost services and your configured test provider; it does not authorize remote publishing. Omit it for offline work with dependencies already installed. Unknown interactive approval requests stop the controller rather than being auto-approved. `--allow-network` is needed for the browser/HTTP and real-provider checks on environments that restrict localhost too.

For image inspection, run `python3 dev/cache_references.py` before lane C. The committed SVG boards are local; commercial game screenshots are linked references, not shipped assets. Codex Goals require a Goals-capable app-server (official Goals guide: 0.128.0 or later); a feature test is stronger than a version label. Unsupported RPC methods stop the run.

## 2. Start four lanes

Run each command in a separate terminal from the main checkout:

```bash
python3 dev/loop.py run A --allow-network
python3 dev/loop.py run B --allow-network
python3 dev/loop.py run C --allow-network
python3 dev/loop.py run D --allow-network
```

There are at most four controller-managed development threads when you run those four commands. A validator replaces its lane's builder; it does not run beside it. Subagent fan-out is disabled in these threads. Product-provider tests can make additional model calls within their own configured limits; these are not extra development lanes. The CLI process must remain running. This setup does not create scheduled cloud jobs.

Lane C must inspect your installed editor, choose one installed supported Unity 6 version, create `unity/`, and commit that exact version and its package lock. Set `UNITY_EDITOR` to the editor executable for tests. C owns all Unity assets. Do not run two editor sessions against the same project or point a validator's MCP at the builder's editor. Close the builder editor before validating its snapshot. Missing editor access stops C; A, B, and D can still proceed.

## 3. What each loop does

```text
Native goal → implementation + journal → scope check → candidate commit
   → fresh validator thread in candidate worktree → independent evidence
       PASS    → next goal
       FAIL    → repair same goal, with a new attempt and fresh validation
       BLOCKED → stop this lane and record the required input
```

`thread/goal/set` sets actual persisted Codex goal state. The controller does not pipe `/goal` text into `codex exec` and pretend it is a slash command. It starts a new thread for every builder attempt and validator, keeping continuity in the lane journal and code. `thread/fork` and `resume --last` are not used for validation.

State, thread IDs, local protocol logs, reports, and candidate SHAs are under `.sidequest/`. Logs stay local and can contain source text. Do not publish them unreviewed. On interruption, inspect the worktree and journal before rerunning. Passed goals are resumed by recorded candidate SHA; unexpected branch or worktree changes stop the controller. After inspecting interrupted, uncommitted owned edits, `python3 dev/loop.py checkpoint A` preserves them as an unvalidated commit. Then rerun A. This does not reset attempt limits or mark a goal passed. A blocked validator reruns against the same candidate after the environment is repaired.

## 4. Merge and validate the product

```bash
python3 dev/loop.py assemble --allow-network
```

This requires all twelve goals to have independent PASS records and their lane heads to match the recorded candidates. It creates `sidequest/integration`, merges the exact approved commits, and runs the fresh I1 integrated validator. It does not push or update main. A conflict or failed integrated run stops; send the finding to the owning lane. A blocked I1 can be rerun with `assemble` against the same unchanged merged candidate. Changed integration inputs require deliberate coordinator reconciliation; no reset or conflict auto-resolution is provided. Do not mark the product done because the merge was clean.

After I1 passes, inspect the recorded build and evidence. Publishing the integrated product is a separate deliberate action. The current main contains the launch kit only.

## Native app alternative

You can use the same goals in the Codex app instead of the controller. Use one permanent worktree per lane and paste `/goal Complete A1 in docs/goals/A-runtime.md. Follow AGENTS.md and do not begin A2.` with the appropriate lane and goal. At each completion, freeze a commit and start a new validator chat in a separate checkout at that SHA. Follow `docs/VALIDATION.md`. This mode needs manual handoffs; a repository instruction alone cannot create app threads. Never run this mode and the controller on the same lane together.
