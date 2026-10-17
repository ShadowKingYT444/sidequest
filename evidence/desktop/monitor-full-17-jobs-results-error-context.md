# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: jobs-live.spec.ts >> real jobs clear stale notices, recover reads and preserve assigned computer results
- Location: tests/browser/jobs-live.spec.ts:88:1

# Error details

```
Test timeout of 90000ms exceeded.
```

```
Error: locator.click: Test timeout of 90000ms exceeded.
Call log:
  - waiting for getByRole('region', { name: 'Computer job results' }).getByRole('button', { name: 'Expand', exact: true })

```

# Page snapshot

```yaml
- main [ref=e3]:
  - generic [ref=e4]:
    - generic [ref=e5]: sidequest
    - generic [ref=e6]: sidequest
    - button "Notifications" [ref=e8] [cursor=pointer]
    - button "Settings" [ref=e12] [cursor=pointer]
    - button "Jobs" [ref=e13] [cursor=pointer]
    - button "Refresh Git" [ref=e14] [cursor=pointer]
  - generic [ref=e20]:
    - generic [ref=e21]:
      - generic [ref=e22]: Computer 19
      - navigation "Computer view" [ref=e23]:
        - button "Trace" [ref=e24] [cursor=pointer]
        - button "Files" [pressed] [ref=e25] [cursor=pointer]
        - button "Task setup" [ref=e26] [cursor=pointer]
      - generic [ref=e27]:
        - button "Expand" [ref=e28] [cursor=pointer]
        - button "Return to office" [ref=e29] [cursor=pointer]: Office Esc
    - region "Computer job results" [ref=e32]:
      - region "Selected job" [ref=e34]:
        - generic [ref=e36]:
          - heading "Browser inspection 2026-10-14T16:19:06.389Z" [level=3] [ref=e37]
          - paragraph [ref=e38]: verifying · $0 budget · e4caf6c1-4401-4f96-84f9-d9efe8e671a7
        - status [ref=e39]: Inspection results ready. Source delivery is disabled; the backend retains the verifying state.
        - generic "Job checks" [ref=e40]:
          - generic [ref=e41]:
            - text: candidate.frozen_identity
            - strong [ref=e42]: pass
        - group [ref=e43]:
          - generic "Run activity (1)" [ref=e44] [cursor=pointer]
        - generic [ref=e45]:
          - generic [ref=e46]: Artifact
          - combobox "Artifact Artifact" [ref=e47]:
            - option "Frozen candidate manifest · file_manifest" [selected]
            - option "Frozen candidate diff · diff"
            - option "Frozen candidate patch · patch"
            - option "test_report · test_report"
            - option ".codex/config.toml · source_file"
            - option ".github/workflows/launch-kit.yml · source_file"
            - option ".gitattributes · source_file"
            - option ".gitignore · source_file"
            - option "README.md · source_file"
            - option "AGENTS.md · source_file"
            - option "SPEC.md · source_file"
            - option "contracts/EXTENSIONS.md · source_file"
            - option "contracts/PROTOCOL.md · source_file"
            - option "contracts/examples/computer.json · source_file"
            - option "contracts/snapshot.json · source_file"
            - option "contracts/STORAGE.md · source_file"
            - option "demo/club-site/README.md · source_file"
            - option "demo/README.md · source_file"
            - option "demo/club-site/bad/index.html · source_file"
            - option "demo/club-site/bad/members/signup.html · source_file"
            - option "demo/club-site/known-good/index.html · source_file"
            - option "demo/club-site/known-good/members/welcome.html · source_file"
            - option "desktop/README.md · source_file"
            - option "desktop/electron/git-reader.cjs · source_file"
            - option "desktop/electron/main.cjs · source_file"
            - option "desktop/electron/preload.cjs · source_file"
            - option "desktop/electron/runtime-client.cjs · source_file"
            - option "desktop/electron/security.cjs · source_file"
            - option "desktop/electron/static-server.cjs · source_file"
            - option "desktop/index.html · source_file"
            - option "desktop/package.json · source_file"
            - option "desktop/package-lock.json · source_file"
            - option "desktop/playwright.config.ts · source_file"
            - option "desktop/scripts/electron-smoke.mjs · source_file"
            - option "desktop/scripts/inspect-assets.mjs · source_file"
            - option "desktop/scripts/install-office.py · source_file"
            - option "desktop/src/App.tsx · source_file"
            - option "desktop/src/DiffEditor.tsx · source_file"
            - option "desktop/src/JobsBoard.tsx · source_file"
            - option "desktop/src/OfficeScene.tsx · source_file"
            - option "desktop/src/bridge.ts · source_file"
            - option "desktop/src/main.tsx · source_file"
            - option "desktop/src/office-bindings.ts · source_file"
            - option "desktop/src/runtime-identity.ts · source_file"
            - option "desktop/src/types.ts · source_file"
            - option "desktop/src/style.css · source_file"
            - option "desktop/tests/assets.test.mjs · source_file"
            - option "desktop/tests/bindings.test.mjs · source_file"
            - option "desktop/tests/browser/jobs-live.spec.ts · source_file"
            - option "desktop/tests/browser/viewer.spec.ts · source_file"
            - option "desktop/tests/git.test.mjs · source_file"
            - option "desktop/tests/runtime-client.test.mjs · source_file"
            - option "desktop/tests/install-office.test.mjs · source_file"
            - option "desktop/tests/runtime-identity.test.mjs · source_file"
            - option "desktop/tests/security.test.mjs · source_file"
            - option "desktop/tsconfig.json · source_file"
            - option "desktop/vite.config.ts · source_file"
            - option "dev/cache_references.py · source_file"
            - option "dev/check.py · source_file"
            - option "dev/loop.py · source_file"
            - option "dev/luna.py · source_file"
            - option "dev/mock_runtime.py · source_file"
            - option "dev/plan.json · source_file"
            - option "dev/references.json · source_file"
            - option "dev/test_loop.py · source_file"
            - option "docs/ARCHITECTURE.md · source_file"
            - option "dev/test_specs.py · source_file"
            - option "dev/test_luna.py · source_file"
            - option "docs/ASSET_BINDING.md · source_file"
            - option "docs/COMPUTER_UI.md · source_file"
            - option "docs/ART_DIRECTION.md · source_file"
            - option "docs/EXECUTION.md · source_file"
            - option "docs/FEATURE_MATRIX.md · source_file"
            - option "docs/MVP_ACCEPTANCE.md · source_file"
            - option "docs/LOW_TOKEN_EXECUTION.md · source_file"
            - option "docs/PARALLEL_PLAN.md · source_file"
            - option "docs/RUN_EVALS.md · source_file"
            - option "docs/RESEARCH.md · source_file"
            - option "docs/SETUP_VERIFICATION.md · source_file"
            - option "docs/START_HERE.md · source_file"
            - option "docs/archive/SPEC-0.2.md · source_file"
            - option "docs/VALIDATION.md · source_file"
            - option "docs/design/screen-layout.svg · source_file"
            - option "docs/design/station-kit.svg · source_file"
            - option "docs/goals/A-runtime.md · source_file"
            - option "docs/goals/C-desktop.md · source_file"
            - option "docs/goals/B-tools.md · source_file"
            - option "docs/goals/C-unity.md · source_file"
            - option "docs/goals/D-workshops.md · source_file"
            - option "docs/goals/I1-integration.md · source_file"
            - option "evidence/A/A1-final-review.json · source_file"
            - option "evidence/A/A1-review-2.json · source_file"
            - option "evidence/A/A1-review.json · source_file"
            - option "evidence/A/A1.json · source_file"
            - option "evidence/A/A2-review.json · source_file"
            - option "evidence/A/A2.json · source_file"
            - option "evidence/A/A2-repair-review.json · source_file"
            - option "evidence/A/A3-repair-review.json · source_file"
            - option "evidence/A/A3-review.json · source_file"
            - option "evidence/A/A3.json · source_file"
          - button "Previous artifacts" [disabled] [ref=e48]
          - button "More artifacts" [ref=e49] [cursor=pointer]
          - generic "d7064e6969a474cff9fae0a51bc24c56049c236dc048f8d96c46b3f10bbf9a60" [ref=e50]: SHA256 d7064e6969a4 · immutable
        - generic [ref=e51]:
          - navigation "Result files" [ref=e52]:
            - button ".codex/config.toml unchanged" [ref=e53] [cursor=pointer]:
              - text: .codex/config.toml
              - generic [ref=e54]: unchanged
            - button ".gitattributes unchanged" [ref=e55] [cursor=pointer]:
              - text: .gitattributes
              - generic [ref=e56]: unchanged
            - button ".github/workflows/launch-kit.yml unchanged" [ref=e57] [cursor=pointer]:
              - text: .github/workflows/launch-kit.yml
              - generic [ref=e58]: unchanged
            - button ".gitignore unchanged" [ref=e59] [cursor=pointer]:
              - text: .gitignore
              - generic [ref=e60]: unchanged
            - button "AGENTS.md unchanged" [ref=e61] [cursor=pointer]:
              - text: AGENTS.md
              - generic [ref=e62]: unchanged
            - button "README.md unchanged" [active] [pressed] [ref=e63] [cursor=pointer]:
              - text: README.md
              - generic [ref=e64]: unchanged
            - button "SPEC.md unchanged" [ref=e65] [cursor=pointer]:
              - text: SPEC.md
              - generic [ref=e66]: unchanged
            - button "contracts/EXTENSIONS.md unchanged" [ref=e67] [cursor=pointer]:
              - text: contracts/EXTENSIONS.md
              - generic [ref=e68]: unchanged
            - button "contracts/PROTOCOL.md unchanged" [ref=e69] [cursor=pointer]:
              - text: contracts/PROTOCOL.md
              - generic [ref=e70]: unchanged
            - button "contracts/STORAGE.md unchanged" [ref=e71] [cursor=pointer]:
              - text: contracts/STORAGE.md
              - generic [ref=e72]: unchanged
            - button "contracts/examples/computer.json unchanged" [ref=e73] [cursor=pointer]:
              - text: contracts/examples/computer.json
              - generic [ref=e74]: unchanged
            - button "contracts/snapshot.json unchanged" [ref=e75] [cursor=pointer]:
              - text: contracts/snapshot.json
              - generic [ref=e76]: unchanged
            - button "demo/README.md unchanged" [ref=e77] [cursor=pointer]:
              - text: demo/README.md
              - generic [ref=e78]: unchanged
            - button "demo/club-site/README.md unchanged" [ref=e79] [cursor=pointer]:
              - text: demo/club-site/README.md
              - generic [ref=e80]: unchanged
            - button "demo/club-site/bad/index.html unchanged" [ref=e81] [cursor=pointer]:
              - text: demo/club-site/bad/index.html
              - generic [ref=e82]: unchanged
            - button "demo/club-site/bad/members/signup.html unchanged" [ref=e83] [cursor=pointer]:
              - text: demo/club-site/bad/members/signup.html
              - generic [ref=e84]: unchanged
            - button "demo/club-site/known-good/index.html unchanged" [ref=e85] [cursor=pointer]:
              - text: demo/club-site/known-good/index.html
              - generic [ref=e86]: unchanged
            - button "demo/club-site/known-good/members/welcome.html unchanged" [ref=e87] [cursor=pointer]:
              - text: demo/club-site/known-good/members/welcome.html
              - generic [ref=e88]: unchanged
            - button "desktop/README.md unchanged" [ref=e89] [cursor=pointer]:
              - text: desktop/README.md
              - generic [ref=e90]: unchanged
            - button "desktop/electron/git-reader.cjs unchanged" [ref=e91] [cursor=pointer]:
              - text: desktop/electron/git-reader.cjs
              - generic [ref=e92]: unchanged
            - button "desktop/electron/main.cjs unchanged" [ref=e93] [cursor=pointer]:
              - text: desktop/electron/main.cjs
              - generic [ref=e94]: unchanged
            - button "desktop/electron/preload.cjs unchanged" [ref=e95] [cursor=pointer]:
              - text: desktop/electron/preload.cjs
              - generic [ref=e96]: unchanged
            - button "desktop/electron/runtime-client.cjs unchanged" [ref=e97] [cursor=pointer]:
              - text: desktop/electron/runtime-client.cjs
              - generic [ref=e98]: unchanged
            - button "desktop/electron/security.cjs unchanged" [ref=e99] [cursor=pointer]:
              - text: desktop/electron/security.cjs
              - generic [ref=e100]: unchanged
            - button "desktop/electron/static-server.cjs unchanged" [ref=e101] [cursor=pointer]:
              - text: desktop/electron/static-server.cjs
              - generic [ref=e102]: unchanged
            - button "desktop/index.html unchanged" [ref=e103] [cursor=pointer]:
              - text: desktop/index.html
              - generic [ref=e104]: unchanged
            - button "desktop/package-lock.json unchanged" [ref=e105] [cursor=pointer]:
              - text: desktop/package-lock.json
              - generic [ref=e106]: unchanged
            - button "desktop/package.json unchanged" [ref=e107] [cursor=pointer]:
              - text: desktop/package.json
              - generic [ref=e108]: unchanged
            - button "desktop/playwright.config.ts unchanged" [ref=e109] [cursor=pointer]:
              - text: desktop/playwright.config.ts
              - generic [ref=e110]: unchanged
            - button "desktop/scripts/electron-smoke.mjs unchanged" [ref=e111] [cursor=pointer]:
              - text: desktop/scripts/electron-smoke.mjs
              - generic [ref=e112]: unchanged
            - button "desktop/scripts/inspect-assets.mjs unchanged" [ref=e113] [cursor=pointer]:
              - text: desktop/scripts/inspect-assets.mjs
              - generic [ref=e114]: unchanged
            - button "desktop/scripts/install-office.py unchanged" [ref=e115] [cursor=pointer]:
              - text: desktop/scripts/install-office.py
              - generic [ref=e116]: unchanged
            - button "desktop/src/App.tsx unchanged" [ref=e117] [cursor=pointer]:
              - text: desktop/src/App.tsx
              - generic [ref=e118]: unchanged
            - button "desktop/src/DiffEditor.tsx unchanged" [ref=e119] [cursor=pointer]:
              - text: desktop/src/DiffEditor.tsx
              - generic [ref=e120]: unchanged
            - button "desktop/src/JobsBoard.tsx unchanged" [ref=e121] [cursor=pointer]:
              - text: desktop/src/JobsBoard.tsx
              - generic [ref=e122]: unchanged
            - button "desktop/src/OfficeScene.tsx unchanged" [ref=e123] [cursor=pointer]:
              - text: desktop/src/OfficeScene.tsx
              - generic [ref=e124]: unchanged
            - button "desktop/src/bridge.ts unchanged" [ref=e125] [cursor=pointer]:
              - text: desktop/src/bridge.ts
              - generic [ref=e126]: unchanged
            - button "desktop/src/main.tsx unchanged" [ref=e127] [cursor=pointer]:
              - text: desktop/src/main.tsx
              - generic [ref=e128]: unchanged
            - button "desktop/src/office-bindings.ts unchanged" [ref=e129] [cursor=pointer]:
              - text: desktop/src/office-bindings.ts
              - generic [ref=e130]: unchanged
            - button "desktop/src/runtime-identity.ts unchanged" [ref=e131] [cursor=pointer]:
              - text: desktop/src/runtime-identity.ts
              - generic [ref=e132]: unchanged
            - button "desktop/src/style.css unchanged" [ref=e133] [cursor=pointer]:
              - text: desktop/src/style.css
              - generic [ref=e134]: unchanged
            - button "desktop/src/types.ts unchanged" [ref=e135] [cursor=pointer]:
              - text: desktop/src/types.ts
              - generic [ref=e136]: unchanged
            - button "desktop/tests/assets.test.mjs unchanged" [ref=e137] [cursor=pointer]:
              - text: desktop/tests/assets.test.mjs
              - generic [ref=e138]: unchanged
            - button "desktop/tests/bindings.test.mjs unchanged" [ref=e139] [cursor=pointer]:
              - text: desktop/tests/bindings.test.mjs
              - generic [ref=e140]: unchanged
            - button "desktop/tests/browser/jobs-live.spec.ts unchanged" [ref=e141] [cursor=pointer]:
              - text: desktop/tests/browser/jobs-live.spec.ts
              - generic [ref=e142]: unchanged
            - button "desktop/tests/browser/viewer.spec.ts unchanged" [ref=e143] [cursor=pointer]:
              - text: desktop/tests/browser/viewer.spec.ts
              - generic [ref=e144]: unchanged
            - button "desktop/tests/git.test.mjs unchanged" [ref=e145] [cursor=pointer]:
              - text: desktop/tests/git.test.mjs
              - generic [ref=e146]: unchanged
            - button "desktop/tests/install-office.test.mjs unchanged" [ref=e147] [cursor=pointer]:
              - text: desktop/tests/install-office.test.mjs
              - generic [ref=e148]: unchanged
            - button "desktop/tests/runtime-client.test.mjs unchanged" [ref=e149] [cursor=pointer]:
              - text: desktop/tests/runtime-client.test.mjs
              - generic [ref=e150]: unchanged
            - button "desktop/tests/runtime-identity.test.mjs unchanged" [ref=e151] [cursor=pointer]:
              - text: desktop/tests/runtime-identity.test.mjs
              - generic [ref=e152]: unchanged
            - button "desktop/tests/security.test.mjs unchanged" [ref=e153] [cursor=pointer]:
              - text: desktop/tests/security.test.mjs
              - generic [ref=e154]: unchanged
            - button "desktop/tsconfig.json unchanged" [ref=e155] [cursor=pointer]:
              - text: desktop/tsconfig.json
              - generic [ref=e156]: unchanged
            - button "desktop/vite.config.ts unchanged" [ref=e157] [cursor=pointer]:
              - text: desktop/vite.config.ts
              - generic [ref=e158]: unchanged
            - button "dev/cache_references.py unchanged" [ref=e159] [cursor=pointer]:
              - text: dev/cache_references.py
              - generic [ref=e160]: unchanged
            - button "dev/check.py unchanged" [ref=e161] [cursor=pointer]:
              - text: dev/check.py
              - generic [ref=e162]: unchanged
            - button "dev/loop.py unchanged" [ref=e163] [cursor=pointer]:
              - text: dev/loop.py
              - generic [ref=e164]: unchanged
            - button "dev/luna.py unchanged" [ref=e165] [cursor=pointer]:
              - text: dev/luna.py
              - generic [ref=e166]: unchanged
            - button "dev/mock_runtime.py unchanged" [ref=e167] [cursor=pointer]:
              - text: dev/mock_runtime.py
              - generic [ref=e168]: unchanged
            - button "dev/plan.json unchanged" [ref=e169] [cursor=pointer]:
              - text: dev/plan.json
              - generic [ref=e170]: unchanged
            - button "dev/references.json unchanged" [ref=e171] [cursor=pointer]:
              - text: dev/references.json
              - generic [ref=e172]: unchanged
            - button "dev/test_loop.py unchanged" [ref=e173] [cursor=pointer]:
              - text: dev/test_loop.py
              - generic [ref=e174]: unchanged
            - button "dev/test_luna.py unchanged" [ref=e175] [cursor=pointer]:
              - text: dev/test_luna.py
              - generic [ref=e176]: unchanged
            - button "dev/test_specs.py unchanged" [ref=e177] [cursor=pointer]:
              - text: dev/test_specs.py
              - generic [ref=e178]: unchanged
            - button "docs/ARCHITECTURE.md unchanged" [ref=e179] [cursor=pointer]:
              - text: docs/ARCHITECTURE.md
              - generic [ref=e180]: unchanged
            - button "docs/ART_DIRECTION.md unchanged" [ref=e181] [cursor=pointer]:
              - text: docs/ART_DIRECTION.md
              - generic [ref=e182]: unchanged
            - button "docs/ASSET_BINDING.md unchanged" [ref=e183] [cursor=pointer]:
              - text: docs/ASSET_BINDING.md
              - generic [ref=e184]: unchanged
            - button "docs/COMPUTER_UI.md unchanged" [ref=e185] [cursor=pointer]:
              - text: docs/COMPUTER_UI.md
              - generic [ref=e186]: unchanged
            - button "docs/EXECUTION.md unchanged" [ref=e187] [cursor=pointer]:
              - text: docs/EXECUTION.md
              - generic [ref=e188]: unchanged
            - button "docs/FEATURE_MATRIX.md unchanged" [ref=e189] [cursor=pointer]:
              - text: docs/FEATURE_MATRIX.md
              - generic [ref=e190]: unchanged
            - button "docs/LOW_TOKEN_EXECUTION.md unchanged" [ref=e191] [cursor=pointer]:
              - text: docs/LOW_TOKEN_EXECUTION.md
              - generic [ref=e192]: unchanged
            - button "docs/MVP_ACCEPTANCE.md unchanged" [ref=e193] [cursor=pointer]:
              - text: docs/MVP_ACCEPTANCE.md
              - generic [ref=e194]: unchanged
            - button "docs/PARALLEL_PLAN.md unchanged" [ref=e195] [cursor=pointer]:
              - text: docs/PARALLEL_PLAN.md
              - generic [ref=e196]: unchanged
            - button "docs/RESEARCH.md unchanged" [ref=e197] [cursor=pointer]:
              - text: docs/RESEARCH.md
              - generic [ref=e198]: unchanged
            - button "docs/RUN_EVALS.md unchanged" [ref=e199] [cursor=pointer]:
              - text: docs/RUN_EVALS.md
              - generic [ref=e200]: unchanged
            - button "docs/SETUP_VERIFICATION.md unchanged" [ref=e201] [cursor=pointer]:
              - text: docs/SETUP_VERIFICATION.md
              - generic [ref=e202]: unchanged
            - button "docs/START_HERE.md unchanged" [ref=e203] [cursor=pointer]:
              - text: docs/START_HERE.md
              - generic [ref=e204]: unchanged
            - button "docs/VALIDATION.md unchanged" [ref=e205] [cursor=pointer]:
              - text: docs/VALIDATION.md
              - generic [ref=e206]: unchanged
            - button "docs/archive/SPEC-0.2.md unchanged" [ref=e207] [cursor=pointer]:
              - text: docs/archive/SPEC-0.2.md
              - generic [ref=e208]: unchanged
            - button "docs/design/screen-layout.svg unchanged" [ref=e209] [cursor=pointer]:
              - text: docs/design/screen-layout.svg
              - generic [ref=e210]: unchanged
            - button "docs/design/station-kit.svg unchanged" [ref=e211] [cursor=pointer]:
              - text: docs/design/station-kit.svg
              - generic [ref=e212]: unchanged
            - button "docs/goals/A-runtime.md unchanged" [ref=e213] [cursor=pointer]:
              - text: docs/goals/A-runtime.md
              - generic [ref=e214]: unchanged
            - button "docs/goals/B-tools.md unchanged" [ref=e215] [cursor=pointer]:
              - text: docs/goals/B-tools.md
              - generic [ref=e216]: unchanged
            - button "docs/goals/C-desktop.md unchanged" [ref=e217] [cursor=pointer]:
              - text: docs/goals/C-desktop.md
              - generic [ref=e218]: unchanged
            - button "docs/goals/C-unity.md unchanged" [ref=e219] [cursor=pointer]:
              - text: docs/goals/C-unity.md
              - generic [ref=e220]: unchanged
            - button "docs/goals/D-workshops.md unchanged" [ref=e221] [cursor=pointer]:
              - text: docs/goals/D-workshops.md
              - generic [ref=e222]: unchanged
            - button "docs/goals/I1-integration.md unchanged" [ref=e223] [cursor=pointer]:
              - text: docs/goals/I1-integration.md
              - generic [ref=e224]: unchanged
            - button "evidence/A/A1-final-review.json unchanged" [ref=e225] [cursor=pointer]:
              - text: evidence/A/A1-final-review.json
              - generic [ref=e226]: unchanged
            - button "evidence/A/A1-review-2.json unchanged" [ref=e227] [cursor=pointer]:
              - text: evidence/A/A1-review-2.json
              - generic [ref=e228]: unchanged
            - button "evidence/A/A1-review.json unchanged" [ref=e229] [cursor=pointer]:
              - text: evidence/A/A1-review.json
              - generic [ref=e230]: unchanged
            - button "evidence/A/A1.json unchanged" [ref=e231] [cursor=pointer]:
              - text: evidence/A/A1.json
              - generic [ref=e232]: unchanged
            - button "evidence/A/A2-repair-review.json unchanged" [ref=e233] [cursor=pointer]:
              - text: evidence/A/A2-repair-review.json
              - generic [ref=e234]: unchanged
            - button "evidence/A/A2-review.json unchanged" [ref=e235] [cursor=pointer]:
              - text: evidence/A/A2-review.json
              - generic [ref=e236]: unchanged
            - button "evidence/A/A2.json unchanged" [ref=e237] [cursor=pointer]:
              - text: evidence/A/A2.json
              - generic [ref=e238]: unchanged
            - button "evidence/A/A3-repair-review.json unchanged" [ref=e239] [cursor=pointer]:
              - text: evidence/A/A3-repair-review.json
              - generic [ref=e240]: unchanged
            - button "evidence/A/A3-review.json unchanged" [ref=e241] [cursor=pointer]:
              - text: evidence/A/A3-review.json
              - generic [ref=e242]: unchanged
            - button "evidence/A/A3.json unchanged" [ref=e243] [cursor=pointer]:
              - text: evidence/A/A3.json
              - generic [ref=e244]: unchanged
            - button "evidence/B/B1-repair-review.json unchanged" [ref=e245] [cursor=pointer]:
              - text: evidence/B/B1-repair-review.json
              - generic [ref=e246]: unchanged
            - button "evidence/B/B1-review.json unchanged" [ref=e247] [cursor=pointer]:
              - text: evidence/B/B1-review.json
              - generic [ref=e248]: unchanged
            - button "evidence/B/B1.json unchanged" [ref=e249] [cursor=pointer]:
              - text: evidence/B/B1.json
              - generic [ref=e250]: unchanged
            - button "evidence/B/B2-readiness.json unchanged" [ref=e251] [cursor=pointer]:
              - text: evidence/B/B2-readiness.json
              - generic [ref=e252]: unchanged
            - generic [ref=e253]:
              - button "Previous files" [disabled] [ref=e254]
              - button "More files" [ref=e255] [cursor=pointer]
          - region "Artifact content" [ref=e256]:
            - generic [ref=e257]:
              - button "File text" [pressed] [ref=e258] [cursor=pointer]
              - button "Git diff" [ref=e259] [cursor=pointer]
              - generic [ref=e260]: README.md
            - generic "Read-only artifact text" [ref=e261]: "1 # Sidequest — Electron presentation work 2 3 Start the current Electron + React + TypeScript client with [desktop/README.md](desktop/README.md). It replaces the Unity presentation decision and provides a read-only local Git diff viewer with lazy Monaco, expandable reading and Escape/state restoration. The office loader expects the owner’s actual GLB and explicit monitor bindings; no replacement art is generated. 4 5 The specified Python/SQLite runtime, scheduling, policy, authenticated artifact API, isolated Git pipeline and trusted checks are implemented. The jobs board completed a genuine local inspection through the browser, runtime and adapters with zero model calls and no source delivery. The Codex app-server adapter and persisted session lifecycle are implemented and tested with a fake transport; native coding execution remains blocked. Browser evidence does not certify Electron or actual office compatibility. See [run/eval instructions](docs/RUN_EVALS.md), [acceptance limits](docs/MVP_ACCEPTANCE.md) and [screenshots/provenance](evidence/desktop/README.md). 6 7 The development-controller instructions below are retained for operator context. The machine plan now points C at Electron; the current MVP was built through explicitly coordinated lanes rather than that controller. Do not start model workers to launch the viewer or local evaluations. 8 9 # Sidequest 10 11 A calm office for real agent swarms, with Electron presentation. Inspect artifacts and diffs directly on a selected computer. Use existing coding agents; do not build another agent framework. 12 13 The owner's completed Blender/GLB office assets are protected inputs. Their archive has been located but the VM transfer is blocked; the checkout contains no actual office art. Do not regenerate the office. Native Electron and Codex readiness are also blocked as recorded in the acceptance evidence. 14 15 Start at [START HERE](docs/START_HERE.md). Read [SPEC](SPEC.md) for scope or [ARCHITECTURE](docs/ARCHITECTURE.md) for the fixed stack. Workers read only their assigned goal and its relevant documents, not the entire research archive. 16 17 | Lane | Exclusive responsibility | 18 |---|---| 19 | A | Local runtime, database, scheduler, artifact HTTP service | 20 | B | Coding-provider adapter, isolated Git, file/diff capture, local monitoring | 21 | C | Existing GLB assets, Electron computer UI, office interaction and build | 22 | D | Independent checks, reusable workshops, demo and final acceptance rig | 23 24 Each lane has three goals. Each candidate gets a new validator thread at its exact commit. Main is not automatically changed by development runs. The [low-token policy](docs/LOW_TOKEN_EXECUTION.md) selects Luna/max, short task packets, deterministic tests first, bounded attempts, and no always-running manager. 25 26 ```bash 27 python3 -m unittest discover -s dev -p 'test_*.py' -v 28 python3 dev/check.py --setup 29 python3 dev/loop.py prepare 30 python3 dev/luna.py run A --allow-network 31 # Start B, C and D in their own terminals from this same checkout. 32 ``` 33 34 Complete the asset/environment preflight in START HERE before preparing worktrees. `dev/luna.py` checks the effective Codex configuration and account model support before allowing a model run. The low-cost configuration is an explicit preference, not an estimate of your account bill. 35 36 [Computer UI](docs/COMPUTER_UI.md) · [Asset binding](docs/ASSET_BINDING.md) · [Protocol](contracts/PROTOCOL.md) · [Extensions](contracts/EXTENSIONS.md) · [Feature coverage](docs/FEATURE_MATRIX.md) · [Upstream sources](docs/RESEARCH.md) 37 38 The diagrams are architecture specifications, not screenshots of an implemented app. Earlier concept images and station-kit drawings are not authority to redesign the owner's completed office."
            - generic [ref=e262]:
              - button "Previous lines" [disabled] [ref=e263]
              - button "More lines" [disabled] [ref=e264]
      - generic [ref=e265]: Runtime local-git · revision 2801 · Coding execution unavailable
  - generic [ref=e266]:
    - combobox "Office navigation" [ref=e267]:
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
    - generic "Original staged poses; recorded runtime ownership is separate from provider connectivity." [ref=e268]: 26 staged · no sessions
    - generic "UI refresh and file viewing make zero model calls." [ref=e269]: Local Git · read-only
