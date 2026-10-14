# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: viewer.spec.ts >> Escape/reopen mounts one selected Monaco editor and keeps its saved scroll
- Location: tests/browser/viewer.spec.ts:57:1

# Error details

```
Error: expect(received).toHaveLength(expected)

Expected length: 1
Received length: 2
Received array:  [{"at": 41677.10000000149, "children": 1, "connected": true, "fileId": "f_03d72050ecef630081601cb44a0cec9a", "phase": "added", "scrollTop": "479", "testId": "diff-editor"}, {"at": 48333.5, "children": 1, "connected": true, "fileId": "f_03d72050ecef630081601cb44a0cec9a", "phase": "added", "scrollTop": "479", "testId": "diff-editor"}]
```

# Page snapshot

```yaml
- generic [ref=e1]:
  - main [ref=e3]:
    - generic [ref=e4]:
      - generic [ref=e5]: sidequest
      - generic [ref=e6]: sidequest
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
          - button "M .gitignore" [ref=e30] [cursor=pointer]:
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
          - button "+ dev/luna.py" [pressed] [ref=e171] [cursor=pointer]:
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
            - text: dev/luna.py
            - generic [ref=e672]: Read-only
          - generic [ref=e674]:
            - code [ref=e676]:
              - generic [ref=e677]:
                - textbox "Original committed file, read-only"
                - textbox [aria-hidden] [ref=e678]
                - generic [ref=e682]:
                  - generic [ref=e685]: 
                  - generic [ref=e686]: "1"
            - code [ref=e701]:
              - generic [ref=e702]:
                - textbox "Modified committed file, read-only" [ref=e703]
                - textbox [aria-hidden] [ref=e704]
                - generic [aria-hidden] [ref=e705]:
                  - text: 
                  - generic [aria-hidden] [ref=e706]:
                    - generic [ref=e707]: 
                    - generic [ref=e710]:
                      - generic [ref=e712]: 
                      - generic [ref=e713]: "21"
                    - generic [ref=e714]: 
                    - generic [ref=e717]:
                      - generic [ref=e719]: 
                      - generic [ref=e720]: "22"
                    - generic [ref=e721]: 
                    - generic [ref=e724]:
                      - generic [ref=e726]: 
                      - generic [ref=e727]: "23"
                    - generic [ref=e728]: 
                    - generic [ref=e731]:
                      - generic [ref=e733]: 
                      - generic [ref=e734]: "24"
                    - generic [ref=e735]:
                      - generic [ref=e737]: 
                      - generic [ref=e738]: "25"
                    - generic [ref=e739]:
                      - generic [ref=e741]: 
                      - generic [ref=e742]: "26"
                    - generic [ref=e743]:
                      - generic [ref=e745]: 
                      - generic [ref=e746]: "27"
                - generic [aria-hidden] [ref=e793]:
                  - generic [ref=e794]: luna"',
                  - generic [ref=e796]: "'-c',"
                  - generic [ref=e798]: "'model_reasoning_effort=\"max\"',"
                  - generic [ref=e800]: "'-c',"
                  - generic [ref=e802]: "'model_reasoning_summary=\"concise\"',"
                  - generic [ref=e804]: "'-c', 'features.goals=true', '-"
                  - generic [ref=e806]: c', 'features.multi_agent=false',
                  - generic [ref=e808]: "'app-server']"
                  - generic [ref=e812]: def verify_selection(rpc,
      - generic [ref=e822]: Agent services are not connected in this desktop build.
    - generic [ref=e823]:
      - combobox "Office navigation" [active] [ref=e824]:
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
      - generic "Original staged poses; recorded runtime ownership is separate from provider connectivity." [ref=e825]: 26 staged · no sessions
      - generic "UI refresh and file viewing make zero model calls." [ref=e826]: Local Git · read-only
  - generic [ref=e827]:
    - alert
    - alert
```

# Test source

