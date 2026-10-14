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
Timeout:  15000ms

Call log:
  - Expect "toHaveCount" getByTestId('diff-editor') with timeout 15000ms
  - waiting for getByTestId('diff-editor')
    5 × locator resolved to 0 elements
      - unexpected value "0"

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
    - region "Computer work viewer" [ref=e31]:
      - generic [ref=e32]:
        - generic [ref=e33]: Git diff
        - generic "69bf06696a93c9f58eee2d088e84404d4f6563d6" [ref=e34]: 69bf0669 → 8a9fb11c
        - generic [ref=e35]: Committed revisions
      - generic [ref=e36]:
        - navigation "Changed files" [ref=e37]:
          - paragraph [ref=e38]: 204 changed files
          - button "M .gitignore" [pressed] [ref=e39] [cursor=pointer]:
            - generic "modified" [ref=e40]: M
            - generic ".gitignore" [ref=e41]
          - button "M AGENTS.md" [ref=e42] [cursor=pointer]:
            - generic "modified" [ref=e43]: M
            - generic "AGENTS.md" [ref=e44]
          - button "M README.md" [ref=e45] [cursor=pointer]:
            - generic "modified" [ref=e46]: M
            - generic "README.md" [ref=e47]
          - button "M SPEC.md" [ref=e48] [cursor=pointer]:
            - generic "modified" [ref=e49]: M
            - generic "SPEC.md" [ref=e50]
          - button "+ contracts/EXTENSIONS.md" [ref=e51] [cursor=pointer]:
            - generic "added" [ref=e52]: +
            - generic "contracts/EXTENSIONS.md" [ref=e53]
          - button "M contracts/PROTOCOL.md" [ref=e54] [cursor=pointer]:
            - generic "modified" [ref=e55]: M
            - generic "contracts/PROTOCOL.md" [ref=e56]
          - button "+ contracts/STORAGE.md" [ref=e57] [cursor=pointer]:
            - generic "added" [ref=e58]: +
            - generic "contracts/STORAGE.md" [ref=e59]
          - button "+ contracts/examples/computer.json" [ref=e60] [cursor=pointer]:
            - generic "added" [ref=e61]: +
            - generic "contracts/examples/computer.json" [ref=e62]
          - button "+ demo/README.md" [ref=e63] [cursor=pointer]:
            - generic "added" [ref=e64]: +
            - generic "demo/README.md" [ref=e65]
          - button "+ demo/club-site/README.md" [ref=e66] [cursor=pointer]:
            - generic "added" [ref=e67]: +
            - generic "demo/club-site/README.md" [ref=e68]
          - button "+ demo/club-site/bad/index.html" [ref=e69] [cursor=pointer]:
            - generic "added" [ref=e70]: +
            - generic "demo/club-site/bad/index.html" [ref=e71]
          - button "+ demo/club-site/bad/members/signup.html" [ref=e72] [cursor=pointer]:
            - generic "added" [ref=e73]: +
            - generic "demo/club-site/bad/members/signup.html" [ref=e74]
          - button "+ demo/club-site/known-good/index.html" [ref=e75] [cursor=pointer]:
            - generic "added" [ref=e76]: +
            - generic "demo/club-site/known-good/index.html" [ref=e77]
          - button "+ demo/club-site/known-good/members/welcome.html" [ref=e78] [cursor=pointer]:
            - generic "added" [ref=e79]: +
            - generic "demo/club-site/known-good/members/welcome.html" [ref=e80]
          - button "+ desktop/README.md" [ref=e81] [cursor=pointer]:
            - generic "added" [ref=e82]: +
            - generic "desktop/README.md" [ref=e83]
          - button "+ desktop/electron/git-reader.cjs" [ref=e84] [cursor=pointer]:
            - generic "added" [ref=e85]: +
            - generic "desktop/electron/git-reader.cjs" [ref=e86]
          - button "+ desktop/electron/main.cjs" [ref=e87] [cursor=pointer]:
            - generic "added" [ref=e88]: +
            - generic "desktop/electron/main.cjs" [ref=e89]
          - button "+ desktop/electron/preload.cjs" [ref=e90] [cursor=pointer]:
            - generic "added" [ref=e91]: +
            - generic "desktop/electron/preload.cjs" [ref=e92]
          - button "+ desktop/electron/runtime-client.cjs" [ref=e93] [cursor=pointer]:
            - generic "added" [ref=e94]: +
            - generic "desktop/electron/runtime-client.cjs" [ref=e95]
          - button "+ desktop/electron/security.cjs" [ref=e96] [cursor=pointer]:
            - generic "added" [ref=e97]: +
            - generic "desktop/electron/security.cjs" [ref=e98]
          - button "+ desktop/electron/static-server.cjs" [ref=e99] [cursor=pointer]:
            - generic "added" [ref=e100]: +
            - generic "desktop/electron/static-server.cjs" [ref=e101]
          - button "+ desktop/index.html" [ref=e102] [cursor=pointer]:
            - generic "added" [ref=e103]: +
            - generic "desktop/index.html" [ref=e104]
          - button "+ desktop/package-lock.json" [ref=e105] [cursor=pointer]:
            - generic "added" [ref=e106]: +
            - generic "desktop/package-lock.json" [ref=e107]
          - button "+ desktop/package.json" [ref=e108] [cursor=pointer]:
            - generic "added" [ref=e109]: +
            - generic "desktop/package.json" [ref=e110]
          - button "+ desktop/scripts/electron-smoke.mjs" [ref=e111] [cursor=pointer]:
            - generic "added" [ref=e112]: +
            - generic "desktop/scripts/electron-smoke.mjs" [ref=e113]
          - button "+ desktop/scripts/inspect-assets.mjs" [ref=e114] [cursor=pointer]:
            - generic "added" [ref=e115]: +
            - generic "desktop/scripts/inspect-assets.mjs" [ref=e116]
          - button "+ desktop/scripts/install-office.py" [ref=e117] [cursor=pointer]:
            - generic "added" [ref=e118]: +
            - generic "desktop/scripts/install-office.py" [ref=e119]
          - button "+ desktop/src/App.tsx" [ref=e120] [cursor=pointer]:
            - generic "added" [ref=e121]: +
            - generic "desktop/src/App.tsx" [ref=e122]
          - button "+ desktop/src/DiffEditor.tsx" [ref=e123] [cursor=pointer]:
            - generic "added" [ref=e124]: +
            - generic "desktop/src/DiffEditor.tsx" [ref=e125]
          - button "+ desktop/src/JobsBoard.tsx" [ref=e126] [cursor=pointer]:
            - generic "added" [ref=e127]: +
            - generic "desktop/src/JobsBoard.tsx" [ref=e128]
          - button "+ desktop/src/OfficeScene.tsx" [ref=e129] [cursor=pointer]:
            - generic "added" [ref=e130]: +
            - generic "desktop/src/OfficeScene.tsx" [ref=e131]
          - button "+ desktop/src/bridge.ts" [ref=e132] [cursor=pointer]:
            - generic "added" [ref=e133]: +
            - generic "desktop/src/bridge.ts" [ref=e134]
          - button "+ desktop/src/main.tsx" [ref=e135] [cursor=pointer]:
            - generic "added" [ref=e136]: +
            - generic "desktop/src/main.tsx" [ref=e137]
          - button "+ desktop/src/office-bindings.ts" [ref=e138] [cursor=pointer]:
            - generic "added" [ref=e139]: +
            - generic "desktop/src/office-bindings.ts" [ref=e140]
          - button "+ desktop/src/runtime-identity.ts" [ref=e141] [cursor=pointer]:
            - generic "added" [ref=e142]: +
            - generic "desktop/src/runtime-identity.ts" [ref=e143]
          - button "+ desktop/src/style.css" [ref=e144] [cursor=pointer]:
            - generic "added" [ref=e145]: +
            - generic "desktop/src/style.css" [ref=e146]
          - button "+ desktop/src/types.ts" [ref=e147] [cursor=pointer]:
            - generic "added" [ref=e148]: +
            - generic "desktop/src/types.ts" [ref=e149]
          - button "+ desktop/tests/assets.test.mjs" [ref=e150] [cursor=pointer]:
            - generic "added" [ref=e151]: +
            - generic "desktop/tests/assets.test.mjs" [ref=e152]
          - button "+ desktop/tests/bindings.test.mjs" [ref=e153] [cursor=pointer]:
            - generic "added" [ref=e154]: +
            - generic "desktop/tests/bindings.test.mjs" [ref=e155]
          - button "+ desktop/tests/browser/jobs-live.spec.ts" [ref=e156] [cursor=pointer]:
            - generic "added" [ref=e157]: +
            - generic "desktop/tests/browser/jobs-live.spec.ts" [ref=e158]
          - button "+ desktop/tests/browser/viewer.spec.ts" [ref=e159] [cursor=pointer]:
            - generic "added" [ref=e160]: +
            - generic "desktop/tests/browser/viewer.spec.ts" [ref=e161]
          - button "+ desktop/tests/git.test.mjs" [ref=e162] [cursor=pointer]:
            - generic "added" [ref=e163]: +
            - generic "desktop/tests/git.test.mjs" [ref=e164]
          - button "+ desktop/tests/install-office.test.mjs" [ref=e165] [cursor=pointer]:
            - generic "added" [ref=e166]: +
            - generic "desktop/tests/install-office.test.mjs" [ref=e167]
          - button "+ desktop/tests/runtime-client.test.mjs" [ref=e168] [cursor=pointer]:
            - generic "added" [ref=e169]: +
            - generic "desktop/tests/runtime-client.test.mjs" [ref=e170]
          - button "+ desktop/tests/runtime-identity.test.mjs" [ref=e171] [cursor=pointer]:
            - generic "added" [ref=e172]: +
            - generic "desktop/tests/runtime-identity.test.mjs" [ref=e173]
          - button "+ desktop/tests/security.test.mjs" [ref=e174] [cursor=pointer]:
            - generic "added" [ref=e175]: +
            - generic "desktop/tests/security.test.mjs" [ref=e176]
          - button "+ desktop/tsconfig.json" [ref=e177] [cursor=pointer]:
            - generic "added" [ref=e178]: +
            - generic "desktop/tsconfig.json" [ref=e179]
          - button "+ dev/luna.py" [ref=e180] [cursor=pointer]:
            - generic "added" [ref=e181]: +
            - generic "dev/luna.py" [ref=e182]
          - button "M dev/plan.json" [ref=e183] [cursor=pointer]:
            - generic "modified" [ref=e184]: M
            - generic "dev/plan.json" [ref=e185]
          - button "+ dev/test_luna.py" [ref=e186] [cursor=pointer]:
            - generic "added" [ref=e187]: +
            - generic "dev/test_luna.py" [ref=e188]
          - button "+ dev/test_specs.py" [ref=e189] [cursor=pointer]:
            - generic "added" [ref=e190]: +
            - generic "dev/test_specs.py" [ref=e191]
          - button "+ docs/ARCHITECTURE.md" [ref=e192] [cursor=pointer]:
            - generic "added" [ref=e193]: +
            - generic "docs/ARCHITECTURE.md" [ref=e194]
          - button "M docs/ART_DIRECTION.md" [ref=e195] [cursor=pointer]:
            - generic "modified" [ref=e196]: M
            - generic "docs/ART_DIRECTION.md" [ref=e197]
          - button "+ docs/ASSET_BINDING.md" [ref=e198] [cursor=pointer]:
            - generic "added" [ref=e199]: +
            - generic "docs/ASSET_BINDING.md" [ref=e200]
          - button "+ docs/COMPUTER_UI.md" [ref=e201] [cursor=pointer]:
            - generic "added" [ref=e202]: +
            - generic "docs/COMPUTER_UI.md" [ref=e203]
          - button "+ docs/EXECUTION.md" [ref=e204] [cursor=pointer]:
            - generic "added" [ref=e205]: +
            - generic "docs/EXECUTION.md" [ref=e206]
          - button "+ docs/FEATURE_MATRIX.md" [ref=e207] [cursor=pointer]:
            - generic "added" [ref=e208]: +
            - generic "docs/FEATURE_MATRIX.md" [ref=e209]
          - button "+ docs/MVP_ACCEPTANCE.md" [ref=e210] [cursor=pointer]:
            - generic "added" [ref=e211]: +
            - generic "docs/MVP_ACCEPTANCE.md" [ref=e212]
          - button "M docs/PARALLEL_PLAN.md" [ref=e213] [cursor=pointer]:
            - generic "modified" [ref=e214]: M
            - generic "docs/PARALLEL_PLAN.md" [ref=e215]
          - button "M docs/RESEARCH.md" [ref=e216] [cursor=pointer]:
            - generic "modified" [ref=e217]: M
            - generic "docs/RESEARCH.md" [ref=e218]
          - button "+ docs/RUN_EVALS.md" [ref=e219] [cursor=pointer]:
            - generic "added" [ref=e220]: +
            - generic "docs/RUN_EVALS.md" [ref=e221]
          - button "M docs/SETUP_VERIFICATION.md" [ref=e222] [cursor=pointer]:
            - generic "modified" [ref=e223]: M
            - generic "docs/SETUP_VERIFICATION.md" [ref=e224]
          - button "M docs/START_HERE.md" [ref=e225] [cursor=pointer]:
            - generic "modified" [ref=e226]: M
            - generic "docs/START_HERE.md" [ref=e227]
          - button "M docs/VALIDATION.md" [ref=e228] [cursor=pointer]:
            - generic "modified" [ref=e229]: M
            - generic "docs/VALIDATION.md" [ref=e230]
          - button "+ docs/archive/SPEC-0.2.md" [ref=e231] [cursor=pointer]:
            - generic "added" [ref=e232]: +
            - generic "docs/archive/SPEC-0.2.md" [ref=e233]
          - button "M docs/goals/A-runtime.md" [ref=e234] [cursor=pointer]:
            - generic "modified" [ref=e235]: M
            - generic "docs/goals/A-runtime.md" [ref=e236]
          - button "M docs/goals/B-tools.md" [ref=e237] [cursor=pointer]:
            - generic "modified" [ref=e238]: M
            - generic "docs/goals/B-tools.md" [ref=e239]
          - button "+ docs/goals/C-desktop.md" [ref=e240] [cursor=pointer]:
            - generic "added" [ref=e241]: +
            - generic "docs/goals/C-desktop.md" [ref=e242]
          - button "M docs/goals/C-unity.md" [ref=e243] [cursor=pointer]:
            - generic "modified" [ref=e244]: M
            - generic "docs/goals/C-unity.md" [ref=e245]
          - button "M docs/goals/D-workshops.md" [ref=e246] [cursor=pointer]:
            - generic "modified" [ref=e247]: M
            - generic "docs/goals/D-workshops.md" [ref=e248]
          - button "M docs/goals/I1-integration.md" [ref=e249] [cursor=pointer]:
            - generic "modified" [ref=e250]: M
            - generic "docs/goals/I1-integration.md" [ref=e251]
          - button "+ evidence/A/A1-final-review.json" [ref=e252] [cursor=pointer]:
            - generic "added" [ref=e253]: +
            - generic "evidence/A/A1-final-review.json" [ref=e254]
          - button "+ evidence/A/A1-review-2.json" [ref=e255] [cursor=pointer]:
            - generic "added" [ref=e256]: +
            - generic "evidence/A/A1-review-2.json" [ref=e257]
          - button "+ evidence/A/A1-review.json" [ref=e258] [cursor=pointer]:
            - generic "added" [ref=e259]: +
            - generic "evidence/A/A1-review.json" [ref=e260]
          - button "+ evidence/A/A1.json" [ref=e261] [cursor=pointer]:
            - generic "added" [ref=e262]: +
            - generic "evidence/A/A1.json" [ref=e263]
          - button "+ evidence/A/A2-repair-review.json" [ref=e264] [cursor=pointer]:
            - generic "added" [ref=e265]: +
            - generic "evidence/A/A2-repair-review.json" [ref=e266]
          - button "+ evidence/A/A2-review.json" [ref=e267] [cursor=pointer]:
            - generic "added" [ref=e268]: +
            - generic "evidence/A/A2-review.json" [ref=e269]
          - button "+ evidence/A/A2.json" [ref=e270] [cursor=pointer]:
            - generic "added" [ref=e271]: +
            - generic "evidence/A/A2.json" [ref=e272]
          - button "+ evidence/A/A3-repair-review.json" [ref=e273] [cursor=pointer]:
            - generic "added" [ref=e274]: +
            - generic "evidence/A/A3-repair-review.json" [ref=e275]
          - button "+ evidence/A/A3-review.json" [ref=e276] [cursor=pointer]:
            - generic "added" [ref=e277]: +
            - generic "evidence/A/A3-review.json" [ref=e278]
          - button "+ evidence/A/A3.json" [ref=e279] [cursor=pointer]:
            - generic "added" [ref=e280]: +
            - generic "evidence/A/A3.json" [ref=e281]
          - button "+ evidence/B/B1-repair-review.json" [ref=e282] [cursor=pointer]:
            - generic "added" [ref=e283]: +
            - generic "evidence/B/B1-repair-review.json" [ref=e284]
          - button "+ evidence/B/B1-review.json" [ref=e285] [cursor=pointer]:
            - generic "added" [ref=e286]: +
            - generic "evidence/B/B1-review.json" [ref=e287]
          - button "+ evidence/B/B1.json" [ref=e288] [cursor=pointer]:
            - generic "added" [ref=e289]: +
            - generic "evidence/B/B1.json" [ref=e290]
          - button "+ evidence/B/B2-readiness.json" [ref=e291] [cursor=pointer]:
            - generic "added" [ref=e292]: +
            - generic "evidence/B/B2-readiness.json" [ref=e293]
          - button "+ evidence/B/B2-repair-review.json" [ref=e294] [cursor=pointer]:
            - generic "added" [ref=e295]: +
            - generic "evidence/B/B2-repair-review.json" [ref=e296]
          - button "+ evidence/B/B2-review.json" [ref=e297] [cursor=pointer]:
            - generic "added" [ref=e298]: +
            - generic "evidence/B/B2-review.json" [ref=e299]
          - button "+ evidence/B/source-filter-repair.json" [ref=e300] [cursor=pointer]:
            - generic "added" [ref=e301]: +
            - generic "evidence/B/source-filter-repair.json" [ref=e302]
          - button "+ evidence/B/source-filter-review.json" [ref=e303] [cursor=pointer]:
            - generic "added" [ref=e304]: +
            - generic "evidence/B/source-filter-review.json" [ref=e305]
          - button "+ evidence/C/final-desktop-review.json" [ref=e306] [cursor=pointer]:
            - generic "added" [ref=e307]: +
            - generic "evidence/C/final-desktop-review.json" [ref=e308]
          - button "+ evidence/C/native-smoke-repair-review.json" [ref=e309] [cursor=pointer]:
            - generic "added" [ref=e310]: +
            - generic "evidence/C/native-smoke-repair-review.json" [ref=e311]
          - button "+ evidence/C/runtime-bridge-repair-review.json" [ref=e312] [cursor=pointer]:
            - generic "added" [ref=e313]: +
            - generic "evidence/C/runtime-bridge-repair-review.json" [ref=e314]
          - button "+ evidence/C/runtime-bridge-review.json" [ref=e315] [cursor=pointer]:
            - generic "added" [ref=e316]: +
            - generic "evidence/C/runtime-bridge-review.json" [ref=e317]
          - button "+ evidence/D/D1-previous-20261014t015727796417z.json" [ref=e318] [cursor=pointer]:
            - generic "added" [ref=e319]: +
            - generic "evidence/D/D1-previous-20261014t015727796417z.json" [ref=e320]
          - button "+ evidence/D/D1-previous-20261014t021328344314z.json" [ref=e321] [cursor=pointer]:
            - generic "added" [ref=e322]: +
            - generic "evidence/D/D1-previous-20261014t021328344314z.json" [ref=e323]
          - button "+ evidence/D/D1-previous-20261014t034618559898z.json" [ref=e324] [cursor=pointer]:
            - generic "added" [ref=e325]: +
            - generic "evidence/D/D1-previous-20261014t034618559898z.json" [ref=e326]
          - button "+ evidence/D/D1-review.json" [ref=e327] [cursor=pointer]:
            - generic "added" [ref=e328]: +
            - generic "evidence/D/D1-review.json" [ref=e329]
          - button "+ evidence/D/D1.json" [ref=e330] [cursor=pointer]:
            - generic "added" [ref=e331]: +
            - generic "evidence/D/D1.json" [ref=e332]
          - button "+ evidence/D/harness-lock-adjustment.json" [ref=e333] [cursor=pointer]:
            - generic "added" [ref=e334]: +
            - generic "evidence/D/harness-lock-adjustment.json" [ref=e335]
          - button "+ evidence/D/inputs/bad-manifest-20261014t015727796417z.json" [ref=e336] [cursor=pointer]:
            - generic "added" [ref=e337]: +
            - generic "evidence/D/inputs/bad-manifest-20261014t015727796417z.json" [ref=e338]
          - button "+ evidence/D/inputs/bad-manifest-20261014t021328344314z.json" [ref=e339] [cursor=pointer]:
            - generic "added" [ref=e340]: +
            - generic "evidence/D/inputs/bad-manifest-20261014t021328344314z.json" [ref=e341]
          - button "+ evidence/D/inputs/bad-manifest-20261014t034618559898z.json" [ref=e342] [cursor=pointer]:
            - generic "added" [ref=e343]: +
            - generic "evidence/D/inputs/bad-manifest-20261014t034618559898z.json" [ref=e344]
          - button "+ evidence/D/inputs/bad-manifest.json" [ref=e345] [cursor=pointer]:
            - generic "added" [ref=e346]: +
            - generic "evidence/D/inputs/bad-manifest.json" [ref=e347]
          - button "+ evidence/D/inputs/known-good-manifest-20261014t015727796417z.json" [ref=e348] [cursor=pointer]:
            - generic "added" [ref=e349]: +
            - generic "evidence/D/inputs/known-good-manifest-20261014t015727796417z.json" [ref=e350]
          - button "+ evidence/D/inputs/known-good-manifest-20261014t021328344314z.json" [ref=e351] [cursor=pointer]:
            - generic "added" [ref=e352]: +
            - generic "evidence/D/inputs/known-good-manifest-20261014t021328344314z.json" [ref=e353]
          - button "+ evidence/D/inputs/known-good-manifest-20261014t034618559898z.json" [ref=e354] [cursor=pointer]:
            - generic "added" [ref=e355]: +
            - generic "evidence/D/inputs/known-good-manifest-20261014t034618559898z.json" [ref=e356]
          - button "+ evidence/D/inputs/known-good-manifest.json" [ref=e357] [cursor=pointer]:
            - generic "added" [ref=e358]: +
            - generic "evidence/D/inputs/known-good-manifest.json" [ref=e359]
          - button "+ evidence/D/outputs/check-d1-bad-20261014t015727796417z-32a04073/after.png binary" [ref=e360] [cursor=pointer]:
            - generic "added" [ref=e361]: +
            - generic "evidence/D/outputs/check-d1-bad-20261014t015727796417z-32a04073/after.png" [ref=e362]
            - generic [ref=e363]: binary
          - button "+ evidence/D/outputs/check-d1-bad-20261014t015727796417z-32a04073/before.png binary" [ref=e364] [cursor=pointer]:
            - generic "added" [ref=e365]: +
            - generic "evidence/D/outputs/check-d1-bad-20261014t015727796417z-32a04073/before.png" [ref=e366]
            - generic [ref=e367]: binary
          - button "+ evidence/D/outputs/check-d1-bad-20261014t015727796417z-32a04073/check-report.json" [ref=e368] [cursor=pointer]:
            - generic "added" [ref=e369]: +
            - generic "evidence/D/outputs/check-d1-bad-20261014t015727796417z-32a04073/check-report.json" [ref=e370]
          - button "+ evidence/D/outputs/check-d1-bad-20261014t021328344314z-32a04073/after.png binary" [ref=e371] [cursor=pointer]:
            - generic "added" [ref=e372]: +
            - generic "evidence/D/outputs/check-d1-bad-20261014t021328344314z-32a04073/after.png" [ref=e373]
            - generic [ref=e374]: binary
          - button "+ evidence/D/outputs/check-d1-bad-20261014t021328344314z-32a04073/before.png binary" [ref=e375] [cursor=pointer]:
            - generic "added" [ref=e376]: +
            - generic "evidence/D/outputs/check-d1-bad-20261014t021328344314z-32a04073/before.png" [ref=e377]
            - generic [ref=e378]: binary
          - button "+ evidence/D/outputs/check-d1-bad-20261014t021328344314z-32a04073/check-report.json" [ref=e379] [cursor=pointer]:
            - generic "added" [ref=e380]: +
            - generic "evidence/D/outputs/check-d1-bad-20261014t021328344314z-32a04073/check-report.json" [ref=e381]
          - button "+ evidence/D/outputs/check-d1-bad-20261014t034618559898z-32a04073/after.png binary" [ref=e382] [cursor=pointer]:
            - generic "added" [ref=e383]: +
            - generic "evidence/D/outputs/check-d1-bad-20261014t034618559898z-32a04073/after.png" [ref=e384]
            - generic [ref=e385]: binary
          - button "+ evidence/D/outputs/check-d1-bad-20261014t034618559898z-32a04073/before.png binary" [ref=e386] [cursor=pointer]:
            - generic "added" [ref=e387]: +
            - generic "evidence/D/outputs/check-d1-bad-20261014t034618559898z-32a04073/before.png" [ref=e388]
            - generic [ref=e389]: binary
          - button "+ evidence/D/outputs/check-d1-bad-20261014t034618559898z-32a04073/check-report.json" [ref=e390] [cursor=pointer]:
            - generic "added" [ref=e391]: +
            - generic "evidence/D/outputs/check-d1-bad-20261014t034618559898z-32a04073/check-report.json" [ref=e392]
          - button "+ evidence/D/outputs/check-d1-bad-32a04073/after.png binary" [ref=e393] [cursor=pointer]:
            - generic "added" [ref=e394]: +
            - generic "evidence/D/outputs/check-d1-bad-32a04073/after.png" [ref=e395]
            - generic [ref=e396]: binary
          - button "+ evidence/D/outputs/check-d1-bad-32a04073/before.png binary" [ref=e397] [cursor=pointer]:
            - generic "added" [ref=e398]: +
            - generic "evidence/D/outputs/check-d1-bad-32a04073/before.png" [ref=e399]
            - generic [ref=e400]: binary
          - button "+ evidence/D/outputs/check-d1-bad-32a04073/check-report.json" [ref=e401] [cursor=pointer]:
            - generic "added" [ref=e402]: +
            - generic "evidence/D/outputs/check-d1-bad-32a04073/check-report.json" [ref=e403]
          - button "+ evidence/D/outputs/check-d1-known-good-20261014t015727796417z-430a53d1/after.png binary" [ref=e404] [cursor=pointer]:
            - generic "added" [ref=e405]: +
            - generic "evidence/D/outputs/check-d1-known-good-20261014t015727796417z-430a53d1/after.png" [ref=e406]
            - generic [ref=e407]: binary
          - button "+ evidence/D/outputs/check-d1-known-good-20261014t015727796417z-430a53d1/before.png binary" [ref=e408] [cursor=pointer]:
            - generic "added" [ref=e409]: +
            - generic "evidence/D/outputs/check-d1-known-good-20261014t015727796417z-430a53d1/before.png" [ref=e410]
            - generic [ref=e411]: binary
          - button "+ evidence/D/outputs/check-d1-known-good-20261014t015727796417z-430a53d1/check-report.json" [ref=e412] [cursor=pointer]:
            - generic "added" [ref=e413]: +
            - generic "evidence/D/outputs/check-d1-known-good-20261014t015727796417z-430a53d1/check-report.json" [ref=e414]
          - button "+ evidence/D/outputs/check-d1-known-good-20261014t021328344314z-430a53d1/after.png binary" [ref=e415] [cursor=pointer]:
            - generic "added" [ref=e416]: +
            - generic "evidence/D/outputs/check-d1-known-good-20261014t021328344314z-430a53d1/after.png" [ref=e417]
            - generic [ref=e418]: binary
          - button "+ evidence/D/outputs/check-d1-known-good-20261014t021328344314z-430a53d1/before.png binary" [ref=e419] [cursor=pointer]:
            - generic "added" [ref=e420]: +
            - generic "evidence/D/outputs/check-d1-known-good-20261014t021328344314z-430a53d1/before.png" [ref=e421]
            - generic [ref=e422]: binary
          - button "+ evidence/D/outputs/check-d1-known-good-20261014t021328344314z-430a53d1/check-report.json" [ref=e423] [cursor=pointer]:
            - generic "added" [ref=e424]: +
            - generic "evidence/D/outputs/check-d1-known-good-20261014t021328344314z-430a53d1/check-report.json" [ref=e425]
          - button "+ evidence/D/outputs/check-d1-known-good-20261014t034618559898z-430a53d1/after.png binary" [ref=e426] [cursor=pointer]:
            - generic "added" [ref=e427]: +
            - generic "evidence/D/outputs/check-d1-known-good-20261014t034618559898z-430a53d1/after.png" [ref=e428]
            - generic [ref=e429]: binary
          - button "+ evidence/D/outputs/check-d1-known-good-20261014t034618559898z-430a53d1/before.png binary" [ref=e430] [cursor=pointer]:
            - generic "added" [ref=e431]: +
            - generic "evidence/D/outputs/check-d1-known-good-20261014t034618559898z-430a53d1/before.png" [ref=e432]
            - generic [ref=e433]: binary
          - button "+ evidence/D/outputs/check-d1-known-good-20261014t034618559898z-430a53d1/check-report.json" [ref=e434] [cursor=pointer]:
            - generic "added" [ref=e435]: +
            - generic "evidence/D/outputs/check-d1-known-good-20261014t034618559898z-430a53d1/check-report.json" [ref=e436]
          - button "+ evidence/D/outputs/check-d1-known-good-430a53d1/after.png binary" [ref=e437] [cursor=pointer]:
            - generic "added" [ref=e438]: +
            - generic "evidence/D/outputs/check-d1-known-good-430a53d1/after.png" [ref=e439]
            - generic [ref=e440]: binary
          - button "+ evidence/D/outputs/check-d1-known-good-430a53d1/before.png binary" [ref=e441] [cursor=pointer]:
            - generic "added" [ref=e442]: +
            - generic "evidence/D/outputs/check-d1-known-good-430a53d1/before.png" [ref=e443]
            - generic [ref=e444]: binary
          - button "+ evidence/D/outputs/check-d1-known-good-430a53d1/check-report.json" [ref=e445] [cursor=pointer]:
            - generic "added" [ref=e446]: +
            - generic "evidence/D/outputs/check-d1-known-good-430a53d1/check-report.json" [ref=e447]
          - button "+ evidence/desktop/README.md" [ref=e448] [cursor=pointer]:
            - generic "added" [ref=e449]: +
            - generic "evidence/desktop/README.md" [ref=e450]
          - button "+ evidence/desktop/accessibility.json" [ref=e451] [cursor=pointer]:
            - generic "added" [ref=e452]: +
            - generic "evidence/desktop/accessibility.json" [ref=e453]
          - button "+ evidence/desktop/asset-transfer.json" [ref=e454] [cursor=pointer]:
            - generic "added" [ref=e455]: +
            - generic "evidence/desktop/asset-transfer.json" [ref=e456]
          - button "+ evidence/desktop/electron-smoke.json" [ref=e457] [cursor=pointer]:
            - generic "added" [ref=e458]: +
            - generic "evidence/desktop/electron-smoke.json" [ref=e459]
          - button "+ evidence/desktop/expanded-diff.png binary" [ref=e460] [cursor=pointer]:
            - generic "added" [ref=e461]: +
            - generic "evidence/desktop/expanded-diff.png" [ref=e462]
            - generic [ref=e463]: binary
          - button "+ evidence/desktop/git-diff.png binary" [ref=e464] [cursor=pointer]:
            - generic "added" [ref=e465]: +
            - generic "evidence/desktop/git-diff.png" [ref=e466]
            - generic [ref=e467]: binary
          - button "+ evidence/desktop/job-390.png binary" [ref=e468] [cursor=pointer]:
            - generic "added" [ref=e469]: +
            - generic "evidence/desktop/job-390.png" [ref=e470]
            - generic [ref=e471]: binary
          - button "+ evidence/desktop/job-960.png binary" [ref=e472] [cursor=pointer]:
            - generic "added" [ref=e473]: +
            - generic "evidence/desktop/job-960.png" [ref=e474]
            - generic [ref=e475]: binary
          - button "+ evidence/desktop/job-accessibility.json" [ref=e476] [cursor=pointer]:
            - generic "added" [ref=e477]: +
            - generic "evidence/desktop/job-accessibility.json" [ref=e478]
          - button "+ evidence/desktop/job-browser.json" [ref=e479] [cursor=pointer]:
            - generic "added" [ref=e480]: +
            - generic "evidence/desktop/job-browser.json" [ref=e481]
          - button "+ evidence/desktop/job-check-report.png binary" [ref=e482] [cursor=pointer]:
            - generic "added" [ref=e483]: +
            - generic "evidence/desktop/job-check-report.png" [ref=e484]
            - generic [ref=e485]: binary
          - button "+ evidence/desktop/job-diff.png binary" [ref=e486] [cursor=pointer]:
            - generic "added" [ref=e487]: +
            - generic "evidence/desktop/job-diff.png" [ref=e488]
            - generic [ref=e489]: binary
          - button "+ evidence/desktop/job-queued.png binary" [ref=e490] [cursor=pointer]:
            - generic "added" [ref=e491]: +
            - generic "evidence/desktop/job-queued.png" [ref=e492]
            - generic [ref=e493]: binary
          - button "+ evidence/desktop/job-readiness.png binary" [ref=e494] [cursor=pointer]:
            - generic "added" [ref=e495]: +
            - generic "evidence/desktop/job-readiness.png" [ref=e496]
            - generic [ref=e497]: binary
          - button "+ evidence/desktop/job-responsive-accessibility.json" [ref=e498] [cursor=pointer]:
            - generic "added" [ref=e499]: +
            - generic "evidence/desktop/job-responsive-accessibility.json" [ref=e500]
          - button "+ evidence/desktop/job-result.png binary" [ref=e501] [cursor=pointer]:
            - generic "added" [ref=e502]: +
            - generic "evidence/desktop/job-result.png" [ref=e503]
            - generic [ref=e504]: binary
          - button "+ evidence/desktop/sanitizer-bundle.json" [ref=e505] [cursor=pointer]:
            - generic "added" [ref=e506]: +
            - generic "evidence/desktop/sanitizer-bundle.json" [ref=e507]
          - button "+ evidence/desktop/security-audit-all.json" [ref=e508] [cursor=pointer]:
            - generic "added" [ref=e509]: +
            - generic "evidence/desktop/security-audit-all.json" [ref=e510]
          - button "+ evidence/desktop/security-audit.json" [ref=e511] [cursor=pointer]:
            - generic "added" [ref=e512]: +
            - generic "evidence/desktop/security-audit.json" [ref=e513]
          - button "+ evidence/desktop/setup-desktop.png binary" [ref=e514] [cursor=pointer]:
            - generic "added" [ref=e515]: +
            - generic "evidence/desktop/setup-desktop.png" [ref=e516]
            - generic [ref=e517]: binary
          - button "+ evidence/desktop/verification.json" [ref=e518] [cursor=pointer]:
            - generic "added" [ref=e519]: +
            - generic "evidence/desktop/verification.json" [ref=e520]
          - button "+ evidence/desktop/viewer-390.png binary" [ref=e521] [cursor=pointer]:
            - generic "added" [ref=e522]: +
            - generic "evidence/desktop/viewer-390.png" [ref=e523]
            - generic [ref=e524]: binary
          - button "+ evidence/desktop/viewer-960.png binary" [ref=e525] [cursor=pointer]:
            - generic "added" [ref=e526]: +
            - generic "evidence/desktop/viewer-960.png" [ref=e527]
            - generic [ref=e528]: binary
          - button "M journals/A.md" [ref=e529] [cursor=pointer]:
            - generic "modified" [ref=e530]: M
            - generic "journals/A.md" [ref=e531]
          - button "M journals/B.md" [ref=e532] [cursor=pointer]:
            - generic "modified" [ref=e533]: M
            - generic "journals/B.md" [ref=e534]
          - button "M journals/C.md" [ref=e535] [cursor=pointer]:
            - generic "modified" [ref=e536]: M
            - generic "journals/C.md" [ref=e537]
          - button "M journals/D.md" [ref=e538] [cursor=pointer]:
            - generic "modified" [ref=e539]: M
            - generic "journals/D.md" [ref=e540]
          - button "+ services/runtime/README.md" [ref=e541] [cursor=pointer]:
            - generic "added" [ref=e542]: +
            - generic "services/runtime/README.md" [ref=e543]
          - button "+ services/runtime/__init__.py" [ref=e544] [cursor=pointer]:
            - generic "added" [ref=e545]: +
            - generic "services/runtime/__init__.py" [ref=e546]
          - button "+ services/runtime/adapters.py" [ref=e547] [cursor=pointer]:
            - generic "added" [ref=e548]: +
            - generic "services/runtime/adapters.py" [ref=e549]
          - button "+ services/runtime/api.py" [ref=e550] [cursor=pointer]:
            - generic "added" [ref=e551]: +
            - generic "services/runtime/api.py" [ref=e552]
          - button "+ services/runtime/artifacts.py" [ref=e553] [cursor=pointer]:
            - generic "added" [ref=e554]: +
            - generic "services/runtime/artifacts.py" [ref=e555]
          - button "+ services/runtime/main.py" [ref=e556] [cursor=pointer]:
            - generic "added" [ref=e557]: +
            - generic "services/runtime/main.py" [ref=e558]
          - button "+ services/runtime/migrations/001_initial.sql" [ref=e559] [cursor=pointer]:
            - generic "added" [ref=e560]: +
            - generic "services/runtime/migrations/001_initial.sql" [ref=e561]
          - button "+ services/runtime/migrations/002_attempt_worker.sql" [ref=e562] [cursor=pointer]:
            - generic "added" [ref=e563]: +
            - generic "services/runtime/migrations/002_attempt_worker.sql" [ref=e564]
          - button "+ services/runtime/migrations/003_codex_lifecycle.sql" [ref=e565] [cursor=pointer]:
            - generic "added" [ref=e566]: +
            - generic "services/runtime/migrations/003_codex_lifecycle.sql" [ref=e567]
          - button "+ services/runtime/models.py" [ref=e568] [cursor=pointer]:
            - generic "added" [ref=e569]: +
            - generic "services/runtime/models.py" [ref=e570]
          - button "+ services/runtime/policy.py" [ref=e571] [cursor=pointer]:
            - generic "added" [ref=e572]: +
            - generic "services/runtime/policy.py" [ref=e573]
          - button "+ services/runtime/requirements.lock" [ref=e574] [cursor=pointer]:
            - generic "added" [ref=e575]: +
            - generic "services/runtime/requirements.lock" [ref=e576]
          - button "+ services/runtime/scheduler.py" [ref=e577] [cursor=pointer]:
            - generic "added" [ref=e578]: +
            - generic "services/runtime/scheduler.py" [ref=e579]
          - button "+ services/runtime/store.py" [ref=e580] [cursor=pointer]:
            - generic "added" [ref=e581]: +
            - generic "services/runtime/store.py" [ref=e582]
          - button "+ services/runtime/tests/test_adapters.py" [ref=e583] [cursor=pointer]:
            - generic "added" [ref=e584]: +
            - generic "services/runtime/tests/test_adapters.py" [ref=e585]
          - button "+ services/runtime/tests/test_api.py" [ref=e586] [cursor=pointer]:
            - generic "added" [ref=e587]: +
            - generic "services/runtime/tests/test_api.py" [ref=e588]
          - button "+ services/runtime/tests/test_codex_lifecycle.py" [ref=e589] [cursor=pointer]:
            - generic "added" [ref=e590]: +
            - generic "services/runtime/tests/test_codex_lifecycle.py" [ref=e591]
          - button "+ services/runtime/tests/test_concurrency.py" [ref=e592] [cursor=pointer]:
            - generic "added" [ref=e593]: +
            - generic "services/runtime/tests/test_concurrency.py" [ref=e594]
          - button "+ services/runtime/tests/test_main.py" [ref=e595] [cursor=pointer]:
            - generic "added" [ref=e596]: +
            - generic "services/runtime/tests/test_main.py" [ref=e597]
          - button "+ services/runtime/tests/test_policy.py" [ref=e598] [cursor=pointer]:
            - generic "added" [ref=e599]: +
            - generic "services/runtime/tests/test_policy.py" [ref=e600]
          - button "+ services/runtime/tests/test_scheduler_pipeline.py" [ref=e601] [cursor=pointer]:
            - generic "added" [ref=e602]: +
            - generic "services/runtime/tests/test_scheduler_pipeline.py" [ref=e603]
          - button "+ services/runtime/tests/test_storage.py" [ref=e604] [cursor=pointer]:
            - generic "added" [ref=e605]: +
            - generic "services/runtime/tests/test_storage.py" [ref=e606]
          - button "+ services/runtime/tests/test_support.py" [ref=e607] [cursor=pointer]:
            - generic "added" [ref=e608]: +
            - generic "services/runtime/tests/test_support.py" [ref=e609]
          - button "+ services/tools/__init__.py" [ref=e610] [cursor=pointer]:
            - generic "added" [ref=e611]: +
            - generic "services/tools/__init__.py" [ref=e612]
          - button "+ services/tools/artifact_capture.py" [ref=e613] [cursor=pointer]:
            - generic "added" [ref=e614]: +
            - generic "services/tools/artifact_capture.py" [ref=e615]
          - button "+ services/tools/codex_bridge.py" [ref=e616] [cursor=pointer]:
            - generic "added" [ref=e617]: +
            - generic "services/tools/codex_bridge.py" [ref=e618]
          - button "+ services/tools/git_ops.py" [ref=e619] [cursor=pointer]:
            - generic "added" [ref=e620]: +
            - generic "services/tools/git_ops.py" [ref=e621]
          - button "+ services/tools/main.py" [ref=e622] [cursor=pointer]:
            - generic "added" [ref=e623]: +
            - generic "services/tools/main.py" [ref=e624]
          - button "+ services/tools/protocol.py" [ref=e625] [cursor=pointer]:
            - generic "added" [ref=e626]: +
            - generic "services/tools/protocol.py" [ref=e627]
          - button "+ services/tools/tests/test_codex_bridge.py" [ref=e628] [cursor=pointer]:
            - generic "added" [ref=e629]: +
            - generic "services/tools/tests/test_codex_bridge.py" [ref=e630]
          - button "+ services/tools/tests/test_git_artifacts.py" [ref=e631] [cursor=pointer]:
            - generic "added" [ref=e632]: +
            - generic "services/tools/tests/test_git_artifacts.py" [ref=e633]
          - button "+ services/tools/tests/test_protocol.py" [ref=e634] [cursor=pointer]:
            - generic "added" [ref=e635]: +
            - generic "services/tools/tests/test_protocol.py" [ref=e636]
          - button "+ services/workshops/__init__.py" [ref=e637] [cursor=pointer]:
            - generic "added" [ref=e638]: +
            - generic "services/workshops/__init__.py" [ref=e639]
          - button "+ services/workshops/browser_checks.py" [ref=e640] [cursor=pointer]:
            - generic "added" [ref=e641]: +
            - generic "services/workshops/browser_checks.py" [ref=e642]
          - button "+ services/workshops/checks.py" [ref=e643] [cursor=pointer]:
            - generic "added" [ref=e644]: +
            - generic "services/workshops/checks.py" [ref=e645]
          - button "+ services/workshops/identity.py" [ref=e646] [cursor=pointer]:
            - generic "added" [ref=e647]: +
            - generic "services/workshops/identity.py" [ref=e648]
          - button "+ services/workshops/main.py" [ref=e649] [cursor=pointer]:
            - generic "added" [ref=e650]: +
            - generic "services/workshops/main.py" [ref=e651]
          - button "+ services/workshops/reports.py" [ref=e652] [cursor=pointer]:
            - generic "added" [ref=e653]: +
            - generic "services/workshops/reports.py" [ref=e654]
          - button "+ services/workshops/requirements.lock" [ref=e655] [cursor=pointer]:
            - generic "added" [ref=e656]: +
            - generic "services/workshops/requirements.lock" [ref=e657]
          - button "+ services/workshops/tests/__init__.py" [ref=e658] [cursor=pointer]:
            - generic "added" [ref=e659]: +
            - generic "services/workshops/tests/__init__.py" [ref=e660]
          - button "+ services/workshops/tests/helpers.py" [ref=e661] [cursor=pointer]:
            - generic "added" [ref=e662]: +
            - generic "services/workshops/tests/helpers.py" [ref=e663]
          - button "+ services/workshops/tests/test_identity.py" [ref=e664] [cursor=pointer]:
            - generic "added" [ref=e665]: +
            - generic "services/workshops/tests/test_identity.py" [ref=e666]
          - button "+ services/workshops/tests/test_protocol_browser.py" [ref=e667] [cursor=pointer]:
            - generic "added" [ref=e668]: +
            - generic "services/workshops/tests/test_protocol_browser.py" [ref=e669]
          - button "+ services/workshops/trust.lock.json" [ref=e670] [cursor=pointer]:
            - generic "added" [ref=e671]: +
            - generic "services/workshops/trust.lock.json" [ref=e672]
          - button "+ services/workshops/trusted_checks.json" [ref=e673] [cursor=pointer]:
            - generic "added" [ref=e674]: +
            - generic "services/workshops/trusted_checks.json" [ref=e675]
          - button "+ tests/e2e/run_d1.py" [ref=e676] [cursor=pointer]:
            - generic "added" [ref=e677]: +
            - generic "tests/e2e/run_d1.py" [ref=e678]
        - region "Selected file diff" [ref=e679]:
          - generic [ref=e680]:
            - text: .gitignore
            - generic [ref=e681]: Read-only
          - status [ref=e682]: Loading diff editor…
      - generic [ref=e683]: Agent services are not connected in this desktop build.
  - generic [ref=e684]:
    - combobox "Office navigation" [ref=e685]:
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
    - generic "Original staged poses; recorded runtime ownership is separate from provider connectivity." [ref=e686]: 26 staged · no sessions
    - generic "UI refresh and file viewing make zero model calls." [ref=e687]: Local Git · read-only
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
  10 |   await page.goto('/');await expect(page.locator('.app-footer')).toHaveAttribute('data-actor-status','ready',{timeout:60000});await expect(page.getByRole('combobox',{name:'Office navigation'})).toBeEnabled();
  11 |   await expect(page.locator('.office-canvas canvas')).toBeVisible();
  12 | 
  13 | 
  14 |   await page.getByRole('combobox',{name:'Office navigation'}).selectOption('parent_019');