```

# Test source

```ts
  23  |   await board.getByRole('button',{name:'Submit inspection',exact:true}).click();
  24  |   await board.getByRole('button',{name:new RegExp(title.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'))}).click();
  25  |   await expect(board.getByRole('button',{name:'Run inspection',exact:true})).toBeEnabled();
  26  |   await page.screenshot({path:path.resolve('../evidence/desktop/job-queued.png')});
  27  |   await board.getByRole('button',{name:'Run inspection',exact:true}).click();
  28  |   await expect(board.locator('.job-state')).toHaveText('verifying',{timeout:20_000});
  29  |   await expect(board.locator('.job-checks')).toContainText('pass',{timeout:90_000});
  30  |   await expect(board).toContainText('Inspection results ready.');
  31  |   await expect(board.locator('.artifact-files>button').first()).toBeVisible();
  32  |   await expect(board.locator('.artifact-text')).not.toContainText('Loading file text…');
  33  |   await expect(board.locator('.artifact-files>button').first()).toBeVisible();
  34  |   await page.screenshot({path:path.resolve('../evidence/desktop/job-result.png')});
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
> 123 |   await result.getByRole('button',{name:'Expand',exact:true}).click();
      |                                                               ^ Error: locator.click: Test timeout of 90000ms exceeded.
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
  135 |   await expect.poll(()=>result.locator('.artifact-text').evaluate(node=>node.scrollTop)).toBeGreaterThan(100);
  136 |   await page.screenshot({path:path.resolve('../evidence/desktop/assigned-result.png')});
  137 |   await writeFile(path.resolve('../evidence/desktop/result-display-browser.json'),JSON.stringify({job_id:completed.id,queued_test_title:queuedTitle,queued_test_executed:false,selected_file:selectedFile,temporary_network_failure:true,recovered:true,scope:'Actual local inspection artifacts; display assignment only; zero coding/model launches'},null,2));
  138 | });
  139 | 
  140 | test('recorded session ownership persists at a figure and renders real contextual events',async({page,request})=>{
  141 |  test.setTimeout(120_000);test.skip(process.env.SIDEQUEST_TEST_INSPECTION!=='1','Requires actual deterministic inspection records; no model calls.');
  142 |  const origin={Origin:'http://127.0.0.1:5173'};
  143 |  const read=async()=>{const response=await request.post('/__sidequest/runtime/snapshot',{data:[],headers:origin});expect(response.ok()).toBe(true);return response.json();};
  144 |  let state=await read();const job=state.jobs.find((job:{run_ids:string[];execution_profile:string})=>job.execution_profile==='local_git_inspection'&&job.run_ids?.length);expect(job).toBeTruthy();
  145 |  const runId=job.run_ids.at(-1);const runReply=await request.post('/__sidequest/runtime/runInfo',{data:[runId],headers:origin});const {run}=await runReply.json();expect(run.worker_id).toBeTruthy();
  146 |  for(const owner of state.office_sessions.filter((owner:{station_id:string;worker_id:string})=>owner.station_id==='parent_019'||owner.worker_id===run.worker_id)){const clear=await request.post('/__sidequest/runtime/clearSession',{data:[owner.station_id,state.revision],headers:origin});expect(clear.ok()).toBe(true);state=await read();}
  147 |  const coding:string[]=[];page.on('request',r=>{if(/__sidequest\/runtime\/(submitCoding|runCoding|enableCoding)$/.test(r.url()))coding.push(r.url());});
  148 |  await page.goto('/');await expect(page.locator('.app-footer')).toHaveAttribute('data-actor-status','ready',{timeout:60000});
  149 |  await page.getByRole('combobox',{name:'Office navigation'}).selectOption('actor:parent_019');
  150 |  let session=page.getByRole('dialog',{name:'Agent session'});await session.getByText('Attach recorded session',{exact:true}).click();
  151 |  await session.getByRole('combobox',{name:'Recorded task',exact:true}).selectOption(job.id);await session.getByRole('combobox',{name:'Recorded run',exact:true}).selectOption(runId);
  152 |  await session.getByRole('button',{name:'Assign session',exact:true}).click();
  153 |  await expect(session.locator('.session-records')).toHaveAttribute('data-session-run',runId);await expect(session).toContainText('Recorded local inspection');
  154 |  await expect(session).toContainText('Checking');await expect(session.locator('.run-activity')).toHaveCount(0);
  155 |  await page.screenshot({path:path.resolve('../evidence/desktop/recorded-session.png')});
  156 |  await session.getByRole('button',{name:'Open monitor',exact:true}).click();const trace=page.getByRole('region',{name:'Session execution trace'});
  157 |  await expect(trace.locator('.monitor-events>li').first()).toBeVisible();await expect(trace).toContainText('Checking');
  158 |  await page.screenshot({path:path.resolve('../evidence/desktop/monitor-pov.png')});
  159 |  await trace.getByText('Run details',{exact:true}).click();await expect(trace).toContainText('No model call');await expect(trace).toContainText('Recorded usage:');await page.keyboard.press('Escape');
  160 |  await page.getByRole('combobox',{name:'Office navigation'}).selectOption('actor:parent_019');session=page.getByRole('dialog',{name:'Agent session'});
  161 |  await session.getByRole('button',{name:'Open results',exact:true}).click();const results=page.getByRole('region',{name:'Computer job results'});await expect(results).toBeVisible();await expect(results.locator('.job-summary')).toContainText(job.title);await page.keyboard.press('Escape');
  162 |  await page.getByRole('combobox',{name:'Office navigation'}).selectOption('actor:parent_019');session=page.getByRole('dialog',{name:'Agent session'});await expect(session.locator('.session-records')).toHaveAttribute('data-session-run',runId);
  163 |  const saved=await read();const owner=saved.office_sessions.find((owner:{station_id:string})=>owner.station_id==='parent_019');expect(owner).toMatchObject({job_id:job.id,run_id:runId,worker_id:run.worker_id,project_id:job.project_id});
  164 |  await page.reload();await expect(page.locator('.app-footer')).toHaveAttribute('data-actor-status','ready',{timeout:60000});await page.getByRole('combobox',{name:'Office navigation'}).selectOption('actor:parent_019');session=page.getByRole('dialog',{name:'Agent session'});await expect(session.locator('.session-records')).toHaveAttribute('data-session-run',runId);
  165 |  await page.setViewportSize({width:390,height:780});await session.getByRole('button',{name:'Open monitor',exact:true}).click();await expect(trace.locator('.monitor-events>li').first()).toBeVisible();
  166 |  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);const axe=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze();await writeFile(path.resolve('../evidence/desktop/session-accessibility.json'),JSON.stringify(axe.violations,null,2));expect(axe.violations.map(v=>v.id)).toEqual([]);
  167 |  await page.screenshot({path:path.resolve('../evidence/desktop/recorded-session-390.png')});
  168 |  await page.route('**/__sidequest/runtime/runInfo',route=>route.fulfill({json:{v:1,run:{...run,worker_id:'fixture-wrong-worker'}}}));await trace.getByRole('button',{name:'Refresh trace',exact:true}).click();await expect(trace).toContainText('Recorded session worker identity changed.');await page.unroute('**/__sidequest/runtime/runInfo');
  169 |  await page.keyboard.press('Escape');await page.getByRole('combobox',{name:'Office navigation'}).selectOption('board');const detail=page.getByRole('region',{name:'Tasks board detail'});await detail.getByRole('combobox',{name:'Task',exact:true}).selectOption(job.id);await expect(detail).toContainText('Recorded worker at Computer 19');await detail.getByRole('button',{name:'Open session',exact:true}).click();
  170 |  session=page.getByRole('dialog',{name:'Agent session'});await expect(session.locator('.session-records')).toHaveAttribute('data-session-run',runId);
  171 |  await session.getByText('Session details',{exact:true}).click();await session.getByRole('button',{name:'Detach session',exact:true}).click();await expect(session).toContainText('No live session attached');expect((await read()).office_sessions.some((row:{station_id:string})=>row.station_id==='parent_019')).toBe(false);expect(coding).toEqual([]);
  172 |  await writeFile(path.resolve('../evidence/desktop/session-browser.json'),JSON.stringify({scope:'Actual local inspection; persistent display ownership, not coding dispatch or live Codex conversation',owner,reload_restored:true,board_links_same_session:true,open_results_same_job:true,wrong_worker_rejected:true,fixtures:['Read-only runInfo response with explicitly fixture-wrong-worker; no persisted state changed'],explicit_detach:true,coding_requests:coding,axe_violations:axe.violations.map(v=>v.id)},null,2));
  173 | });
  174 | 
```