# Independent native Electron smoke — 17 October 2026

**The separate cloud-desktop tester reported a passing native shell/IPC smoke test. Office rendering subsequently failed with `WebGL2 blocklisted`.** Setup/build and actual Electron smoke both exited 0 with the sandbox intact. Real Git IPC returned `local-git`; the renderer had no Node access, and expected isolated bridge/runtime methods were verified. The transferred archive plus patch matched functional source `8e39baba943c32da1c09944313e47286c69672ee`.

[Original independent results](imported/RESULTS.txt), [shell/IPC smoke JSON](imported/smoke/electron-smoke.json), [native startup log](imported/native-ui.log) and [artifact hashes](import-manifest.json) are now imported from the supplied Library archive without content edits. The window and inspection screenshots were visually inspected during integration. This was a separate-host test, not a local rerun.

The coding container's earlier sandbox/display failure remains in its original evidence; it does not negate the supported VM's native success. Real native Monaco Git diff, Expand/Escape/reopen, provider executable detection, zero-model inspection and immutable file result viewing also passed. The office render, OS clipboard/file-chooser and live provider acceptance remain separate. Codex 0.159.2 initializes successfully with its default `/home/agent/.codex` and exits 0, but login status reports `Not logged in`. The user approved device sign-in, but its request failed before a URL/code was issued; no saved authentication or model turn resulted. The parent subsequently found that desktop direct egress to auth.openai.com fails while the separate shell reaches it through its managed proxy. Desktop proxy variables are unset; no proxy or security settings were changed. Supported desktop egress setup is required. Result display assignment works but does not attach a recorded session; Trace remains empty, and populated notifications were not proved.

## Native pictures

[Graphics failure](imported/screenshots/native-office-blocked.png) · [Git diff](imported/screenshots/native-git-diff.png) · [Reopened diff](imported/screenshots/native-diff-reopened.png) · [Settings](imported/screenshots/native-settings.png) · [Usage](imported/screenshots/native-usage.png) · [Real inspection result](imported/screenshots/native-inspection-result.png) · [No attached session](imported/screenshots/native-session-outcome.png).

The inspection is a deterministic local Git fixture, not AI output. [Codex initialize](imported/codex-initialize.json) proves only auth-free protocol startup; [login status](imported/codex-status.log) remains unauthenticated.

## Credential-free evidence transfer

On the host that can read the files, use the Library `create_library_file` tool with an explicit list containing `electron-smoke.json`, `electron-window.png`, and any final UI screenshots/video plus a small verification manifest. Record SHA-256 hashes, sizes, the exact source checkpoint, commands/exit codes and mock boundaries. Do not include account homes, private runtime databases, tokens or credentials. Apply any returned version xattrs to the originals.

Send the returned `library_file_id`, `file_id`, filename and SHA-256 for each artifact. The implementation workspace can then call Library `prepare_materialize` into a fresh incoming directory, verify all hashes, inspect the result and copy evidence here without overwriting older runs. No shared host path, account login, credential copying or public upload is required.