> 15 |   await expect(page.getByTestId('diff-editor')).toHaveCount(1);
     |                                                 ^ Error: expect(locator).toHaveCount(expected) failed
  16 |   await expect(page.getByRole('button',{name:'Expand',exact:true})).toBeVisible();
  17 | 
  18 |   await page.getByRole('button',{name:'Expand',exact:true}).click();
  19 |   await expect(page.getByRole('dialog',{name:'Computer work viewer'})).toBeVisible();
  20 | 
  21 |   const selected=await page.getByTestId('diff-editor').getAttribute('data-file-id');
  22 |   await page.getByRole('button',{name:'Settings',exact:true}).click();
  23 |   const settings=page.getByRole('dialog',{name:'Provider settings dialog'});
  24 |   await expect(settings).toBeVisible();await expect(settings.getByRole('heading',{name:/Codex$/})).toBeVisible();
  25 |   await expect(settings.getByLabel('Binary path')).toHaveValue(/codex/);
  26 |   await expect(settings.getByText('Authentication',{exact:true})).toBeVisible();
  27 |   await expect(settings.getByText('Service reachability',{exact:true})).toBeVisible();
  28 | 
  29 |   if(width===1440){
  30 |     await settings.getByRole('button',{name:/Claude/}).click();
  31 |     await expect(settings.getByRole('heading',{name:/Claude$/})).toBeVisible();
  32 |     await settings.getByRole('button',{name:/Codex/}).click();
  33 |   }else{
  34 |     await settings.locator('.provider-mobile-picker__button').click();
  35 |     await settings.getByRole('navigation',{name:'Choose provider'}).getByRole('button',{name:'Claude',exact:true}).click();
  36 |     await expect(settings.getByRole('heading',{name:/Claude$/})).toBeVisible();
  37 |     await settings.locator('.provider-mobile-picker__button').click();
  38 |     await settings.getByRole('navigation',{name:'Choose provider'}).getByRole('button',{name:'Codex',exact:true}).click();
  39 |   }
  40 |   await settings.getByRole('button',{name:'Refresh provider discovery'}).click();
  41 |   await expect(settings.getByRole('button',{name:'Refresh provider discovery'})).toBeEnabled();
  42 |   expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  43 |   await page.screenshot({path:path.join(evidence,`provider-settings${width===1440?'':'-390'}.png`)});
  44 |   await settings.getByRole('navigation',{name:'Settings view'}).getByRole('button',{name:'Usage',exact:true}).click();
  45 |   await expect(settings.getByText('No usage data reported',{exact:true})).toBeVisible();
  46 |   await settings.getByRole('group',{name:'Usage metric'}).getByRole('button',{name:'Tokens',exact:true}).click();
  47 |   await expect(settings.getByText('Processed tokens unavailable',{exact:true})).toBeVisible();
  48 |   await settings.getByRole('group',{name:'Usage breakdown'}).getByRole('button',{name:'Day',exact:true}).click();
  49 |   await expect(settings.getByText('No daily usage data reported',{exact:true})).toBeVisible();
  50 |   await page.screenshot({path:path.join(evidence,`provider-settings-analytics${width===1440?'':'-390'}.png`)});
  51 |   await settings.getByRole('group',{name:'Usage metric'}).getByRole('button',{name:'Limits',exact:true}).click();
  52 |   await expect(settings.getByText('— remaining',{exact:true})).toHaveCount(2);
  53 |   await expect(settings.getByText('Reset unknown',{exact:true})).toHaveCount(2);
  54 |   await page.screenshot({path:path.join(evidence,`provider-settings-limits${width===1440?'':'-390'}.png`)});
  55 |   const result=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze();
  56 |   await writeFile(path.join(evidence,`provider-accessibility-${width}.json`),JSON.stringify(result.violations,null,2));
  57 |   expect(result.violations.map(v=>({id:v.id,impact:v.impact}))).toEqual([]);
  58 |   const first=settings.locator('button:visible:not(:disabled),input:visible,select:visible,[tabindex="0"]:visible').first(),last=settings.locator('button:visible:not(:disabled),input:visible,select:visible,[tabindex="0"]:visible').last();
  59 |   await last.focus();await page.keyboard.press('Tab');await expect(first).toBeFocused();
  60 |   await page.keyboard.press('Escape');await expect(settings).toHaveCount(0);
  61 |   await expect(page.getByRole('dialog',{name:'Computer work viewer'})).toBeVisible();
  62 |   await expect(page.getByTestId('diff-editor')).toHaveAttribute('data-file-id',selected!);
  63 |   await page.keyboard.press('Escape');await expect(page.getByTestId('diff-editor')).toHaveCount(0);
  64 |   expect(errors).toEqual([]);
  65 | });
  66 | 
  67 | for(const width of [1440,390]) test(`compact provider picker and guarded monitor task setup at ${width}px`,async({page})=>{
  68 |   const errors:string[]=[];page.on('pageerror',error=>errors.push(error.message));await page.setViewportSize({width,height:width===390?780:1000});await page.emulateMedia({reducedMotion:'reduce'});await page.goto('/');await expect(page.locator('.app-footer')).toHaveAttribute('data-actor-status','ready',{timeout:60000});
  69 |   const settings=page.getByRole('dialog',{name:'Provider settings dialog'});
  70 |   const mutations:string[]=[];page.on('request',request=>{if(/__sidequest\/runtime\/(submitCoding|runCoding|enableCoding)$/.test(request.url()))mutations.push(request.url());});
  71 |   await page.getByRole('combobox',{name:'Office navigation'}).selectOption('work:parent_019');
  72 |   const picker=page.getByRole('dialog',{name:'Choose provider'});await expect(picker).toBeVisible();await expect(picker).toContainText('No connected providers');
  73 |   await expect(picker.getByRole('button',{name:'Connect provider'})).toBeEnabled();await expect(picker.locator('input,select,textarea,form')).toHaveCount(0);await expect(picker.getByRole('button',{name:'Submit task'})).toHaveCount(0);await expect(picker.locator('.provider-tile')).toHaveCount(0);
  74 |   const pickerBox=(await picker.boundingBox())!;expect(pickerBox.width).toBeLessThanOrEqual(280);expect(pickerBox.height).toBeLessThan(200);
  75 |   await page.screenshot({path:path.join(evidence,`provider-selector${width===1440?'':'-390'}.png`)});
  76 |   await picker.getByRole('button',{name:'Connect provider'}).click();await expect(settings).toBeVisible();await page.keyboard.press('Escape');
  77 |   await page.getByRole('combobox',{name:'Office navigation'}).selectOption('monitor:parent_019');await page.getByRole('button',{name:'Task setup',exact:true}).click();const launcher=page.getByRole('region',{name:'Task setup',exact:true});await expect(launcher).toBeVisible();
  78 |   await expect(launcher.getByLabel('Prompt',{exact:true})).toHaveValue('');await launcher.getByLabel('Prompt',{exact:true}).fill('Test-only draft prompt. No coding task will be submitted.');
  79 |   await launcher.getByText('Scope and spending',{exact:false}).click();await expect(launcher.getByLabel('Allowed folder',{exact:true})).toHaveValue('');await expect(launcher.getByLabel('USD limit',{exact:true})).toHaveValue('');
  80 |   await launcher.getByLabel('Allowed folder',{exact:true}).fill('desktop/src');await launcher.getByLabel('USD limit',{exact:true}).fill('0.01');await expect(launcher.getByRole('button',{name:'Submit task',exact:true})).toBeDisabled();
  81 |   await launcher.getByRole('button',{name:'Refresh setup',exact:true}).click();await expect(launcher.getByRole('button',{name:'Submit task',exact:true})).toBeDisabled();
  82 |   const launcherAxe=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze();expect(launcherAxe.violations.map(v=>({id:v.id,impact:v.impact}))).toEqual([]);
  83 |   await page.screenshot({path:path.join(evidence,`monitor-task-setup${width===1440?'':'-390'}.png`)});await page.keyboard.press('Escape');await expect(launcher).toHaveCount(0);
  84 |   await page.getByRole('combobox',{name:'Office navigation'}).selectOption('actor:parent_019');
  85 |   const session=page.getByRole('dialog',{name:'Agent session'});await expect(session).toContainText('No live session attached');
  86 |   await page.screenshot({path:path.join(evidence,`agent-session${width===1440?'':'-390'}.png`)});
  87 |   await page.keyboard.press('Escape');await expect(session).toHaveCount(0);
  88 |   expect(mutations).toEqual([]);
  89 |   expect(errors).toEqual([]);
  90 | });
  91 | 
```