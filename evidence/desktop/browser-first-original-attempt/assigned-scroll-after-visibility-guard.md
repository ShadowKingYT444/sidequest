# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: jobs-live.spec.ts >> real jobs clear stale notices, recover reads and preserve assigned computer results
- Location: tests/browser/jobs-live.spec.ts:88:1

# Error details

```
Error: expect(received).toBeGreaterThan(expected)

Expected: > 100
Received:   0

Call Log:
- Timeout 15000ms exceeded while waiting on the predicate
```

# Page snapshot

```yaml
- main [ref=e3]:
  - generic [ref=e4]:
    - generic [ref=e5]: sidequest
    - generic [ref=e6]: sidequest
    - button "Settings" [ref=e7] [cursor=pointer]
    - button "Jobs" [ref=e8] [cursor=pointer]
    - button "Refresh Git" [ref=e9] [cursor=pointer]
  - region "Computer job results" [ref=e16]:
    - generic [ref=e17]:
      - generic [ref=e18]:
        - paragraph [ref=e19]: Assigned job · Read-only
        - heading "Job results" [level=2] [ref=e20]
      - generic [ref=e21]:
        - button "Expand" [ref=e22] [cursor=pointer]
        - button "Refresh status" [ref=e23] [cursor=pointer]
        - button "Office Esc" [ref=e24] [cursor=pointer]
    - region "Selected job" [ref=e26]:
      - generic [ref=e28]:
        - heading "Browser inspection 2026-10-14T08:18:06.506Z" [level=3] [ref=e29]
        - paragraph [ref=e30]: verifying · $0 budget · c3a6eb1d-5fef-42ce-8f7e-3b9b77df693c
      - status [ref=e31]: Inspection results ready. Source delivery is disabled; the backend retains the verifying state.
      - generic "Job checks" [ref=e32]:
        - generic [ref=e33]:
          - text: candidate.frozen_identity
          - strong [ref=e34]: pass
      - group [ref=e35]:
        - generic "Run activity (1)" [ref=e36] [cursor=pointer]
      - generic [ref=e37]:
        - generic [ref=e38]: Artifact
        - combobox "Artifact Artifact" [ref=e39]:
          - option "Frozen candidate manifest · file_manifest" [selected]
          - option "Frozen candidate diff · diff"
          - option "Frozen candidate patch · patch"
          - option "test_report · test_report"
          - option ".codex/config.toml · source_file"
          - option ".gitattributes · source_file"
          - option ".github/workflows/launch-kit.yml · source_file"
          - option "AGENTS.md · source_file"
          - option "README.md · source_file"
          - option ".gitignore · source_file"
          - option "contracts/EXTENSIONS.md · source_file"
          - option "SPEC.md · source_file"
          - option "contracts/STORAGE.md · source_file"
          - option "contracts/PROTOCOL.md · source_file"
          - option "contracts/examples/computer.json · source_file"
          - option "demo/club-site/README.md · source_file"
          - option "contracts/snapshot.json · source_file"
          - option "demo/README.md · source_file"
          - option "demo/club-site/bad/members/signup.html · source_file"
          - option "demo/club-site/known-good/index.html · source_file"
          - option "demo/club-site/bad/index.html · source_file"
          - option "desktop/README.md · source_file"
          - option "demo/club-site/known-good/members/welcome.html · source_file"
          - option "desktop/electron/git-reader.cjs · source_file"
          - option "desktop/electron/security.cjs · source_file"
          - option "desktop/electron/runtime-client.cjs · source_file"
          - option "desktop/electron/main.cjs · source_file"
          - option "desktop/electron/preload.cjs · source_file"
          - option "desktop/electron/static-server.cjs · source_file"
          - option "desktop/package-lock.json · source_file"
          - option "desktop/index.html · source_file"
          - option "desktop/scripts/electron-smoke.mjs · source_file"
          - option "desktop/package.json · source_file"
          - option "desktop/playwright.config.ts · source_file"
          - option "desktop/scripts/inspect-assets.mjs · source_file"
          - option "desktop/scripts/install-office.py · source_file"
          - option "desktop/src/App.tsx · source_file"
          - option "desktop/src/DiffEditor.tsx · source_file"
          - option "desktop/src/JobsBoard.tsx · source_file"
          - option "desktop/src/OfficeScene.tsx · source_file"
          - option "desktop/src/office-bindings.ts · source_file"
          - option "desktop/src/bridge.ts · source_file"
          - option "desktop/src/main.tsx · source_file"
          - option "desktop/src/runtime-identity.ts · source_file"
          - option "desktop/src/style.css · source_file"
          - option "desktop/src/types.ts · source_file"
          - option "desktop/tests/browser/jobs-live.spec.ts · source_file"
          - option "desktop/tests/assets.test.mjs · source_file"
          - option "desktop/tests/bindings.test.mjs · source_file"
          - option "desktop/tests/git.test.mjs · source_file"
          - option "desktop/tests/browser/viewer.spec.ts · source_file"
          - option "desktop/tests/install-office.test.mjs · source_file"
          - option "desktop/tests/runtime-identity.test.mjs · source_file"
          - option "desktop/tests/runtime-client.test.mjs · source_file"
          - option "dev/cache_references.py · source_file"
          - option "desktop/tsconfig.json · source_file"
          - option "desktop/tests/security.test.mjs · source_file"
          - option "desktop/vite.config.ts · source_file"
          - option "dev/check.py · source_file"
          - option "dev/loop.py · source_file"
          - option "dev/luna.py · source_file"
          - option "dev/mock_runtime.py · source_file"
          - option "dev/plan.json · source_file"
          - option "dev/references.json · source_file"
          - option "dev/test_loop.py · source_file"
          - option "dev/test_luna.py · source_file"
          - option "dev/test_specs.py · source_file"
          - option "docs/ASSET_BINDING.md · source_file"
          - option "docs/ARCHITECTURE.md · source_file"
          - option "docs/ART_DIRECTION.md · source_file"
          - option "docs/COMPUTER_UI.md · source_file"
          - option "docs/EXECUTION.md · source_file"
          - option "docs/FEATURE_MATRIX.md · source_file"
          - option "docs/LOW_TOKEN_EXECUTION.md · source_file"
          - option "docs/PARALLEL_PLAN.md · source_file"
          - option "docs/MVP_ACCEPTANCE.md · source_file"
          - option "docs/RESEARCH.md · source_file"
          - option "docs/SETUP_VERIFICATION.md · source_file"
          - option "docs/RUN_EVALS.md · source_file"
          - option "docs/VALIDATION.md · source_file"
          - option "docs/START_HERE.md · source_file"
          - option "docs/design/station-kit.svg · source_file"
          - option "docs/design/screen-layout.svg · source_file"
          - option "docs/archive/SPEC-0.2.md · source_file"
          - option "docs/goals/B-tools.md · source_file"
          - option "docs/goals/C-desktop.md · source_file"
          - option "docs/goals/A-runtime.md · source_file"
          - option "docs/goals/C-unity.md · source_file"
          - option "docs/goals/I1-integration.md · source_file"
          - option "docs/goals/D-workshops.md · source_file"
          - option "evidence/A/A1-review-2.json · source_file"
          - option "evidence/A/A1-final-review.json · source_file"
          - option "evidence/A/A2-review.json · source_file"
          - option "evidence/A/A2-repair-review.json · source_file"
          - option "evidence/A/A1.json · source_file"
          - option "evidence/A/A1-review.json · source_file"
          - option "evidence/A/A3-repair-review.json · source_file"
          - option "evidence/A/A2.json · source_file"
          - option "evidence/A/A3-review.json · source_file"
          - option "evidence/A/A3.json · source_file"
        - button "Previous artifacts" [disabled] [ref=e40]
        - button "More artifacts" [ref=e41] [cursor=pointer]
        - generic "4bd3adfcac7cd19b384eb23dff211a106d5049f99ba2df7611186dec209ad15d" [ref=e42]: SHA256 4bd3adfcac7c · immutable
      - generic [ref=e43]:
        - navigation "Result files" [ref=e44]:
          - button ".codex/config.toml unchanged" [ref=e45] [cursor=pointer]:
            - text: .codex/config.toml
            - generic [ref=e46]: unchanged
          - button ".gitattributes unchanged" [ref=e47] [cursor=pointer]:
            - text: .gitattributes
            - generic [ref=e48]: unchanged
          - button ".github/workflows/launch-kit.yml unchanged" [ref=e49] [cursor=pointer]:
            - text: .github/workflows/launch-kit.yml
            - generic [ref=e50]: unchanged
          - button ".gitignore unchanged" [ref=e51] [cursor=pointer]:
            - text: .gitignore
            - generic [ref=e52]: unchanged
          - button "AGENTS.md unchanged" [ref=e53] [cursor=pointer]:
            - text: AGENTS.md
            - generic [ref=e54]: unchanged
          - button "README.md unchanged" [pressed] [ref=e55] [cursor=pointer]:
            - text: README.md
            - generic [ref=e56]: unchanged
          - button "SPEC.md unchanged" [ref=e57] [cursor=pointer]:
            - text: SPEC.md
            - generic [ref=e58]: unchanged
          - button "contracts/EXTENSIONS.md unchanged" [ref=e59] [cursor=pointer]:
            - text: contracts/EXTENSIONS.md
            - generic [ref=e60]: unchanged
          - button "contracts/PROTOCOL.md unchanged" [ref=e61] [cursor=pointer]:
            - text: contracts/PROTOCOL.md
            - generic [ref=e62]: unchanged
          - button "contracts/STORAGE.md unchanged" [ref=e63] [cursor=pointer]:
            - text: contracts/STORAGE.md
            - generic [ref=e64]: unchanged
          - button "contracts/examples/computer.json unchanged" [ref=e65] [cursor=pointer]:
            - text: contracts/examples/computer.json
            - generic [ref=e66]: unchanged
          - button "contracts/snapshot.json unchanged" [ref=e67] [cursor=pointer]:
            - text: contracts/snapshot.json
            - generic [ref=e68]: unchanged
          - button "demo/README.md unchanged" [ref=e69] [cursor=pointer]:
            - text: demo/README.md
            - generic [ref=e70]: unchanged
          - button "demo/club-site/README.md unchanged" [ref=e71] [cursor=pointer]:
            - text: demo/club-site/README.md
            - generic [ref=e72]: unchanged
          - button "demo/club-site/bad/index.html unchanged" [ref=e73] [cursor=pointer]:
            - text: demo/club-site/bad/index.html
            - generic [ref=e74]: unchanged
          - button "demo/club-site/bad/members/signup.html unchanged" [ref=e75] [cursor=pointer]:
            - text: demo/club-site/bad/members/signup.html
            - generic [ref=e76]: unchanged
          - button "demo/club-site/known-good/index.html unchanged" [ref=e77] [cursor=pointer]:
            - text: demo/club-site/known-good/index.html
            - generic [ref=e78]: unchanged
          - button "demo/club-site/known-good/members/welcome.html unchanged" [ref=e79] [cursor=pointer]:
            - text: demo/club-site/known-good/members/welcome.html
            - generic [ref=e80]: unchanged
          - button "desktop/README.md unchanged" [ref=e81] [cursor=pointer]:
            - text: desktop/README.md
            - generic [ref=e82]: unchanged
          - button "desktop/electron/git-reader.cjs unchanged" [ref=e83] [cursor=pointer]:
            - text: desktop/electron/git-reader.cjs
            - generic [ref=e84]: unchanged
          - button "desktop/electron/main.cjs unchanged" [ref=e85] [cursor=pointer]:
            - text: desktop/electron/main.cjs
            - generic [ref=e86]: unchanged
          - button "desktop/electron/preload.cjs unchanged" [ref=e87] [cursor=pointer]:
            - text: desktop/electron/preload.cjs
            - generic [ref=e88]: unchanged
          - button "desktop/electron/runtime-client.cjs unchanged" [ref=e89] [cursor=pointer]:
            - text: desktop/electron/runtime-client.cjs
            - generic [ref=e90]: unchanged
          - button "desktop/electron/security.cjs unchanged" [ref=e91] [cursor=pointer]:
            - text: desktop/electron/security.cjs
            - generic [ref=e92]: unchanged
          - button "desktop/electron/static-server.cjs unchanged" [ref=e93] [cursor=pointer]:
            - text: desktop/electron/static-server.cjs
            - generic [ref=e94]: unchanged
          - button "desktop/index.html unchanged" [ref=e95] [cursor=pointer]:
            - text: desktop/index.html
            - generic [ref=e96]: unchanged
          - button "desktop/package-lock.json unchanged" [ref=e97] [cursor=pointer]:
            - text: desktop/package-lock.json
            - generic [ref=e98]: unchanged
          - button "desktop/package.json unchanged" [ref=e99] [cursor=pointer]:
            - text: desktop/package.json
            - generic [ref=e100]: unchanged
          - button "desktop/playwright.config.ts unchanged" [ref=e101] [cursor=pointer]:
            - text: desktop/playwright.config.ts
            - generic [ref=e102]: unchanged
          - button "desktop/scripts/electron-smoke.mjs unchanged" [ref=e103] [cursor=pointer]:
            - text: desktop/scripts/electron-smoke.mjs
            - generic [ref=e104]: unchanged
          - button "desktop/scripts/inspect-assets.mjs unchanged" [ref=e105] [cursor=pointer]:
            - text: desktop/scripts/inspect-assets.mjs
            - generic [ref=e106]: unchanged
          - button "desktop/scripts/install-office.py unchanged" [ref=e107] [cursor=pointer]:
            - text: desktop/scripts/install-office.py
            - generic [ref=e108]: unchanged
          - button "desktop/src/App.tsx unchanged" [ref=e109] [cursor=pointer]:
            - text: desktop/src/App.tsx
            - generic [ref=e110]: unchanged
          - button "desktop/src/DiffEditor.tsx unchanged" [ref=e111] [cursor=pointer]:
            - text: desktop/src/DiffEditor.tsx
            - generic [ref=e112]: unchanged
          - button "desktop/src/JobsBoard.tsx unchanged" [ref=e113] [cursor=pointer]:
            - text: desktop/src/JobsBoard.tsx
            - generic [ref=e114]: unchanged
          - button "desktop/src/OfficeScene.tsx unchanged" [ref=e115] [cursor=pointer]:
            - text: desktop/src/OfficeScene.tsx
            - generic [ref=e116]: unchanged
          - button "desktop/src/bridge.ts unchanged" [ref=e117] [cursor=pointer]:
            - text: desktop/src/bridge.ts
            - generic [ref=e118]: unchanged
          - button "desktop/src/main.tsx unchanged" [ref=e119] [cursor=pointer]:
            - text: desktop/src/main.tsx
            - generic [ref=e120]: unchanged
          - button "desktop/src/office-bindings.ts unchanged" [ref=e121] [cursor=pointer]:
            - text: desktop/src/office-bindings.ts
            - generic [ref=e122]: unchanged
          - button "desktop/src/runtime-identity.ts unchanged" [ref=e123] [cursor=pointer]:
            - text: desktop/src/runtime-identity.ts
            - generic [ref=e124]: unchanged
          - button "desktop/src/style.css unchanged" [ref=e125] [cursor=pointer]:
            - text: desktop/src/style.css
            - generic [ref=e126]: unchanged
          - button "desktop/src/types.ts unchanged" [ref=e127] [cursor=pointer]:
            - text: desktop/src/types.ts
            - generic [ref=e128]: unchanged
          - button "desktop/tests/assets.test.mjs unchanged" [ref=e129] [cursor=pointer]:
            - text: desktop/tests/assets.test.mjs
            - generic [ref=e130]: unchanged
          - button "desktop/tests/bindings.test.mjs unchanged" [ref=e131] [cursor=pointer]:
            - text: desktop/tests/bindings.test.mjs
            - generic [ref=e132]: unchanged
          - button "desktop/tests/browser/jobs-live.spec.ts unchanged" [ref=e133] [cursor=pointer]:
            - text: desktop/tests/browser/jobs-live.spec.ts
            - generic [ref=e134]: unchanged
          - button "desktop/tests/browser/viewer.spec.ts unchanged" [ref=e135] [cursor=pointer]:
            - text: desktop/tests/browser/viewer.spec.ts
            - generic [ref=e136]: unchanged
          - button "desktop/tests/git.test.mjs unchanged" [ref=e137] [cursor=pointer]:
            - text: desktop/tests/git.test.mjs
            - generic [ref=e138]: unchanged
          - button "desktop/tests/install-office.test.mjs unchanged" [ref=e139] [cursor=pointer]:
            - text: desktop/tests/install-office.test.mjs
            - generic [ref=e140]: unchanged
          - button "desktop/tests/runtime-client.test.mjs unchanged" [ref=e141] [cursor=pointer]:
            - text: desktop/tests/runtime-client.test.mjs
            - generic [ref=e142]: unchanged
          - button "desktop/tests/runtime-identity.test.mjs unchanged" [ref=e143] [cursor=pointer]:
            - text: desktop/tests/runtime-identity.test.mjs
            - generic [ref=e144]: unchanged
          - button "desktop/tests/security.test.mjs unchanged" [ref=e145] [cursor=pointer]:
            - text: desktop/tests/security.test.mjs
            - generic [ref=e146]: unchanged
          - button "desktop/tsconfig.json unchanged" [ref=e147] [cursor=pointer]:
            - text: desktop/tsconfig.json
            - generic [ref=e148]: unchanged
          - button "desktop/vite.config.ts unchanged" [ref=e149] [cursor=pointer]:
            - text: desktop/vite.config.ts
            - generic [ref=e150]: unchanged
          - button "dev/cache_references.py unchanged" [ref=e151] [cursor=pointer]:
            - text: dev/cache_references.py
            - generic [ref=e152]: unchanged
          - button "dev/check.py unchanged" [ref=e153] [cursor=pointer]:
            - text: dev/check.py
            - generic [ref=e154]: unchanged
          - button "dev/loop.py unchanged" [ref=e155] [cursor=pointer]:
            - text: dev/loop.py
            - generic [ref=e156]: unchanged
          - button "dev/luna.py unchanged" [ref=e157] [cursor=pointer]:
            - text: dev/luna.py
            - generic [ref=e158]: unchanged
          - button "dev/mock_runtime.py unchanged" [ref=e159] [cursor=pointer]:
            - text: dev/mock_runtime.py
            - generic [ref=e160]: unchanged
          - button "dev/plan.json unchanged" [ref=e161] [cursor=pointer]:
            - text: dev/plan.json
            - generic [ref=e162]: unchanged
          - button "dev/references.json unchanged" [ref=e163] [cursor=pointer]:
            - text: dev/references.json
            - generic [ref=e164]: unchanged
          - button "dev/test_loop.py unchanged" [ref=e165] [cursor=pointer]:
            - text: dev/test_loop.py
            - generic [ref=e166]: unchanged
          - button "dev/test_luna.py unchanged" [ref=e167] [cursor=pointer]:
            - text: dev/test_luna.py
            - generic [ref=e168]: unchanged
          - button "dev/test_specs.py unchanged" [ref=e169] [cursor=pointer]:
            - text: dev/test_specs.py
            - generic [ref=e170]: unchanged
          - button "docs/ARCHITECTURE.md unchanged" [ref=e171] [cursor=pointer]:
            - text: docs/ARCHITECTURE.md
            - generic [ref=e172]: unchanged
          - button "docs/ART_DIRECTION.md unchanged" [ref=e173] [cursor=pointer]:
            - text: docs/ART_DIRECTION.md
            - generic [ref=e174]: unchanged
          - button "docs/ASSET_BINDING.md unchanged" [ref=e175] [cursor=pointer]:
            - text: docs/ASSET_BINDING.md
            - generic [ref=e176]: unchanged
          - button "docs/COMPUTER_UI.md unchanged" [ref=e177] [cursor=pointer]:
            - text: docs/COMPUTER_UI.md
            - generic [ref=e178]: unchanged
          - button "docs/EXECUTION.md unchanged" [ref=e179] [cursor=pointer]:
            - text: docs/EXECUTION.md
            - generic [ref=e180]: unchanged
          - button "docs/FEATURE_MATRIX.md unchanged" [ref=e181] [cursor=pointer]:
            - text: docs/FEATURE_MATRIX.md
            - generic [ref=e182]: unchanged
          - button "docs/LOW_TOKEN_EXECUTION.md unchanged" [ref=e183] [cursor=pointer]:
            - text: docs/LOW_TOKEN_EXECUTION.md
            - generic [ref=e184]: unchanged
          - button "docs/MVP_ACCEPTANCE.md unchanged" [ref=e185] [cursor=pointer]:
            - text: docs/MVP_ACCEPTANCE.md
            - generic [ref=e186]: unchanged
          - button "docs/PARALLEL_PLAN.md unchanged" [ref=e187] [cursor=pointer]:
            - text: docs/PARALLEL_PLAN.md
            - generic [ref=e188]: unchanged
          - button "docs/RESEARCH.md unchanged" [ref=e189] [cursor=pointer]:
            - text: docs/RESEARCH.md
            - generic [ref=e190]: unchanged
          - button "docs/RUN_EVALS.md unchanged" [ref=e191] [cursor=pointer]:
            - text: docs/RUN_EVALS.md
            - generic [ref=e192]: unchanged
          - button "docs/SETUP_VERIFICATION.md unchanged" [ref=e193] [cursor=pointer]:
            - text: docs/SETUP_VERIFICATION.md
            - generic [ref=e194]: unchanged
          - button "docs/START_HERE.md unchanged" [ref=e195] [cursor=pointer]:
            - text: docs/START_HERE.md
            - generic [ref=e196]: unchanged
          - button "docs/VALIDATION.md unchanged" [ref=e197] [cursor=pointer]:
            - text: docs/VALIDATION.md
            - generic [ref=e198]: unchanged
          - button "docs/archive/SPEC-0.2.md unchanged" [ref=e199] [cursor=pointer]:
            - text: docs/archive/SPEC-0.2.md
            - generic [ref=e200]: unchanged
          - button "docs/design/screen-layout.svg unchanged" [ref=e201] [cursor=pointer]:
            - text: docs/design/screen-layout.svg
            - generic [ref=e202]: unchanged
          - button "docs/design/station-kit.svg unchanged" [ref=e203] [cursor=pointer]:
            - text: docs/design/station-kit.svg
            - generic [ref=e204]: unchanged
          - button "docs/goals/A-runtime.md unchanged" [ref=e205] [cursor=pointer]:
            - text: docs/goals/A-runtime.md
            - generic [ref=e206]: unchanged
          - button "docs/goals/B-tools.md unchanged" [ref=e207] [cursor=pointer]:
            - text: docs/goals/B-tools.md
            - generic [ref=e208]: unchanged
          - button "docs/goals/C-desktop.md unchanged" [ref=e209] [cursor=pointer]:
            - text: docs/goals/C-desktop.md
            - generic [ref=e210]: unchanged
          - button "docs/goals/C-unity.md unchanged" [ref=e211] [cursor=pointer]:
            - text: docs/goals/C-unity.md
            - generic [ref=e212]: unchanged
          - button "docs/goals/D-workshops.md unchanged" [ref=e213] [cursor=pointer]:
            - text: docs/goals/D-workshops.md
            - generic [ref=e214]: unchanged
          - button "docs/goals/I1-integration.md unchanged" [ref=e215] [cursor=pointer]:
            - text: docs/goals/I1-integration.md
            - generic [ref=e216]: unchanged
          - button "evidence/A/A1-final-review.json unchanged" [ref=e217] [cursor=pointer]:
            - text: evidence/A/A1-final-review.json
            - generic [ref=e218]: unchanged
          - button "evidence/A/A1-review-2.json unchanged" [ref=e219] [cursor=pointer]:
            - text: evidence/A/A1-review-2.json
            - generic [ref=e220]: unchanged
          - button "evidence/A/A1-review.json unchanged" [ref=e221] [cursor=pointer]:
            - text: evidence/A/A1-review.json
            - generic [ref=e222]: unchanged
          - button "evidence/A/A1.json unchanged" [ref=e223] [cursor=pointer]:
            - text: evidence/A/A1.json
            - generic [ref=e224]: unchanged
          - button "evidence/A/A2-repair-review.json unchanged" [ref=e225] [cursor=pointer]:
            - text: evidence/A/A2-repair-review.json
            - generic [ref=e226]: unchanged
          - button "evidence/A/A2-review.json unchanged" [ref=e227] [cursor=pointer]:
            - text: evidence/A/A2-review.json
            - generic [ref=e228]: unchanged
          - button "evidence/A/A2.json unchanged" [ref=e229] [cursor=pointer]:
            - text: evidence/A/A2.json
            - generic [ref=e230]: unchanged
          - button "evidence/A/A3-repair-review.json unchanged" [ref=e231] [cursor=pointer]:
            - text: evidence/A/A3-repair-review.json
            - generic [ref=e232]: unchanged
          - button "evidence/A/A3-review.json unchanged" [ref=e233] [cursor=pointer]:
            - text: evidence/A/A3-review.json
            - generic [ref=e234]: unchanged
          - button "evidence/A/A3.json unchanged" [ref=e235] [cursor=pointer]:
            - text: evidence/A/A3.json
            - generic [ref=e236]: unchanged
          - button "evidence/B/B1-repair-review.json unchanged" [ref=e237] [cursor=pointer]:
            - text: evidence/B/B1-repair-review.json
            - generic [ref=e238]: unchanged
          - button "evidence/B/B1-review.json unchanged" [ref=e239] [cursor=pointer]:
            - text: evidence/B/B1-review.json
            - generic [ref=e240]: unchanged
          - button "evidence/B/B1.json unchanged" [ref=e241] [cursor=pointer]:
            - text: evidence/B/B1.json
            - generic [ref=e242]: unchanged
          - button "evidence/B/B2-readiness.json unchanged" [ref=e243] [cursor=pointer]:
            - text: evidence/B/B2-readiness.json
            - generic [ref=e244]: unchanged
          - generic [ref=e245]:
            - button "Previous files" [disabled] [ref=e246]
            - button "More files" [ref=e247] [cursor=pointer]
        - region "Artifact content" [ref=e248]:
          - generic [ref=e249]:
            - button "File text" [pressed] [ref=e250] [cursor=pointer]
            - button "Git diff" [ref=e251] [cursor=pointer]
            - generic [ref=e252]: README.md
          - generic "Read-only artifact text" [ref=e253]: "1 # Sidequest — Electron presentation work 2 3 Start the current Electron + React + TypeScript client with [desktop/README.md](desktop/README.md). It replaces the Unity presentation decision and provides a read-only local Git diff viewer with lazy Monaco, expandable reading and Escape/state restoration. The office loader expects the owner’s actual GLB and explicit monitor bindings; no replacement art is generated. 4 5 The specified Python/SQLite runtime, scheduling, policy, authenticated artifact API, isolated Git pipeline and trusted checks are implemented. The jobs board completed a genuine local inspection through the browser, runtime and adapters with zero model calls and no source delivery. The Codex app-server adapter and persisted session lifecycle are implemented and tested with a fake transport; native coding execution remains blocked. Browser evidence does not certify Electron or actual office compatibility. See [run/eval instructions](docs/RUN_EVALS.md), [acceptance limits](docs/MVP_ACCEPTANCE.md) and [screenshots/provenance](evidence/desktop/README.md). 6 7 The development-controller instructions below are retained for operator context. The machine plan now points C at Electron; the current MVP was built through explicitly coordinated lanes rather than that controller. Do not start model workers to launch the viewer or local evaluations. 8 9 # Sidequest 10 11 A calm office for real agent swarms, with Electron presentation. Inspect artifacts and diffs directly on a selected computer. Use existing coding agents; do not build another agent framework. 12 13 The owner's completed Blender/GLB office assets are protected inputs. Their archive has been located but the VM transfer is blocked; the checkout contains no actual office art. Do not regenerate the office. Native Electron and Codex readiness are also blocked as recorded in the acceptance evidence. 14 15 Start at [START HERE](docs/START_HERE.md). Read [SPEC](SPEC.md) for scope or [ARCHITECTURE](docs/ARCHITECTURE.md) for the fixed stack. Workers read only their assigned goal and its relevant documents, not the entire research archive. 16 17 | Lane | Exclusive responsibility | 18 |---|---| 19 | A | Local runtime, database, scheduler, artifact HTTP service | 20 | B | Coding-provider adapter, isolated Git, file/diff capture, local monitoring | 21 | C | Existing GLB assets, Electron computer UI, office interaction and build | 22 | D | Independent checks, reusable workshops, demo and final acceptance rig | 23 24 Each lane has three goals. Each candidate gets a new validator thread at its exact commit. Main is not automatically changed by development runs. The [low-token policy](docs/LOW_TOKEN_EXECUTION.md) selects Luna/max, short task packets, deterministic tests first, bounded attempts, and no always-running manager. 25 26 ```bash 27 python3 -m unittest discover -s dev -p 'test_*.py' -v 28 python3 dev/check.py --setup 29 python3 dev/loop.py prepare 30 python3 dev/luna.py run A --allow-network 31 # Start B, C and D in their own terminals from this same checkout. 32 ``` 33 34 Complete the asset/environment preflight in START HERE before preparing worktrees. `dev/luna.py` checks the effective Codex configuration and account model support before allowing a model run. The low-cost configuration is an explicit preference, not an estimate of your account bill. 35 36 [Computer UI](docs/COMPUTER_UI.md) · [Asset binding](docs/ASSET_BINDING.md) · [Protocol](contracts/PROTOCOL.md) · [Extensions](contracts/EXTENSIONS.md) · [Feature coverage](docs/FEATURE_MATRIX.md) · [Upstream sources](docs/RESEARCH.md) 37 38 The diagrams are architecture specifications, not screenshots of an implemented app. Earlier concept images and station-kit drawings are not authority to redesign the owner's completed office."
          - generic [ref=e254]:
            - button "Previous lines" [disabled] [ref=e255]
            - button "More lines" [disabled] [ref=e256]
    - generic [ref=e257]: Runtime local-git · revision 1515 · Coding execution unavailable
  - generic [ref=e258]:
    - combobox "Office navigation" [active] [ref=e259]:
      - option "Navigate…" [selected]
      - option "Tasks board"
      - option "Computer 01"
      - option "Computer 02"
      - option "Computer 03"
      - option "Computer 04"
      - option "Computer 05"
      - option "Computer 06"
      - option "Computer 07"
      - option "Computer 08"
      - option "Computer 09"
      - option "Computer 10"
      - option "Computer 11"
      - option "Computer 12"
      - option "Computer 13"
      - option "Computer 14"
      - option "Computer 15"
      - option "Computer 16"
      - option "Computer 17"
      - option "Computer 18"
      - option "Computer 19"
      - option "Computer 20"
      - option "Computer 21"
      - option "Computer 22"
      - option "Computer 23"
      - option "Computer 24"
      - option "Computer 01"
      - option "Computer 02"
      - option "Computer 03"
      - option "Computer 04"
      - option "Computer 05"
      - option "Computer 06"
      - option "Computer 07"
      - option "Computer 08"
      - option "Computer 09"
      - option "Computer 10"
      - option "Computer 11"
      - option "Computer 12"
      - option "Computer 13"
      - option "Computer 14"
      - option "Computer 15"
      - option "Computer 16"
      - option "Computer 17"
      - option "Computer 18"
      - option "Computer 19"
      - option "Computer 20"
      - option "Computer 21"
      - option "Computer 22"
      - option "Computer 23"
      - option "Computer 24"
      - option "Computer 01"
      - option "Computer 02"
      - option "Computer 03"
      - option "Computer 04"
      - option "Computer 05"
      - option "Computer 06"
      - option "Computer 07"
      - option "Computer 08"
      - option "Computer 09"
      - option "Computer 10"
      - option "Computer 11"
      - option "Computer 12"
      - option "Computer 13"
      - option "Computer 14"
      - option "Computer 15"
      - option "Computer 16"
      - option "Computer 17"
      - option "Computer 18"
      - option "Computer 19"
      - option "Computer 20"
      - option "Computer 21"
      - option "Computer 22"
      - option "Computer 23"
      - option "Computer 24"
    - generic "Original staged poses; no coding session is connected." [ref=e260]: 26 staged · no sessions
    - generic "UI refresh and file viewing make zero model calls." [ref=e261]: Local Git · read-only
