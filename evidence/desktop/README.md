# Desktop slice evidence — 2026-10-14

This is a partial frontend/Git implementation, not completed Sidequest or live agent integration. The actual office and native Electron slice remain blocked.

The current browser screenshots show genuine committed Sidequest Git data, using base `69bf06696a93c9f58eee2d088e84404d4f6563d6` and candidate `674f1477efb7327fe46fbe3aa6f5d622766c1723`. Worker/agent status is unavailable, not simulated working activity. Screenshot pixels prove rendering only.

- [Setup / missing-assets state](setup-desktop.png)
- [Actual Git diff with source syntax](git-diff.png)
- [Expanded Git diff](expanded-diff.png)
- [960px reading layout](viewer-960.png)
- [390px reading layout](viewer-390.png)

All six browser checks passed on Chromium at 1440×900, 960×780 and 390×780: real immutable Git reads, one lazy selected editor, file/scroll continuity through Expand/Escape/reopen, keyboard/focus return, reduced motion, no horizontal page overflow, and rejected cross-origin/mutation API requests. The hostile-text/error-retry and automated WCAG A/AA scans also passed (0 reported violations). Exact verification and source hashes are in [verification.json](verification.json). Synthetic fixtures are used only in unit/security tests and are not pictured as a working office.

`npm run build` and TypeScript passed. The large Monaco diff and Three.js chunks are separate lazy modules; no memory/frame-rate promise has been measured. Independent review identified and prompted correction of the default Draco decoder CDN path, Git environment/config exposure, potential credential content, and Monaco worker packaging. [The run instructions](../../desktop/README.md) describe the surviving heuristic secret-filter limitation.

## Exact blockers

**Actual art transfer: blocked.** Drive successfully exposes all eight archive parts (535,951,540 bytes total) for the owner's October 7 kit. Every VM transfer to the returned authenticated asset host failed with `Tunnel connection failed: 403 Forbidden`, including the additional-network/escalated route. An approved direct connection then failed DNS resolution. No archive bytes were obtained, so the expected archive SHA was not independently verified here. No `.blend`, GLB, replacement art, fabricated anchors or screenshots of an invented office were committed. The offline safe installer and GLB inspector are available for pickup after transfer.

**Native Electron startup: blocked.** The Electron 44.7.1 runtime downloaded successfully. Direct sandbox-preserving native startup aborted because the local `chrome-sandbox` helper is not configured with root ownership/mode 4755; the user-namespace alternative reported `No usable sandbox`. [Native smoke result](electron-smoke.json) records the exact failure. No root/system/auth change was made. An earlier Playwright convenience-launch attempt implicitly included its sandbox-disabling flag and also failed; it is excluded from acceptance. The retained smoke script launches the native executable directly and never adds that flag. A sandbox-capable desktop host is required for runtime proof.

UI Git/status actions invoke no model. No agent job, provider inference, authentication flow, Cooki eval or character work was launched. No merge or deployment is authorized.
