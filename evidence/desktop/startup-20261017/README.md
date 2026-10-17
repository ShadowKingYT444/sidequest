# Startup repair verification — 2026-10-17

This follow-up preserves the approved office and all execution gates. Native results below apply to this coding container, not to another desktop VM.

## Changes

- `sidequest.py setup/run/doctor` installs locked dependencies, starts an authenticated local runtime and office together, handles single-commit Git repositories, supervises shutdown, and prevents concurrent launchers using one state directory. The local API token is generated in memory only and is never written to a credential file. Coding is explicitly disabled in this convenience launcher.
- Electron startup errors now fail nonzero with safe setup/doctor guidance instead of silently quitting successfully. Missing builds do not open a broken window.
- Codex initialization returns bounded allowlisted diagnostics; failed readiness probes retain their timestamp, and changed settings discard stale diagnostics and model identities.
- CI covers application tests/build. Browser/native output can be redirected to preserve earlier evidence.

## Checks at the first checkpoint

| Check | Result |
| --- | --- |
| Locked npm/Python dependency installation | Pass in clean local dependency directories |
| Desktop unit tests | 85 passed, including 3 startup regressions; baseline was 82 |
| Launcher tests | 9 passed |
| Provider tests | 59 passed |
| Runtime tests | 66 passed |
| Workshop tests | 13 passed, including actual headless browser red/green fixtures |
| Development-controller tests/setup | 31 passed; setup check passed |
| Production TypeScript/Vite build | Pass (existing chunk-size advisory remains) |
| Real launcher port-collision check | Runtime ready, Vite refuses occupied 5173, launcher exits 1, runtime shuts down, zero token files |
| Original office assets | All 126 tracked files unchanged |
| Full product browser suite | In progress at this checkpoint; later evidence is separate |

The startup and provider regressions were run red before implementation; their failure and green logs are retained here. Test doubles do not establish live provider acceptance. No model inference, paid turn, credential copying, source delivery, merge or deployment occurred.

## Native host blockers reproduced

- [Electron](electron-smoke.json): exit SIGTRAP; SUID sandbox helper is not supported in this container. No display is available to the shell. No sandbox flag or system permission was changed.
- [Codex](provider-native-after.json): `initialize` only, exit 1, zero stdout responses. [Path evidence](provider-state-paths.json) identifies `open(/run/codex-environment/codex-home/installation_id, O_RDWR|O_CREAT)` returning EROFS. SQLite state was already writable under `/tmp`; the original CODEX_HOME is on a read-only mount. No account, catalog or turn request followed.
- Production `usd_cost_enforced` remains false. A different host may solve startup, but it does not by itself solve the spending-authority gate.

## Separate native desktop verification

1. Extract the exact source checkpoint including assets and locks; record its SHA and archive digest. Use Python 3.12, Node 24 and Git. Run `python3 sidequest.py setup` then `python3 sidequest.py doctor` in the actual desktop session.
2. Use a small trusted Git project with two commits (or a single initial commit). Run `python3 sidequest.py run --repo /absolute/project --state-dir /absolute/private/state`. Keep Electron sandboxing enabled. Never copy CLI credentials from this container.
3. Verify the office, workstations, figures and workboard; monitor Trace/Files, text/file/image local drafts, Expand/Escape retention, Settings truthfulness, and the real zero-budget Git inspection flow. Confirm jobs/files/check activity remain connected and closing the window stops the owned runtime.
4. Run `SIDEQUEST_EVIDENCE_DIR=/absolute/new/evidence SIDEQUEST_REPO=/absolute/project npm --prefix desktop run test:electron`. Capture isolated IPC, Node-disabled renderer and native screenshot evidence. This smoke covers the built window/Git bridge, not live coding or OS clipboard.
5. Record native paste/file chooser and restart behavior manually. Only initialize the existing authenticated provider if supported. Stop at any permission/authentication blocker and preserve the exact error. Do not run a model turn until spending/consent/scope controls can be enforced.

The PR stays draft until native and live-provider acceptance is established.
