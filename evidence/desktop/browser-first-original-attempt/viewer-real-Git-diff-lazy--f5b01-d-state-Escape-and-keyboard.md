# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: viewer.spec.ts >> real Git diff, lazy single editor, expanded state, Escape and keyboard
- Location: tests/browser/viewer.spec.ts:6:1

# Error details

```
Error: expect(locator).toHaveAttribute(expected) failed

Locator: getByTestId('diff-editor')
Expected: "f_0dd9971f4a6e9bf13eb5e48cbb2d370a"
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toHaveAttribute" getByTestId('diff-editor') with timeout 5000ms
  - waiting for getByTestId('diff-editor')

```

```yaml
- main:
  - text: sidequestlocal workspace sidequestfeat/electron-office-diff
  - button "Settings"
  - button "Jobs"
  - button "Refresh Git"
  - region "Computer work viewer":
    - paragraph: Computer 19 · Read-only
    - heading "sidequest" [level=2]
    - button "Expand"
    - button "Return to office": Office Esc
    - text: Git diff 69bf0669 → 8a9fb11c Committed revisions
    - navigation "Changed files":
      - paragraph: 204 changed files
      - button "M .gitignore"
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
      - button "+ desktop/electron/git-reader.cjs"
      - button "+ desktop/electron/main.cjs"
      - button "+ desktop/electron/preload.cjs"
      - button "+ desktop/electron/runtime-client.cjs"
      - button "+ desktop/electron/security.cjs"
      - button "+ desktop/electron/static-server.cjs"
      - button "+ desktop/index.html"
      - button "+ desktop/package-lock.json"
      - button "+ desktop/package.json"
      - button "+ desktop/scripts/electron-smoke.mjs"
      - button "+ desktop/scripts/inspect-assets.mjs"
      - button "+ desktop/scripts/install-office.py"
      - button "+ desktop/src/App.tsx"
      - button "+ desktop/src/DiffEditor.tsx"
      - button "+ desktop/src/JobsBoard.tsx"
      - button "+ desktop/src/OfficeScene.tsx"
      - button "+ desktop/src/bridge.ts"
      - button "+ desktop/src/main.tsx"
      - button "+ desktop/src/office-bindings.ts"
      - button "+ desktop/src/runtime-identity.ts"
      - button "+ desktop/src/style.css"
      - button "+ desktop/src/types.ts"
      - button "+ desktop/tests/assets.test.mjs"
      - button "+ desktop/tests/bindings.test.mjs"
      - button "+ desktop/tests/browser/jobs-live.spec.ts"
      - button "+ desktop/tests/browser/viewer.spec.ts"
      - button "+ desktop/tests/git.test.mjs"
      - button "+ desktop/tests/install-office.test.mjs"
      - button "+ desktop/tests/runtime-client.test.mjs"
      - button "+ desktop/tests/runtime-identity.test.mjs"
      - button "+ desktop/tests/security.test.mjs"
      - button "+ desktop/tsconfig.json"
      - button "+ dev/luna.py" [pressed]
      - button "M dev/plan.json"
      - button "+ dev/test_luna.py"
      - button "+ dev/test_specs.py"
      - button "+ docs/ARCHITECTURE.md"
      - button "M docs/ART_DIRECTION.md"
      - button "+ docs/ASSET_BINDING.md"
      - button "+ docs/COMPUTER_UI.md"
      - button "+ docs/EXECUTION.md"
      - button "+ docs/FEATURE_MATRIX.md"
      - button "+ docs/MVP_ACCEPTANCE.md"
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
      - button "+ evidence/desktop/asset-transfer.json"
      - button "+ evidence/desktop/electron-smoke.json"
      - button "+ evidence/desktop/expanded-diff.png binary"
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
      - button "+ evidence/desktop/sanitizer-bundle.json"
      - button "+ evidence/desktop/security-audit-all.json"
      - button "+ evidence/desktop/security-audit.json"
      - button "+ evidence/desktop/setup-desktop.png binary"
      - button "+ evidence/desktop/verification.json"
      - button "+ evidence/desktop/viewer-390.png binary"
      - button "+ evidence/desktop/viewer-960.png binary"
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
      - text: dev/luna.py Read-only
      - status: Loading Git diff…
    - text: Agent services are not connected in this desktop build.
  - text: Original office 26 staged figures · Sessions unconnected Git read-only · 0 UI model calls
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
> 39 |   await expect(editor).toHaveAttribute('data-file-id',source.id);
     |                        ^ Error: expect(locator).toHaveAttribute(expected) failed
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
  52 |   await expect(page.getByTestId('diff-editor')).toHaveCount(1);
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