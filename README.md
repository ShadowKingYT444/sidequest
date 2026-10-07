# Sidequest

A calm Unity office for real agent swarms. Inspect artifacts and diffs directly on the main worker's computer. Use existing coding agents; do not build another agent framework.

**Current state:** implementation specification and development tooling. The owner has completed the office assets; they are protected inputs. The inspected repository does not yet contain the Unity asset project. Do not regenerate the office.

Start at [START HERE](docs/START_HERE.md). Read [SPEC](SPEC.md) for scope or [ARCHITECTURE](docs/ARCHITECTURE.md) for the fixed stack. Workers read only their assigned goal and its relevant documents, not the entire research archive.

| Lane | Exclusive responsibility |
|---|---|
| A | Local runtime, database, scheduler, artifact HTTP service |
| B | Coding-provider adapter, isolated Git, file/diff capture, local monitoring |
| C | Existing Unity assets, computer UI, office interaction and build |
| D | Independent checks, reusable workshops, demo and final acceptance rig |

Each lane has three goals. Each candidate gets a new validator thread at its exact commit. Main is not automatically changed by development runs. The [low-token policy](docs/LOW_TOKEN_EXECUTION.md) selects Luna/max, short task packets, deterministic tests first, bounded attempts, and no always-running manager.

```bash
python3 -m unittest discover -s dev -p 'test_*.py' -v
python3 dev/check.py --setup
python3 dev/loop.py prepare
python3 dev/luna.py run A --allow-network
# Start B, C and D in their own terminals from this same checkout.
```

Complete the asset/environment preflight in START HERE before preparing worktrees. `dev/luna.py` checks the effective Codex configuration and account model support before allowing a model run. The low-cost configuration is an explicit preference, not an estimate of your account bill.

[Computer UI](docs/COMPUTER_UI.md) · [Asset binding](docs/ASSET_BINDING.md) · [Protocol](contracts/PROTOCOL.md) · [Extensions](contracts/EXTENSIONS.md) · [Feature coverage](docs/FEATURE_MATRIX.md) · [Upstream sources](docs/RESEARCH.md)

The diagrams are architecture specifications, not screenshots of an implemented app. Earlier concept images and station-kit drawings are not authority to redesign the owner's completed office.
