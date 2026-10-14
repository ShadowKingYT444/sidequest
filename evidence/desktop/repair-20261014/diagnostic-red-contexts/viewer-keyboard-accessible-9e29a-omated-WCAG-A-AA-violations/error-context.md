# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: viewer.spec.ts >> keyboard-accessible viewer has no automated WCAG A/AA violations
- Location: tests/browser/viewer.spec.ts:106:1

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByTestId('diff-editor').locator('.monaco-editor').last()
Expected: visible
Timeout: 15000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" getByTestId('diff-editor').locator('.monaco-editor').last() with timeout 15000ms
  - waiting for getByTestId('diff-editor').locator('.monaco-editor').last()

```

```yaml
- main:
  - text: sidequest sidequest-eval-source
  - button "Notifications, 2 recorded, 2 need attention": Notifications
  - button "Settings"
  - button "Jobs"
  - button "Refresh Git"
  - text: Computer 19
  - navigation "Computer view":
    - button "Trace"
    - button "Files" [pressed]
    - button "Task setup"
  - button "Expand"
  - button "Return to office": Office Esc
  - region "Computer work viewer":
    - text: Git diff 69bf0669 → 5f02817d Committed revisions
    - navigation "Changed files":
      - paragraph: 505 changed files
      - button "M .gitignore" [pressed]
      - button "M AGENTS.md"
      - button "M README.md"
      - button "M SPEC.md"
      - button "+ contracts/EXTENSIONS.md"
      - button "M contracts/PROTOCOL.md"
      - button "+ contracts/STORAGE.md"
      - button "+ contracts/examples/computer.json"
      - button "+ demo/README.md"
      - button "+ demo/club-site/README.md"
      - button "+ demo/club-site/bad/index.html"
      - button "+ demo/club-site/bad/members/signup.html"
      - button "+ demo/club-site/known-good/index.html"
      - button "+ demo/club-site/known-good/members/welcome.html"
      - button "+ desktop/README.md"
      - button "+ desktop/THIRD_PARTY_NOTICES.md"
      - button "+ desktop/archive/rejected-2026-10-14/ProviderSettings.css.txt"
      - button "+ desktop/archive/rejected-2026-10-14/ProviderSettings.tsx.txt"
      - button "+ desktop/archive/rejected-2026-10-14/README.md"
      - button "+ desktop/archive/rejected-2026-10-14/TemporaryOffice.tsx.txt"
      - button "+ desktop/archive/rejected-2026-10-14/visual-office.spec.ts.txt"
      - button "+ desktop/electron/git-reader.cjs"
      - button "+ desktop/electron/main.cjs"
      - button "+ desktop/electron/preload.cjs"
      - button "+ desktop/electron/provider-discovery.cjs"
      - button "+ desktop/electron/runtime-client.cjs"
      - button "+ desktop/electron/security.cjs"
      - button "+ desktop/electron/static-server.cjs"
      - button "+ desktop/index.html"
      - button "+ desktop/package-lock.json"
      - button "+ desktop/package.json"
      - button "+ desktop/public/office/actors.json"
      - button "+ desktop/public/office/actors/SQ_HUMAN_01_INK_HOODIE.glb binary"
      - button "+ desktop/public/office/actors/SQ_HUMAN_02_CLAY_CARDIGAN.glb binary"
      - button "+ desktop/public/office/actors/SQ_HUMAN_03_SAGE_OVERSHIRT.glb binary"
      - button "+ desktop/public/office/actors/SQ_HUMAN_04_SLATE_BEANIE.glb binary"
      - button "+ desktop/public/office/actors/SQ_HUMAN_04_SLATE_BEANIE__CAP_READY.glb binary"
      - button "+ desktop/public/office/actors/SQ_HUMAN_05_OAT_HEADPHONES.glb binary"
      - button "+ desktop/public/office/actors/SQ_HUMAN_06_PLUM_WAVE.glb binary"
      - button "+ desktop/public/office/bindings.json"
      - button "+ desktop/public/office/caps/SQ_CAP_BASE_01_INK_HOODIE.glb binary"
      - button "+ desktop/public/office/caps/SQ_CAP_BASE_02_CLAY_CARDIGAN.glb binary"
      - button "+ desktop/public/office/caps/SQ_CAP_BASE_03_SAGE_OVERSHIRT.glb binary"
      - button "+ desktop/public/office/caps/SQ_CAP_BASE_04_SLATE_BEANIE.glb binary"
      - button "+ desktop/public/office/caps/SQ_CAP_BASE_05_OAT_HEADPHONES.glb binary"
      - button "+ desktop/public/office/caps/SQ_CAP_BASE_06_PLUM_WAVE.glb binary"
      - button "+ desktop/public/office/caps/SQ_CAP_CLAUDE_CODE.glb binary"
      - button "+ desktop/public/office/caps/SQ_CAP_CODEX.glb binary"
      - button "+ desktop/public/office/caps/SQ_CAP_DEEPSEEK.glb binary"
      - button "+ desktop/public/office/caps/SQ_CAP_GOOGLE_GEMINI.glb binary"
      - button "+ desktop/public/office/caps/SQ_CAP_HARNESS_OPENCODE.glb binary"
      - button "+ desktop/public/office/caps/SQ_CAP_XAI_GROK.glb binary"
      - button "+ desktop/public/office/caps/attachment-profiles.json"
      - button "+ desktop/public/office/caps/textures/CLAUDE_CODE_cap_RGBA.png binary"
      - button "+ desktop/public/office/caps/textures/CODEX_cap_RGBA.png binary"
      - button "+ desktop/public/office/caps/textures/DEEPSEEK_cap_RGBA.png binary"
      - button "+ desktop/public/office/caps/textures/GOOGLE_GEMINI_cap_RGBA.png binary"
      - button "+ desktop/public/office/caps/textures/HARNESS_OPENCODE_cap_RGBA.png binary"
      - button "+ desktop/public/office/caps/textures/XAI_GROK_cap_RGBA.png binary"
      - button "+ desktop/public/office/caps/textures/portable_CLAUDE_CODE_cap_RGBA.png binary"
      - button "+ desktop/public/office/caps/textures/portable_CODEX_cap_RGBA.png binary"
      - button "+ desktop/public/office/caps/textures/portable_DEEPSEEK_cap_RGBA.png binary"
      - button "+ desktop/public/office/caps/textures/portable_GOOGLE_GEMINI_cap_RGBA.png binary"
      - button "+ desktop/public/office/caps/textures/portable_HARNESS_OPENCODE_cap_RGBA.png binary"
      - button "+ desktop/public/office/caps/textures/portable_XAI_GROK_cap_RGBA.png binary"
      - button "+ desktop/public/office/office.glb binary"
      - button "+ desktop/public/office/provenance.json"
      - button "+ desktop/public/office/textures/000-5f7bdfb1f68d.png binary"
      - button "+ desktop/public/office/textures/001-e3f0f809bf28.png binary"
      - button "+ desktop/public/office/textures/002-73a581383e55.png binary"
      - button "+ desktop/public/office/textures/003-42a6cb087d1a.png binary"
      - button "+ desktop/public/office/textures/004-aa3684ec0d5d.png binary"
      - button "+ desktop/public/office/textures/005-c67eef46c964.png binary"
      - button "+ desktop/public/office/textures/006-cfef99972f8d.png binary"
      - button "+ desktop/public/office/textures/007-d7f09932a45e.png binary"
      - button "+ desktop/public/office/textures/008-261f2dc0c27f.png binary"
      - button "+ desktop/public/office/textures/009-5ec1531a7774.png binary"
      - button "+ desktop/public/office/textures/010-b50cde1be412.png binary"
      - button "+ desktop/public/office/textures/011-da20a21009b0.png binary"
      - button "+ desktop/public/office/textures/012-5fb6a195a6d0.png binary"
      - button "+ desktop/public/office/textures/013-030bbd3c246a.png binary"
      - button "+ desktop/public/office/textures/014-95ba0185529a.png binary"
      - button "+ desktop/public/office/textures/015-e91284228ee5.png binary"
      - button "+ desktop/public/office/textures/016-8d6b2608d7d4.png binary"
      - button "+ desktop/public/office/textures/017-cf079bee7cc0.png binary"
      - button "+ desktop/public/office/textures/018-dad4731dd5e9.png binary"
      - button "+ desktop/public/office/textures/019-6cc42254870a.png binary"
      - button "+ desktop/public/office/textures/020-cf38045cff0b.png binary"
      - button "+ desktop/public/office/textures/021-f11261547ae2.png binary"
      - button "+ desktop/public/office/textures/022-3a28bf00e6f3.png binary"
      - button "+ desktop/public/office/textures/023-3353bcb15da6.png binary"
      - button "+ desktop/public/office/textures/024-8b94eb98daa7.png binary"
      - button "+ desktop/public/office/textures/025-a7641b9f0046.png binary"
      - button "+ desktop/public/office/textures/026-1756bda8e2da.png binary"
      - button "+ desktop/public/office/textures/027-31d9705ab53c.png binary"
      - button "+ desktop/public/office/textures/028-57a4d2641279.png binary"
      - button "+ desktop/public/office/textures/029-bc9ae9cc5f4e.png binary"
      - button "+ desktop/public/office/textures/030-1c956c3052dc.png binary"
      - button "+ desktop/public/office/textures/031-0f66c39463bd.png binary"
      - button "+ desktop/public/office/textures/032-0deb2c916372.png binary"
      - button "+ desktop/public/office/textures/033-913df5ba81b4.png binary"
      - button "+ desktop/public/office/textures/034-5d8f204e7952.png binary"
      - button "+ desktop/public/office/textures/035-b8835794a99b.png binary"
      - button "+ desktop/public/office/textures/036-f33d1e12dbbf.png binary"
      - button "+ desktop/public/office/textures/037-6ca35f69eac2.png binary"
      - button "+ desktop/public/office/textures/038-a3948a0a97a4.png binary"
      - button "+ desktop/public/office/textures/039-eb77053a262d.png binary"
      - button "+ desktop/public/office/textures/040-c99aa6581e46.png binary"
      - button "+ desktop/public/office/textures/041-402697d1f0d9.png binary"
      - button "+ desktop/public/office/textures/042-1c3b858d4453.png binary"
      - button "+ desktop/public/office/textures/043-7dbcdfb43917.png binary"
      - button "+ desktop/public/office/textures/044-1f3bb8f1b133.png binary"
      - button "+ desktop/public/office/textures/045-39b7bd7d8508.png binary"
      - button "+ desktop/public/office/textures/046-de6441941c79.png binary"
      - button "+ desktop/public/office/textures/047-d7e935df6e30.png binary"
      - button "+ desktop/public/office/textures/048-c45ac1f37852.png binary"
      - button "+ desktop/public/office/textures/049-0429fe89e120.png binary"
      - button "+ desktop/public/office/textures/050-e5c6e6efd949.png binary"
      - button "+ desktop/public/office/textures/051-f7c99779e3e3.png binary"
      - button "+ desktop/public/office/textures/052-abfa3f18fc21.png binary"
      - button "+ desktop/public/office/textures/053-d8f017bee59e.png binary"
      - button "+ desktop/public/office/textures/054-3bd8e1c67ea0.png binary"
      - button "+ desktop/public/office/textures/055-89153dc540de.png binary"
      - button "+ desktop/public/office/textures/056-48198a777799.png binary"
      - button "+ desktop/public/office/textures/057-683e62491afd.png binary"
      - button "+ desktop/public/office/textures/058-53815d7064c5.png binary"
      - button "+ desktop/public/office/textures/059-465b8243feca.png binary"
      - button "+ desktop/public/office/textures/060-b129cc854ff7.png binary"
      - button "+ desktop/public/office/textures/061-221b55c5bae1.png binary"
      - button "+ desktop/public/office/textures/062-2e201ba51820.png binary"
      - button "+ desktop/public/office/textures/063-3275357c4515.png binary"
      - button "+ desktop/public/office/textures/064-d96f787276fc.png binary"
      - button "+ desktop/public/office/textures/065-3bc93c8664f1.png binary"
      - button "+ desktop/public/office/textures/066-b9560a27c56c.png binary"
      - button "+ desktop/public/office/textures/067-4806882067d2.png binary"
      - button "+ desktop/public/office/textures/068-02ecefed9c39.png binary"
      - button "+ desktop/public/office/textures/069-557863d8cbcb.png binary"
      - button "+ desktop/public/office/textures/070-7f8c8d3a8075.png binary"
      - button "+ desktop/public/office/textures/071-d59410915911.png binary"
      - button "+ desktop/public/office/textures/072-506efc8123ff.png binary"
      - button "+ desktop/public/office/textures/073-7d17b351727a.png binary"
      - button "+ desktop/public/office/textures/074-7f8c8d3a8075.png binary"
      - button "+ desktop/public/office/textures/075-86157fa8db15.png binary"
      - button "+ desktop/public/office/textures/076-9a83fbac9122.png binary"
      - button "+ desktop/public/office/textures/077-79e389e4f05a.png binary"
      - button "+ desktop/public/office/textures/078-67a486543e20.png binary"
      - button "+ desktop/public/office/textures/079-98399ba6ba8b.png binary"
      - button "+ desktop/public/office/textures/080-368504af228e.png binary"
      - button "+ desktop/public/office/textures/081-5e1fcfa3a20d.png binary"
      - button "+ desktop/public/office/textures/082-5729b7ff67ce.png binary"
      - button "+ desktop/public/office/textures/083-870eac0ac896.png binary"
      - button "+ desktop/public/office/textures/084-586373354fb7.png binary"
      - button "+ desktop/public/office/textures/085-ea4b2da7b618.png binary"
      - button "+ desktop/public/office/textures/086-2120d65837c5.png binary"
      - button "+ desktop/public/office/textures/087-83d4a5392a03.png binary"
      - button "+ desktop/public/office/textures/088-817ff0490416.png binary"
      - button "+ desktop/public/office/textures/089-add7c0a1e4fc.png binary"
      - button "+ desktop/scripts/electron-smoke.mjs"
      - button "+ desktop/scripts/inspect-assets.mjs"
      - button "+ desktop/scripts/install-office.py"
      - button "+ desktop/src/AgentBadge.tsx"
      - button "+ desktop/src/App.tsx"
      - button "+ desktop/src/DiffEditor.tsx"
      - button "+ desktop/src/JobsBoard.tsx"
      - button "+ desktop/src/MonitorSession.css"
      - button "+ desktop/src/MonitorSession.tsx"
      - button "+ desktop/src/NotificationTray.css"
      - button "+ desktop/src/NotificationTray.tsx"
      - button "+ desktop/src/OfficeScene.tsx"
      - button "+ desktop/src/OriginalActors.tsx"
      - button "+ desktop/src/PromptComposer.css"
      - button "+ desktop/src/PromptComposer.tsx"
      - button "+ desktop/src/ProviderPicker.css"
      - button "+ desktop/src/ProviderPicker.tsx"
      - button "+ desktop/src/ProviderSettings.css"
      - button "+ desktop/src/ProviderSettings.tsx"
      - button "+ desktop/src/ProviderTiles.css"
      - button "+ desktop/src/ProviderTiles.tsx"
      - button "+ desktop/src/RunActivity.css"
      - button "+ desktop/src/RunActivity.tsx"
      - button "+ desktop/src/SessionCard.tsx"
      - button "+ desktop/src/StationLauncher.css"
      - button "+ desktop/src/StationLauncher.tsx"
      - button "+ desktop/src/UsageTank.css"
      - button "+ desktop/src/UsageTank.tsx"
      - button "+ desktop/src/bridge.ts"
      - button "+ desktop/src/local-drafts.ts"
      - button "+ desktop/src/main.tsx"
      - button "+ desktop/src/notifications.ts"
      - button "+ desktop/src/office-bindings.ts"
      - button "+ desktop/src/provider-readiness.ts"
      - button "+ desktop/src/runtime-identity.ts"
      - button "+ desktop/src/style.css"
      - button "+ desktop/src/types.ts"
      - button "+ desktop/tests/assets.test.mjs"
      - button "+ desktop/tests/bindings.test.mjs"
      - button "+ desktop/tests/browser/jobs-live.spec.ts"
      - button "+ desktop/tests/browser/monitor-ui.spec.ts"
      - button "+ desktop/tests/browser/viewer.spec.ts"
      - button "+ desktop/tests/browser/visual-office.spec.ts"
      - button "+ desktop/tests/git.test.mjs"
      - button "+ desktop/tests/install-office.test.mjs"
      - button "+ desktop/tests/local-drafts.test.mjs"
      - button "+ desktop/tests/notifications.test.mjs"
      - button "+ desktop/tests/provider-readiness.test.mjs"
      - button "+ desktop/tests/runtime-client.test.mjs"
      - button "+ desktop/tests/runtime-identity.test.mjs"
      - button "+ desktop/tests/security.test.mjs"
      - button "+ desktop/tsconfig.json"
      - button "+ dev/luna.py"
      - button "M dev/plan.json"
      - button "+ dev/test_luna.py"
      - button "+ dev/test_specs.py"
      - button "+ docs/ARCHITECTURE.md"
      - button "M docs/ART_DIRECTION.md"
      - button "+ docs/ASSET_BINDING.md"
      - button "+ docs/CLOUD_HANDOFF.md"
      - button "+ docs/COMPUTER_UI.md"
      - button "+ docs/EXECUTION.md"
      - button "+ docs/FEATURE_MATRIX.md"
      - button "+ docs/MVP_ACCEPTANCE.md"
      - button "+ docs/NATIVE_HOST_STATUS.md"
      - button "M docs/PARALLEL_PLAN.md"
      - button "M docs/RESEARCH.md"
      - button "+ docs/RUN_EVALS.md"
      - button "M docs/SETUP_VERIFICATION.md"
      - button "M docs/START_HERE.md"
      - button "M docs/VALIDATION.md"
      - button "+ docs/archive/SPEC-0.2.md"
      - button "M docs/goals/A-runtime.md"
      - button "M docs/goals/B-tools.md"
      - button "+ docs/goals/C-desktop.md"
      - button "M docs/goals/C-unity.md"
      - button "M docs/goals/D-workshops.md"
      - button "M docs/goals/I1-integration.md"
      - button "+ evidence/A/A1-final-review.json"
      - button "+ evidence/A/A1-review-2.json"
      - button "+ evidence/A/A1-review.json"
      - button "+ evidence/A/A1.json"
      - button "+ evidence/A/A2-repair-review.json"
      - button "+ evidence/A/A2-review.json"
      - button "+ evidence/A/A2.json"
      - button "+ evidence/A/A3-repair-review.json"
      - button "+ evidence/A/A3-review.json"
      - button "+ evidence/A/A3.json"
      - button "+ evidence/B/B1-repair-review.json"
      - button "+ evidence/B/B1-review.json"
      - button "+ evidence/B/B1.json"
      - button "+ evidence/B/B2-readiness.json"
      - button "+ evidence/B/B2-repair-review.json"
      - button "+ evidence/B/B2-review.json"
      - button "+ evidence/B/native-setup-diagnosis.json"
      - button "+ evidence/B/source-filter-repair.json"
      - button "+ evidence/B/source-filter-review.json"
      - button "+ evidence/C/final-desktop-review.json"
      - button "+ evidence/C/native-smoke-repair-review.json"
      - button "+ evidence/C/runtime-bridge-repair-review.json"
      - button "+ evidence/C/runtime-bridge-review.json"
      - button "+ evidence/D/D1-previous-20261014t015727796417z.json"
      - button "+ evidence/D/D1-previous-20261014t021328344314z.json"
      - button "+ evidence/D/D1-previous-20261014t034618559898z.json"
      - button "+ evidence/D/D1-review.json"
      - button "+ evidence/D/D1.json"
      - button "+ evidence/D/harness-lock-adjustment.json"
      - button "+ evidence/D/inputs/bad-manifest-20261014t015727796417z.json"
      - button "+ evidence/D/inputs/bad-manifest-20261014t021328344314z.json"
      - button "+ evidence/D/inputs/bad-manifest-20261014t034618559898z.json"
      - button "+ evidence/D/inputs/bad-manifest.json"
      - button "+ evidence/D/inputs/known-good-manifest-20261014t015727796417z.json"
      - button "+ evidence/D/inputs/known-good-manifest-20261014t021328344314z.json"
      - button "+ evidence/D/inputs/known-good-manifest-20261014t034618559898z.json"
      - button "+ evidence/D/inputs/known-good-manifest.json"
      - button "+ evidence/D/outputs/check-d1-bad-20261014t015727796417z-32a04073/after.png binary"
      - button "+ evidence/D/outputs/check-d1-bad-20261014t015727796417z-32a04073/before.png binary"
      - button "+ evidence/D/outputs/check-d1-bad-20261014t015727796417z-32a04073/check-report.json"
      - button "+ evidence/D/outputs/check-d1-bad-20261014t021328344314z-32a04073/after.png binary"
      - button "+ evidence/D/outputs/check-d1-bad-20261014t021328344314z-32a04073/before.png binary"
      - button "+ evidence/D/outputs/check-d1-bad-20261014t021328344314z-32a04073/check-report.json"
      - button "+ evidence/D/outputs/check-d1-bad-20261014t034618559898z-32a04073/after.png binary"
      - button "+ evidence/D/outputs/check-d1-bad-20261014t034618559898z-32a04073/before.png binary"
      - button "+ evidence/D/outputs/check-d1-bad-20261014t034618559898z-32a04073/check-report.json"
      - button "+ evidence/D/outputs/check-d1-bad-32a04073/after.png binary"
      - button "+ evidence/D/outputs/check-d1-bad-32a04073/before.png binary"
      - button "+ evidence/D/outputs/check-d1-bad-32a04073/check-report.json"
      - button "+ evidence/D/outputs/check-d1-known-good-20261014t015727796417z-430a53d1/after.png binary"
      - button "+ evidence/D/outputs/check-d1-known-good-20261014t015727796417z-430a53d1/before.png binary"
      - button "+ evidence/D/outputs/check-d1-known-good-20261014t015727796417z-430a53d1/check-report.json"
      - button "+ evidence/D/outputs/check-d1-known-good-20261014t021328344314z-430a53d1/after.png binary"
      - button "+ evidence/D/outputs/check-d1-known-good-20261014t021328344314z-430a53d1/before.png binary"
      - button "+ evidence/D/outputs/check-d1-known-good-20261014t021328344314z-430a53d1/check-report.json"
      - button "+ evidence/D/outputs/check-d1-known-good-20261014t034618559898z-430a53d1/after.png binary"
      - button "+ evidence/D/outputs/check-d1-known-good-20261014t034618559898z-430a53d1/before.png binary"
      - button "+ evidence/D/outputs/check-d1-known-good-20261014t034618559898z-430a53d1/check-report.json"
      - button "+ evidence/D/outputs/check-d1-known-good-430a53d1/after.png binary"
      - button "+ evidence/D/outputs/check-d1-known-good-430a53d1/before.png binary"
      - button "+ evidence/D/outputs/check-d1-known-good-430a53d1/check-report.json"
      - button "+ evidence/desktop/README.md"
      - button "+ evidence/desktop/accessibility.json"
      - button "+ evidence/desktop/agent-session-390.png binary"
      - button "+ evidence/desktop/agent-session.png binary"
      - button "+ evidence/desktop/asset-transfer.json"
      - button "+ evidence/desktop/assigned-result.png binary"
      - button "+ evidence/desktop/badge-pixel-verification.json"
      - button "+ evidence/desktop/browser-first-original-attempt/assigned-scroll-after-visibility-guard.md"
      - button "+ evidence/desktop/browser-first-original-attempt/jobs-live-real-jobs-clear--ce5fb-e-assigned-computer-results.md"
      - button "+ evidence/desktop/browser-first-original-attempt/scroll-placeholder-trace.txt"
      - button "+ evidence/desktop/browser-first-original-attempt/session-host-bridge-before-restart.md"
      - button "+ evidence/desktop/browser-first-original-attempt/session-target-size-full-suite.md"
      - button "+ evidence/desktop/browser-first-original-attempt/viewer-hostile-source-stay-43665-and-a-failed-read-can-retry.md"
      - button "+ evidence/desktop/browser-first-original-attempt/viewer-real-Git-diff-lazy--f5b01-d-state-Escape-and-keyboard.md"
      - button "+ evidence/desktop/browser-first-original-attempt/viewer-viewer-reflows-at-390px-with-reduced-motion.md"
      - button "+ evidence/desktop/browser-first-original-attempt/visual-office-provider-settings-and-preserved-work-at-1440px.md"
      - button "+ evidence/desktop/checkpoint.json"
      - button "+ evidence/desktop/electron-smoke.json"
      - button "+ evidence/desktop/expanded-diff.png binary"
      - button "+ evidence/desktop/final-11-run.json"
      - button "+ evidence/desktop/final-11-viewer-error-context.md"
      - button "+ evidence/desktop/git-diff.png binary"
      - button "+ evidence/desktop/job-390.png binary"
      - button "+ evidence/desktop/job-960.png binary"
      - button "+ evidence/desktop/job-accessibility.json"
      - button "+ evidence/desktop/job-browser.json"
      - button "+ evidence/desktop/job-check-report.png binary"
      - button "+ evidence/desktop/job-diff.png binary"
      - button "+ evidence/desktop/job-queued.png binary"
      - button "+ evidence/desktop/job-readiness.png binary"
      - button "+ evidence/desktop/job-responsive-accessibility.json"
      - button "+ evidence/desktop/job-result.png binary"
      - button "+ evidence/desktop/monaco-reopen-before-fix.json"
      - button "+ evidence/desktop/monaco-reopen-diagnosis.json"
      - button "+ evidence/desktop/monaco-reopen-repair.json"
      - button "+ evidence/desktop/monaco-single-reopen-red-context.md"
      - button "+ evidence/desktop/monaco-single-reopen-red.json"
      - button "+ evidence/desktop/monaco-single-reopen-scroll-setup.txt"
      - button "+ evidence/desktop/monaco-single-reopen.json"
      - button "+ evidence/desktop/monitor-camera-browser.json"
      - button "+ evidence/desktop/monitor-camera-timing.json"
      - button "+ evidence/desktop/monitor-full-17-desktop-settings-startup-error-context.md"
      - button "+ evidence/desktop/monitor-full-17-jobs-results-error-context.md"
      - button "+ evidence/desktop/monitor-full-17-recorded-session-error-context.md"
      - button "+ evidence/desktop/monitor-full-17-run.json"
      - button "+ evidence/desktop/monitor-full-17-viewer-accessibility-startup-error-context.md"
      - button "+ evidence/desktop/monitor-library-upload.json"
      - button "+ evidence/desktop/monitor-local-draft-390.png binary"
      - button "+ evidence/desktop/monitor-pov-local-draft.png binary"
      - button "+ evidence/desktop/monitor-pov.png binary"
      - button "+ evidence/desktop/monitor-recovery-notes.md"
      - button "+ evidence/desktop/monitor-reviewed-checkpoint.json"
      - button "+ evidence/desktop/monitor-revision-audit.json"
      - button "+ evidence/desktop/monitor-revision-checkpoint.json"
      - button "+ evidence/desktop/monitor-task-setup-390.png binary"
      - button "+ evidence/desktop/monitor-task-setup.png binary"
      - button "+ evidence/desktop/monitor-ui-browser.json"
      - button "+ evidence/desktop/monitor-ui-fifth-timing.json"
      - button "+ evidence/desktop/monitor-ui-timing.json"
      - button "+ evidence/desktop/native-supported-paths.json"
      - button "+ evidence/desktop/notifications-badges-fixture.png binary"
      - button "+ evidence/desktop/notifications-browser.json"
      - button "+ evidence/desktop/office-desk-debug.png binary"
      - button "+ evidence/desktop/office-desk.png binary"
      - button "+ evidence/desktop/office-expanded.png binary"
      - button "+ evidence/desktop/office-temporary.png binary"
      - button "+ evidence/desktop/original-office-pending.png binary"
      - button "+ evidence/desktop/original-office/README.md"
      - button "+ evidence/desktop/original-office/actor-import-verification.json"
      - button "+ evidence/desktop/original-office/archive-paths.json"
      - button "+ evidence/desktop/original-office/archive-verification.json"
      - button "+ evidence/desktop/original-office/asset-import-browser-validation.json"
      - button "+ evidence/desktop/original-office/asset-import-original-office-expanded.png binary"
      - button "+ evidence/desktop/original-office/asset-import-original-office-monitor.png binary"
      - button "+ evidence/desktop/original-office/asset-import-original-office-overview.png binary"
      - button "+ evidence/desktop/original-office/asset-validation.json"
      - button "+ evidence/desktop/original-office/binding-measurements.json"
      - button "+ evidence/desktop/original-office/browser-actor-validation.json"
      - button "+ evidence/desktop/original-office/browser-binding-validation.json"
      - button "+ evidence/desktop/original-office/browser-validation.json"
      - button "+ evidence/desktop/original-office/capture-browser.mjs"
      - button "+ evidence/desktop/original-office/check-browser-actors.mjs"
      - button "+ evidence/desktop/original-office/check-browser-bindings.mjs"
      - button "+ evidence/desktop/original-office/context-screenshot-library.json"
      - button "+ evidence/desktop/original-office/create-bindings.py"
      - button "+ evidence/desktop/original-office/externalize-images.py"
      - button "+ evidence/desktop/original-office/import-actors.py"
      - button "+ evidence/desktop/original-office/installer-result.json"
      - button "+ evidence/desktop/original-office/loader-fix-probe.json"
      - button "+ evidence/desktop/original-office/lossless-resource-verification.json"
      - button "+ evidence/desktop/original-office/measure-native.py"
      - button "+ evidence/desktop/original-office/native-measurements.json"
      - button "+ evidence/desktop/original-office/office-inspection.json"
      - button "+ evidence/desktop/original-office/original-actor-context-card.png binary"
      - button "+ evidence/desktop/original-office/original-board-task-detail.png binary"
      - button "+ evidence/desktop/original-office/original-office-expanded.png binary"
      - button "+ evidence/desktop/original-office/original-office-monitor.png binary"
      - button "+ evidence/desktop/original-office/original-office-overview.png binary"
      - button "+ evidence/desktop/original-office/original-workstation-context-card.png binary"
      - button "+ evidence/desktop/original-office/physical-monitor-occlusion-first-attempt.txt"
      - button "+ evidence/desktop/original-office/probe-loader-fix.mjs"
      - button "+ evidence/desktop/original-office/runtime-inspection.json"
      - button "+ evidence/desktop/original-office/safe-extract.py"
      - button "+ evidence/desktop/original-office/screenshot-library.json"
      - button "+ evidence/desktop/original-office/sidequest-original-actor-assembly-result.json"
      - button "+ evidence/desktop/original-office/sidequest-original-actors-react-result.json"
      - button "+ evidence/desktop/original-office/sidequest-original-slate-static.png binary"
      - button "+ evidence/desktop/original-office/validate-assets.mjs"
      - button "+ evidence/desktop/prior-monaco-reopen-12-verification.json"
      - button "+ evidence/desktop/prior-office-verification.json"
      - button "+ evidence/desktop/prior-recovery-checkpoint.json"
      - button "+ evidence/desktop/prior-sanitizer-bundle.json"
      - button "+ evidence/desktop/prior-verification.json"
      - button "+ evidence/desktop/prior-visual/accessibility.json"
      - button "+ evidence/desktop/prior-visual/expanded-diff.png binary"
      - button "+ evidence/desktop/prior-visual/git-diff.png binary"
      - button "+ evidence/desktop/prior-visual/job-browser.json"
      - button "+ evidence/desktop/prior-visual/job-check-report.png binary"
      - button "+ evidence/desktop/prior-visual/job-result.png binary"
      - button "+ evidence/desktop/prior-visual/setup-desktop.png binary"
      - button "+ evidence/desktop/prior-visual/verification.json"
      - button "+ evidence/desktop/prior-visual/viewer-390.png binary"
      - button "+ evidence/desktop/prior-visual/viewer-960.png binary"
      - button "+ evidence/desktop/provider-accessibility-1440.json"
      - button "+ evidence/desktop/provider-accessibility-390.json"
      - button "+ evidence/desktop/provider-selector-390.png binary"
      - button "+ evidence/desktop/provider-selector.png binary"
      - button "+ evidence/desktop/provider-settings-390.png binary"
      - button "+ evidence/desktop/provider-settings-analytics-390.png binary"
      - button "+ evidence/desktop/provider-settings-analytics.png binary"
      - button "+ evidence/desktop/provider-settings-limits-390.png binary"
      - button "+ evidence/desktop/provider-settings-limits.png binary"
      - button "+ evidence/desktop/provider-settings-rejected.png binary"
      - button "+ evidence/desktop/provider-settings.png binary"
      - button "+ evidence/desktop/recorded-session-390.png binary"
      - button "+ evidence/desktop/recorded-session.png binary"
      - button "+ evidence/desktop/recovered-office.png binary"
      - button "+ evidence/desktop/recovery-capture.json"
      - button "+ evidence/desktop/repaired-12-run.json"
      - button "+ evidence/desktop/result-display-browser.json"
      - button "+ evidence/desktop/run-activity-actual.png binary"
      - button "+ evidence/desktop/run-activity-checkpoint-qa.json"
      - button "+ evidence/desktop/run-activity-visibility-recheck.json"
      - button "+ evidence/desktop/sanitizer-bundle.json"
      - button "+ evidence/desktop/scroll-restoration-body-ready-pass.txt"
      - button "+ evidence/desktop/security-audit-all.json"
      - button "+ evidence/desktop/security-audit.json"
      - button "+ evidence/desktop/session-accessibility.json"
      - button "+ evidence/desktop/session-browser.json"
      - button "+ evidence/desktop/session-library-upload.json"
      - button "+ evidence/desktop/settings-screenshot-library.json"
      - button "+ evidence/desktop/setup-desktop.png binary"
      - button "+ evidence/desktop/t3-source.json"
      - button "+ evidence/desktop/verification.json"
      - button "+ evidence/desktop/viewer-390.png binary"
      - button "+ evidence/desktop/viewer-960.png binary"
      - button "+ evidence/desktop/workstation-launcher-390.png binary"
      - button "+ evidence/desktop/workstation-launcher.png binary"
      - button "M journals/A.md"
      - button "M journals/B.md"
      - button "M journals/C.md"
      - button "M journals/D.md"
      - button "+ services/runtime/README.md"
      - button "+ services/runtime/__init__.py"
      - button "+ services/runtime/adapters.py"
      - button "+ services/runtime/api.py"
      - button "+ services/runtime/artifacts.py"
      - button "+ services/runtime/main.py"
      - button "+ services/runtime/migrations/001_initial.sql"
      - button "+ services/runtime/migrations/002_attempt_worker.sql"
      - button "+ services/runtime/migrations/003_codex_lifecycle.sql"
      - button "+ services/runtime/migrations/004_office_sessions.sql"
      - button "+ services/runtime/models.py"
      - button "+ services/runtime/policy.py"
      - button "+ services/runtime/requirements.lock"
      - button "+ services/runtime/scheduler.py"
      - button "+ services/runtime/store.py"
      - button "+ services/runtime/tests/test_adapters.py"
      - button "+ services/runtime/tests/test_api.py"
      - button "+ services/runtime/tests/test_codex_lifecycle.py"
      - button "+ services/runtime/tests/test_concurrency.py"
      - button "+ services/runtime/tests/test_main.py"
      - button "+ services/runtime/tests/test_policy.py"
      - button "+ services/runtime/tests/test_scheduler_pipeline.py"
      - button "+ services/runtime/tests/test_storage.py"
      - button "+ services/runtime/tests/test_support.py"
      - button "+ services/tools/__init__.py"
      - button "+ services/tools/artifact_capture.py"
      - button "+ services/tools/codex_bridge.py"
      - button "+ services/tools/git_ops.py"
      - button "+ services/tools/main.py"
      - button "+ services/tools/protocol.py"
      - button "+ services/tools/tests/test_codex_bridge.py"
      - button "+ services/tools/tests/test_git_artifacts.py"
      - button "+ services/tools/tests/test_protocol.py"
      - button "+ services/workshops/__init__.py"
      - button "+ services/workshops/browser_checks.py"
      - button "+ services/workshops/checks.py"
      - button "+ services/workshops/identity.py"
      - button "+ services/workshops/main.py"
      - button "+ services/workshops/reports.py"
      - button "+ services/workshops/requirements.lock"
      - button "+ services/workshops/tests/__init__.py"
      - button "+ services/workshops/tests/helpers.py"
      - button "+ services/workshops/tests/test_identity.py"
      - button "+ services/workshops/tests/test_protocol_browser.py"
      - button "+ services/workshops/trust.lock.json"
      - button "+ services/workshops/trusted_checks.json"
      - button "+ tests/e2e/run_d1.py"
    - region "Selected file diff":
      - text: .gitignore Read-only
      - status: Loading diff editor…
    - text: Agent services are not connected in this desktop build.
  - combobox "Office navigation":
    - option "Navigate…" [selected]
    - option "Tasks board"
  - text: 26 staged · 1 recorded sessions Local Git · read-only
