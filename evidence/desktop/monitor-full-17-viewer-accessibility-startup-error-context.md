# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: viewer.spec.ts >> keyboard-accessible viewer has no automated WCAG A/AA violations
- Location: tests/browser/viewer.spec.ts:105:1

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
  - text: sidequest sidequest
  - button "Notifications"
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
    - text: Git diff 69bf0669 → 8a9fb11c Committed revisions
    - navigation "Changed files":
      - paragraph: 204 changed files
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
      - button "+ dev/luna.py"
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
      - text: .gitignore Read-only
      - status: Loading diff editor…
    - text: Agent services are not connected in this desktop build.
  - combobox "Office navigation":
    - option "Navigate…" [selected]
    - option "Tasks board"
  - text: 26 staged · no sessions Local Git · read-only
```

# Test source

```ts
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
  58  |   const reads:string[]=[];page.on('request',read=>{if(read.url().includes('/__sidequest/diff/'))reads.push(read.url());});
  59  |   await traceEditorMounts(page);
  60  |   await page.emulateMedia({reducedMotion:'reduce'});
  61  |   const snapshot=await (await request.get('/__sidequest/snapshot')).json();
  62  |   const source=snapshot.files.find((file:{path:string})=>file.path==='dev/luna.py')??snapshot.files.find((file:{additions:number})=>file.additions>120);
  63  |   expect(source).toBeTruthy();
  64  |   await page.goto('/');await expect(page.locator('.app-footer')).toHaveAttribute('data-actor-status','ready',{timeout:60000});
  65  |   const nav=page.getByRole('combobox',{name:'Office navigation'}),editor=page.getByTestId('diff-editor');
  66  |   await nav.selectOption('parent_019');await page.locator(`.file-list button[data-file-id="${source.id}"]`).click();
  67  |   await expect(editor.locator('.view-lines').last()).toBeVisible();
  68  |   await editor.locator('.monaco-editor').last().hover();
  69  |   for(let index=0;index<10;index++){await page.mouse.wheel(0,800);await page.waitForTimeout(80);}
  70  |   await expect.poll(async()=>Number(await editor.getAttribute('data-scroll-top'))).toBeGreaterThan(300);
  71  |   await page.keyboard.press('Escape');await expect(editor).toHaveCount(0);
  72  |   await page.evaluate(()=>{(window as unknown as {__editorLifecycle:unknown[]}).__editorLifecycle.length=0;});
  73  |   await nav.selectOption('parent_019');
  74  |   await expect(editor).toHaveAttribute('data-file-id',source.id);
  75  |   await page.waitForLoadState('networkidle');
  76  |   await expect(editor).toHaveCount(1);
  77  |   await expect.poll(async()=>Number(await editor.getAttribute('data-scroll-top'))).toBeGreaterThan(100);
  78  |   const trace=await page.evaluate(()=>(window as unknown as {__editorLifecycle:{phase:string;fileId:string}[]}).__editorLifecycle);
  79  |   await writeFile(path.join(evidence,'monaco-single-reopen.json'),JSON.stringify({sourceId:source.id,trace},null,2));
  80  |   expect(trace.filter(event=>event.phase==='added'&&event.fileId===source.id)).toHaveLength(1);
  81  |   const beforeRefresh=reads.filter(url=>url.endsWith(source.id)).length;
  82  |   await page.getByRole('button',{name:'Refresh Git',exact:true}).click();
  83  |   await expect.poll(()=>reads.filter(url=>url.endsWith(source.id)).length).toBeGreaterThan(beforeRefresh);
  84  |   await expect(editor).toHaveAttribute('data-file-id',source.id);
  85  |   await expect(editor.locator('.view-lines').last()).toBeVisible();
  86  |   await writeFile(path.join(evidence,'monaco-single-reopen.json'),JSON.stringify({sourceId:source.id,trace,reopenMounts:trace.filter(event=>event.phase==='added'&&event.fileId===source.id).length,readsBeforeRefresh:beforeRefresh,readsAfterRefresh:reads.filter(url=>url.endsWith(source.id)).length,refreshRereadVerified:true},null,2));
  87  | });
  88  | test('read API rejects outside origins and mutations',async ({request})=>{
  89  |   expect((await request.get('/__sidequest/snapshot',{headers:{Origin:'https://example.com'}})).status()).toBe(403);
  90  |   expect((await request.post('/__sidequest/snapshot')).status()).toBe(405);
  91  |   expect((await request.get('/__sidequest/diff/not-a-file')).status()).toBe(404);
  92  | });
  93  | for (const width of [960,390]) test(`viewer reflows at ${width}px with reduced motion`,async ({page})=>{
  94  |   const errors:string[]=[];page.on('pageerror',error=>errors.push(error.message));
  95  |   await page.setViewportSize({width,height:780});await page.emulateMedia({reducedMotion:'reduce'});
  96  |   await page.goto('/');await expect(page.locator('.app-footer')).toHaveAttribute('data-actor-status','ready',{timeout:60000});await page.getByRole('combobox',{name:'Office navigation'}).selectOption('parent_019');
  97  |   await expect(page.getByTestId('diff-editor')).toHaveCount(1);
  98  |   await page.getByRole('button',{name:'Expand',exact:true}).click();
  99  |   expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  100 |   await page.screenshot({path:path.join(evidence,`viewer-${width}.png`)});
  101 |   await page.keyboard.press('Escape');await expect(page.getByTestId('diff-editor')).toHaveCount(0);
  102 |   expect(errors).toEqual([]);
  103 | });
  104 | 
  105 | test('keyboard-accessible viewer has no automated WCAG A/AA violations',async({page})=>{
  106 |   await page.goto('/');await expect(page.locator('.app-footer')).toHaveAttribute('data-actor-status','ready',{timeout:60000}); await page.getByRole('combobox',{name:'Office navigation'}).selectOption('parent_019');
> 107 |   await expect(page.getByTestId('diff-editor').locator('.monaco-editor').last()).toBeVisible();
      |                                                                                  ^ Error: expect(locator).toBeVisible() failed
  108 |   await page.getByRole('button',{name:'Expand',exact:true}).click();
  109 |   await expect(page.getByTestId('diff-editor').locator('.monaco-editor').last()).toBeVisible();
  110 |   const code=page.getByRole('button',{name:/dev\/luna\.py/});
  111 |   if(await code.count()) {await code.click();await expect(page.getByTestId('diff-editor').locator('.view-lines').last()).toBeVisible();}
  112 |   const results=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze();
  113 |   await writeFile(path.join(evidence,'accessibility.json'),JSON.stringify(results.violations,null,2));
  114 |   expect(results.violations.map(item=>({id:item.id,impact:item.impact,description:item.description}))).toEqual([]);
  115 | });
  116 | 
  117 | test('hostile source stays literal and a failed read can retry',async({page})=>{
  118 |   let fail=true;
  119 |   await page.route('**/__sidequest/diff/*',async route=>{
  120 |     if(fail){await route.fulfill({status:503,json:{error:'test-only failure'}});return;}
  121 |     const response=await route.fetch();const data=await response.json();
  122 |     await route.fulfill({json:{...data,original:'',modified:'<script>window.__executed=true</script>\n<img src=x onerror="window.__executed=true">',language:'plaintext'}});
  123 |   });
  124 |   await page.goto('/');await expect(page.locator('.app-footer')).toHaveAttribute('data-actor-status','ready',{timeout:60000});await page.getByRole('combobox',{name:'Office navigation'}).selectOption('parent_019');
  125 |   await expect(page.getByRole('alert')).toContainText('Local Git read failed');
  126 |   fail=false;await page.getByRole('button',{name:'Refresh repository'}).click();
  127 |   await expect(page.getByTestId('diff-editor')).toHaveCount(1);
  128 |   await expect(page.getByTestId('diff-editor').locator('.view-lines').last()).toContainText('<script>');
  129 |   expect(await page.evaluate(()=>Object.hasOwn(window,'__executed'))).toBe(false);
  130 | });
  131 | 
```