```ts
  1   | import { test, expect, type Page } from '@playwright/test';
  2   | import path from 'node:path';
  3   | import { writeFile } from 'node:fs/promises';
  4   | import AxeBuilder from '@axe-core/playwright';
  5   | const evidence = path.resolve('../evidence/desktop');
  6   | async function traceEditorMounts(page:Page){
  7   |   await page.addInitScript(()=>{
  8   |     const trace:unknown[]=[];(window as unknown as {__editorLifecycle:unknown[]}).__editorLifecycle=trace;
  9   |     const record=(phase:string,node:HTMLElement)=>{if(trace.length<100)trace.push({phase,at:performance.now(),testId:node.dataset.testid,fileId:node.dataset.fileId,scrollTop:node.dataset.scrollTop,connected:node.isConnected,children:node.childElementCount});};
  10  |     new MutationObserver(records=>{for(const entry of records){for(const node of entry.addedNodes)if(node instanceof HTMLElement){if(node.matches('.diff-editor'))record('added',node);node.querySelectorAll<HTMLElement>('.diff-editor').forEach(child=>record('added',child));}for(const node of entry.removedNodes)if(node instanceof HTMLElement){if(node.matches('.diff-editor'))record('removed',node);node.querySelectorAll<HTMLElement>('.diff-editor').forEach(child=>record('removed',child));}}}).observe(document,{childList:true,subtree:true});
  11  |   });
  12  | }
  13  | test('real Git diff, lazy single editor, expanded state, Escape and keyboard', async ({ page, request }) => {
  14  |   const errors: string[] = []; page.on('pageerror', error => errors.push(error.message));
  15  |   const consoleErrors:string[]=[];page.on('console',message=>{if(message.type()==='error')consoleErrors.push(message.text());});
  16  |   await traceEditorMounts(page);
  17  |   try {
  18  |   const snapshotResponse = await request.get('/__sidequest/snapshot');
  19  |   expect(snapshotResponse.ok()).toBeTruthy();
  20  |   const snapshot = await snapshotResponse.json();
  21  |   expect(snapshot.mode).toBe('local-git');
  22  |   expect(snapshot.agent.state).toBe('unavailable');
  23  |   const source = snapshot.files.find((file: {path:string}) => file.path === 'dev/luna.py') ?? snapshot.files.find((file: { additions?:number; path:string }) => (file.additions ?? 0) > 120 && /\.(tsx?|py|md)$/.test(file.path)) ?? snapshot.files[0];
  24  |   const diff = await (await request.get(`/__sidequest/diff/${source.id}`)).json();
  25  |   expect(diff.readOnly).toBe(true); expect(diff.modified.length).toBeGreaterThan(100);
  26  |   await page.goto('/');await expect(page.locator('.app-footer')).toHaveAttribute('data-actor-status','ready',{timeout:60000});
  27  |   await expect(page.getByTestId('diff-editor')).toHaveCount(0);
  28  |   await expect(page.getByRole('combobox',{name:'Office navigation'})).toBeEnabled();
  29  |   await page.screenshot({path:path.join(evidence,'setup-desktop.png')});
  30  |   await page.getByRole('combobox',{name:'Office navigation'}).selectOption('parent_019');
  31  |   await page.locator(`.file-list button[data-file-id="${source.id}"]`).click();
  32  |   const editor = page.getByTestId('diff-editor');
  33  |   await expect(editor).toHaveCount(1);
  34  |   await expect(editor.locator('.view-lines').last()).toBeVisible();
  35  |   await editor.locator('.monaco-editor').last().hover();
  36  |   for (let count=0;count<10;count++) { await page.mouse.wheel(0, 800); await page.waitForTimeout(80); }
  37  |   await expect.poll(async () => Number(await editor.getAttribute('data-scroll-top'))).toBeGreaterThan(300);
  38  |   const before = Number(await editor.getAttribute('data-scroll-top'));
  39  |   await page.screenshot({path:path.join(evidence,'git-diff.png')});
  40  |   await page.getByRole('button',{name:'Expand',exact:true}).click();
  41  |   await expect(page.getByRole('dialog', {name:'Computer work viewer'})).toBeVisible();
  42  |   await expect(editor).toHaveCount(1);
  43  |   await expect.poll(async () => Number(await editor.getAttribute('data-scroll-top'))).toBeGreaterThan(Math.max(100,before-250));
  44  |   await page.screenshot({path:path.join(evidence,'expanded-diff.png')});
  45  |   await page.keyboard.press('Escape');
  46  |   await expect(editor).toHaveCount(0);
  47  |   await expect(page.getByRole('combobox',{name:'Office navigation'})).toBeFocused();
  48  |   await page.getByRole('combobox',{name:'Office navigation'}).selectOption('parent_019');
  49  |   await expect(editor).toHaveAttribute('data-file-id',source.id);
  50  |   await expect.poll(async () => Number(await editor.getAttribute('data-scroll-top'))).toBeGreaterThan(100);
  51  |   expect(errors).toEqual([]);
  52  |   } finally {
  53  |     const dom=await page.evaluate(()=>({trace:(window as unknown as {__editorLifecycle:unknown[]}).__editorLifecycle,editors:Array.from(document.querySelectorAll<HTMLElement>('.diff-editor')).map(node=>({testId:node.dataset.testid,fileId:node.dataset.fileId,scrollTop:node.dataset.scrollTop,children:node.childElementCount,htmlPrefix:node.outerHTML.slice(0,400)})),modifiedInputs:document.querySelectorAll('[aria-label="Modified committed file, read-only"]').length,mode:document.querySelector('main')?.getAttribute('data-mode')}));
  54  |     await writeFile(path.join(evidence,'monaco-reopen-diagnosis.json'),JSON.stringify({errors,consoleErrors,...dom},null,2));
  55  |   }
  56  | });
  57  | test('Escape/reopen mounts one selected Monaco editor and keeps its saved scroll',async({page,request})=>{
  58  |   await traceEditorMounts(page);
  59  |   await page.emulateMedia({reducedMotion:'reduce'});
  60  |   const snapshot=await (await request.get('/__sidequest/snapshot')).json();
  61  |   const source=snapshot.files.find((file:{path:string})=>file.path==='dev/luna.py')??snapshot.files.find((file:{additions:number})=>file.additions>120);
  62  |   expect(source).toBeTruthy();
  63  |   await page.goto('/');await expect(page.locator('.app-footer')).toHaveAttribute('data-actor-status','ready',{timeout:60000});
  64  |   const nav=page.getByRole('combobox',{name:'Office navigation'}),editor=page.getByTestId('diff-editor');
  65  |   await nav.selectOption('parent_019');await page.locator(`.file-list button[data-file-id="${source.id}"]`).click();
  66  |   await expect(editor.locator('.view-lines').last()).toBeVisible();
  67  |   await editor.locator('.monaco-editor').last().hover();
  68  |   for(let index=0;index<10;index++){await page.mouse.wheel(0,800);await page.waitForTimeout(80);}
  69  |   await expect.poll(async()=>Number(await editor.getAttribute('data-scroll-top'))).toBeGreaterThan(300);
  70  |   await page.keyboard.press('Escape');await expect(editor).toHaveCount(0);
  71  |   await page.evaluate(()=>{(window as unknown as {__editorLifecycle:unknown[]}).__editorLifecycle.length=0;});
  72  |   await nav.selectOption('parent_019');
  73  |   await expect(editor).toHaveAttribute('data-file-id',source.id);
  74  |   await page.waitForLoadState('networkidle');
  75  |   await expect(editor).toHaveCount(1);
  76  |   await expect.poll(async()=>Number(await editor.getAttribute('data-scroll-top'))).toBeGreaterThan(100);
  77  |   const trace=await page.evaluate(()=>(window as unknown as {__editorLifecycle:{phase:string;fileId:string}[]}).__editorLifecycle);
  78  |   await writeFile(path.join(evidence,'monaco-single-reopen.json'),JSON.stringify({sourceId:source.id,trace},null,2));
> 79  |   expect(trace.filter(event=>event.phase==='added'&&event.fileId===source.id)).toHaveLength(1);
      |                                                                                ^ Error: expect(received).toHaveLength(expected)
  80  | });
  81  | test('read API rejects outside origins and mutations',async ({request})=>{
  82  |   expect((await request.get('/__sidequest/snapshot',{headers:{Origin:'https://example.com'}})).status()).toBe(403);
  83  |   expect((await request.post('/__sidequest/snapshot')).status()).toBe(405);
  84  |   expect((await request.get('/__sidequest/diff/not-a-file')).status()).toBe(404);
  85  | });
  86  | for (const width of [960,390]) test(`viewer reflows at ${width}px with reduced motion`,async ({page})=>{
  87  |   const errors:string[]=[];page.on('pageerror',error=>errors.push(error.message));
  88  |   await page.setViewportSize({width,height:780});await page.emulateMedia({reducedMotion:'reduce'});
  89  |   await page.goto('/');await expect(page.locator('.app-footer')).toHaveAttribute('data-actor-status','ready',{timeout:60000});await page.getByRole('combobox',{name:'Office navigation'}).selectOption('parent_019');
  90  |   await expect(page.getByTestId('diff-editor')).toHaveCount(1);
  91  |   await page.getByRole('button',{name:'Expand',exact:true}).click();
  92  |   expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  93  |   await page.screenshot({path:path.join(evidence,`viewer-${width}.png`)});
  94  |   await page.keyboard.press('Escape');await expect(page.getByTestId('diff-editor')).toHaveCount(0);
  95  |   expect(errors).toEqual([]);
  96  | });
  97  |
  98  | test('keyboard-accessible viewer has no automated WCAG A/AA violations',async({page})=>{
  99  |   await page.goto('/');await expect(page.locator('.app-footer')).toHaveAttribute('data-actor-status','ready',{timeout:60000}); await page.getByRole('combobox',{name:'Office navigation'}).selectOption('parent_019');
  100 |   await expect(page.getByTestId('diff-editor').locator('.monaco-editor').last()).toBeVisible();
  101 |   await page.getByRole('button',{name:'Expand',exact:true}).click();
  102 |   await expect(page.getByTestId('diff-editor').locator('.monaco-editor').last()).toBeVisible();
  103 |   const code=page.getByRole('button',{name:/dev\/luna\.py/});
  104 |   if(await code.count()) {await code.click();await expect(page.getByTestId('diff-editor').locator('.view-lines').last()).toBeVisible();}
  105 |   const results=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze();
  106 |   await writeFile(path.join(evidence,'accessibility.json'),JSON.stringify(results.violations,null,2));
  107 |   expect(results.violations.map(item=>({id:item.id,impact:item.impact,description:item.description}))).toEqual([]);
  108 | });
  109 |
  110 | test('hostile source stays literal and a failed read can retry',async({page})=>{
  111 |   let fail=true;
  112 |   await page.route('**/__sidequest/diff/*',async route=>{
  113 |     if(fail){await route.fulfill({status:503,json:{error:'test-only failure'}});return;}
  114 |     const response=await route.fetch();const data=await response.json();
  115 |     await route.fulfill({json:{...data,original:'',modified:'<script>window.__executed=true</script>\n<img src=x onerror="window.__executed=true">',language:'plaintext'}});
  116 |   });
  117 |   await page.goto('/');await expect(page.locator('.app-footer')).toHaveAttribute('data-actor-status','ready',{timeout:60000});await page.getByRole('combobox',{name:'Office navigation'}).selectOption('parent_019');
  118 |   await expect(page.getByRole('alert')).toContainText('Local Git read failed');
  119 |   fail=false;await page.getByRole('button',{name:'Refresh repository'}).click();
  120 |   await expect(page.getByTestId('diff-editor')).toHaveCount(1);
  121 |   await expect(page.getByTestId('diff-editor').locator('.view-lines').last()).toContainText('<script>');
  122 |   expect(await page.evaluate(()=>Object.hasOwn(window,'__executed'))).toBe(false);
  123 | });
  124 |
```
