# Start implementation

This is the fixed 0.3 specification, not a finished app. Use Linux, Git, Python 3.11+, a signed-in Codex CLI and the owner's supplied Unity office. Do not rebuild the art. The checked GitHub main did not include that asset project, so the local import/binding gate remains necessary.

## Prepare once

Read SPEC.md, ARCHITECTURE.md and ASSET_BINDING.md. Import the supplied assets/project without regenerating GUIDs or replacing art, record the actual editor/package/input setup in unity/SETUP.md and commit the baseline. Resolve service dependency patches once and pin lane-local locks during their first goals. No worker gets permission to select another stack.

Before updating an old development checkout, stop and preserve its current work. Existing .sidequest/setup.json and sidequest/A..D branches are not automatically migrated. Reconcile their changes deliberately; do not delete or reset them just to make prepare succeed. New lanes must share a base with the v0.3 specs and configuration.

```bash
git clone https://github.com/ShadowKingYT444/sidequest.git
cd sidequest
# Import/commit the owner's actual office project, then:
python3 -m unittest discover -s dev -p 'test_*.py' -v
python3 dev/check.py --setup
python3 dev/luna.py check
python3 dev/loop.py prepare
```

The no-turn preflight confirms the account advertises Luna/max and the effective configuration matches. If the project is untrusted or settings are overridden, correct the local Codex setup explicitly; do not silently substitute a model. Keep local configuration stable while workers run. This environment has not executed your Codex or Unity installation.

Review MCP/account settings before granting network access. Do not expose unrelated write-capable accounts or production credentials. --allow-network permits dependency downloads, localhost testing and the configured provider; it does not authorize publishing or account changes. Worktrees are coordination isolation, not a hostile-code sandbox.

## Four implementation lanes

Run in separate terminals from this main checkout, not inside the sibling worktrees:

```bash
python3 dev/luna.py run A --allow-network
python3 dev/luna.py run B --allow-network
python3 dev/luna.py run C --allow-network
python3 dev/luna.py run D --allow-network
```

Run only two commands at a time when laptop memory, Unity or local vision makes four inefficient. The lanes remain orthogonal. A lane's validator replaces its builder; there is no nested model tree. B's provider smoke tests are separately bounded calls. Missing credentials/editor/portal capability produce explicit blockers, not fake results.

Set UNITY_EDITOR to the installed executable for C. Do not run two editor sessions on one project or point a reviewer at the builder's editor. A fresh validator opens its own exact-candidate checkout. Each service owns its environment. Do not create shared caches that change source files across lanes.

Read LOW_TOKEN_EXECUTION.md for 40k builder/12k validator goal ceilings, three attempts and bounded escalation. The controller does not run automatically from GitHub, and it is not an account-wide hard billing firewall. Keep the controlling processes open; do not wrap stopped commands in an endless restart loop.

## Resume and integrate

Each builder writes its journal, runs named tests and writes .sidequest/handoff.json. The controller scopes/commits a candidate, starts a fresh reviewer at that SHA and advances only on PASS. FAIL uses a bounded attempt; BLOCKED preserves the candidate. Inspect interrupted changes before `python3 dev/loop.py checkpoint A`; this records an unvalidated checkpoint, not a pass or reset of attempts.

```bash
python3 dev/luna.py assemble --allow-network
```

This requires all twelve approved goals and exact lane heads. It merges into sidequest/integration and runs I1 against real services and the actual Unity build. No automatic main update or remote push. The full screen-watch profile additionally needs selected-source portal capture and the configured local vision endpoint; capability failure cannot become a passing claim.

## Manual Codex app use

The same goal docs work in the app: open the correct permanent worktree, select Luna/max, and use `/goal Complete A1 in docs/goals/A-runtime.md. Follow its Read list and AGENTS.md. Do not start A2.` Substitute the lane/goal. Freeze each candidate and start a completely new validation chat in a separate checkout. Repository instructions alone cannot create those app threads; the CLI controller automates that handoff. Never mix manual writers and the controller on the same lane.
