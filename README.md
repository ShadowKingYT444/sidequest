# Sidequest

Sidequest is a local visual office for inspecting coding work: click computers to view recorded sessions, draft text with files/images, browse Git diffs and immutable artifacts, or use the workboard to run zero-model Git inspections. Settings detect installed CLIs and show their verified connection state. **Native shell/IPC passes; office rendering needs working WebGL2. Live coding awaits sign-in and verified spending controls.** See the [feature-by-feature proof](docs/ACCEPTANCE.md).

## Dependencies

Linux or macOS, **Python 3.12+**, **Node.js 24 LTS** with npm, and **Git**. Native Electron needs a desktop session with a supported OS sandbox. Native Windows is not supported yet.

## Install and run

```sh
git clone --depth 1 --branch feat/electron-office-diff https://github.com/ShadowKingYT444/sidequest.git
cd sidequest
python3 sidequest.py setup
python3 sidequest.py run --repo /absolute/path/to/your/git-project
```

Use a small trusted Git project with at least one commit. Setup installs locked dependencies and builds the app; closing the app stops its runtime.

For browser mode:

```sh
python3 sidequest.py setup --browser
python3 sidequest.py run --browser --repo /absolute/path/to/your/git-project
```

Open **http://127.0.0.1:5173**; press **Ctrl+C** to stop. Diagnose prerequisites with `python3 sidequest.py doctor` (or `doctor --browser`). No provider turn or new login is required.

[Setup details](docs/GETTING_STARTED.md) · [Screenshots and acceptance](docs/ACCEPTANCE.md) · [Developer docs](docs/README.md) · [Evidence index](evidence/README.md)