```

# Test source

```ts
  8   |   await page.addInitScript(()=>{
  9   |     const trace:unknown[]=[];(window as unknown as {__editorLifecycle:unknown[]}).__editorLifecycle=trace;
  10  |     const record=(phase:string,node:HTMLElement)=>{if(trace.length<100)trace.push({phase,at:performance.now(),testId:node.dataset.testid,fileId:node.dataset.fileId,scrollTop:node.dataset.scrollTop,connected:node.isConnected,children:node.childElementCount});};
  11  |     new MutationObserver(records=>{for(const entry of records){for(const node of entry.addedNodes)if(node instanceof HTMLElement){if(node.matches('.diff-editor'))record('added',node);node.querySelectorAll<HTMLElement>('.diff-editor').forEach(child=>record('added',child));}for(const node of entry.removedNodes)if(node instanceof HTMLElement){if(node.matches('.diff-editor'))record('removed',node);node.querySelectorAll<HTMLElement>('.diff-editor').forEach(child=>record('removed',child));}}}).observe(document,{childList:true,subtree:true});
  12  |   });
  13  | }
  14  | test('real Git diff, lazy single editor, expanded state, Escape and keyboard', async ({ page, request }) => {
  15  |   const errors: string[] = []; page.on('pageerror', error => errors.push(error.message));
  16  |   const consoleErrors:string[]=[];page.on('console',message=>{if(message.type()==='error')consoleErrors.push(message.text());});
  17  |   await traceEditorMounts(page);
  18  |   try {
  19  |   const snapshotResponse = await request.get('/__sidequest/snapshot');
  20  |   expect(snapshotResponse.ok()).toBeTruthy();
  21  |   const snapshot = await snapshotResponse.json();
  22  |   expect(snapshot.mode).toBe('local-git');
  23  |   expect(snapshot.agent.state).toBe('unavailable');
  24  |   const source = snapshot.files.find((file: {path:string}) => file.path === 'dev/luna.py') ?? snapshot.files.find((file: { additions?:number; path:string }) => (file.additions ?? 0) > 120 && /\.(tsx?|py|md)$/.test(file.path)) ?? snapshot.files[0];
  25  |   const diff = await (await request.get(`/__sidequest/diff/${source.id}`)).json();
  26  |   expect(diff.readOnly).toBe(true); expect(diff.modified.length).toBeGreaterThan(100);
  27  |   await page.goto('/');await expect(page.locator('.app-footer')).toHaveAttribute('data-actor-status','ready',{timeout:60000});
  28  |   await expect(page.getByTestId('diff-editor')).toHaveCount(0);
  29  |   await expect(page.getByRole('combobox',{name:'Office navigation'})).toBeEnabled();
  30  |   await page.screenshot({path:path.join(evidence,'setup-desktop.png')});
  31  |   await page.getByRole('combobox',{name:'Office navigation'}).selectOption('parent_019');
  32  |   await page.locator(`.file-list button[data-file-id="${source.id}"]`).click();
  33  |   const editor = page.getByTestId('diff-editor');
  34  |   await expect(editor).toHaveCount(1);
  35  |   await expect(editor.locator('.view-lines').last()).toBeVisible();
  36  |   await editor.locator('.monaco-editor').last().hover();
  37  |   for (let count=0;count<10;count++) { await page.mouse.wheel(0, 800); await page.waitForTimeout(80); }
  38  |   await expect.poll(async () => Number(await editor.getAttribute('data-scroll-top'))).toBeGreaterThan(300);
  39  |   const before = Number(await editor.getAttribute('data-scroll-top'));
  40  |   await page.screenshot({path:path.join(evidence,'git-diff.png')});
  41  |   await page.getByRole('button',{name:'Expand',exact:true}).click();
  42  |   await expect(page.getByRole('dialog', {name:'Computer work viewer'})).toBeVisible();
  43  |   await expect(editor).toHaveCount(1);
  44  |   await expect.poll(async () => Number(await editor.getAttribute('data-scroll-top'))).toBeGreaterThan(Math.max(100,before-250));
  45  |   await page.screenshot({path:path.join(evidence,'expanded-diff.png')});
  46  |   await page.keyboard.press('Escape');
  47  |   await expect(editor).toHaveCount(0);
  48  |   await expect(page.getByRole('combobox',{name:'Office navigation'})).toBeFocused();
  49  |   await page.getByRole('combobox',{name:'Office navigation'}).selectOption('parent_019');
  50  |   await expect(editor).toHaveAttribute('data-file-id',source.id);
  51  |   await expect.poll(async () => Number(await editor.getAttribute('data-scroll-top'))).toBeGreaterThan(100);
  52  |   expect(errors).toEqual([]);
  53  |   } finally {
  54  |     const dom=await page.evaluate(()=>({trace:(window as unknown as {__editorLifecycle:unknown[]}).__editorLifecycle,editors:Array.from(document.querySelectorAll<HTMLElement>('.diff-editor')).map(node=>({testId:node.dataset.testid,fileId:node.dataset.fileId,scrollTop:node.dataset.scrollTop,children:node.childElementCount,htmlPrefix:node.outerHTML.slice(0,400)})),modifiedInputs:document.querySelectorAll('[aria-label="Modified committed file, read-only"]').length,mode:document.querySelector('main')?.getAttribute('data-mode')}));
  55  |     await writeFile(path.join(evidence,'monaco-reopen-diagnosis.json'),JSON.stringify({errors,consoleErrors,...dom},null,2));
  56  |   }
  57  | });
  58  | test('Escape/reopen mounts one selected Monaco editor and keeps its saved scroll',async({page,request})=>{
  59  |   const reads:string[]=[];page.on('request',read=>{if(read.url().includes('/__sidequest/diff/'))reads.push(read.url());});
  60  |   await traceEditorMounts(page);
  61  |   await page.emulateMedia({reducedMotion:'reduce'});
  62  |   const snapshot=await (await request.get('/__sidequest/snapshot')).json();
  63  |   const source=snapshot.files.find((file:{path:string})=>file.path==='dev/luna.py')??snapshot.files.find((file:{additions:number})=>file.additions>120);
  64  |   expect(source).toBeTruthy();
  65  |   await page.goto('/');await expect(page.locator('.app-footer')).toHaveAttribute('data-actor-status','ready',{timeout:60000});
  66  |   const nav=page.getByRole('combobox',{name:'Office navigation'}),editor=page.getByTestId('diff-editor');
  67  |   await nav.selectOption('parent_019');await page.locator(`.file-list button[data-file-id="${source.id}"]`).click();
  68  |   await expect(editor.locator('.view-lines').last()).toBeVisible();
  69  |   await editor.locator('.monaco-editor').last().hover();
  70  |   for(let index=0;index<10;index++){await page.mouse.wheel(0,800);await page.waitForTimeout(80);}
  71  |   await expect.poll(async()=>Number(await editor.getAttribute('data-scroll-top'))).toBeGreaterThan(300);
  72  |   await page.keyboard.press('Escape');await expect(editor).toHaveCount(0);
  73  |   await page.evaluate(()=>{(window as unknown as {__editorLifecycle:unknown[]}).__editorLifecycle.length=0;});
  74  |   await nav.selectOption('parent_019');
  75  |   await expect(editor).toHaveAttribute('data-file-id',source.id);
  76  |   await page.waitForLoadState('networkidle');
  77  |   await expect(editor).toHaveCount(1);
  78  |   await expect.poll(async()=>Number(await editor.getAttribute('data-scroll-top'))).toBeGreaterThan(100);
  79  |   const trace=await page.evaluate(()=>(window as unknown as {__editorLifecycle:{phase:string;fileId:string}[]}).__editorLifecycle);
  80  |   await writeFile(path.join(evidence,'monaco-single-reopen.json'),JSON.stringify({sourceId:source.id,trace},null,2));
  81  |   expect(trace.filter(event=>event.phase==='added'&&event.fileId===source.id)).toHaveLength(1);
  82  |   const beforeRefresh=reads.filter(url=>url.endsWith(source.id)).length;
  83  |   await page.getByRole('button',{name:'Refresh Git',exact:true}).click();
  84  |   await expect.poll(()=>reads.filter(url=>url.endsWith(source.id)).length).toBeGreaterThan(beforeRefresh);
  85  |   await expect(editor).toHaveAttribute('data-file-id',source.id);
  86  |   await expect(editor.locator('.view-lines').last()).toBeVisible();
  87  |   await writeFile(path.join(evidence,'monaco-single-reopen.json'),JSON.stringify({sourceId:source.id,trace,reopenMounts:trace.filter(event=>event.phase==='added'&&event.fileId===source.id).length,readsBeforeRefresh:beforeRefresh,readsAfterRefresh:reads.filter(url=>url.endsWith(source.id)).length,refreshRereadVerified:true},null,2));
  88  | });
  89  | test('read API rejects outside origins and mutations',async ({request})=>{
  90  |   expect((await request.get('/__sidequest/snapshot',{headers:{Origin:'https://example.com'}})).status()).toBe(403);
  91  |   expect((await request.post('/__sidequest/snapshot')).status()).toBe(405);
  92  |   expect((await request.get('/__sidequest/diff/not-a-file')).status()).toBe(404);
  93  | });
  94  | for (const width of [960,390]) test(`viewer reflows at ${width}px with reduced motion`,async ({page})=>{
  95  |   const errors:string[]=[];page.on('pageerror',error=>errors.push(error.message));
  96  |   await page.setViewportSize({width,height:780});await page.emulateMedia({reducedMotion:'reduce'});
  97  |   await page.goto('/');await expect(page.locator('.app-footer')).toHaveAttribute('data-actor-status','ready',{timeout:60000});await page.getByRole('combobox',{name:'Office navigation'}).selectOption('parent_019');
  98  |   await expect(page.getByTestId('diff-editor')).toHaveCount(1);
  99  |   await page.getByRole('button',{name:'Expand',exact:true}).click();
  100 |   expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  101 |   await page.screenshot({path:path.join(evidence,`viewer-${width}.png`)});
  102 |   await page.keyboard.press('Escape');await expect(page.getByTestId('diff-editor')).toHaveCount(0);
  103 |   expect(errors).toEqual([]);
  104 | });
  105 | 
  106 | test('keyboard-accessible viewer has no automated WCAG A/AA violations',async({page})=>{
  107 |   await page.goto('/');await expect(page.locator('.app-footer')).toHaveAttribute('data-actor-status','ready',{timeout:60000}); await page.getByRole('combobox',{name:'Office navigation'}).selectOption('parent_019');
> 108 |   await expect(page.getByTestId('diff-editor').locator('.monaco-editor').last()).toBeVisible();
      |                                                                                  ^ Error: expect(locator).toBeVisible() failed
  109 |   await page.getByRole('button',{name:'Expand',exact:true}).click();
  110 |   await expect(page.getByTestId('diff-editor').locator('.monaco-editor').last()).toBeVisible();
  111 |   const code=page.getByRole('button',{name:/dev\/luna\.py/});
  112 |   if(await code.count()) {await code.click();await expect(page.getByTestId('diff-editor').locator('.view-lines').last()).toBeVisible();}
  113 |   const results=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze();
  114 |   await writeFile(path.join(evidence,'accessibility.json'),JSON.stringify(results.violations,null,2));
  115 |   expect(results.violations.map(item=>({id:item.id,impact:item.impact,description:item.description}))).toEqual([]);
  116 | });
  117 | 
  118 | test('hostile source stays literal and a failed read can retry',async({page})=>{
  119 |   let fail=true;
  120 |   await page.route('**/__sidequest/diff/*',async route=>{
  121 |     if(fail){await route.fulfill({status:503,json:{error:'test-only failure'}});return;}
  122 |     const response=await route.fetch();const data=await response.json();
  123 |     await route.fulfill({json:{...data,original:'',modified:'<script>window.__executed=true</script>\n<img src=x onerror="window.__executed=true">',language:'plaintext'}});
  124 |   });
  125 |   await page.goto('/');await expect(page.locator('.app-footer')).toHaveAttribute('data-actor-status','ready',{timeout:60000});await page.getByRole('combobox',{name:'Office navigation'}).selectOption('parent_019');
  126 |   await expect(page.getByRole('alert')).toContainText('Local Git read failed');
  127 |   fail=false;await page.getByRole('button',{name:'Refresh repository'}).click();
  128 |   await expect(page.getByTestId('diff-editor')).toHaveCount(1);
  129 |   await expect(page.getByTestId('diff-editor').locator('.view-lines').last()).toContainText('<script>');
  130 |   expect(await page.evaluate(()=>Object.hasOwn(window,'__executed'))).toBe(false);
  131 | });
  132 | 
```