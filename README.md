# Sidequest

A local Electron office for inspecting coding work, recorded sessions, files and Git diffs. The original office assets are included. Python owns the local runtime; React and Electron display it.

**Current limit:** local Git inspection and office interactions work. Live coding is still unavailable: the Codex adapter cannot enforce the required spending ceiling. Other detected CLIs have no execution adapter. Installed does not mean connected. See [current verification and blockers](evidence/desktop/startup-20261017/README.md).

## Quick start

Requires **Python 3.12+**, **Node.js 24 LTS** (with npm), and **Git**, on Linux or macOS. Native Electron also needs a desktop session with a working OS sandbox. Native Windows is not supported by the Python runtime yet.

From the Sidequest folder:

```sh
python3 sidequest.py setup
python3 sidequest.py run --repo /absolute/path/to/your/project
```

The project must be a trusted local Git repository with at least one commit. Setup installs the locked dependencies and Electron, then builds the app. Run starts the authenticated runtime and office together, waits for readiness, and stops both when you close the app. It rebuilds changed renderer source automatically. There is no token to copy, provider login to create, or paid turn to start.

For a headless host or browser-only use:

```sh
python3 sidequest.py setup --browser
python3 sidequest.py run --browser --repo /absolute/path/to/your/project
```

Open **http://127.0.0.1:5173** after Vite reports ready. Press **Ctrl+C** to stop. Browser mode exercises the office and runtime but does not establish native Electron acceptance. On identified software GPUs, camera focus moves directly to the selected computer to reduce stalls; hardware GPUs retain the animated transition.

```sh
python3 sidequest.py doctor          # dependencies and desktop display
python3 sidequest.py doctor --browser
```

Git compares the previous commit with HEAD; a one-commit repository uses HEAD for an empty comparison. Use `--base <commit>` to choose a different base. The viewer displays committed files. Jobs performs an immutable inspection and does not deliver changes to your source.

Runtime history lives outside Git, under `~/.local/share/sidequest` on Linux (or `$XDG_DATA_HOME/sidequest`) and `~/Library/Application Support/Sidequest` on macOS. Use `--state-dir /absolute/private/directory` to change it. The launcher uses a new in-memory local API token each session; no persistent credential is generated. A lock prevents two launcher instances from using the same state at once. Your CLI account configuration is unchanged.

## Use the office

- Click a workstation for provider choices. **Connect provider** opens Settings; detected CLIs show their honest connection state.
- Click a computer for its recorded output and local text/file/image draft. **Files** opens Git or assigned results. **Expand** and **Escape** retain your place.
- Open **Jobs**, register the configured repository, submit an inspection, then click **Run inspection**. Inspect its immutable files, diff, report and activity; assign the result to a computer.
- Click a figure for recorded session ownership, or the workboard for tasks. Notifications distinguish completed work from work needing attention.

Live Send/Launch remains gated. No model inference is needed to view the office, edit local drafts or run a Git inspection. Large repositories are bounded by the existing inspection limits; the asset-heavy Sidequest checkout itself exceeds those limits, so use a small project for the first inspection.

## Development and verification

[Desktop details](desktop/README.md) · [Evaluation commands](docs/RUN_EVALS.md) · [PR handoff](docs/PR1_HANDOFF.md) · [Original asset provenance](desktop/public/office/provenance.json)

```sh
python3 -m unittest discover -s tests -p test_launcher.py -v
npm --prefix desktop test
npm --prefix desktop run build
.venv/bin/python -m unittest discover -s services/runtime/tests -p 'test_*.py' -v
.venv/bin/python -m unittest discover -s services/tools/tests -p 'test_*.py' -v
```

CI runs the application unit suites and production build as well as the retained controller checks. Browser and native results are recorded separately. Do not disable Electron's sandbox to make a native check pass.

The original managed development documents remain under [START HERE](docs/START_HERE.md), [SPEC](SPEC.md) and [ARCHITECTURE](docs/ARCHITECTURE.md). Their Unity/controller instructions are historical where superseded by the current Electron branch. `dev/luna.py` runs development model workers; it is not needed to install or use the office.
