# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: visual-office.spec.ts >> provider settings and preserved work at 1440px
- Location: tests/browser/visual-office.spec.ts:6:32

# Error details

```
Error: expect(locator).toHaveCount(expected) failed

Locator:  getByTestId('diff-editor')
Expected: 1
Received: 0
Timeout:  5000ms

Call log:
  - Expect "toHaveCount" getByTestId('diff-editor') with timeout 5000ms
  - waiting for getByTestId('diff-editor')
    6 × locator resolved to 0 elements
      - unexpected value "0"

```

# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - main [ref=e3]:
    - generic [ref=e4]:
      - generic [ref=e5]: sidequestlocal workspace
      - generic [ref=e6]: sidequestfeat/electron-office-diff
      - button "Settings" [ref=e7] [cursor=pointer]
      - button "Jobs" [ref=e8] [cursor=pointer]
      - button "Refresh Git" [ref=e9] [cursor=pointer]
    - region "Computer work viewer" [ref=e15]:
      - generic [ref=e16]:
        - generic [ref=e17]:
          - paragraph [ref=e18]: Computer 19 · Read-only
          - heading "sidequest" [level=2] [ref=e19]
        - generic [ref=e20]:
          - button "Expand" [ref=e21] [cursor=pointer]
          - button "Return to office" [ref=e22] [cursor=pointer]: Office Esc
      - generic [ref=e23]:
        - generic [ref=e24]: Git diff
        - generic "69bf06696a93c9f58eee2d088e84404d4f6563d6" [ref=e25]: 69bf0669 → 8a9fb11c
        - generic [ref=e26]: Committed revisions
      - generic [ref=e27]:
        - navigation "Changed files" [ref=e28]:
          - paragraph [ref=e29]: 204 changed files
          - button "M .gitignore" [pressed] [ref=e30] [cursor=pointer]:
            - generic "modified" [ref=e31]: M
            - generic ".gitignore" [ref=e32]
          - button "M AGENTS.md" [ref=e33] [cursor=pointer]:
            - generic "modified" [ref=e34]: M
            - generic "AGENTS.md" [ref=e35]
          - button "M README.md" [ref=e36] [cursor=pointer]:
            - generic "modified" [ref=e37]: M
            - generic "README.md" [ref=e38]
          - button "M SPEC.md" [ref=e39] [cursor=pointer]:
            - generic "modified" [ref=e40]: M
            - generic "SPEC.md" [ref=e41]
          - button "+ contracts/EXTENSIONS.md" [ref=e42] [cursor=pointer]:
            - generic "added" [ref=e43]: +
            - generic "contracts/EXTENSIONS.md" [ref=e44]
          - button "M contracts/PROTOCOL.md" [ref=e45] [cursor=pointer]:
            - generic "modified" [ref=e46]: M
            - generic "contracts/PROTOCOL.md" [ref=e47]
          - button "+ contracts/STORAGE.md" [ref=e48] [cursor=pointer]:
            - generic "added" [ref=e49]: +
            - generic "contracts/STORAGE.md" [ref=e50]
          - button "+ contracts/examples/computer.json" [ref=e51] [cursor=pointer]:
            - generic "added" [ref=e52]: +
            - generic "contracts/examples/computer.json" [ref=e53]
          - button "+ demo/README.md" [ref=e54] [cursor=pointer]:
            - generic "added" [ref=e55]: +
            - generic "demo/README.md" [ref=e56]
          - button "+ demo/club-site/README.md" [ref=e57] [cursor=pointer]:
            - generic "added" [ref=e58]: +
            - generic "demo/club-site/README.md" [ref=e59]
          - button "+ demo/club-site/bad/index.html" [ref=e60] [cursor=pointer]:
            - generic "added" [ref=e61]: +
            - generic "demo/club-site/bad/index.html" [ref=e62]
          - button "+ demo/club-site/bad/members/signup.html" [ref=e63] [cursor=pointer]:
            - generic "added" [ref=e64]: +
            - generic "demo/club-site/bad/members/signup.html" [ref=e65]
          - button "+ demo/club-site/known-good/index.html" [ref=e66] [cursor=pointer]:
            - generic "added" [ref=e67]: +
            - generic "demo/club-site/known-good/index.html" [ref=e68]
          - button "+ demo/club-site/known-good/members/welcome.html" [ref=e69] [cursor=pointer]:
            - generic "added" [ref=e70]: +
            - generic "demo/club-site/known-good/members/welcome.html" [ref=e71]
          - button "+ desktop/README.md" [ref=e72] [cursor=pointer]:
            - generic "added" [ref=e73]: +
            - generic "desktop/README.md" [ref=e74]
          - button "+ desktop/electron/git-reader.cjs" [ref=e75] [cursor=pointer]:
            - generic "added" [ref=e76]: +
            - generic "desktop/electron/git-reader.cjs" [ref=e77]
          - button "+ desktop/electron/main.cjs" [ref=e78] [cursor=pointer]:
            - generic "added" [ref=e79]: +
            - generic "desktop/electron/main.cjs" [ref=e80]
          - button "+ desktop/electron/preload.cjs" [ref=e81] [cursor=pointer]:
            - generic "added" [ref=e82]: +
            - generic "desktop/electron/preload.cjs" [ref=e83]
          - button "+ desktop/electron/runtime-client.cjs" [ref=e84] [cursor=pointer]:
            - generic "added" [ref=e85]: +
            - generic "desktop/electron/runtime-client.cjs" [ref=e86]
          - button "+ desktop/electron/security.cjs" [ref=e87] [cursor=pointer]:
            - generic "added" [ref=e88]: +
            - generic "desktop/electron/security.cjs" [ref=e89]
          - button "+ desktop/electron/static-server.cjs" [ref=e90] [cursor=pointer]:
            - generic "added" [ref=e91]: +
            - generic "desktop/electron/static-server.cjs" [ref=e92]
          - button "+ desktop/index.html" [ref=e93] [cursor=pointer]:
            - generic "added" [ref=e94]: +
            - generic "desktop/index.html" [ref=e95]
          - button "+ desktop/package-lock.json" [ref=e96] [cursor=pointer]:
            - generic "added" [ref=e97]: +
            - generic "desktop/package-lock.json" [ref=e98]
          - button "+ desktop/package.json" [ref=e99] [cursor=pointer]:
            - generic "added" [ref=e100]: +
            - generic "desktop/package.json" [ref=e101]
          - button "+ desktop/scripts/electron-smoke.mjs" [ref=e102] [cursor=pointer]:
            - generic "added" [ref=e103]: +
            - generic "desktop/scripts/electron-smoke.mjs" [ref=e104]
          - button "+ desktop/scripts/inspect-assets.mjs" [ref=e105] [cursor=pointer]:
            - generic "added" [ref=e106]: +
            - generic "desktop/scripts/inspect-assets.mjs" [ref=e107]
          - button "+ desktop/scripts/install-office.py" [ref=e108] [cursor=pointer]:
            - generic "added" [ref=e109]: +
            - generic "desktop/scripts/install-office.py" [ref=e110]
          - button "+ desktop/src/App.tsx" [ref=e111] [cursor=pointer]:
            - generic "added" [ref=e112]: +
            - generic "desktop/src/App.tsx" [ref=e113]
          - button "+ desktop/src/DiffEditor.tsx" [ref=e114] [cursor=pointer]:
            - generic "added" [ref=e115]: +
            - generic "desktop/src/DiffEditor.tsx" [ref=e116]
          - button "+ desktop/src/JobsBoard.tsx" [ref=e117] [cursor=pointer]:
            - generic "added" [ref=e118]: +
            - generic "desktop/src/JobsBoard.tsx" [ref=e119]
          - button "+ desktop/src/OfficeScene.tsx" [ref=e120] [cursor=pointer]:
            - generic "added" [ref=e121]: +
            - generic "desktop/src/OfficeScene.tsx" [ref=e122]
          - button "+ desktop/src/bridge.ts" [ref=e123] [cursor=pointer]:
            - generic "added" [ref=e124]: +
            - generic "desktop/src/bridge.ts" [ref=e125]
          - button "+ desktop/src/main.tsx" [ref=e126] [cursor=pointer]:
            - generic "added" [ref=e127]: +
            - generic "desktop/src/main.tsx" [ref=e128]
          - button "+ desktop/src/office-bindings.ts" [ref=e129] [cursor=pointer]:
            - generic "added" [ref=e130]: +
            - generic "desktop/src/office-bindings.ts" [ref=e131]
          - button "+ desktop/src/runtime-identity.ts" [ref=e132] [cursor=pointer]:
            - generic "added" [ref=e133]: +
            - generic "desktop/src/runtime-identity.ts" [ref=e134]
          - button "+ desktop/src/style.css" [ref=e135] [cursor=pointer]:
            - generic "added" [ref=e136]: +
            - generic "desktop/src/style.css" [ref=e137]
          - button "+ desktop/src/types.ts" [ref=e138] [cursor=pointer]:
            - generic "added" [ref=e139]: +
            - generic "desktop/src/types.ts" [ref=e140]
          - button "+ desktop/tests/assets.test.mjs" [ref=e141] [cursor=pointer]:
            - generic "added" [ref=e142]: +
            - generic "desktop/tests/assets.test.mjs" [ref=e143]
          - button "+ desktop/tests/bindings.test.mjs" [ref=e144] [cursor=pointer]:
            - generic "added" [ref=e145]: +
            - generic "desktop/tests/bindings.test.mjs" [ref=e146]
          - button "+ desktop/tests/browser/jobs-live.spec.ts" [ref=e147] [cursor=pointer]:
            - generic "added" [ref=e148]: +
            - generic "desktop/tests/browser/jobs-live.spec.ts" [ref=e149]
          - button "+ desktop/tests/browser/viewer.spec.ts" [ref=e150] [cursor=pointer]:
            - generic "added" [ref=e151]: +
            - generic "desktop/tests/browser/viewer.spec.ts" [ref=e152]
          - button "+ desktop/tests/git.test.mjs" [ref=e153] [cursor=pointer]:
            - generic "added" [ref=e154]: +
            - generic "desktop/tests/git.test.mjs" [ref=e155]
          - button "+ desktop/tests/install-office.test.mjs" [ref=e156] [cursor=pointer]:
            - generic "added" [ref=e157]: +
            - generic "desktop/tests/install-office.test.mjs" [ref=e158]
          - button "+ desktop/tests/runtime-client.test.mjs" [ref=e159] [cursor=pointer]:
            - generic "added" [ref=e160]: +
            - generic "desktop/tests/runtime-client.test.mjs" [ref=e161]
          - button "+ desktop/tests/runtime-identity.test.mjs" [ref=e162] [cursor=pointer]:
            - generic "added" [ref=e163]: +
            - generic "desktop/tests/runtime-identity.test.mjs" [ref=e164]
          - button "+ desktop/tests/security.test.mjs" [ref=e165] [cursor=pointer]:
            - generic "added" [ref=e166]: +
            - generic "desktop/tests/security.test.mjs" [ref=e167]
          - button "+ desktop/tsconfig.json" [ref=e168] [cursor=pointer]:
            - generic "added" [ref=e169]: +
            - generic "desktop/tsconfig.json" [ref=e170]
          - button "+ dev/luna.py" [ref=e171] [cursor=pointer]:
            - generic "added" [ref=e172]: +
            - generic "dev/luna.py" [ref=e173]
          - button "M dev/plan.json" [ref=e174] [cursor=pointer]:
            - generic "modified" [ref=e175]: M
            - generic "dev/plan.json" [ref=e176]
          - button "+ dev/test_luna.py" [ref=e177] [cursor=pointer]:
            - generic "added" [ref=e178]: +
            - generic "dev/test_luna.py" [ref=e179]
          - button "+ dev/test_specs.py" [ref=e180] [cursor=pointer]:
            - generic "added" [ref=e181]: +
            - generic "dev/test_specs.py" [ref=e182]
          - button "+ docs/ARCHITECTURE.md" [ref=e183] [cursor=pointer]:
            - generic "added" [ref=e184]: +
            - generic "docs/ARCHITECTURE.md" [ref=e185]
          - button "M docs/ART_DIRECTION.md" [ref=e186] [cursor=pointer]:
            - generic "modified" [ref=e187]: M
            - generic "docs/ART_DIRECTION.md" [ref=e188]
          - button "+ docs/ASSET_BINDING.md" [ref=e189] [cursor=pointer]:
            - generic "added" [ref=e190]: +
            - generic "docs/ASSET_BINDING.md" [ref=e191]
          - button "+ docs/COMPUTER_UI.md" [ref=e192] [cursor=pointer]:
            - generic "added" [ref=e193]: +
            - generic "docs/COMPUTER_UI.md" [ref=e194]
          - button "+ docs/EXECUTION.md" [ref=e195] [cursor=pointer]:
            - generic "added" [ref=e196]: +
            - generic "docs/EXECUTION.md" [ref=e197]
          - button "+ docs/FEATURE_MATRIX.md" [ref=e198] [cursor=pointer]:
            - generic "added" [ref=e199]: +
            - generic "docs/FEATURE_MATRIX.md" [ref=e200]
          - button "+ docs/MVP_ACCEPTANCE.md" [ref=e201] [cursor=pointer]:
            - generic "added" [ref=e202]: +
            - generic "docs/MVP_ACCEPTANCE.md" [ref=e203]
          - button "M docs/PARALLEL_PLAN.md" [ref=e204] [cursor=pointer]:
            - generic "modified" [ref=e205]: M
            - generic "docs/PARALLEL_PLAN.md" [ref=e206]
          - button "M docs/RESEARCH.md" [ref=e207] [cursor=pointer]:
            - generic "modified" [ref=e208]: M
            - generic "docs/RESEARCH.md" [ref=e209]
          - button "+ docs/RUN_EVALS.md" [ref=e210] [cursor=pointer]:
            - generic "added" [ref=e211]: +
            - generic "docs/RUN_EVALS.md" [ref=e212]
          - button "M docs/SETUP_VERIFICATION.md" [ref=e213] [cursor=pointer]:
            - generic "modified" [ref=e214]: M
            - generic "docs/SETUP_VERIFICATION.md" [ref=e215]
          - button "M docs/START_HERE.md" [ref=e216] [cursor=pointer]:
            - generic "modified" [ref=e217]: M
            - generic "docs/START_HERE.md" [ref=e218]
          - button "M docs/VALIDATION.md" [ref=e219] [cursor=pointer]:
            - generic "modified" [ref=e220]: M
            - generic "docs/VALIDATION.md" [ref=e221]
          - button "+ docs/archive/SPEC-0.2.md" [ref=e222] [cursor=pointer]:
            - generic "added" [ref=e223]: +
            - generic "docs/archive/SPEC-0.2.md" [ref=e224]
          - button "M docs/goals/A-runtime.md" [ref=e225] [cursor=pointer]:
            - generic "modified" [ref=e226]: M
            - generic "docs/goals/A-runtime.md" [ref=e227]
          - button "M docs/goals/B-tools.md" [ref=e228] [cursor=pointer]:
            - generic "modified" [ref=e229]: M
            - generic "docs/goals/B-tools.md" [ref=e230]
          - button "+ docs/goals/C-desktop.md" [ref=e231] [cursor=pointer]:
            - generic "added" [ref=e232]: +
            - generic "docs/goals/C-desktop.md" [ref=e233]
          - button "M docs/goals/C-unity.md" [ref=e234] [cursor=pointer]:
            - generic "modified" [ref=e235]: M
            - generic "docs/goals/C-unity.md" [ref=e236]
          - button "M docs/goals/D-workshops.md" [ref=e237] [cursor=pointer]:
            - generic "modified" [ref=e238]: M
            - generic "docs/goals/D-workshops.md" [ref=e239]
          - button "M docs/goals/I1-integration.md" [ref=e240] [cursor=pointer]:
            - generic "modified" [ref=e241]: M
            - generic "docs/goals/I1-integration.md" [ref=e242]
          - button "+ evidence/A/A1-final-review.json" [ref=e243] [cursor=pointer]:
            - generic "added" [ref=e244]: +
            - generic "evidence/A/A1-final-review.json" [ref=e245]
          - button "+ evidence/A/A1-review-2.json" [ref=e246] [cursor=pointer]:
            - generic "added" [ref=e247]: +
            - generic "evidence/A/A1-review-2.json" [ref=e248]
          - button "+ evidence/A/A1-review.json" [ref=e249] [cursor=pointer]:
            - generic "added" [ref=e250]: +
            - generic "evidence/A/A1-review.json" [ref=e251]
          - button "+ evidence/A/A1.json" [ref=e252] [cursor=pointer]:
            - generic "added" [ref=e253]: +
            - generic "evidence/A/A1.json" [ref=e254]
          - button "+ evidence/A/A2-repair-review.json" [ref=e255] [cursor=pointer]:
            - generic "added" [ref=e256]: +
            - generic "evidence/A/A2-repair-review.json" [ref=e257]
          - button "+ evidence/A/A2-review.json" [ref=e258] [cursor=pointer]:
            - generic "added" [ref=e259]: +
            - generic "evidence/A/A2-review.json" [ref=e260]
          - button "+ evidence/A/A2.json" [ref=e261] [cursor=pointer]:
            - generic "added" [ref=e262]: +
            - generic "evidence/A/A2.json" [ref=e263]
          - button "+ evidence/A/A3-repair-review.json" [ref=e264] [cursor=pointer]:
            - generic "added" [ref=e265]: +
            - generic "evidence/A/A3-repair-review.json" [ref=e266]
          - button "+ evidence/A/A3-review.json" [ref=e267] [cursor=pointer]:
            - generic "added" [ref=e268]: +
            - generic "evidence/A/A3-review.json" [ref=e269]
          - button "+ evidence/A/A3.json" [ref=e270] [cursor=pointer]:
            - generic "added" [ref=e271]: +
            - generic "evidence/A/A3.json" [ref=e272]
          - button "+ evidence/B/B1-repair-review.json" [ref=e273] [cursor=pointer]:
            - generic "added" [ref=e274]: +
            - generic "evidence/B/B1-repair-review.json" [ref=e275]
          - button "+ evidence/B/B1-review.json" [ref=e276] [cursor=pointer]:
            - generic "added" [ref=e277]: +
            - generic "evidence/B/B1-review.json" [ref=e278]
          - button "+ evidence/B/B1.json" [ref=e279] [cursor=pointer]:
            - generic "added" [ref=e280]: +
            - generic "evidence/B/B1.json" [ref=e281]
          - button "+ evidence/B/B2-readiness.json" [ref=e282] [cursor=pointer]:
            - generic "added" [ref=e283]: +
            - generic "evidence/B/B2-readiness.json" [ref=e284]
          - button "+ evidence/B/B2-repair-review.json" [ref=e285] [cursor=pointer]:
            - generic "added" [ref=e286]: +
            - generic "evidence/B/B2-repair-review.json" [ref=e287]
          - button "+ evidence/B/B2-review.json" [ref=e288] [cursor=pointer]:
            - generic "added" [ref=e289]: +
            - generic "evidence/B/B2-review.json" [ref=e290]
          - button "+ evidence/B/source-filter-repair.json" [ref=e291] [cursor=pointer]:
            - generic "added" [ref=e292]: +
            - generic "evidence/B/source-filter-repair.json" [ref=e293]
          - button "+ evidence/B/source-filter-review.json" [ref=e294] [cursor=pointer]:
            - generic "added" [ref=e295]: +
            - generic "evidence/B/source-filter-review.json" [ref=e296]
          - button "+ evidence/C/final-desktop-review.json" [ref=e297] [cursor=pointer]:
            - generic "added" [ref=e298]: +
            - generic "evidence/C/final-desktop-review.json" [ref=e299]
          - button "+ evidence/C/native-smoke-repair-review.json" [ref=e300] [cursor=pointer]:
            - generic "added" [ref=e301]: +
            - generic "evidence/C/native-smoke-repair-review.json" [ref=e302]
          - button "+ evidence/C/runtime-bridge-repair-review.json" [ref=e303] [cursor=pointer]:
            - generic "added" [ref=e304]: +
            - generic "evidence/C/runtime-bridge-repair-review.json" [ref=e305]
          - button "+ evidence/C/runtime-bridge-review.json" [ref=e306] [cursor=pointer]:
            - generic "added" [ref=e307]: +
            - generic "evidence/C/runtime-bridge-review.json" [ref=e308]
          - button "+ evidence/D/D1-previous-20261014t015727796417z.json" [ref=e309] [cursor=pointer]:
            - generic "added" [ref=e310]: +
            - generic "evidence/D/D1-previous-20261014t015727796417z.json" [ref=e311]
          - button "+ evidence/D/D1-previous-20261014t021328344314z.json" [ref=e312] [cursor=pointer]:
            - generic "added" [ref=e313]: +
            - generic "evidence/D/D1-previous-20261014t021328344314z.json" [ref=e314]
          - button "+ evidence/D/D1-previous-20261014t034618559898z.json" [ref=e315] [cursor=pointer]:
            - generic "added" [ref=e316]: +
            - generic "evidence/D/D1-previous-20261014t034618559898z.json" [ref=e317]
          - button "+ evidence/D/D1-review.json" [ref=e318] [cursor=pointer]:
            - generic "added" [ref=e319]: +
            - generic "evidence/D/D1-review.json" [ref=e320]
          - button "+ evidence/D/D1.json" [ref=e321] [cursor=pointer]:
            - generic "added" [ref=e322]: +
            - generic "evidence/D/D1.json" [ref=e323]
          - button "+ evidence/D/harness-lock-adjustment.json" [ref=e324] [cursor=pointer]:
            - generic "added" [ref=e325]: +
            - generic "evidence/D/harness-lock-adjustment.json" [ref=e326]
          - button "+ evidence/D/inputs/bad-manifest-20261014t015727796417z.json" [ref=e327] [cursor=pointer]:
            - generic "added" [ref=e328]: +
            - generic "evidence/D/inputs/bad-manifest-20261014t015727796417z.json" [ref=e329]
          - button "+ evidence/D/inputs/bad-manifest-20261014t021328344314z.json" [ref=e330] [cursor=pointer]:
            - generic "added" [ref=e331]: +
            - generic "evidence/D/inputs/bad-manifest-20261014t021328344314z.json" [ref=e332]
          - button "+ evidence/D/inputs/bad-manifest-20261014t034618559898z.json" [ref=e333] [cursor=pointer]:
            - generic "added" [ref=e334]: +
            - generic "evidence/D/inputs/bad-manifest-20261014t034618559898z.json" [ref=e335]
          - button "+ evidence/D/inputs/bad-manifest.json" [ref=e336] [cursor=pointer]:
            - generic "added" [ref=e337]: +
            - generic "evidence/D/inputs/bad-manifest.json" [ref=e338]
          - button "+ evidence/D/inputs/known-good-manifest-20261014t015727796417z.json" [ref=e339] [cursor=pointer]:
            - generic "added" [ref=e340]: +
            - generic "evidence/D/inputs/known-good-manifest-20261014t015727796417z.json" [ref=e341]
          - button "+ evidence/D/inputs/known-good-manifest-20261014t021328344314z.json" [ref=e342] [cursor=pointer]:
            - generic "added" [ref=e343]: +
            - generic "evidence/D/inputs/known-good-manifest-20261014t021328344314z.json" [ref=e344]
          - button "+ evidence/D/inputs/known-good-manifest-20261014t034618559898z.json" [ref=e345] [cursor=pointer]:
            - generic "added" [ref=e346]: +
            - generic "evidence/D/inputs/known-good-manifest-20261014t034618559898z.json" [ref=e347]
          - button "+ evidence/D/inputs/known-good-manifest.json" [ref=e348] [cursor=pointer]:
            - generic "added" [ref=e349]: +
            - generic "evidence/D/inputs/known-good-manifest.json" [ref=e350]
          - button "+ evidence/D/outputs/check-d1-bad-20261014t015727796417z-32a04073/after.png binary" [ref=e351] [cursor=pointer]:
            - generic "added" [ref=e352]: +
            - generic "evidence/D/outputs/check-d1-bad-20261014t015727796417z-32a04073/after.png" [ref=e353]
            - generic [ref=e354]: binary
          - button "+ evidence/D/outputs/check-d1-bad-20261014t015727796417z-32a04073/before.png binary" [ref=e355] [cursor=pointer]:
            - generic "added" [ref=e356]: +
            - generic "evidence/D/outputs/check-d1-bad-20261014t015727796417z-32a04073/before.png" [ref=e357]
            - generic [ref=e358]: binary
          - button "+ evidence/D/outputs/check-d1-bad-20261014t015727796417z-32a04073/check-report.json" [ref=e359] [cursor=pointer]:
            - generic "added" [ref=e360]: +
            - generic "evidence/D/outputs/check-d1-bad-20261014t015727796417z-32a04073/check-report.json" [ref=e361]
          - button "+ evidence/D/outputs/check-d1-bad-20261014t021328344314z-32a04073/after.png binary" [ref=e362] [cursor=pointer]:
            - generic "added" [ref=e363]: +
            - generic "evidence/D/outputs/check-d1-bad-20261014t021328344314z-32a04073/after.png" [ref=e364]
            - generic [ref=e365]: binary
          - button "+ evidence/D/outputs/check-d1-bad-20261014t021328344314z-32a04073/before.png binary" [ref=e366] [cursor=pointer]:
            - generic "added" [ref=e367]: +
            - generic "evidence/D/outputs/check-d1-bad-20261014t021328344314z-32a04073/before.png" [ref=e368]
            - generic [ref=e369]: binary
          - button "+ evidence/D/outputs/check-d1-bad-20261014t021328344314z-32a04073/check-report.json" [ref=e370] [cursor=pointer]:
            - generic "added" [ref=e371]: +
            - generic "evidence/D/outputs/check-d1-bad-20261014t021328344314z-32a04073/check-report.json" [ref=e372]
          - button "+ evidence/D/outputs/check-d1-bad-20261014t034618559898z-32a04073/after.png binary" [ref=e373] [cursor=pointer]:
            - generic "added" [ref=e374]: +
            - generic "evidence/D/outputs/check-d1-bad-20261014t034618559898z-32a04073/after.png" [ref=e375]
            - generic [ref=e376]: binary
          - button "+ evidence/D/outputs/check-d1-bad-20261014t034618559898z-32a04073/before.png binary" [ref=e377] [cursor=pointer]:
            - generic "added" [ref=e378]: +
            - generic "evidence/D/outputs/check-d1-bad-20261014t034618559898z-32a04073/before.png" [ref=e379]
            - generic [ref=e380]: binary
          - button "+ evidence/D/outputs/check-d1-bad-20261014t034618559898z-32a04073/check-report.json" [ref=e381] [cursor=pointer]:
            - generic "added" [ref=e382]: +
            - generic "evidence/D/outputs/check-d1-bad-20261014t034618559898z-32a04073/check-report.json" [ref=e383]
          - button "+ evidence/D/outputs/check-d1-bad-32a04073/after.png binary" [ref=e384] [cursor=pointer]:
            - generic "added" [ref=e385]: +
            - generic "evidence/D/outputs/check-d1-bad-32a04073/after.png" [ref=e386]
            - generic [ref=e387]: binary
          - button "+ evidence/D/outputs/check-d1-bad-32a04073/before.png binary" [ref=e388] [cursor=pointer]:
            - generic "added" [ref=e389]: +
            - generic "evidence/D/outputs/check-d1-bad-32a04073/before.png" [ref=e390]
            - generic [ref=e391]: binary
          - button "+ evidence/D/outputs/check-d1-bad-32a04073/check-report.json" [ref=e392] [cursor=pointer]:
            - generic "added" [ref=e393]: +
            - generic "evidence/D/outputs/check-d1-bad-32a04073/check-report.json" [ref=e394]
          - button "+ evidence/D/outputs/check-d1-known-good-20261014t015727796417z-430a53d1/after.png binary" [ref=e395] [cursor=pointer]:
            - generic "added" [ref=e396]: +
            - generic "evidence/D/outputs/check-d1-known-good-20261014t015727796417z-430a53d1/after.png" [ref=e397]
            - generic [ref=e398]: binary
          - button "+ evidence/D/outputs/check-d1-known-good-20261014t015727796417z-430a53d1/before.png binary" [ref=e399] [cursor=pointer]:
            - generic "added" [ref=e400]: +
            - generic "evidence/D/outputs/check-d1-known-good-20261014t015727796417z-430a53d1/before.png" [ref=e401]
            - generic [ref=e402]: binary
          - button "+ evidence/D/outputs/check-d1-known-good-20261014t015727796417z-430a53d1/check-report.json" [ref=e403] [cursor=pointer]:
            - generic "added" [ref=e404]: +
            - generic "evidence/D/outputs/check-d1-known-good-20261014t015727796417z-430a53d1/check-report.json" [ref=e405]
          - button "+ evidence/D/outputs/check-d1-known-good-20261014t021328344314z-430a53d1/after.png binary" [ref=e406] [cursor=pointer]:
            - generic "added" [ref=e407]: +
            - generic "evidence/D/outputs/check-d1-known-good-20261014t021328344314z-430a53d1/after.png" [ref=e408]
            - generic [ref=e409]: binary
          - button "+ evidence/D/outputs/check-d1-known-good-20261014t021328344314z-430a53d1/before.png binary" [ref=e410] [cursor=pointer]:
            - generic "added" [ref=e411]: +
            - generic "evidence/D/outputs/check-d1-known-good-20261014t021328344314z-430a53d1/before.png" [ref=e412]
            - generic [ref=e413]: binary
          - button "+ evidence/D/outputs/check-d1-known-good-20261014t021328344314z-430a53d1/check-report.json" [ref=e414] [cursor=pointer]:
            - generic "added" [ref=e415]: +
            - generic "evidence/D/outputs/check-d1-known-good-20261014t021328344314z-430a53d1/check-report.json" [ref=e416]
          - button "+ evidence/D/outputs/check-d1-known-good-20261014t034618559898z-430a53d1/after.png binary" [ref=e417] [cursor=pointer]:
            - generic "added" [ref=e418]: +
            - generic "evidence/D/outputs/check-d1-known-good-20261014t034618559898z-430a53d1/after.png" [ref=e419]
            - generic [ref=e420]: binary
          - button "+ evidence/D/outputs/check-d1-known-good-20261014t034618559898z-430a53d1/before.png binary" [ref=e421] [cursor=pointer]:
            - generic "added" [ref=e422]: +
            - generic "evidence/D/outputs/check-d1-known-good-20261014t034618559898z-430a53d1/before.png" [ref=e423]
            - generic [ref=e424]: binary
          - button "+ evidence/D/outputs/check-d1-known-good-20261014t034618559898z-430a53d1/check-report.json" [ref=e425] [cursor=pointer]:
            - generic "added" [ref=e426]: +
            - generic "evidence/D/outputs/check-d1-known-good-20261014t034618559898z-430a53d1/check-report.json" [ref=e427]
          - button "+ evidence/D/outputs/check-d1-known-good-430a53d1/after.png binary" [ref=e428] [cursor=pointer]:
            - generic "added" [ref=e429]: +
            - generic "evidence/D/outputs/check-d1-known-good-430a53d1/after.png" [ref=e430]
            - generic [ref=e431]: binary
          - button "+ evidence/D/outputs/check-d1-known-good-430a53d1/before.png binary" [ref=e432] [cursor=pointer]:
            - generic "added" [ref=e433]: +
            - generic "evidence/D/outputs/check-d1-known-good-430a53d1/before.png" [ref=e434]
            - generic [ref=e435]: binary
          - button "+ evidence/D/outputs/check-d1-known-good-430a53d1/check-report.json" [ref=e436] [cursor=pointer]:
            - generic "added" [ref=e437]: +
            - generic "evidence/D/outputs/check-d1-known-good-430a53d1/check-report.json" [ref=e438]
          - button "+ evidence/desktop/README.md" [ref=e439] [cursor=pointer]:
            - generic "added" [ref=e440]: +
            - generic "evidence/desktop/README.md" [ref=e441]
          - button "+ evidence/desktop/accessibility.json" [ref=e442] [cursor=pointer]:
            - generic "added" [ref=e443]: +
            - generic "evidence/desktop/accessibility.json" [ref=e444]
          - button "+ evidence/desktop/asset-transfer.json" [ref=e445] [cursor=pointer]:
            - generic "added" [ref=e446]: +
            - generic "evidence/desktop/asset-transfer.json" [ref=e447]
          - button "+ evidence/desktop/electron-smoke.json" [ref=e448] [cursor=pointer]:
            - generic "added" [ref=e449]: +
            - generic "evidence/desktop/electron-smoke.json" [ref=e450]
          - button "+ evidence/desktop/expanded-diff.png binary" [ref=e451] [cursor=pointer]:
            - generic "added" [ref=e452]: +
            - generic "evidence/desktop/expanded-diff.png" [ref=e453]
            - generic [ref=e454]: binary
          - button "+ evidence/desktop/git-diff.png binary" [ref=e455] [cursor=pointer]:
            - generic "added" [ref=e456]: +
            - generic "evidence/desktop/git-diff.png" [ref=e457]
            - generic [ref=e458]: binary
          - button "+ evidence/desktop/job-390.png binary" [ref=e459] [cursor=pointer]:
            - generic "added" [ref=e460]: +
            - generic "evidence/desktop/job-390.png" [ref=e461]
            - generic [ref=e462]: binary
          - button "+ evidence/desktop/job-960.png binary" [ref=e463] [cursor=pointer]:
            - generic "added" [ref=e464]: +
            - generic "evidence/desktop/job-960.png" [ref=e465]
            - generic [ref=e466]: binary
          - button "+ evidence/desktop/job-accessibility.json" [ref=e467] [cursor=pointer]:
            - generic "added" [ref=e468]: +
            - generic "evidence/desktop/job-accessibility.json" [ref=e469]
          - button "+ evidence/desktop/job-browser.json" [ref=e470] [cursor=pointer]:
            - generic "added" [ref=e471]: +
            - generic "evidence/desktop/job-browser.json" [ref=e472]
          - button "+ evidence/desktop/job-check-report.png binary" [ref=e473] [cursor=pointer]:
            - generic "added" [ref=e474]: +
            - generic "evidence/desktop/job-check-report.png" [ref=e475]
            - generic [ref=e476]: binary
          - button "+ evidence/desktop/job-diff.png binary" [ref=e477] [cursor=pointer]:
            - generic "added" [ref=e478]: +
            - generic "evidence/desktop/job-diff.png" [ref=e479]
            - generic [ref=e480]: binary
          - button "+ evidence/desktop/job-queued.png binary" [ref=e481] [cursor=pointer]:
            - generic "added" [ref=e482]: +
            - generic "evidence/desktop/job-queued.png" [ref=e483]
            - generic [ref=e484]: binary
          - button "+ evidence/desktop/job-readiness.png binary" [ref=e485] [cursor=pointer]:
            - generic "added" [ref=e486]: +
            - generic "evidence/desktop/job-readiness.png" [ref=e487]
            - generic [ref=e488]: binary
          - button "+ evidence/desktop/job-responsive-accessibility.json" [ref=e489] [cursor=pointer]:
            - generic "added" [ref=e490]: +
            - generic "evidence/desktop/job-responsive-accessibility.json" [ref=e491]
          - button "+ evidence/desktop/job-result.png binary" [ref=e492] [cursor=pointer]:
            - generic "added" [ref=e493]: +
            - generic "evidence/desktop/job-result.png" [ref=e494]
            - generic [ref=e495]: binary
          - button "+ evidence/desktop/sanitizer-bundle.json" [ref=e496] [cursor=pointer]:
            - generic "added" [ref=e497]: +
            - generic "evidence/desktop/sanitizer-bundle.json" [ref=e498]
          - button "+ evidence/desktop/security-audit-all.json" [ref=e499] [cursor=pointer]:
            - generic "added" [ref=e500]: +
            - generic "evidence/desktop/security-audit-all.json" [ref=e501]
          - button "+ evidence/desktop/security-audit.json" [ref=e502] [cursor=pointer]:
            - generic "added" [ref=e503]: +
            - generic "evidence/desktop/security-audit.json" [ref=e504]
          - button "+ evidence/desktop/setup-desktop.png binary" [ref=e505] [cursor=pointer]:
            - generic "added" [ref=e506]: +
            - generic "evidence/desktop/setup-desktop.png" [ref=e507]
            - generic [ref=e508]: binary
          - button "+ evidence/desktop/verification.json" [ref=e509] [cursor=pointer]:
            - generic "added" [ref=e510]: +
            - generic "evidence/desktop/verification.json" [ref=e511]
          - button "+ evidence/desktop/viewer-390.png binary" [ref=e512] [cursor=pointer]:
            - generic "added" [ref=e513]: +
            - generic "evidence/desktop/viewer-390.png" [ref=e514]
            - generic [ref=e515]: binary
          - button "+ evidence/desktop/viewer-960.png binary" [ref=e516] [cursor=pointer]:
            - generic "added" [ref=e517]: +
            - generic "evidence/desktop/viewer-960.png" [ref=e518]
            - generic [ref=e519]: binary
          - button "M journals/A.md" [ref=e520] [cursor=pointer]:
            - generic "modified" [ref=e521]: M
            - generic "journals/A.md" [ref=e522]
          - button "M journals/B.md" [ref=e523] [cursor=pointer]:
            - generic "modified" [ref=e524]: M
            - generic "journals/B.md" [ref=e525]
          - button "M journals/C.md" [ref=e526] [cursor=pointer]:
            - generic "modified" [ref=e527]: M
            - generic "journals/C.md" [ref=e528]
          - button "M journals/D.md" [ref=e529] [cursor=pointer]:
            - generic "modified" [ref=e530]: M
            - generic "journals/D.md" [ref=e531]
          - button "+ services/runtime/README.md" [ref=e532] [cursor=pointer]:
            - generic "added" [ref=e533]: +
            - generic "services/runtime/README.md" [ref=e534]
          - button "+ services/runtime/__init__.py" [ref=e535] [cursor=pointer]:
            - generic "added" [ref=e536]: +
            - generic "services/runtime/__init__.py" [ref=e537]
          - button "+ services/runtime/adapters.py" [ref=e538] [cursor=pointer]:
            - generic "added" [ref=e539]: +
            - generic "services/runtime/adapters.py" [ref=e540]
          - button "+ services/runtime/api.py" [ref=e541] [cursor=pointer]:
            - generic "added" [ref=e542]: +
            - generic "services/runtime/api.py" [ref=e543]
          - button "+ services/runtime/artifacts.py" [ref=e544] [cursor=pointer]:
            - generic "added" [ref=e545]: +
            - generic "services/runtime/artifacts.py" [ref=e546]
          - button "+ services/runtime/main.py" [ref=e547] [cursor=pointer]:
            - generic "added" [ref=e548]: +
            - generic "services/runtime/main.py" [ref=e549]
          - button "+ services/runtime/migrations/001_initial.sql" [ref=e550] [cursor=pointer]:
            - generic "added" [ref=e551]: +
            - generic "services/runtime/migrations/001_initial.sql" [ref=e552]
          - button "+ services/runtime/migrations/002_attempt_worker.sql" [ref=e553] [cursor=pointer]:
            - generic "added" [ref=e554]: +
            - generic "services/runtime/migrations/002_attempt_worker.sql" [ref=e555]
          - button "+ services/runtime/migrations/003_codex_lifecycle.sql" [ref=e556] [cursor=pointer]:
            - generic "added" [ref=e557]: +
            - generic "services/runtime/migrations/003_codex_lifecycle.sql" [ref=e558]
          - button "+ services/runtime/models.py" [ref=e559] [cursor=pointer]:
            - generic "added" [ref=e560]: +
            - generic "services/runtime/models.py" [ref=e561]
          - button "+ services/runtime/policy.py" [ref=e562] [cursor=pointer]:
            - generic "added" [ref=e563]: +
            - generic "services/runtime/policy.py" [ref=e564]
          - button "+ services/runtime/requirements.lock" [ref=e565] [cursor=pointer]:
            - generic "added" [ref=e566]: +
            - generic "services/runtime/requirements.lock" [ref=e567]
          - button "+ services/runtime/scheduler.py" [ref=e568] [cursor=pointer]:
            - generic "added" [ref=e569]: +
            - generic "services/runtime/scheduler.py" [ref=e570]
          - button "+ services/runtime/store.py" [ref=e571] [cursor=pointer]:
            - generic "added" [ref=e572]: +
            - generic "services/runtime/store.py" [ref=e573]
          - button "+ services/runtime/tests/test_adapters.py" [ref=e574] [cursor=pointer]:
            - generic "added" [ref=e575]: +
            - generic "services/runtime/tests/test_adapters.py" [ref=e576]
          - button "+ services/runtime/tests/test_api.py" [ref=e577] [cursor=pointer]:
            - generic "added" [ref=e578]: +
            - generic "services/runtime/tests/test_api.py" [ref=e579]
          - button "+ services/runtime/tests/test_codex_lifecycle.py" [ref=e580] [cursor=pointer]:
            - generic "added" [ref=e581]: +
            - generic "services/runtime/tests/test_codex_lifecycle.py" [ref=e582]
          - button "+ services/runtime/tests/test_concurrency.py" [ref=e583] [cursor=pointer]:
            - generic "added" [ref=e584]: +
            - generic "services/runtime/tests/test_concurrency.py" [ref=e585]
          - button "+ services/runtime/tests/test_main.py" [ref=e586] [cursor=pointer]:
            - generic "added" [ref=e587]: +
            - generic "services/runtime/tests/test_main.py" [ref=e588]
          - button "+ services/runtime/tests/test_policy.py" [ref=e589] [cursor=pointer]:
            - generic "added" [ref=e590]: +
            - generic "services/runtime/tests/test_policy.py" [ref=e591]
          - button "+ services/runtime/tests/test_scheduler_pipeline.py" [ref=e592] [cursor=pointer]:
            - generic "added" [ref=e593]: +
            - generic "services/runtime/tests/test_scheduler_pipeline.py" [ref=e594]
          - button "+ services/runtime/tests/test_storage.py" [ref=e595] [cursor=pointer]:
            - generic "added" [ref=e596]: +
            - generic "services/runtime/tests/test_storage.py" [ref=e597]
          - button "+ services/runtime/tests/test_support.py" [ref=e598] [cursor=pointer]:
            - generic "added" [ref=e599]: +
            - generic "services/runtime/tests/test_support.py" [ref=e600]
          - button "+ services/tools/__init__.py" [ref=e601] [cursor=pointer]:
            - generic "added" [ref=e602]: +
            - generic "services/tools/__init__.py" [ref=e603]
          - button "+ services/tools/artifact_capture.py" [ref=e604] [cursor=pointer]:
            - generic "added" [ref=e605]: +
            - generic "services/tools/artifact_capture.py" [ref=e606]
          - button "+ services/tools/codex_bridge.py" [ref=e607] [cursor=pointer]:
            - generic "added" [ref=e608]: +
            - generic "services/tools/codex_bridge.py" [ref=e609]
          - button "+ services/tools/git_ops.py" [ref=e610] [cursor=pointer]:
            - generic "added" [ref=e611]: +
            - generic "services/tools/git_ops.py" [ref=e612]
          - button "+ services/tools/main.py" [ref=e613] [cursor=pointer]:
            - generic "added" [ref=e614]: +
            - generic "services/tools/main.py" [ref=e615]
          - button "+ services/tools/protocol.py" [ref=e616] [cursor=pointer]:
            - generic "added" [ref=e617]: +
            - generic "services/tools/protocol.py" [ref=e618]
          - button "+ services/tools/tests/test_codex_bridge.py" [ref=e619] [cursor=pointer]:
            - generic "added" [ref=e620]: +
            - generic "services/tools/tests/test_codex_bridge.py" [ref=e621]
          - button "+ services/tools/tests/test_git_artifacts.py" [ref=e622] [cursor=pointer]:
            - generic "added" [ref=e623]: +
            - generic "services/tools/tests/test_git_artifacts.py" [ref=e624]
          - button "+ services/tools/tests/test_protocol.py" [ref=e625] [cursor=pointer]:
            - generic "added" [ref=e626]: +
            - generic "services/tools/tests/test_protocol.py" [ref=e627]
          - button "+ services/workshops/__init__.py" [ref=e628] [cursor=pointer]:
            - generic "added" [ref=e629]: +
            - generic "services/workshops/__init__.py" [ref=e630]
          - button "+ services/workshops/browser_checks.py" [ref=e631] [cursor=pointer]:
            - generic "added" [ref=e632]: +
            - generic "services/workshops/browser_checks.py" [ref=e633]
          - button "+ services/workshops/checks.py" [ref=e634] [cursor=pointer]:
            - generic "added" [ref=e635]: +
            - generic "services/workshops/checks.py" [ref=e636]
          - button "+ services/workshops/identity.py" [ref=e637] [cursor=pointer]:
            - generic "added" [ref=e638]: +
            - generic "services/workshops/identity.py" [ref=e639]
          - button "+ services/workshops/main.py" [ref=e640] [cursor=pointer]:
            - generic "added" [ref=e641]: +
            - generic "services/workshops/main.py" [ref=e642]
          - button "+ services/workshops/reports.py" [ref=e643] [cursor=pointer]:
            - generic "added" [ref=e644]: +
            - generic "services/workshops/reports.py" [ref=e645]
          - button "+ services/workshops/requirements.lock" [ref=e646] [cursor=pointer]:
            - generic "added" [ref=e647]: +
            - generic "services/workshops/requirements.lock" [ref=e648]
          - button "+ services/workshops/tests/__init__.py" [ref=e649] [cursor=pointer]:
            - generic "added" [ref=e650]: +
            - generic "services/workshops/tests/__init__.py" [ref=e651]
          - button "+ services/workshops/tests/helpers.py" [ref=e652] [cursor=pointer]:
            - generic "added" [ref=e653]: +
            - generic "services/workshops/tests/helpers.py" [ref=e654]
          - button "+ services/workshops/tests/test_identity.py" [ref=e655] [cursor=pointer]:
            - generic "added" [ref=e656]: +
            - generic "services/workshops/tests/test_identity.py" [ref=e657]
          - button "+ services/workshops/tests/test_protocol_browser.py" [ref=e658] [cursor=pointer]:
            - generic "added" [ref=e659]: +
            - generic "services/workshops/tests/test_protocol_browser.py" [ref=e660]
          - button "+ services/workshops/trust.lock.json" [ref=e661] [cursor=pointer]:
            - generic "added" [ref=e662]: +
            - generic "services/workshops/trust.lock.json" [ref=e663]
          - button "+ services/workshops/trusted_checks.json" [ref=e664] [cursor=pointer]:
            - generic "added" [ref=e665]: +
            - generic "services/workshops/trusted_checks.json" [ref=e666]
          - button "+ tests/e2e/run_d1.py" [ref=e667] [cursor=pointer]:
            - generic "added" [ref=e668]: +
            - generic "tests/e2e/run_d1.py" [ref=e669]
        - region "Selected file diff" [ref=e670]:
          - generic [ref=e671]:
            - text: .gitignore
            - generic [ref=e672]: Read-only
          - generic [ref=e674]:
            - code [ref=e676]:
              - generic [ref=e677]:
                - textbox "Original committed file, read-only"
                - textbox [aria-hidden] [ref=e678]
                - generic [aria-hidden] [ref=e680]:
                  - generic [ref=e681]: "1"
                  - generic [ref=e684]: "2"
                  - generic [ref=e686]: "3"
                  - generic [ref=e688]: "4"
                  - generic [ref=e690]: "5"
                  - generic [ref=e692]: "6"
                  - generic [ref=e694]: "7"
                  - generic [ref=e696]: "8"
                  - generic [ref=e698]: "9"
                  - generic [ref=e700]: "10"
                - generic [aria-hidden] [ref=e714]:
                  - generic [ref=e715]: "# Local development state and secrets"
                  - generic [ref=e717]: .sidequest/
                  - generic [ref=e719]: .env
                  - generic [ref=e721]: .env.*
                  - generic [ref=e723]: "!.env.example"
                  - generic [ref=e725]: "*.pem"
                  - generic [ref=e727]: "*.key"
                  - generic [ref=e729]: __pycache__/
                  - generic [ref=e731]: "*.py[cod]"
                  - generic [ref=e733]: .venv/
            - code [ref=e740]:
              - generic [ref=e741]:
                - textbox "Modified committed file, read-only" [ref=e742]
                - textbox [aria-hidden] [ref=e743]
                - generic [aria-hidden] [ref=e745]:
                  - generic [ref=e746]: "1"
                  - generic [ref=e749]: "2"
                  - generic [ref=e751]: "3"
                  - generic [ref=e753]: "4"
                  - generic [ref=e755]: "5"
                  - generic [ref=e757]: "6"
                  - generic [ref=e759]: "7"
                  - generic [ref=e761]: "8"
                  - generic [ref=e763]: "9"
                  - generic [ref=e765]: "10"
                - generic [aria-hidden] [ref=e779]:
                  - generic [ref=e780]: "# Local development state and secrets"
                  - generic [ref=e782]: .sidequest/
                  - generic [ref=e784]: .env
                  - generic [ref=e786]: .env.*
                  - generic [ref=e788]: "!.env.example"
                  - generic [ref=e790]: "*.pem"
                  - generic [ref=e792]: "*.key"
                  - generic [ref=e794]: __pycache__/
                  - generic [ref=e796]: "*.py[cod]"
                  - generic [ref=e798]: .venv/
      - generic [ref=e805]: Agent services are not connected in this desktop build.
    - generic [ref=e806]:
      - generic [ref=e808]: Original office
      - generic "Supplied reference poses are static artwork. No live coding session is attached to a figure." [ref=e810]: 26 staged figures · Sessions unconnected
      - generic [ref=e811]: Git read-only · 0 UI model calls
  - generic [ref=e812]:
    - alert
    - alert