```

# Test source

```ts
  35  |   await board.getByRole('button',{name:'Git diff',exact:true}).click();
  36  |   await expect(board.locator('.artifact-text')).toContainText('No textual changes in this inspected candidate.');
  37  |   await page.screenshot({path:path.resolve('../evidence/desktop/job-diff.png')});
  38  |   await board.locator('#job-artifact').selectOption({label:await board.locator('#job-artifact option').filter({hasText:'test_report'}).first().textContent()??''});
  39  |   await expect(board.locator('.artifact-text')).toContainText('candidate.frozen_identity');
  40  |   await expect.poll(async()=>JSON.parse(await board.locator('.artifact-text').textContent()??'{}').inference_calls).toBe(0);
  41  |   const report=JSON.parse(await board.locator('.artifact-text').textContent()??'{}');
  42  |   await page.screenshot({path:path.resolve('../evidence/desktop/job-check-report.png')});
  43  |   await board.locator('.job-activity > summary').click();
  44  |   const activity=board.getByRole('region',{name:'Run activity'});
  45  |   await expect(activity).toContainText('No model call');
  46  |   await expect(activity.locator('.run-activity-state')).toHaveText('completed');
  47  |   await expect.poll(()=>activity.locator('.run-activity-timeline>li').count()).toBeGreaterThan(0);
  48  |   await page.screenshot({path:path.resolve('../evidence/desktop/run-activity-actual.png')});
  49  |   await board.locator('.job-activity > summary').click();
  50  |   await board.locator('.coding-readiness summary').click();
  51  |   await expect(board.locator('.coding-readiness')).toContainText('Coding tasks remain blocked.');
  52  |   const refreshStart=calls.length;
  53  |   await board.getByRole('button',{name:'Refresh status',exact:true}).click();
  54  |   await expect.poll(()=>calls.slice(refreshStart).filter(call=>call.method==='capabilities').length).toBeGreaterThan(0);
  55  |   expect(calls.slice(refreshStart).every(call=>['snapshot','capabilities','artifacts','artifact','files','text','diff','runInfo','runEvents'].includes(call.method))).toBe(true);
  56  |   await page.screenshot({path:path.resolve('../evidence/desktop/job-readiness.png')});
  57  |   await board.locator('.coding-readiness summary').click();
  58  |   const responsiveAccessibility:{width:number;violations:unknown[]}[]=[];
  59  |   for(const width of [960,390]){
  60  |     await page.setViewportSize({width,height:780});
  61  |     await board.locator('.artifact-content').scrollIntoViewIfNeeded();
  62  |     await expect(board.locator('.artifact-text')).toBeInViewport();
  63  |     expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBe(true);
  64  |     await page.screenshot({path:path.resolve(`../evidence/desktop/job-${width}.png`)});
  65  |     const result=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze();
  66  |     responsiveAccessibility.push({width,violations:result.violations});
  67  |     expect(result.violations.map(item=>({id:item.id,impact:item.impact}))).toEqual([]);
  68  |   }
  69  |   await writeFile(path.resolve('../evidence/desktop/job-responsive-accessibility.json'),JSON.stringify(responsiveAccessibility,null,2));
  70  |   await page.setViewportSize({width:1440,height:900});
  71  |   const accessibility=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze();
  72  |   await writeFile(path.resolve('../evidence/desktop/job-accessibility.json'),JSON.stringify(accessibility.violations,null,2));
  73  |   expect(accessibility.violations.map(item=>({id:item.id,impact:item.impact}))).toEqual([]);
  74  |   const selectedArtifact=await board.locator('#job-artifact').inputValue();
  75  |   await page.keyboard.press('Escape');await expect(board).toBeHidden();
  76  |   await expect(page.getByRole('button',{name:'Jobs',exact:true})).toBeFocused();
  77  |   await page.getByRole('button',{name:'Jobs',exact:true}).click();
  78  |   await expect(board.locator('#job-artifact')).toHaveValue(selectedArtifact);
  79  |   const response=await request.get('/__sidequest/snapshot');const git=await response.json();
  80  |   const state=await page.evaluate(async()=>{const response=await fetch('/__sidequest/runtime/snapshot',{method:'POST',headers:{'Content-Type':'application/json'},body:'[]'});if(!response.ok)throw new Error('Final local snapshot unavailable.');return response.json();});
  81  |   const completedJob=state.jobs.find((item:{title:string})=>item.title===title);
  82  |   expect(completedJob?.spent_usd).toBe(0);
  83  |   const registeredProject=state.projects.find((item:{id:string})=>item.id===completedJob.project_id);
  84  |   await writeFile(path.resolve('../evidence/desktop/job-browser.json'),JSON.stringify({title,source:{base:git.baseRevision,candidate:git.candidateRevision},registered_project:registeredProject,job:completedJob,frozen_check_report:report,browser_requests:calls,model_calls:report.inference_calls,scope:'Real deterministic local Git inspection through UI/HTTP/B/D; no coding agent or provider run',page_errors:errors},null,2));
  85  |   expect(errors).toEqual([]);
  86  | });
  87  | 
  88  | test('real jobs clear stale notices, recover reads and preserve assigned computer results',async({page,request})=>{
  89  |   test.setTimeout(90_000);
  90  |   test.skip(process.env.SIDEQUEST_TEST_INSPECTION!=='1','Requires actual local inspection records; never launches coding.');
  91  |   const response=await request.post('/__sidequest/runtime/snapshot',{data:[],headers:{Origin:'http://127.0.0.1:5173'}});expect(response.ok()).toBe(true);const state=await response.json();
  92  |   const completed=state.jobs.find((job:{execution_profile:string;checks:{state:string}[];tasks:{state:string}[]})=>job.execution_profile==='local_git_inspection'&&job.tasks.every(t=>t.state==='completed')&&job.checks.length&&job.checks.every(c=>c.state==='pass'));
  93  |   expect(completed).toBeTruthy();
  94  |   await page.goto('/');await expect(page.locator('.app-footer')).toHaveAttribute('data-actor-status','ready',{timeout:60000});await page.getByRole('button',{name:'Jobs',exact:true}).click();
  95  |   const board=page.getByRole('region',{name:'Local jobs board'});
  96  |   await board.getByRole('button',{name:new RegExp(completed.title.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'))}).click();
  97  |   await expect(board).toContainText('Inspection results ready.');
  98  |   await expect(board).not.toContainText('Run accepted. Waiting for status.');
  99  |   const queuedTitle=`Repeated submission ${new Date().toISOString()}`;
  100 |   await board.getByLabel('Inspection title').fill(queuedTitle);
  101 |   await board.getByRole('button',{name:'Submit inspection',exact:true}).click();
  102 |   await expect(board.locator('.job-summary')).toContainText(queuedTitle);
  103 |   await expect(board.locator('.job-state')).toHaveText('queued');
  104 |   await board.getByRole('button',{name:new RegExp(completed.title.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'))}).click();
  105 |   await expect(board).not.toContainText('Job queued. Review the job, then run it explicitly.');
  106 |   let disconnected=true;
  107 |   await page.route('**/__sidequest/runtime/snapshot',route=>disconnected?route.fulfill({status:503,json:{error:'test-only network failure'}}):route.continue());
  108 |   await board.getByRole('button',{name:'Refresh status',exact:true}).click();
  109 |   await expect(board.getByRole('alert').first()).toBeVisible();
  110 |   await expect(board.getByRole('button',{name:'Submit inspection',exact:true})).toBeDisabled();
  111 |   disconnected=false;await board.getByRole('button',{name:'Refresh status',exact:true}).click();
  112 |   await expect(board.getByRole('button',{name:'Submit inspection',exact:true})).toBeEnabled();
  113 |   await expect(board.getByRole('alert')).toHaveCount(0);
  114 |   await board.getByLabel('Show results on').selectOption('parent_019');
  115 |   await board.getByRole('button',{name:'Assign result display',exact:true}).click();
  116 |   const result=page.getByRole('region',{name:'Computer job results'});
  117 |   await expect(result).toBeVisible();await expect(result.locator('.job-summary')).toContainText(completed.title);
  118 |   await result.locator('.artifact-files button[title="README.md"]').click();
  119 |   await expect(result.locator('.artifact-text')).not.toContainText('Loading file text');
  120 |   const selectedFile=await result.locator('.artifact-files button[aria-pressed="true"]').getAttribute('title');
  121 |   await result.locator('.artifact-text').evaluate(node=>{node.scrollTop=180;node.dispatchEvent(new Event('scroll',{bubbles:true}));});
  122 |   await expect.poll(()=>result.locator('.artifact-text').evaluate(node=>node.scrollTop)).toBeGreaterThan(100);
  123 |   await result.getByRole('button',{name:'Expand',exact:true}).click();
  124 |   await expect(page.getByRole('dialog',{name:'Computer job viewer'})).toBeVisible();
  125 |   await expect(result.locator('.artifact-files button[aria-pressed="true"]')).toHaveAttribute('title',selectedFile!);
  126 |   await page.getByRole('button',{name:'Settings',exact:true}).click();
  127 |   await expect(page.getByRole('dialog',{name:'Provider settings dialog'})).toBeVisible();
  128 |   await page.keyboard.press('Escape');
  129 |   await expect(page.getByRole('dialog',{name:'Computer job viewer'})).toBeVisible();
  130 |   await expect(page.getByRole('button',{name:'Settings',exact:true})).toBeFocused();
  131 |   await page.keyboard.press('Escape');await expect(result).toHaveCount(0);
  132 |   await page.getByRole('combobox',{name:'Office navigation'}).selectOption('parent_019');
  133 |   await expect(result).toBeVisible();
  134 |   await expect(result.locator('.artifact-files button[aria-pressed="true"]')).toHaveAttribute('title',selectedFile!);
> 135 |   await expect.poll(()=>result.locator('.artifact-text').evaluate(node=>node.scrollTop)).toBeGreaterThan(100);
      |                                                                                          ^ Error: expect(received).toBeGreaterThan(expected)
  136 |   await page.screenshot({path:path.resolve('../evidence/desktop/assigned-result.png')});
  137 |   await writeFile(path.resolve('../evidence/desktop/result-display-browser.json'),JSON.stringify({job_id:completed.id,queued_test_title:queuedTitle,queued_test_executed:false,selected_file:selectedFile,temporary_network_failure:true,recovered:true,scope:'Actual local inspection artifacts; display assignment only; zero coding/model launches'},null,2));
  138 | });
  139 | 
```