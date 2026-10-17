# Startup repair verification — 2026-10-17

This follow-up preserves the approved office and all execution gates. Native results below apply to this coding container, not to another desktop VM.

## Changes

- `sidequest.py setup/run/doctor` installs locked dependencies, starts an authenticated local runtime and office together, handles single-commit Git repositories, supervises shutdown, and prevents concurrent launchers using one state directory. The local API token is generated in memory only and is never written to a credential file. Coding is explicitly disabled in this convenience launcher.
- Electron startup errors now fail nonzero with safe setup/doctor guidance instead of silently quitting successfully. Missing builds do not open a broken window.
- Codex initialization returns bounded allowlisted diagnostics; failed readiness probes retain their timestamp, and changed settings discard stale diagnostics and model identities.
- CI covers application tests/build. Browser/native output can be redirected to preserve earlier evidence.

## Checks at the first checkpoint (`6a6b8a3`)

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

The startup and provider regressions were run red before implementation; their failure and green logs are retained here. Test doubles do not establish live provider acceptance. No model inference, paid turn, credential copying, repository-change delivery, merge or deployment occurred.

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

## Fresh-install acceptance and software graphics follow-up

The credential-free source archive at `6a6b8a3` passed `python3 sidequest.py setup` from an empty extracted dependency tree, including Electron installation and the production build. Its actual `run --browser` launcher loaded all 26 figures, handled a one-commit project in a path with spaces, registered/submitted/ran a zero-model Git inspection, passed `candidate.frozen_identity`, and displayed the immutable README through the file viewer. Closing the launcher stopped its runtime; no token files were created. [Verification](fresh-launch-verification.json), [setup log](fresh-setup.log), [office](fresh-launch-office.png), [actual file viewer](fresh-launch-artifact.png), [transfer manifest](source-transfer.json). This is browser/local-runtime acceptance, not a native Electron claim.

An additional real-runtime authentication regression brings launcher coverage to **10 tests**. The runtime's documented unauthenticated status is 403; the initial new test expected 401, and that test-authoring failure is preserved separately. No runtime auth behavior was changed.

Two longer browser journeys exhausted their unchanged timeouts on this container's SwiftShader renderer. A CDP CPU profile attributed 89% of sampled time to native `(program)` work, with little intersection work; actor geometry was left untouched. Identified software renderers now use the existing immediate camera positioning path. Hardware/unknown renderers retain animation; all assets, lighting, materials, resolution and security settings stay intact. The exact 90-second results/recovery journey then passed in **46.8 seconds**, and the 120-second recorded-session/reload journey passed in about **one minute**. Native graphics stalls remain measurable, so smooth software-GPU performance is not claimed. [Detailed browser evidence](../startup-browser-20261017/README.md).

Software-renderer classifier tests cover SwiftShader/llvmpipe/softpipe/basic-render-driver and hardware/unknown cases. Desktop coverage is now **87 tests**, and TypeScript/build pass. Final integrated browser results are recorded separately against the published source checkpoint.

[Published software-graphics checkpoint CI](https://github.com/ShadowKingYT444/sidequest/actions/runs/38992876405) passed at `8e39baba943c32da1c09944313e47286c69672ee`. [Preservation check](final-preservation.json) confirms all 126 original asset files and 834 earlier evidence files are unchanged from the initial PR head.

## Final integrated browser acceptance

At frozen `8e39baba943c32da1c09944313e47286c69672ee`, the full suite passed **25/25**, zero failures, skips or retries, in **12.9 minutes**. It covers real local Git/runtime inspection, immutable files/checks, recorded sessions, monitor navigation, draft/file/image retention, responsive office/settings and automated accessibility. Five composer cases intentionally use fake provider protocols with real IndexedDB/File behavior. Runtime/Vite stopped cleanly. See [complete browser evidence and exact source hashes](../startup-browser-20261017/README.md). This establishes browser acceptance; the native/live blockers above remain unresolved.