```

# Test source

```ts
  1  | import {test,expect} from '@playwright/test';
  2  | import path from 'node:path';
  3  | import {writeFile} from 'node:fs/promises';
  4  | import AxeBuilder from '@axe-core/playwright';
  5  | const evidence=path.resolve('../evidence/desktop');
  6  | for(const width of [1440,390]) test(`provider settings and preserved work at ${width}px`,async({page})=>{
  7  |   const errors:string[]=[];page.on('pageerror',error=>errors.push(error.message));
  8  |   await page.setViewportSize({width,height:width===390?780:1000});
  9  |   await page.emulateMedia({reducedMotion:'reduce'});
  10 |   await page.goto('/');await expect(page.locator('.station-nav button[data-station-id="parent_019"]')).toBeEnabled();
  11 |   await expect(page.locator('.office-canvas canvas')).toBeVisible();
  12 | 
  13 |   await page.waitForTimeout(1000);
  14 |   
  15 |   await page.locator('.station-nav button[data-station-id="parent_019"]').click();
> 16 |   await expect(page.getByTestId('diff-editor')).toHaveCount(1);
     |                                                 ^ Error: expect(locator).toHaveCount(expected) failed
  17 |   await expect(page.getByRole('button',{name:'Expand',exact:true})).toBeVisible();
  18 | 
  19 |   await page.getByRole('button',{name:'Expand',exact:true}).click();
  20 |   await expect(page.getByRole('dialog',{name:'Computer work viewer'})).toBeVisible();
  21 | 
  22 |   const selected=await page.getByTestId('diff-editor').getAttribute('data-file-id');
  23 |   await page.getByRole('button',{name:'Settings',exact:true}).click();
  24 |   const settings=page.getByRole('dialog',{name:'Provider settings dialog'});
  25 |   await expect(settings).toBeVisible();await expect(settings.getByRole('heading',{name:/Codex$/})).toBeVisible();
  26 |   await expect(settings.getByLabel('Binary path')).toHaveValue(/codex/);
  27 |   await expect(settings.getByText('Authentication',{exact:true})).toBeVisible();
  28 |   await expect(settings.getByText('Service reachability',{exact:true})).toBeVisible();
  29 | 
  30 |   if(width===1440){
  31 |     await settings.getByRole('button',{name:/Claude/}).click();
  32 |     await expect(settings.getByRole('heading',{name:/Claude$/})).toBeVisible();
  33 |     await settings.getByRole('button',{name:/Codex/}).click();
  34 |   }else{
  35 |     await settings.locator('.provider-mobile-picker__button').click();
  36 |     await settings.getByRole('navigation',{name:'Choose provider'}).getByRole('button',{name:'Claude',exact:true}).click();
  37 |     await expect(settings.getByRole('heading',{name:/Claude$/})).toBeVisible();
  38 |     await settings.locator('.provider-mobile-picker__button').click();
  39 |     await settings.getByRole('navigation',{name:'Choose provider'}).getByRole('button',{name:'Codex',exact:true}).click();
  40 |   }
  41 |   await settings.getByRole('button',{name:'Refresh provider discovery'}).click();
  42 |   await expect(settings.getByRole('button',{name:'Refresh provider discovery'})).toBeEnabled();
  43 |   expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  44 |   await page.screenshot({path:path.join(evidence,`provider-settings${width===1440?'':'-390'}.png`)});
  45 |   await settings.getByRole('navigation',{name:'Settings view'}).getByRole('button',{name:'Usage',exact:true}).click();
  46 |   await expect(settings.getByText('No usage data reported',{exact:true})).toBeVisible();
  47 |   await settings.getByRole('group',{name:'Usage metric'}).getByRole('button',{name:'Tokens',exact:true}).click();
  48 |   await expect(settings.getByText('Processed tokens unavailable',{exact:true})).toBeVisible();
  49 |   await settings.getByRole('group',{name:'Usage breakdown'}).getByRole('button',{name:'Day',exact:true}).click();
  50 |   await expect(settings.getByText('No daily usage data reported',{exact:true})).toBeVisible();
  51 |   await page.screenshot({path:path.join(evidence,`provider-settings-analytics${width===1440?'':'-390'}.png`)});
  52 |   await settings.getByRole('group',{name:'Usage metric'}).getByRole('button',{name:'Limits',exact:true}).click();
  53 |   await expect(settings.getByText('— remaining',{exact:true})).toHaveCount(2);
  54 |   await expect(settings.getByText('Reset unknown',{exact:true})).toHaveCount(2);
  55 |   await page.screenshot({path:path.join(evidence,`provider-settings-limits${width===1440?'':'-390'}.png`)});
  56 |   const result=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze();
  57 |   await writeFile(path.join(evidence,`provider-accessibility-${width}.json`),JSON.stringify(result.violations,null,2));
  58 |   expect(result.violations.map(v=>({id:v.id,impact:v.impact}))).toEqual([]);
  59 |   const first=settings.locator('button:visible:not(:disabled),input:visible,select:visible,[tabindex="0"]:visible').first(),last=settings.locator('button:visible:not(:disabled),input:visible,select:visible,[tabindex="0"]:visible').last();
  60 |   await last.focus();await page.keyboard.press('Tab');await expect(first).toBeFocused();
  61 |   await page.keyboard.press('Escape');await expect(settings).toHaveCount(0);
  62 |   await expect(page.getByRole('dialog',{name:'Computer work viewer'})).toBeVisible();
  63 |   await expect(page.getByTestId('diff-editor')).toHaveAttribute('data-file-id',selected!);
  64 |   await page.keyboard.press('Escape');await expect(page.getByTestId('diff-editor')).toHaveCount(0);
  65 |   expect(errors).toEqual([]);
  66 | });
  67 | 
```