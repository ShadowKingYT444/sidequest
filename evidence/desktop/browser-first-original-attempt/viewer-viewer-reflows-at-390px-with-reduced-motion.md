# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: viewer.spec.ts >> viewer reflows at 390px with reduced motion
- Location: tests/browser/viewer.spec.ts:48:32

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
    7 × locator resolved to 0 elements
      - unexpected value "0"

```

# Page snapshot

```yaml
- generic [ref=e1]:
  - main [ref=e3]:
    - generic [ref=e4]:
      - generic [ref=e5]: sidequest
      - button "Settings" [ref=e6] [cursor=pointer]
      - button "Jobs" [ref=e7] [cursor=pointer]
      - button "Refresh Git" [ref=e8] [cursor=pointer]
    - region "Computer work viewer" [ref=e14]:
      - generic [ref=e15]:
        - generic [ref=e16]:
          - paragraph [ref=e17]: Computer 19 · Read-only
          - heading "sidequest" [level=2] [ref=e18]
        - generic [ref=e19]:
          - button "Expand" [active] [ref=e20] [cursor=pointer]
          - button "Return to office" [ref=e21] [cursor=pointer]: Office
      - generic [ref=e22]:
        - generic [ref=e23]: Git diff
        - generic "69bf06696a93c9f58eee2d088e84404d4f6563d6" [ref=e24]: 69bf0669 → 8a9fb11c
      - generic [ref=e25]:
        - navigation "Changed files" [ref=e26]:
          - button "M .gitignore" [pressed] [ref=e27] [cursor=pointer]:
            - generic "modified" [ref=e28]: M
            - generic ".gitignore" [ref=e29]
          - button "M AGENTS.md" [ref=e30] [cursor=pointer]:
            - generic "modified" [ref=e31]: M
            - generic "AGENTS.md" [ref=e32]
          - button "M README.md" [ref=e33] [cursor=pointer]:
            - generic "modified" [ref=e34]: M
            - generic "README.md" [ref=e35]
          - button "M SPEC.md" [ref=e36] [cursor=pointer]:
            - generic "modified" [ref=e37]: M
            - generic "SPEC.md" [ref=e38]
          - button "+ contracts/EXTENSIONS.md" [ref=e39] [cursor=pointer]:
            - generic "added" [ref=e40]: +
            - generic "contracts/EXTENSIONS.md" [ref=e41]
          - button "M contracts/PROTOCOL.md" [ref=e42] [cursor=pointer]:
            - generic "modified" [ref=e43]: M
            - generic "contracts/PROTOCOL.md" [ref=e44]
          - button "+ contracts/STORAGE.md" [ref=e45] [cursor=pointer]:
            - generic "added" [ref=e46]: +
            - generic "contracts/STORAGE.md" [ref=e47]
          - button "+ contracts/examples/computer.json" [ref=e48] [cursor=pointer]:
            - generic "added" [ref=e49]: +
            - generic "contracts/examples/computer.json" [ref=e50]
          - button "+ demo/README.md" [ref=e51] [cursor=pointer]:
            - generic "added" [ref=e52]: +
            - generic "demo/README.md" [ref=e53]
          - button "+ demo/club-site/README.md" [ref=e54] [cursor=pointer]:
            - generic "added" [ref=e55]: +
            - generic "demo/club-site/README.md" [ref=e56]
          - button "+ demo/club-site/bad/index.html" [ref=e57] [cursor=pointer]:
            - generic "added" [ref=e58]: +
            - generic "demo/club-site/bad/index.html" [ref=e59]
          - button "+ demo/club-site/bad/members/signup.html" [ref=e60] [cursor=pointer]:
            - generic "added" [ref=e61]: +
            - generic "demo/club-site/bad/members/signup.html" [ref=e62]
          - button "+ demo/club-site/known-good/index.html" [ref=e63] [cursor=pointer]:
            - generic "added" [ref=e64]: +
            - generic "demo/club-site/known-good/index.html" [ref=e65]
          - button "+ demo/club-site/known-good/members/welcome.html" [ref=e66] [cursor=pointer]:
            - generic "added" [ref=e67]: +
            - generic "demo/club-site/known-good/members/welcome.html" [ref=e68]
          - button "+ desktop/README.md" [ref=e69] [cursor=pointer]:
            - generic "added" [ref=e70]: +
            - generic "desktop/README.md" [ref=e71]
          - button "+ desktop/electron/git-reader.cjs" [ref=e72] [cursor=pointer]:
            - generic "added" [ref=e73]: +
            - generic "desktop/electron/git-reader.cjs" [ref=e74]
          - button "+ desktop/electron/main.cjs" [ref=e75] [cursor=pointer]:
            - generic "added" [ref=e76]: +
            - generic "desktop/electron/main.cjs" [ref=e77]
          - button "+ desktop/electron/preload.cjs" [ref=e78] [cursor=pointer]:
            - generic "added" [ref=e79]: +
            - generic "desktop/electron/preload.cjs" [ref=e80]
          - button "+ desktop/electron/runtime-client.cjs" [ref=e81] [cursor=pointer]:
            - generic "added" [ref=e82]: +
            - generic "desktop/electron/runtime-client.cjs" [ref=e83]
          - button "+ desktop/electron/security.cjs" [ref=e84] [cursor=pointer]:
            - generic "added" [ref=e85]: +
            - generic "desktop/electron/security.cjs" [ref=e86]
          - button "+ desktop/electron/static-server.cjs" [ref=e87] [cursor=pointer]:
            - generic "added" [ref=e88]: +
            - generic "desktop/electron/static-server.cjs" [ref=e89]
          - button "+ desktop/index.html" [ref=e90] [cursor=pointer]:
            - generic "added" [ref=e91]: +
            - generic "desktop/index.html" [ref=e92]
          - button "+ desktop/package-lock.json" [ref=e93] [cursor=pointer]:
            - generic "added" [ref=e94]: +
            - generic "desktop/package-lock.json" [ref=e95]
          - button "+ desktop/package.json" [ref=e96] [cursor=pointer]:
            - generic "added" [ref=e97]: +
            - generic "desktop/package.json" [ref=e98]
          - button "+ desktop/scripts/electron-smoke.mjs" [ref=e99] [cursor=pointer]:
            - generic "added" [ref=e100]: +
            - generic "desktop/scripts/electron-smoke.mjs" [ref=e101]
          - button "+ desktop/scripts/inspect-assets.mjs" [ref=e102] [cursor=pointer]:
            - generic "added" [ref=e103]: +
            - generic "desktop/scripts/inspect-assets.mjs" [ref=e104]
          - button "+ desktop/scripts/install-office.py" [ref=e105] [cursor=pointer]:
            - generic "added" [ref=e106]: +
            - generic "desktop/scripts/install-office.py" [ref=e107]
          - button "+ desktop/src/App.tsx" [ref=e108] [cursor=pointer]:
            - generic "added" [ref=e109]: +
            - generic "desktop/src/App.tsx" [ref=e110]
          - button "+ desktop/src/DiffEditor.tsx" [ref=e111] [cursor=pointer]:
            - generic "added" [ref=e112]: +
            - generic "desktop/src/DiffEditor.tsx" [ref=e113]
          - button "+ desktop/src/JobsBoard.tsx" [ref=e114] [cursor=pointer]:
            - generic "added" [ref=e115]: +
            - generic "desktop/src/JobsBoard.tsx" [ref=e116]
          - button "+ desktop/src/OfficeScene.tsx" [ref=e117] [cursor=pointer]:
            - generic "added" [ref=e118]: +
            - generic "desktop/src/OfficeScene.tsx" [ref=e119]
          - button "+ desktop/src/bridge.ts" [ref=e120] [cursor=pointer]:
            - generic "added" [ref=e121]: +
            - generic "desktop/src/bridge.ts" [ref=e122]
          - button "+ desktop/src/main.tsx" [ref=e123] [cursor=pointer]:
            - generic "added" [ref=e124]: +
            - generic "desktop/src/main.tsx" [ref=e125]
          - button "+ desktop/src/office-bindings.ts" [ref=e126] [cursor=pointer]:
            - generic "added" [ref=e127]: +
            - generic "desktop/src/office-bindings.ts" [ref=e128]
          - button "+ desktop/src/runtime-identity.ts" [ref=e129] [cursor=pointer]:
            - generic "added" [ref=e130]: +
            - generic "desktop/src/runtime-identity.ts" [ref=e131]
          - button "+ desktop/src/style.css" [ref=e132] [cursor=pointer]:
            - generic "added" [ref=e133]: +
            - generic "desktop/src/style.css" [ref=e134]
          - button "+ desktop/src/types.ts" [ref=e135] [cursor=pointer]:
            - generic "added" [ref=e136]: +
            - generic "desktop/src/types.ts" [ref=e137]
          - button "+ desktop/tests/assets.test.mjs" [ref=e138] [cursor=pointer]:
            - generic "added" [ref=e139]: +
            - generic "desktop/tests/assets.test.mjs" [ref=e140]
          - button "+ desktop/tests/bindings.test.mjs" [ref=e141] [cursor=pointer]:
            - generic "added" [ref=e142]: +
            - generic "desktop/tests/bindings.test.mjs" [ref=e143]
          - button "+ desktop/tests/browser/jobs-live.spec.ts" [ref=e144] [cursor=pointer]:
            - generic "added" [ref=e145]: +
            - generic "desktop/tests/browser/jobs-live.spec.ts" [ref=e146]
          - button "+ desktop/tests/browser/viewer.spec.ts" [ref=e147] [cursor=pointer]:
            - generic "added" [ref=e148]: +
            - generic "desktop/tests/browser/viewer.spec.ts" [ref=e149]
          - button "+ desktop/tests/git.test.mjs" [ref=e150] [cursor=pointer]:
            - generic "added" [ref=e151]: +
            - generic "desktop/tests/git.test.mjs" [ref=e152]
          - button "+ desktop/tests/install-office.test.mjs" [ref=e153] [cursor=pointer]:
            - generic "added" [ref=e154]: +
            - generic "desktop/tests/install-office.test.mjs" [ref=e155]
          - button "+ desktop/tests/runtime-client.test.mjs" [ref=e156] [cursor=pointer]:
            - generic "added" [ref=e157]: +
            - generic "desktop/tests/runtime-client.test.mjs" [ref=e158]
          - button "+ desktop/tests/runtime-identity.test.mjs" [ref=e159] [cursor=pointer]:
            - generic "added" [ref=e160]: +
            - generic "desktop/tests/runtime-identity.test.mjs" [ref=e161]
          - button "+ desktop/tests/security.test.mjs" [ref=e162] [cursor=pointer]:
            - generic "added" [ref=e163]: +
            - generic "desktop/tests/security.test.mjs" [ref=e164]
          - button "+ desktop/tsconfig.json" [ref=e165] [cursor=pointer]:
            - generic "added" [ref=e166]: +
            - generic "desktop/tsconfig.json" [ref=e167]
          - button "+ dev/luna.py" [ref=e168] [cursor=pointer]:
            - generic "added" [ref=e169]: +
            - generic "dev/luna.py" [ref=e170]
          - button "M dev/plan.json" [ref=e171] [cursor=pointer]:
            - generic "modified" [ref=e172]: M
            - generic "dev/plan.json" [ref=e173]
          - button "+ dev/test_luna.py" [ref=e174] [cursor=pointer]:
            - generic "added" [ref=e175]: +
            - generic "dev/test_luna.py" [ref=e176]
          - button "+ dev/test_specs.py" [ref=e177] [cursor=pointer]:
            - generic "added" [ref=e178]: +
            - generic "dev/test_specs.py" [ref=e179]
          - button "+ docs/ARCHITECTURE.md" [ref=e180] [cursor=pointer]:
            - generic "added" [ref=e181]: +
            - generic "docs/ARCHITECTURE.md" [ref=e182]
          - button "M docs/ART_DIRECTION.md" [ref=e183] [cursor=pointer]:
            - generic "modified" [ref=e184]: M
            - generic "docs/ART_DIRECTION.md" [ref=e185]
          - button "+ docs/ASSET_BINDING.md" [ref=e186] [cursor=pointer]:
            - generic "added" [ref=e187]: +
            - generic "docs/ASSET_BINDING.md" [ref=e188]
          - button "+ docs/COMPUTER_UI.md" [ref=e189] [cursor=pointer]:
            - generic "added" [ref=e190]: +
            - generic "docs/COMPUTER_UI.md" [ref=e191]
          - button "+ docs/EXECUTION.md" [ref=e192] [cursor=pointer]:
            - generic "added" [ref=e193]: +
            - generic "docs/EXECUTION.md" [ref=e194]
          - button "+ docs/FEATURE_MATRIX.md" [ref=e195] [cursor=pointer]:
            - generic "added" [ref=e196]: +
            - generic "docs/FEATURE_MATRIX.md" [ref=e197]
          - button "+ docs/MVP_ACCEPTANCE.md" [ref=e198] [cursor=pointer]:
            - generic "added" [ref=e199]: +
            - generic "docs/MVP_ACCEPTANCE.md" [ref=e200]
          - button "M docs/PARALLEL_PLAN.md" [ref=e201] [cursor=pointer]:
            - generic "modified" [ref=e202]: M
            - generic "docs/PARALLEL_PLAN.md" [ref=e203]
          - button "M docs/RESEARCH.md" [ref=e204] [cursor=pointer]:
            - generic "modified" [ref=e205]: M
            - generic "docs/RESEARCH.md" [ref=e206]
          - button "+ docs/RUN_EVALS.md" [ref=e207] [cursor=pointer]:
            - generic "added" [ref=e208]: +
            - generic "docs/RUN_EVALS.md" [ref=e209]
          - button "M docs/SETUP_VERIFICATION.md" [ref=e210] [cursor=pointer]:
            - generic "modified" [ref=e211]: M
            - generic "docs/SETUP_VERIFICATION.md" [ref=e212]
          - button "M docs/START_HERE.md" [ref=e213] [cursor=pointer]:
            - generic "modified" [ref=e214]: M
            - generic "docs/START_HERE.md" [ref=e215]
          - button "M docs/VALIDATION.md" [ref=e216] [cursor=pointer]:
            - generic "modified" [ref=e217]: M
            - generic "docs/VALIDATION.md" [ref=e218]
          - button "+ docs/archive/SPEC-0.2.md" [ref=e219] [cursor=pointer]:
            - generic "added" [ref=e220]: +
            - generic "docs/archive/SPEC-0.2.md" [ref=e221]
          - button "M docs/goals/A-runtime.md" [ref=e222] [cursor=pointer]:
            - generic "modified" [ref=e223]: M
            - generic "docs/goals/A-runtime.md" [ref=e224]
          - button "M docs/goals/B-tools.md" [ref=e225] [cursor=pointer]:
            - generic "modified" [ref=e226]: M
            - generic "docs/goals/B-tools.md" [ref=e227]
          - button "+ docs/goals/C-desktop.md" [ref=e228] [cursor=pointer]:
            - generic "added" [ref=e229]: +
            - generic "docs/goals/C-desktop.md" [ref=e230]
          - button "M docs/goals/C-unity.md" [ref=e231] [cursor=pointer]:
            - generic "modified" [ref=e232]: M
            - generic "docs/goals/C-unity.md" [ref=e233]
          - button "M docs/goals/D-workshops.md" [ref=e234] [cursor=pointer]:
            - generic "modified" [ref=e235]: M
            - generic "docs/goals/D-workshops.md" [ref=e236]
          - button "M docs/goals/I1-integration.md" [ref=e237] [cursor=pointer]:
            - generic "modified" [ref=e238]: M
            - generic "docs/goals/I1-integration.md" [ref=e239]
          - button "+ evidence/A/A1-final-review.json" [ref=e240] [cursor=pointer]:
            - generic "added" [ref=e241]: +
            - generic "evidence/A/A1-final-review.json" [ref=e242]
          - button "+ evidence/A/A1-review-2.json" [ref=e243] [cursor=pointer]:
            - generic "added" [ref=e244]: +
            - generic "evidence/A/A1-review-2.json" [ref=e245]
          - button "+ evidence/A/A1-review.json" [ref=e246] [cursor=pointer]:
            - generic "added" [ref=e247]: +
            - generic "evidence/A/A1-review.json" [ref=e248]
          - button "+ evidence/A/A1.json" [ref=e249] [cursor=pointer]:
            - generic "added" [ref=e250]: +
            - generic "evidence/A/A1.json" [ref=e251]
          - button "+ evidence/A/A2-repair-review.json" [ref=e252] [cursor=pointer]:
            - generic "added" [ref=e253]: +
            - generic "evidence/A/A2-repair-review.json" [ref=e254]
          - button "+ evidence/A/A2-review.json" [ref=e255] [cursor=pointer]:
            - generic "added" [ref=e256]: +
            - generic "evidence/A/A2-review.json" [ref=e257]
          - button "+ evidence/A/A2.json" [ref=e258] [cursor=pointer]:
            - generic "added" [ref=e259]: +
            - generic "evidence/A/A2.json" [ref=e260]
          - button "+ evidence/A/A3-repair-review.json" [ref=e261] [cursor=pointer]:
            - generic "added" [ref=e262]: +
            - generic "evidence/A/A3-repair-review.json" [ref=e263]
          - button "+ evidence/A/A3-review.json" [ref=e264] [cursor=pointer]:
            - generic "added" [ref=e265]: +
            - generic "evidence/A/A3-review.json" [ref=e266]
          - button "+ evidence/A/A3.json" [ref=e267] [cursor=pointer]:
            - generic "added" [ref=e268]: +
            - generic "evidence/A/A3.json" [ref=e269]
          - button "+ evidence/B/B1-repair-review.json" [ref=e270] [cursor=pointer]:
            - generic "added" [ref=e271]: +
            - generic "evidence/B/B1-repair-review.json" [ref=e272]
          - button "+ evidence/B/B1-review.json" [ref=e273] [cursor=pointer]:
            - generic "added" [ref=e274]: +
            - generic "evidence/B/B1-review.json" [ref=e275]
          - button "+ evidence/B/B1.json" [ref=e276] [cursor=pointer]:
            - generic "added" [ref=e277]: +
            - generic "evidence/B/B1.json" [ref=e278]
          - button "+ evidence/B/B2-readiness.json" [ref=e279] [cursor=pointer]:
            - generic "added" [ref=e280]: +
            - generic "evidence/B/B2-readiness.json" [ref=e281]
          - button "+ evidence/B/B2-repair-review.json" [ref=e282] [cursor=pointer]:
            - generic "added" [ref=e283]: +
            - generic "evidence/B/B2-repair-review.json" [ref=e284]
          - button "+ evidence/B/B2-review.json" [ref=e285] [cursor=pointer]:
            - generic "added" [ref=e286]: +
            - generic "evidence/B/B2-review.json" [ref=e287]
          - button "+ evidence/B/source-filter-repair.json" [ref=e288] [cursor=pointer]:
            - generic "added" [ref=e289]: +
            - generic "evidence/B/source-filter-repair.json" [ref=e290]
          - button "+ evidence/B/source-filter-review.json" [ref=e291] [cursor=pointer]:
            - generic "added" [ref=e292]: +
            - generic "evidence/B/source-filter-review.json" [ref=e293]
          - button "+ evidence/C/final-desktop-review.json" [ref=e294] [cursor=pointer]:
            - generic "added" [ref=e295]: +
            - generic "evidence/C/final-desktop-review.json" [ref=e296]
          - button "+ evidence/C/native-smoke-repair-review.json" [ref=e297] [cursor=pointer]:
            - generic "added" [ref=e298]: +
            - generic "evidence/C/native-smoke-repair-review.json" [ref=e299]
          - button "+ evidence/C/runtime-bridge-repair-review.json" [ref=e300] [cursor=pointer]:
            - generic "added" [ref=e301]: +
            - generic "evidence/C/runtime-bridge-repair-review.json" [ref=e302]
          - button "+ evidence/C/runtime-bridge-review.json" [ref=e303] [cursor=pointer]:
            - generic "added" [ref=e304]: +
            - generic "evidence/C/runtime-bridge-review.json" [ref=e305]
          - button "+ evidence/D/D1-previous-20261014t015727796417z.json" [ref=e306] [cursor=pointer]:
            - generic "added" [ref=e307]: +
            - generic "evidence/D/D1-previous-20261014t015727796417z.json" [ref=e308]
          - button "+ evidence/D/D1-previous-20261014t021328344314z.json" [ref=e309] [cursor=pointer]:
            - generic "added" [ref=e310]: +
            - generic "evidence/D/D1-previous-20261014t021328344314z.json" [ref=e311]
          - button "+ evidence/D/D1-previous-20261014t034618559898z.json" [ref=e312] [cursor=pointer]:
            - generic "added" [ref=e313]: +
            - generic "evidence/D/D1-previous-20261014t034618559898z.json" [ref=e314]
          - button "+ evidence/D/D1-review.json" [ref=e315] [cursor=pointer]:
            - generic "added" [ref=e316]: +
            - generic "evidence/D/D1-review.json" [ref=e317]
          - button "+ evidence/D/D1.json" [ref=e318] [cursor=pointer]:
            - generic "added" [ref=e319]: +
            - generic "evidence/D/D1.json" [ref=e320]
          - button "+ evidence/D/harness-lock-adjustment.json" [ref=e321] [cursor=pointer]:
            - generic "added" [ref=e322]: +
            - generic "evidence/D/harness-lock-adjustment.json" [ref=e323]
          - button "+ evidence/D/inputs/bad-manifest-20261014t015727796417z.json" [ref=e324] [cursor=pointer]:
            - generic "added" [ref=e325]: +
            - generic "evidence/D/inputs/bad-manifest-20261014t015727796417z.json" [ref=e326]
          - button "+ evidence/D/inputs/bad-manifest-20261014t021328344314z.json" [ref=e327] [cursor=pointer]:
            - generic "added" [ref=e328]: +
            - generic "evidence/D/inputs/bad-manifest-20261014t021328344314z.json" [ref=e329]
          - button "+ evidence/D/inputs/bad-manifest-20261014t034618559898z.json" [ref=e330] [cursor=pointer]:
            - generic "added" [ref=e331]: +
            - generic "evidence/D/inputs/bad-manifest-20261014t034618559898z.json" [ref=e332]
          - button "+ evidence/D/inputs/bad-manifest.json" [ref=e333] [cursor=pointer]:
            - generic "added" [ref=e334]: +
            - generic "evidence/D/inputs/bad-manifest.json" [ref=e335]
          - button "+ evidence/D/inputs/known-good-manifest-20261014t015727796417z.json" [ref=e336] [cursor=pointer]:
            - generic "added" [ref=e337]: +
            - generic "evidence/D/inputs/known-good-manifest-20261014t015727796417z.json" [ref=e338]
          - button "+ evidence/D/inputs/known-good-manifest-20261014t021328344314z.json" [ref=e339] [cursor=pointer]:
            - generic "added" [ref=e340]: +
            - generic "evidence/D/inputs/known-good-manifest-20261014t021328344314z.json" [ref=e341]
          - button "+ evidence/D/inputs/known-good-manifest-20261014t034618559898z.json" [ref=e342] [cursor=pointer]:
            - generic "added" [ref=e343]: +
            - generic "evidence/D/inputs/known-good-manifest-20261014t034618559898z.json" [ref=e344]
          - button "+ evidence/D/inputs/known-good-manifest.json" [ref=e345] [cursor=pointer]:
            - generic "added" [ref=e346]: +
            - generic "evidence/D/inputs/known-good-manifest.json" [ref=e347]
          - button "+ evidence/D/outputs/check-d1-bad-20261014t015727796417z-32a04073/after.png binary" [ref=e348] [cursor=pointer]:
            - generic "added" [ref=e349]: +
            - generic "evidence/D/outputs/check-d1-bad-20261014t015727796417z-32a04073/after.png" [ref=e350]
            - generic [ref=e351]: binary
          - button "+ evidence/D/outputs/check-d1-bad-20261014t015727796417z-32a04073/before.png binary" [ref=e352] [cursor=pointer]:
            - generic "added" [ref=e353]: +
            - generic "evidence/D/outputs/check-d1-bad-20261014t015727796417z-32a04073/before.png" [ref=e354]
            - generic [ref=e355]: binary
          - button "+ evidence/D/outputs/check-d1-bad-20261014t015727796417z-32a04073/check-report.json" [ref=e356] [cursor=pointer]:
            - generic "added" [ref=e357]: +
            - generic "evidence/D/outputs/check-d1-bad-20261014t015727796417z-32a04073/check-report.json" [ref=e358]
          - button "+ evidence/D/outputs/check-d1-bad-20261014t021328344314z-32a04073/after.png binary" [ref=e359] [cursor=pointer]:
            - generic "added" [ref=e360]: +
            - generic "evidence/D/outputs/check-d1-bad-20261014t021328344314z-32a04073/after.png" [ref=e361]
            - generic [ref=e362]: binary
          - button "+ evidence/D/outputs/check-d1-bad-20261014t021328344314z-32a04073/before.png binary" [ref=e363] [cursor=pointer]:
            - generic "added" [ref=e364]: +
            - generic "evidence/D/outputs/check-d1-bad-20261014t021328344314z-32a04073/before.png" [ref=e365]
            - generic [ref=e366]: binary
          - button "+ evidence/D/outputs/check-d1-bad-20261014t021328344314z-32a04073/check-report.json" [ref=e367] [cursor=pointer]:
            - generic "added" [ref=e368]: +
            - generic "evidence/D/outputs/check-d1-bad-20261014t021328344314z-32a04073/check-report.json" [ref=e369]
          - button "+ evidence/D/outputs/check-d1-bad-20261014t034618559898z-32a04073/after.png binary" [ref=e370] [cursor=pointer]:
            - generic "added" [ref=e371]: +
            - generic "evidence/D/outputs/check-d1-bad-20261014t034618559898z-32a04073/after.png" [ref=e372]
            - generic [ref=e373]: binary
          - button "+ evidence/D/outputs/check-d1-bad-20261014t034618559898z-32a04073/before.png binary" [ref=e374] [cursor=pointer]:
            - generic "added" [ref=e375]: +
            - generic "evidence/D/outputs/check-d1-bad-20261014t034618559898z-32a04073/before.png" [ref=e376]
            - generic [ref=e377]: binary
          - button "+ evidence/D/outputs/check-d1-bad-20261014t034618559898z-32a04073/check-report.json" [ref=e378] [cursor=pointer]:
            - generic "added" [ref=e379]: +
            - generic "evidence/D/outputs/check-d1-bad-20261014t034618559898z-32a04073/check-report.json" [ref=e380]
          - button "+ evidence/D/outputs/check-d1-bad-32a04073/after.png binary" [ref=e381] [cursor=pointer]:
            - generic "added" [ref=e382]: +
            - generic "evidence/D/outputs/check-d1-bad-32a04073/after.png" [ref=e383]
            - generic [ref=e384]: binary
          - button "+ evidence/D/outputs/check-d1-bad-32a04073/before.png binary" [ref=e385] [cursor=pointer]:
            - generic "added" [ref=e386]: +
            - generic "evidence/D/outputs/check-d1-bad-32a04073/before.png" [ref=e387]
            - generic [ref=e388]: binary
          - button "+ evidence/D/outputs/check-d1-bad-32a04073/check-report.json" [ref=e389] [cursor=pointer]:
            - generic "added" [ref=e390]: +
            - generic "evidence/D/outputs/check-d1-bad-32a04073/check-report.json" [ref=e391]
          - button "+ evidence/D/outputs/check-d1-known-good-20261014t015727796417z-430a53d1/after.png binary" [ref=e392] [cursor=pointer]:
            - generic "added" [ref=e393]: +
            - generic "evidence/D/outputs/check-d1-known-good-20261014t015727796417z-430a53d1/after.png" [ref=e394]
            - generic [ref=e395]: binary
          - button "+ evidence/D/outputs/check-d1-known-good-20261014t015727796417z-430a53d1/before.png binary" [ref=e396] [cursor=pointer]:
            - generic "added" [ref=e397]: +
            - generic "evidence/D/outputs/check-d1-known-good-20261014t015727796417z-430a53d1/before.png" [ref=e398]
            - generic [ref=e399]: binary
          - button "+ evidence/D/outputs/check-d1-known-good-20261014t015727796417z-430a53d1/check-report.json" [ref=e400] [cursor=pointer]:
            - generic "added" [ref=e401]: +
            - generic "evidence/D/outputs/check-d1-known-good-20261014t015727796417z-430a53d1/check-report.json" [ref=e402]
          - button "+ evidence/D/outputs/check-d1-known-good-20261014t021328344314z-430a53d1/after.png binary" [ref=e403] [cursor=pointer]:
            - generic "added" [ref=e404]: +
            - generic "evidence/D/outputs/check-d1-known-good-20261014t021328344314z-430a53d1/after.png" [ref=e405]
            - generic [ref=e406]: binary
          - button "+ evidence/D/outputs/check-d1-known-good-20261014t021328344314z-430a53d1/before.png binary" [ref=e407] [cursor=pointer]:
            - generic "added" [ref=e408]: +
            - generic "evidence/D/outputs/check-d1-known-good-20261014t021328344314z-430a53d1/before.png" [ref=e409]
            - generic [ref=e410]: binary
          - button "+ evidence/D/outputs/check-d1-known-good-20261014t021328344314z-430a53d1/check-report.json" [ref=e411] [cursor=pointer]:
            - generic "added" [ref=e412]: +
            - generic "evidence/D/outputs/check-d1-known-good-20261014t021328344314z-430a53d1/check-report.json" [ref=e413]
          - button "+ evidence/D/outputs/check-d1-known-good-20261014t034618559898z-430a53d1/after.png binary" [ref=e414] [cursor=pointer]:
            - generic "added" [ref=e415]: +
            - generic "evidence/D/outputs/check-d1-known-good-20261014t034618559898z-430a53d1/after.png" [ref=e416]
            - generic [ref=e417]: binary
          - button "+ evidence/D/outputs/check-d1-known-good-20261014t034618559898z-430a53d1/before.png binary" [ref=e418] [cursor=pointer]:
            - generic "added" [ref=e419]: +
            - generic "evidence/D/outputs/check-d1-known-good-20261014t034618559898z-430a53d1/before.png" [ref=e420]
            - generic [ref=e421]: binary
          - button "+ evidence/D/outputs/check-d1-known-good-20261014t034618559898z-430a53d1/check-report.json" [ref=e422] [cursor=pointer]:
            - generic "added" [ref=e423]: +
            - generic "evidence/D/outputs/check-d1-known-good-20261014t034618559898z-430a53d1/check-report.json" [ref=e424]
          - button "+ evidence/D/outputs/check-d1-known-good-430a53d1/after.png binary" [ref=e425] [cursor=pointer]:
            - generic "added" [ref=e426]: +
            - generic "evidence/D/outputs/check-d1-known-good-430a53d1/after.png" [ref=e427]
            - generic [ref=e428]: binary
          - button "+ evidence/D/outputs/check-d1-known-good-430a53d1/before.png binary" [ref=e429] [cursor=pointer]:
            - generic "added" [ref=e430]: +
            - generic "evidence/D/outputs/check-d1-known-good-430a53d1/before.png" [ref=e431]
            - generic [ref=e432]: binary
          - button "+ evidence/D/outputs/check-d1-known-good-430a53d1/check-report.json" [ref=e433] [cursor=pointer]:
            - generic "added" [ref=e434]: +
            - generic "evidence/D/outputs/check-d1-known-good-430a53d1/check-report.json" [ref=e435]
          - button "+ evidence/desktop/README.md" [ref=e436] [cursor=pointer]:
            - generic "added" [ref=e437]: +
            - generic "evidence/desktop/README.md" [ref=e438]
          - button "+ evidence/desktop/accessibility.json" [ref=e439] [cursor=pointer]:
            - generic "added" [ref=e440]: +
            - generic "evidence/desktop/accessibility.json" [ref=e441]
          - button "+ evidence/desktop/asset-transfer.json" [ref=e442] [cursor=pointer]:
            - generic "added" [ref=e443]: +
            - generic "evidence/desktop/asset-transfer.json" [ref=e444]
          - button "+ evidence/desktop/electron-smoke.json" [ref=e445] [cursor=pointer]:
            - generic "added" [ref=e446]: +
            - generic "evidence/desktop/electron-smoke.json" [ref=e447]
          - button "+ evidence/desktop/expanded-diff.png binary" [ref=e448] [cursor=pointer]:
            - generic "added" [ref=e449]: +
            - generic "evidence/desktop/expanded-diff.png" [ref=e450]
            - generic [ref=e451]: binary
          - button "+ evidence/desktop/git-diff.png binary" [ref=e452] [cursor=pointer]:
            - generic "added" [ref=e453]: +
            - generic "evidence/desktop/git-diff.png" [ref=e454]
            - generic [ref=e455]: binary
          - button "+ evidence/desktop/job-390.png binary" [ref=e456] [cursor=pointer]:
            - generic "added" [ref=e457]: +
            - generic "evidence/desktop/job-390.png" [ref=e458]
            - generic [ref=e459]: binary
          - button "+ evidence/desktop/job-960.png binary" [ref=e460] [cursor=pointer]:
            - generic "added" [ref=e461]: +
            - generic "evidence/desktop/job-960.png" [ref=e462]
            - generic [ref=e463]: binary
          - button "+ evidence/desktop/job-accessibility.json" [ref=e464] [cursor=pointer]:
            - generic "added" [ref=e465]: +
            - generic "evidence/desktop/job-accessibility.json" [ref=e466]
          - button "+ evidence/desktop/job-browser.json" [ref=e467] [cursor=pointer]:
            - generic "added" [ref=e468]: +
            - generic "evidence/desktop/job-browser.json" [ref=e469]
          - button "+ evidence/desktop/job-check-report.png binary" [ref=e470] [cursor=pointer]:
            - generic "added" [ref=e471]: +
            - generic "evidence/desktop/job-check-report.png" [ref=e472]
            - generic [ref=e473]: binary
          - button "+ evidence/desktop/job-diff.png binary" [ref=e474] [cursor=pointer]:
            - generic "added" [ref=e475]: +
            - generic "evidence/desktop/job-diff.png" [ref=e476]
            - generic [ref=e477]: binary
          - button "+ evidence/desktop/job-queued.png binary" [ref=e478] [cursor=pointer]:
            - generic "added" [ref=e479]: +
            - generic "evidence/desktop/job-queued.png" [ref=e480]
            - generic [ref=e481]: binary
          - button "+ evidence/desktop/job-readiness.png binary" [ref=e482] [cursor=pointer]:
            - generic "added" [ref=e483]: +
            - generic "evidence/desktop/job-readiness.png" [ref=e484]
            - generic [ref=e485]: binary
          - button "+ evidence/desktop/job-responsive-accessibility.json" [ref=e486] [cursor=pointer]:
            - generic "added" [ref=e487]: +
            - generic "evidence/desktop/job-responsive-accessibility.json" [ref=e488]
          - button "+ evidence/desktop/job-result.png binary" [ref=e489] [cursor=pointer]:
            - generic "added" [ref=e490]: +
            - generic "evidence/desktop/job-result.png" [ref=e491]
            - generic [ref=e492]: binary
          - button "+ evidence/desktop/sanitizer-bundle.json" [ref=e493] [cursor=pointer]:
            - generic "added" [ref=e494]: +
            - generic "evidence/desktop/sanitizer-bundle.json" [ref=e495]
          - button "+ evidence/desktop/security-audit-all.json" [ref=e496] [cursor=pointer]:
            - generic "added" [ref=e497]: +
            - generic "evidence/desktop/security-audit-all.json" [ref=e498]
          - button "+ evidence/desktop/security-audit.json" [ref=e499] [cursor=pointer]:
            - generic "added" [ref=e500]: +
            - generic "evidence/desktop/security-audit.json" [ref=e501]
          - button "+ evidence/desktop/setup-desktop.png binary" [ref=e502] [cursor=pointer]:
            - generic "added" [ref=e503]: +
            - generic "evidence/desktop/setup-desktop.png" [ref=e504]
            - generic [ref=e505]: binary
          - button "+ evidence/desktop/verification.json" [ref=e506] [cursor=pointer]:
            - generic "added" [ref=e507]: +
            - generic "evidence/desktop/verification.json" [ref=e508]
          - button "+ evidence/desktop/viewer-390.png binary" [ref=e509] [cursor=pointer]:
            - generic "added" [ref=e510]: +
            - generic "evidence/desktop/viewer-390.png" [ref=e511]
            - generic [ref=e512]: binary
          - button "+ evidence/desktop/viewer-960.png binary" [ref=e513] [cursor=pointer]:
            - generic "added" [ref=e514]: +
            - generic "evidence/desktop/viewer-960.png" [ref=e515]
            - generic [ref=e516]: binary
          - button "M journals/A.md" [ref=e517] [cursor=pointer]:
            - generic "modified" [ref=e518]: M
            - generic "journals/A.md" [ref=e519]
          - button "M journals/B.md" [ref=e520] [cursor=pointer]:
            - generic "modified" [ref=e521]: M
            - generic "journals/B.md" [ref=e522]
          - button "M journals/C.md" [ref=e523] [cursor=pointer]:
            - generic "modified" [ref=e524]: M
            - generic "journals/C.md" [ref=e525]
          - button "M journals/D.md" [ref=e526] [cursor=pointer]:
            - generic "modified" [ref=e527]: M
            - generic "journals/D.md" [ref=e528]
          - button "+ services/runtime/README.md" [ref=e529] [cursor=pointer]:
            - generic "added" [ref=e530]: +
            - generic "services/runtime/README.md" [ref=e531]
          - button "+ services/runtime/__init__.py" [ref=e532] [cursor=pointer]:
            - generic "added" [ref=e533]: +
            - generic "services/runtime/__init__.py" [ref=e534]
          - button "+ services/runtime/adapters.py" [ref=e535] [cursor=pointer]:
            - generic "added" [ref=e536]: +
            - generic "services/runtime/adapters.py" [ref=e537]
          - button "+ services/runtime/api.py" [ref=e538] [cursor=pointer]:
            - generic "added" [ref=e539]: +
            - generic "services/runtime/api.py" [ref=e540]
          - button "+ services/runtime/artifacts.py" [ref=e541] [cursor=pointer]:
            - generic "added" [ref=e542]: +
            - generic "services/runtime/artifacts.py" [ref=e543]
          - button "+ services/runtime/main.py" [ref=e544] [cursor=pointer]:
            - generic "added" [ref=e545]: +
            - generic "services/runtime/main.py" [ref=e546]
          - button "+ services/runtime/migrations/001_initial.sql" [ref=e547] [cursor=pointer]:
            - generic "added" [ref=e548]: +
            - generic "services/runtime/migrations/001_initial.sql" [ref=e549]
          - button "+ services/runtime/migrations/002_attempt_worker.sql" [ref=e550] [cursor=pointer]:
            - generic "added" [ref=e551]: +
            - generic "services/runtime/migrations/002_attempt_worker.sql" [ref=e552]
          - button "+ services/runtime/migrations/003_codex_lifecycle.sql" [ref=e553] [cursor=pointer]:
            - generic "added" [ref=e554]: +
            - generic "services/runtime/migrations/003_codex_lifecycle.sql" [ref=e555]
          - button "+ services/runtime/models.py" [ref=e556] [cursor=pointer]:
            - generic "added" [ref=e557]: +
            - generic "services/runtime/models.py" [ref=e558]
          - button "+ services/runtime/policy.py" [ref=e559] [cursor=pointer]:
            - generic "added" [ref=e560]: +
            - generic "services/runtime/policy.py" [ref=e561]
          - button "+ services/runtime/requirements.lock" [ref=e562] [cursor=pointer]:
            - generic "added" [ref=e563]: +
            - generic "services/runtime/requirements.lock" [ref=e564]
          - button "+ services/runtime/scheduler.py" [ref=e565] [cursor=pointer]:
            - generic "added" [ref=e566]: +
            - generic "services/runtime/scheduler.py" [ref=e567]
          - button "+ services/runtime/store.py" [ref=e568] [cursor=pointer]:
            - generic "added" [ref=e569]: +
            - generic "services/runtime/store.py" [ref=e570]
          - button "+ services/runtime/tests/test_adapters.py" [ref=e571] [cursor=pointer]:
            - generic "added" [ref=e572]: +
            - generic "services/runtime/tests/test_adapters.py" [ref=e573]
          - button "+ services/runtime/tests/test_api.py" [ref=e574] [cursor=pointer]:
            - generic "added" [ref=e575]: +
            - generic "services/runtime/tests/test_api.py" [ref=e576]
          - button "+ services/runtime/tests/test_codex_lifecycle.py" [ref=e577] [cursor=pointer]:
            - generic "added" [ref=e578]: +
            - generic "services/runtime/tests/test_codex_lifecycle.py" [ref=e579]
          - button "+ services/runtime/tests/test_concurrency.py" [ref=e580] [cursor=pointer]:
            - generic "added" [ref=e581]: +
            - generic "services/runtime/tests/test_concurrency.py" [ref=e582]
          - button "+ services/runtime/tests/test_main.py" [ref=e583] [cursor=pointer]:
            - generic "added" [ref=e584]: +
            - generic "services/runtime/tests/test_main.py" [ref=e585]
          - button "+ services/runtime/tests/test_policy.py" [ref=e586] [cursor=pointer]:
            - generic "added" [ref=e587]: +
            - generic "services/runtime/tests/test_policy.py" [ref=e588]
          - button "+ services/runtime/tests/test_scheduler_pipeline.py" [ref=e589] [cursor=pointer]:
            - generic "added" [ref=e590]: +
            - generic "services/runtime/tests/test_scheduler_pipeline.py" [ref=e591]
          - button "+ services/runtime/tests/test_storage.py" [ref=e592] [cursor=pointer]:
            - generic "added" [ref=e593]: +
            - generic "services/runtime/tests/test_storage.py" [ref=e594]
          - button "+ services/runtime/tests/test_support.py" [ref=e595] [cursor=pointer]:
            - generic "added" [ref=e596]: +
            - generic "services/runtime/tests/test_support.py" [ref=e597]
          - button "+ services/tools/__init__.py" [ref=e598] [cursor=pointer]:
            - generic "added" [ref=e599]: +
            - generic "services/tools/__init__.py" [ref=e600]
          - button "+ services/tools/artifact_capture.py" [ref=e601] [cursor=pointer]:
            - generic "added" [ref=e602]: +
            - generic "services/tools/artifact_capture.py" [ref=e603]
          - button "+ services/tools/codex_bridge.py" [ref=e604] [cursor=pointer]:
            - generic "added" [ref=e605]: +
            - generic "services/tools/codex_bridge.py" [ref=e606]
          - button "+ services/tools/git_ops.py" [ref=e607] [cursor=pointer]:
            - generic "added" [ref=e608]: +
            - generic "services/tools/git_ops.py" [ref=e609]
          - button "+ services/tools/main.py" [ref=e610] [cursor=pointer]:
            - generic "added" [ref=e611]: +
            - generic "services/tools/main.py" [ref=e612]
          - button "+ services/tools/protocol.py" [ref=e613] [cursor=pointer]:
            - generic "added" [ref=e614]: +
            - generic "services/tools/protocol.py" [ref=e615]
          - button "+ services/tools/tests/test_codex_bridge.py" [ref=e616] [cursor=pointer]:
            - generic "added" [ref=e617]: +
            - generic "services/tools/tests/test_codex_bridge.py" [ref=e618]
          - button "+ services/tools/tests/test_git_artifacts.py" [ref=e619] [cursor=pointer]:
            - generic "added" [ref=e620]: +
            - generic "services/tools/tests/test_git_artifacts.py" [ref=e621]
          - button "+ services/tools/tests/test_protocol.py" [ref=e622] [cursor=pointer]:
            - generic "added" [ref=e623]: +
            - generic "services/tools/tests/test_protocol.py" [ref=e624]
          - button "+ services/workshops/__init__.py" [ref=e625] [cursor=pointer]:
            - generic "added" [ref=e626]: +
            - generic "services/workshops/__init__.py" [ref=e627]
          - button "+ services/workshops/browser_checks.py" [ref=e628] [cursor=pointer]:
            - generic "added" [ref=e629]: +
            - generic "services/workshops/browser_checks.py" [ref=e630]
          - button "+ services/workshops/checks.py" [ref=e631] [cursor=pointer]:
            - generic "added" [ref=e632]: +
            - generic "services/workshops/checks.py" [ref=e633]
          - button "+ services/workshops/identity.py" [ref=e634] [cursor=pointer]:
            - generic "added" [ref=e635]: +
            - generic "services/workshops/identity.py" [ref=e636]
          - button "+ services/workshops/main.py" [ref=e637] [cursor=pointer]:
            - generic "added" [ref=e638]: +
            - generic "services/workshops/main.py" [ref=e639]
          - button "+ services/workshops/reports.py" [ref=e640] [cursor=pointer]:
            - generic "added" [ref=e641]: +
            - generic "services/workshops/reports.py" [ref=e642]
          - button "+ services/workshops/requirements.lock" [ref=e643] [cursor=pointer]:
            - generic "added" [ref=e644]: +
            - generic "services/workshops/requirements.lock" [ref=e645]
          - button "+ services/workshops/tests/__init__.py" [ref=e646] [cursor=pointer]:
            - generic "added" [ref=e647]: +
            - generic "services/workshops/tests/__init__.py" [ref=e648]
          - button "+ services/workshops/tests/helpers.py" [ref=e649] [cursor=pointer]:
            - generic "added" [ref=e650]: +
            - generic "services/workshops/tests/helpers.py" [ref=e651]
          - button "+ services/workshops/tests/test_identity.py" [ref=e652] [cursor=pointer]:
            - generic "added" [ref=e653]: +
            - generic "services/workshops/tests/test_identity.py" [ref=e654]
          - button "+ services/workshops/tests/test_protocol_browser.py" [ref=e655] [cursor=pointer]:
            - generic "added" [ref=e656]: +
            - generic "services/workshops/tests/test_protocol_browser.py" [ref=e657]
          - button "+ services/workshops/trust.lock.json" [ref=e658] [cursor=pointer]:
            - generic "added" [ref=e659]: +
            - generic "services/workshops/trust.lock.json" [ref=e660]
          - button "+ services/workshops/trusted_checks.json" [ref=e661] [cursor=pointer]:
            - generic "added" [ref=e662]: +
            - generic "services/workshops/trusted_checks.json" [ref=e663]
          - button "+ tests/e2e/run_d1.py" [ref=e664] [cursor=pointer]:
            - generic "added" [ref=e665]: +
            - generic "tests/e2e/run_d1.py" [ref=e666]
        - region "Selected file diff" [ref=e667]:
          - generic [ref=e668]:
            - text: .gitignore
            - generic [ref=e669]: Read-only
          - generic [ref=e671]:
            - code [ref=e673]:
              - generic [ref=e674]:
                - textbox "Original committed file, read-only"
                - textbox [aria-hidden] [ref=e675]
                - generic [aria-hidden] [ref=e677]:
                  - generic [ref=e678]: "1"
                  - generic [ref=e681]: "2"
                  - generic [ref=e683]: "3"
                  - generic [ref=e685]: "4"
                  - generic [ref=e687]: "5"
                  - generic [ref=e689]: "6"
                  - generic [ref=e691]: "7"
                  - generic [ref=e693]: "8"
                  - generic [ref=e695]: "9"
                  - generic [ref=e697]: "10"
                  - generic [ref=e699]: "11"
                  - generic [ref=e701]: "12"
                  - generic [ref=e703]: "13"
                  - generic [ref=e705]: "14"
                  - generic [ref=e707]: "15"
                  - generic [ref=e709]: "16"
                  - generic [ref=e711]: "17"
                  - generic [ref=e713]: "18"
                  - generic [ref=e715]: "19"
                  - generic [ref=e717]: "20"
                - generic [aria-hidden] [ref=e741]:
                  - generic [ref=e742]: "# Local development state and secrets"
                  - generic [ref=e744]: .sidequest/
                  - generic [ref=e746]: .env
                  - generic [ref=e748]: .env.*
                  - generic [ref=e750]: "!.env.example"
                  - generic [ref=e752]: "*.pem"
                  - generic [ref=e754]: "*.key"
                  - generic [ref=e756]: __pycache__/
                  - generic [ref=e758]: "*.py[cod]"
                  - generic [ref=e760]: .venv/
                  - generic [ref=e762]: .pytest_cache/
                  - generic [ref=e764]: "# Unity generated files"
                  - generic [ref=e766]: "[Ll]ibrary/"
                  - generic [ref=e768]: "[Tt]emp/"
                  - generic [ref=e770]: "[Oo]bj/"
                  - generic [ref=e772]: "[Ll]ogs/"
                  - generic [ref=e774]: "[Bb]uild/"
                  - generic [ref=e776]: "[Bb]uilds/"
                  - generic [ref=e778]: "[Uu]ser[Ss]ettings/"
                  - generic [ref=e780]: "[Mm]emoryCaptures/"
            - code [ref=e787]:
              - generic [ref=e788]:
                - textbox "Modified committed file, read-only" [ref=e789]
                - textbox [aria-hidden] [ref=e790]
                - generic [aria-hidden] [ref=e792]:
                  - generic [ref=e793]: "1"
                  - generic [ref=e798]: "2"
                  - generic [ref=e800]: "3"
                  - generic [ref=e802]: "4"
                  - generic [ref=e804]: "5"
                  - generic [ref=e806]: "6"
                  - generic [ref=e808]: "7"
                  - generic [ref=e810]: "8"
                  - generic [ref=e812]: "9"
                  - generic [ref=e814]: "10"
                  - generic [ref=e816]: "11"
                  - generic [ref=e818]: "12"
                  - generic [ref=e820]: "13"
                  - generic [ref=e822]: "14"
                  - generic [ref=e824]: "15"
                  - generic [ref=e826]: "16"
                  - generic [ref=e828]: "17"
                  - generic [ref=e830]: "18"
                  - generic [ref=e832]: "19"
                - generic [aria-hidden] [ref=e857]:
                  - generic [ref=e858]: "# Local development state and"
                  - generic [ref=e860]: secrets
                  - generic [ref=e862]: .sidequest/
                  - generic [ref=e864]: .env
                  - generic [ref=e866]: .env.*
                  - generic [ref=e868]: "!.env.example"
                  - generic [ref=e870]: "*.pem"
                  - generic [ref=e872]: "*.key"
                  - generic [ref=e874]: __pycache__/
                  - generic [ref=e876]: "*.py[cod]"
                  - generic [ref=e878]: .venv/
                  - generic [ref=e880]: .pytest_cache/
                  - generic [ref=e882]: "# Unity generated files"
                  - generic [ref=e884]: "[Ll]ibrary/"
                  - generic [ref=e886]: "[Tt]emp/"
                  - generic [ref=e888]: "[Oo]bj/"
                  - generic [ref=e890]: "[Ll]ogs/"
                  - generic [ref=e892]: "[Bb]uild/"
                  - generic [ref=e894]: "[Bb]uilds/"
                  - generic [ref=e896]: "[Uu]ser[Ss]ettings/"
      - generic [ref=e905]: Agent services are not connected in this desktop build.
    - generic [ref=e906]:
      - generic [ref=e908]: Original office
      - generic "Supplied reference poses are static artwork. No live coding session is attached to a figure." [ref=e910]: Loading staged figures · Sessions unconnected
  - generic [ref=e911]:
    - alert
    - alert
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | import path from 'node:path';
  3  | import { writeFile } from 'node:fs/promises';
  4  | import AxeBuilder from '@axe-core/playwright';
  5  | const evidence = path.resolve('../evidence/desktop');
  6  | test('real Git diff, lazy single editor, expanded state, Escape and keyboard', async ({ page, request }) => {
  7  |   const errors: string[] = []; page.on('pageerror', error => errors.push(error.message));
  8  |   const snapshotResponse = await request.get('/__sidequest/snapshot');
  9  |   expect(snapshotResponse.ok()).toBeTruthy();
  10 |   const snapshot = await snapshotResponse.json();
  11 |   expect(snapshot.mode).toBe('local-git');
  12 |   expect(snapshot.agent.state).toBe('unavailable');
  13 |   const source = snapshot.files.find((file: {path:string}) => file.path === 'dev/luna.py') ?? snapshot.files.find((file: { additions?:number; path:string }) => (file.additions ?? 0) > 120 && /\.(tsx?|py|md)$/.test(file.path)) ?? snapshot.files[0];
  14 |   const diff = await (await request.get(`/__sidequest/diff/${source.id}`)).json();
  15 |   expect(diff.readOnly).toBe(true); expect(diff.modified.length).toBeGreaterThan(100);
  16 |   await page.goto('/');
  17 |   await expect(page.getByTestId('diff-editor')).toHaveCount(0);
  18 |   await expect(page.locator('.station-nav button[data-station-id="parent_019"]')).toBeEnabled();
  19 |   await page.screenshot({path:path.join(evidence,'setup-desktop.png')});
  20 |   await page.locator('.station-nav button[data-station-id="parent_019"]').click();
  21 |   await page.locator(`.file-list button[data-file-id="${source.id}"]`).click();
  22 |   const editor = page.getByTestId('diff-editor');
  23 |   await expect(editor).toHaveCount(1);
  24 |   await expect(editor.locator('.view-lines').last()).toBeVisible();
  25 |   await editor.locator('.monaco-editor').last().hover();
  26 |   for (let count=0;count<10;count++) { await page.mouse.wheel(0, 800); await page.waitForTimeout(80); }
  27 |   await expect.poll(async () => Number(await editor.getAttribute('data-scroll-top'))).toBeGreaterThan(300);
  28 |   const before = Number(await editor.getAttribute('data-scroll-top'));
  29 |   await page.screenshot({path:path.join(evidence,'git-diff.png')});
  30 |   await page.getByRole('button',{name:'Expand',exact:true}).click();
  31 |   await expect(page.getByRole('dialog', {name:'Computer work viewer'})).toBeVisible();
  32 |   await expect(editor).toHaveCount(1);
  33 |   await expect.poll(async () => Number(await editor.getAttribute('data-scroll-top'))).toBeGreaterThan(Math.max(100,before-250));
  34 |   await page.screenshot({path:path.join(evidence,'expanded-diff.png')});
  35 |   await page.keyboard.press('Escape');
  36 |   await expect(editor).toHaveCount(0);
  37 |   await expect(page.locator('.station-nav button[data-station-id="parent_019"]')).toBeFocused();
  38 |   await page.keyboard.press('Enter');
  39 |   await expect(editor).toHaveAttribute('data-file-id',source.id);
  40 |   await expect.poll(async () => Number(await editor.getAttribute('data-scroll-top'))).toBeGreaterThan(100);
  41 |   expect(errors).toEqual([]);
  42 | });
  43 | test('read API rejects outside origins and mutations',async ({request})=>{
  44 |   expect((await request.get('/__sidequest/snapshot',{headers:{Origin:'https://example.com'}})).status()).toBe(403);
  45 |   expect((await request.post('/__sidequest/snapshot')).status()).toBe(405);
  46 |   expect((await request.get('/__sidequest/diff/not-a-file')).status()).toBe(404);
  47 | });
  48 | for (const width of [960,390]) test(`viewer reflows at ${width}px with reduced motion`,async ({page})=>{
  49 |   const errors:string[]=[];page.on('pageerror',error=>errors.push(error.message));
  50 |   await page.setViewportSize({width,height:780});await page.emulateMedia({reducedMotion:'reduce'});
  51 |   await page.goto('/');await page.locator('.station-nav button[data-station-id="parent_019"]').click();
> 52 |   await expect(page.getByTestId('diff-editor')).toHaveCount(1);
     |                                                 ^ Error: expect(locator).toHaveCount(expected) failed
  53 |   await page.getByRole('button',{name:'Expand',exact:true}).click();
  54 |   expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  55 |   await page.screenshot({path:path.join(evidence,`viewer-${width}.png`)});
  56 |   await page.keyboard.press('Escape');await expect(page.getByTestId('diff-editor')).toHaveCount(0);
  57 |   expect(errors).toEqual([]);
  58 | });
  59 | 
  60 | test('keyboard-accessible viewer has no automated WCAG A/AA violations',async({page})=>{
  61 |   await page.goto('/'); await page.locator('.station-nav button[data-station-id="parent_019"]').click();
  62 |   await expect(page.getByTestId('diff-editor').locator('.monaco-editor').last()).toBeVisible();
  63 |   await page.getByRole('button',{name:'Expand',exact:true}).click();
  64 |   await expect(page.getByTestId('diff-editor').locator('.monaco-editor').last()).toBeVisible();
  65 |   const code=page.getByRole('button',{name:/dev\/luna\.py/});
  66 |   if(await code.count()) {await code.click();await expect(page.getByTestId('diff-editor').locator('.view-lines').last()).toBeVisible();}
  67 |   const results=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze();
  68 |   await writeFile(path.join(evidence,'accessibility.json'),JSON.stringify(results.violations,null,2));
  69 |   expect(results.violations.map(item=>({id:item.id,impact:item.impact,description:item.description}))).toEqual([]);
  70 | });
  71 | 
  72 | test('hostile source stays literal and a failed read can retry',async({page})=>{
  73 |   let fail=true;
  74 |   await page.route('**/__sidequest/diff/*',async route=>{
  75 |     if(fail){await route.fulfill({status:503,json:{error:'test-only failure'}});return;}
  76 |     const response=await route.fetch();const data=await response.json();
  77 |     await route.fulfill({json:{...data,original:'',modified:'<script>window.__executed=true</script>\n<img src=x onerror="window.__executed=true">',language:'plaintext'}});
  78 |   });
  79 |   await page.goto('/');await page.locator('.station-nav button[data-station-id="parent_019"]').click();
  80 |   await expect(page.getByRole('alert')).toContainText('Local Git read failed');
  81 |   fail=false;await page.getByRole('button',{name:'Refresh repository'}).click();
  82 |   await expect(page.getByTestId('diff-editor')).toHaveCount(1);
  83 |   await expect(page.getByTestId('diff-editor').locator('.view-lines').last()).toContainText('<script>');
  84 |   expect(await page.evaluate(()=>Object.hasOwn(window,'__executed'))).toBe(false);
  85 | });
  86 | 
```