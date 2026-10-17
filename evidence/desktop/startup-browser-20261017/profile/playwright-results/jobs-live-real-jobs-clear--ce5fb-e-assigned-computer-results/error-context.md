# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: jobs-live.spec.ts >> real jobs clear stale notices, recover reads and preserve assigned computer results
- Location: tests/browser/jobs-live.spec.ts:90:1

# Error details

```
Test timeout of 90000ms exceeded.
```

```
Error: expect(locator).toHaveAttribute(expected) failed

Locator: getByRole('region', { name: 'Computer job results' }).locator('.artifact-files button[aria-pressed="true"]')
Expected: "README.md"
Error: element(s) not found

Call log:
  - Expect "toHaveAttribute" getByRole('region', { name: 'Computer job results' }).locator('.artifact-files button[aria-pressed="true"]') with timeout 15000ms
  - waiting for getByRole('region', { name: 'Computer job results' }).locator('.artifact-files button[aria-pressed="true"]')
  - Test timeout of 90000ms exceeded.

```

```yaml
- main:
  - text: sidequest source
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
  - region "Computer job results":
    - region "Selected job":
      - heading "Browser inspection 2026-10-17T01:37:20.261Z" [level=3]
      - paragraph: verifying · $0 budget · 3c4b2cca-7d08-49a7-8917-e7fdf3deacb7
      - status: Inspection results ready. Source delivery is disabled; the backend retains the verifying state.
      - text: candidate.frozen_identity
      - strong: pass
      - group: Run activity (1)
      - text: Artifact
      - combobox "Artifact Artifact":
        - option "Frozen candidate manifest · file_manifest" [selected]
        - option "Frozen candidate diff · diff"
        - option "Frozen candidate patch · patch"
        - option "test_report · test_report"
        - option ".codex/config.toml · source_file"
        - option ".gitignore · source_file"
        - option ".github/workflows/launch-kit.yml · source_file"
        - option "AGENTS.md · source_file"
        - option ".gitattributes · source_file"
        - option "contracts/EXTENSIONS.md · source_file"
        - option "README.md · source_file"
        - option "SPEC.md · source_file"
        - option "contracts/STORAGE.md · source_file"
        - option "contracts/examples/computer.json · source_file"
        - option "contracts/PROTOCOL.md · source_file"
        - option "contracts/snapshot.json · source_file"
        - option "demo/README.md · source_file"
        - option "demo/club-site/README.md · source_file"
        - option "demo/club-site/known-good/members/welcome.html · source_file"
        - option "demo/club-site/bad/members/signup.html · source_file"
        - option "demo/club-site/known-good/index.html · source_file"
        - option "demo/club-site/bad/index.html · source_file"
        - option "desktop/README.md · source_file"
        - option "desktop/electron/main.cjs · source_file"
        - option "desktop/electron/git-reader.cjs · source_file"
        - option "desktop/electron/security.cjs · source_file"
        - option "desktop/electron/runtime-client.cjs · source_file"
        - option "desktop/electron/preload.cjs · source_file"
        - option "desktop/index.html · source_file"
        - option "desktop/electron/static-server.cjs · source_file"
        - option "desktop/package-lock.json · source_file"
        - option "desktop/package.json · source_file"
        - option "desktop/scripts/electron-smoke.mjs · source_file"
        - option "desktop/playwright.config.ts · source_file"
        - option "desktop/scripts/install-office.py · source_file"
        - option "desktop/scripts/inspect-assets.mjs · source_file"
        - option "desktop/src/App.tsx · source_file"
        - option "desktop/src/DiffEditor.tsx · source_file"
        - option "desktop/src/OfficeScene.tsx · source_file"
        - option "desktop/src/JobsBoard.tsx · source_file"
        - option "desktop/src/bridge.ts · source_file"
        - option "desktop/src/office-bindings.ts · source_file"
        - option "desktop/src/main.tsx · source_file"
        - option "desktop/src/types.ts · source_file"
        - option "desktop/src/runtime-identity.ts · source_file"
        - option "desktop/src/style.css · source_file"
        - option "desktop/tests/bindings.test.mjs · source_file"
        - option "desktop/tests/assets.test.mjs · source_file"
        - option "desktop/tests/browser/viewer.spec.ts · source_file"
        - option "desktop/tests/git.test.mjs · source_file"
        - option "desktop/tests/browser/jobs-live.spec.ts · source_file"
        - option "desktop/tests/runtime-identity.test.mjs · source_file"
        - option "desktop/tests/install-office.test.mjs · source_file"
        - option "desktop/tests/runtime-client.test.mjs · source_file"
        - option "dev/cache_references.py · source_file"
        - option "desktop/tests/security.test.mjs · source_file"
        - option "desktop/tsconfig.json · source_file"
        - option "desktop/vite.config.ts · source_file"
        - option "dev/loop.py · source_file"
        - option "dev/luna.py · source_file"
        - option "dev/check.py · source_file"
        - option "dev/references.json · source_file"
        - option "dev/mock_runtime.py · source_file"
        - option "dev/plan.json · source_file"
        - option "docs/ARCHITECTURE.md · source_file"
        - option "dev/test_specs.py · source_file"
        - option "dev/test_loop.py · source_file"
        - option "dev/test_luna.py · source_file"
        - option "docs/ASSET_BINDING.md · source_file"
        - option "docs/ART_DIRECTION.md · source_file"
        - option "docs/COMPUTER_UI.md · source_file"
        - option "docs/EXECUTION.md · source_file"
        - option "docs/MVP_ACCEPTANCE.md · source_file"
        - option "docs/PARALLEL_PLAN.md · source_file"
        - option "docs/LOW_TOKEN_EXECUTION.md · source_file"
        - option "docs/FEATURE_MATRIX.md · source_file"
        - option "docs/SETUP_VERIFICATION.md · source_file"
        - option "docs/RUN_EVALS.md · source_file"
        - option "docs/RESEARCH.md · source_file"
        - option "docs/archive/SPEC-0.2.md · source_file"
        - option "docs/VALIDATION.md · source_file"
        - option "docs/START_HERE.md · source_file"
        - option "docs/design/station-kit.svg · source_file"
        - option "docs/design/screen-layout.svg · source_file"
        - option "docs/goals/B-tools.md · source_file"
        - option "docs/goals/A-runtime.md · source_file"
        - option "docs/goals/D-workshops.md · source_file"
        - option "docs/goals/C-unity.md · source_file"
        - option "docs/goals/C-desktop.md · source_file"
        - option "docs/goals/I1-integration.md · source_file"
        - option "evidence/A/A1-final-review.json · source_file"
        - option "evidence/A/A1-review-2.json · source_file"
        - option "evidence/A/A1-review.json · source_file"
        - option "evidence/A/A2-repair-review.json · source_file"
        - option "evidence/A/A1.json · source_file"
        - option "evidence/A/A3-repair-review.json · source_file"
        - option "evidence/A/A2-review.json · source_file"
        - option "evidence/A/A2.json · source_file"
        - option "evidence/A/A3-review.json · source_file"
        - option "evidence/A/A3.json · source_file"
      - button "Previous artifacts" [disabled]
      - button "More artifacts"
      - text: SHA256 b5f573d7fdea · immutable
      - navigation "Result files":
        - button "Previous files" [disabled]
        - button "More files" [disabled]
      - region "Artifact content":
        - button "File text" [pressed]
        - button "Git diff"
        - text: Loading file text…
        - button "Previous lines" [disabled]
        - button "More lines" [disabled]
    - text: Runtime local-git · revision 261 · Coding execution unavailable
  - combobox "Office navigation":
    - option "Navigate…" [selected]
    - option "Tasks board"
  - text: 26 staged · 1 recorded sessions Local Git · read-only
```

# Test source

```ts
  36  |   await page.screenshot({path:path.join(evidence,'job-result.png')});
  37  |   await board.getByRole('button',{name:'Git diff',exact:true}).click();
  38  |   await expect(board.locator('.artifact-text')).toContainText('No textual changes in this inspected candidate.');
  39  |   await page.screenshot({path:path.join(evidence,'job-diff.png')});
  40  |   await board.locator('#job-artifact').selectOption({label:await board.locator('#job-artifact option').filter({hasText:'test_report'}).first().textContent()??''});
  41  |   await expect(board.locator('.artifact-text')).toContainText('candidate.frozen_identity');
  42  |   await expect.poll(async()=>JSON.parse(await board.locator('.artifact-text').textContent()??'{}').inference_calls).toBe(0);
  43  |   const report=JSON.parse(await board.locator('.artifact-text').textContent()??'{}');
  44  |   await page.screenshot({path:path.join(evidence,'job-check-report.png')});
  45  |   await board.locator('.job-activity > summary').click();
  46  |   const activity=board.getByRole('region',{name:'Run activity'});
  47  |   await expect(activity).toContainText('No model call');
  48  |   await expect(activity.locator('.run-activity-state')).toHaveText('completed');
  49  |   await expect.poll(()=>activity.locator('.run-activity-timeline>li').count()).toBeGreaterThan(0);
  50  |   await page.screenshot({path:path.join(evidence,'run-activity-actual.png')});
  51  |   await board.locator('.job-activity > summary').click();
  52  |   await board.locator('.coding-readiness summary').click();
  53  |   await expect(board.locator('.coding-readiness')).toContainText('Coding tasks remain blocked.');
  54  |   const refreshStart=calls.length;
  55  |   await board.getByRole('button',{name:'Refresh status',exact:true}).click();
  56  |   await expect.poll(()=>calls.slice(refreshStart).filter(call=>call.method==='capabilities').length).toBeGreaterThan(0);
  57  |   expect(calls.slice(refreshStart).every(call=>['snapshot','capabilities','artifacts','artifact','files','text','diff','runInfo','runEvents'].includes(call.method))).toBe(true);
  58  |   await page.screenshot({path:path.join(evidence,'job-readiness.png')});
  59  |   await board.locator('.coding-readiness summary').click();
  60  |   const responsiveAccessibility:{width:number;violations:unknown[]}[]=[];
  61  |   for(const width of [960,390]){
  62  |     await page.setViewportSize({width,height:780});
  63  |     await board.locator('.artifact-content').scrollIntoViewIfNeeded();
  64  |     await expect(board.locator('.artifact-text')).toBeInViewport();
  65  |     expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBe(true);
  66  |     await page.screenshot({path:path.join(evidence,`job-${width}.png`)});
  67  |     const result=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze();
  68  |     responsiveAccessibility.push({width,violations:result.violations});
  69  |     expect(result.violations.map(item=>({id:item.id,impact:item.impact}))).toEqual([]);
  70  |   }
  71  |   await writeFile(path.join(evidence,'job-responsive-accessibility.json'),JSON.stringify(responsiveAccessibility,null,2));
  72  |   await page.setViewportSize({width:1440,height:900});
  73  |   const accessibility=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze();
  74  |   await writeFile(path.join(evidence,'job-accessibility.json'),JSON.stringify(accessibility.violations,null,2));
  75  |   expect(accessibility.violations.map(item=>({id:item.id,impact:item.impact}))).toEqual([]);
  76  |   const selectedArtifact=await board.locator('#job-artifact').inputValue();
  77  |   await page.keyboard.press('Escape');await expect(board).toBeHidden();
  78  |   await expect(page.getByRole('button',{name:'Jobs',exact:true})).toBeFocused();
  79  |   await page.getByRole('button',{name:'Jobs',exact:true}).click();
  80  |   await expect(board.locator('#job-artifact')).toHaveValue(selectedArtifact);
  81  |   const response=await request.get('/__sidequest/snapshot');const git=await response.json();
  82  |   const state=await page.evaluate(async()=>{const response=await fetch('/__sidequest/runtime/snapshot',{method:'POST',headers:{'Content-Type':'application/json'},body:'[]'});if(!response.ok)throw new Error('Final local snapshot unavailable.');return response.json();});
  83  |   const completedJob=state.jobs.find((item:{title:string})=>item.title===title);
  84  |   expect(completedJob?.spent_usd).toBe(0);
  85  |   const registeredProject=state.projects.find((item:{id:string})=>item.id===completedJob.project_id);
  86  |   await writeFile(path.join(evidence,'job-browser.json'),JSON.stringify({title,source:{base:git.baseRevision,candidate:git.candidateRevision},registered_project:registeredProject,job:completedJob,frozen_check_report:report,browser_requests:calls,model_calls:report.inference_calls,scope:'Real deterministic local Git inspection through UI/HTTP/B/D; no coding agent or provider run',page_errors:errors},null,2));
  87  |   expect(errors).toEqual([]);
  88  | });
  89  | 
  90  | test('real jobs clear stale notices, recover reads and preserve assigned computer results',async({page,request})=>{
  91  |   test.setTimeout(90_000);
  92  |   test.skip(process.env.SIDEQUEST_TEST_INSPECTION!=='1','Requires actual local inspection records; never launches coding.');
  93  |   const response=await request.post('/__sidequest/runtime/snapshot',{data:[],headers:{Origin:'http://127.0.0.1:5173'}});expect(response.ok()).toBe(true);const state=await response.json();
  94  |   const completed=state.jobs.find((job:{execution_profile:string;checks:{state:string}[];tasks:{state:string}[]})=>job.execution_profile==='local_git_inspection'&&job.tasks.every(t=>t.state==='completed')&&job.checks.length&&job.checks.every(c=>c.state==='pass'));
  95  |   expect(completed).toBeTruthy();
  96  |   await page.goto('/');await expect(page.locator('.app-footer')).toHaveAttribute('data-actor-status','ready',{timeout:60000});await page.getByRole('button',{name:'Jobs',exact:true}).click();
  97  |   const board=page.getByRole('region',{name:'Local jobs board'});
  98  |   await board.getByRole('button',{name:new RegExp(completed.title.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'))}).click();
  99  |   await expect(board).toContainText('Inspection results ready.');
  100 |   await expect(board).not.toContainText('Run accepted. Waiting for status.');
  101 |   const queuedTitle=`Repeated submission ${new Date().toISOString()}`;
  102 |   await board.getByLabel('Inspection title').fill(queuedTitle);
  103 |   await board.getByRole('button',{name:'Submit inspection',exact:true}).click();
  104 |   await expect(board.locator('.job-summary')).toContainText(queuedTitle);
  105 |   await expect(board.locator('.job-state')).toHaveText('queued');
  106 |   await board.getByRole('button',{name:new RegExp(completed.title.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'))}).click();
  107 |   await expect(board).not.toContainText('Job queued. Review the job, then run it explicitly.');
  108 |   let disconnected=true;
  109 |   await page.route('**/__sidequest/runtime/snapshot',route=>disconnected?route.fulfill({status:503,json:{error:'test-only network failure'}}):route.continue());
  110 |   await board.getByRole('button',{name:'Refresh status',exact:true}).click();
  111 |   await expect(board.getByRole('alert').first()).toBeVisible();
  112 |   await expect(board.getByRole('button',{name:'Submit inspection',exact:true})).toBeDisabled();
  113 |   disconnected=false;await board.getByRole('button',{name:'Refresh status',exact:true}).click();
  114 |   await expect(board.getByRole('button',{name:'Submit inspection',exact:true})).toBeEnabled();
  115 |   await expect(board.getByRole('alert')).toHaveCount(0);
  116 |   await board.getByLabel('Show results on').selectOption('parent_019');
  117 |   await board.getByRole('button',{name:'Assign result display',exact:true}).click();
  118 |   const result=page.getByRole('region',{name:'Computer job results'});
  119 |   await expect(result).toBeVisible();await expect(result.locator('.job-summary')).toContainText(completed.title);
  120 |   await result.locator('.artifact-files button[title="README.md"]').click();
  121 |   await expect(result.locator('.artifact-text')).not.toContainText('Loading file text');
  122 |   const selectedFile=await result.locator('.artifact-files button[aria-pressed="true"]').getAttribute('title');
  123 |   await result.locator('.artifact-text').evaluate(node=>{node.scrollTop=180;node.dispatchEvent(new Event('scroll',{bubbles:true}));});
  124 |   await expect.poll(()=>result.locator('.artifact-text').evaluate(node=>node.scrollTop)).toBeGreaterThan(100);
  125 |   await page.locator('.monitor-header').getByRole('button',{name:'Expand',exact:true}).click();
  126 |   await expect(page.getByRole('dialog',{name:'Computer job viewer'})).toBeVisible();
  127 |   await expect(result.locator('.artifact-files button[aria-pressed="true"]')).toHaveAttribute('title',selectedFile!);
  128 |   await page.getByRole('button',{name:'Settings',exact:true}).click();
  129 |   await expect(page.getByRole('dialog',{name:'Provider settings dialog'})).toBeVisible();
  130 |   await page.keyboard.press('Escape');
  131 |   await expect(page.getByRole('dialog',{name:'Computer job viewer'})).toBeVisible();
  132 |   await expect(page.getByRole('button',{name:'Settings',exact:true})).toBeFocused();
  133 |   await page.keyboard.press('Escape');await expect(result).toHaveCount(0);
  134 |   await page.getByRole('combobox',{name:'Office navigation'}).selectOption('parent_019');
  135 |   await expect(result).toBeVisible();
> 136 |   await expect(result.locator('.artifact-files button[aria-pressed="true"]')).toHaveAttribute('title',selectedFile!);
      |                                                                               ^ Error: expect(locator).toHaveAttribute(expected) failed
  137 |   await expect.poll(()=>result.locator('.artifact-text').evaluate(node=>node.scrollTop)).toBeGreaterThan(100);
  138 |   await page.screenshot({path:path.join(evidence,'assigned-result.png')});
  139 |   await writeFile(path.join(evidence,'result-display-browser.json'),JSON.stringify({job_id:completed.id,queued_test_title:queuedTitle,queued_test_executed:false,selected_file:selectedFile,temporary_network_failure:true,recovered:true,scope:'Actual local inspection artifacts; display assignment only; zero coding/model launches'},null,2));
  140 | });
  141 | 
  142 | test('recorded session ownership persists at a figure and renders real contextual events',async({page,request})=>{
  143 |  const sessionTestStarted=Date.now();
  144 |  test.setTimeout(120_000);test.skip(process.env.SIDEQUEST_TEST_INSPECTION!=='1','Requires actual deterministic inspection records; no model calls.');
  145 |  const origin={Origin:'http://127.0.0.1:5173'};
  146 |  const read=async()=>{const response=await request.post('/__sidequest/runtime/snapshot',{data:[],headers:origin});expect(response.ok()).toBe(true);return response.json();};
  147 |  let state=await read();const job=state.jobs.find((job:{run_ids:string[];execution_profile:string})=>job.execution_profile==='local_git_inspection'&&job.run_ids?.length);expect(job).toBeTruthy();
  148 |  const runId=job.run_ids.at(-1);const runReply=await request.post('/__sidequest/runtime/runInfo',{data:[runId],headers:origin});const {run}=await runReply.json();expect(run.worker_id).toBeTruthy();
  149 |  for(const owner of state.office_sessions.filter((owner:{station_id:string;worker_id:string})=>owner.station_id==='parent_019'||owner.worker_id===run.worker_id)){const clear=await request.post('/__sidequest/runtime/clearSession',{data:[owner.station_id,state.revision],headers:origin});expect(clear.ok()).toBe(true);state=await read();}
  150 |  const coding:string[]=[];page.on('request',r=>{if(/__sidequest\/runtime\/(submitCoding|runCoding|enableCoding)$/.test(r.url()))coding.push(r.url());});
  151 |  await page.goto('/');await expect(page.locator('.app-footer')).toHaveAttribute('data-actor-status','ready',{timeout:60000});
  152 |  await page.getByRole('combobox',{name:'Office navigation'}).selectOption('actor:parent_019');
  153 |  let session=page.getByRole('dialog',{name:'Agent session'});await session.getByText('Attach recorded session',{exact:true}).click();
  154 |  await session.getByRole('combobox',{name:'Recorded task',exact:true}).selectOption(job.id);await session.getByRole('combobox',{name:'Recorded run',exact:true}).selectOption(runId);
  155 |  await session.getByRole('button',{name:'Assign session',exact:true}).click();
  156 |  await expect(session.locator('.session-records')).toHaveAttribute('data-session-run',runId);await expect(session).toContainText('Recorded local inspection');
  157 |  await expect(session).toContainText('Checking');await expect(session.locator('.run-activity')).toHaveCount(0);
  158 |  await page.screenshot({path:path.join(evidence,'recorded-session.png')});
  159 |  await session.getByRole('button',{name:'Open monitor',exact:true}).click();const trace=page.getByRole('region',{name:'Session execution trace'});
  160 |  await expect(trace.locator('.monitor-events>li').first()).toBeVisible();await expect(trace).toContainText('Checking');
  161 |  await page.screenshot({path:path.join(evidence,'monitor-pov.png')});
  162 |  await trace.getByText('Run details',{exact:true}).click();await expect(trace).toContainText('No model call');await expect(trace).toContainText('Recorded usage:');await page.keyboard.press('Escape');
  163 |  await page.getByRole('combobox',{name:'Office navigation'}).selectOption('actor:parent_019');session=page.getByRole('dialog',{name:'Agent session'});
  164 |  await session.getByRole('button',{name:'Open results',exact:true}).click();const results=page.getByRole('region',{name:'Computer job results'});await expect(results).toBeVisible();await expect(results.locator('.job-summary')).toContainText(job.title);await page.keyboard.press('Escape');
  165 |  await page.getByRole('combobox',{name:'Office navigation'}).selectOption('actor:parent_019');session=page.getByRole('dialog',{name:'Agent session'});await expect(session.locator('.session-records')).toHaveAttribute('data-session-run',runId);
  166 |  const saved=await read();const owner=saved.office_sessions.find((owner:{station_id:string})=>owner.station_id==='parent_019');expect(owner).toMatchObject({job_id:job.id,run_id:runId,worker_id:run.worker_id,project_id:job.project_id});
  167 |  await writeFile(path.join(evidenceDirectory(process.env.SIDEQUEST_EVIDENCE_DIR?'timings':'repair-20261014'),`session-before-reload-${process.env.SIDEQUEST_EVIDENCE_RUN??'timings'}.json`),JSON.stringify({elapsedMs:Date.now()-sessionTestStarted,entries:await page.evaluate(()=>performance.getEntries().filter(e=>e.name.startsWith('sidequest:')).map(e=>e.toJSON()))},null,2));
  168 |  await page.reload();await expect(page.locator('.app-footer')).toHaveAttribute('data-actor-status','ready',{timeout:60000});await page.getByRole('combobox',{name:'Office navigation'}).selectOption('actor:parent_019');session=page.getByRole('dialog',{name:'Agent session'});await expect(session.locator('.session-records')).toHaveAttribute('data-session-run',runId);
  169 |  await page.setViewportSize({width:390,height:780});await session.getByRole('button',{name:'Open monitor',exact:true}).click();await expect(trace.locator('.monitor-events>li').first()).toBeVisible();
  170 |  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);const axe=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze();await writeFile(path.join(evidence,'session-accessibility.json'),JSON.stringify(axe.violations,null,2));expect(axe.violations.map(v=>v.id)).toEqual([]);
  171 |  await page.screenshot({path:path.join(evidence,'recorded-session-390.png')});
  172 |  await page.route('**/__sidequest/runtime/runInfo',route=>route.fulfill({json:{v:1,run:{...run,worker_id:'fixture-wrong-worker'}}}));await trace.getByRole('button',{name:'Refresh trace',exact:true}).click();await expect(trace).toContainText('Recorded session worker identity changed.');await page.unroute('**/__sidequest/runtime/runInfo');
  173 |  await page.keyboard.press('Escape');await page.getByRole('combobox',{name:'Office navigation'}).selectOption('board');const detail=page.getByRole('region',{name:'Tasks board detail'});await detail.getByRole('combobox',{name:'Task',exact:true}).selectOption(job.id);await expect(detail).toContainText('Recorded worker at Computer 19');await detail.getByRole('button',{name:'Open session',exact:true}).click();
  174 |  session=page.getByRole('dialog',{name:'Agent session'});await expect(session.locator('.session-records')).toHaveAttribute('data-session-run',runId);
  175 |  await session.getByText('Session details',{exact:true}).click();await session.getByRole('button',{name:'Detach session',exact:true}).click();await expect(session).toContainText('No live session attached');expect((await read()).office_sessions.some((row:{station_id:string})=>row.station_id==='parent_019')).toBe(false);expect(coding).toEqual([]);
  176 |  await writeFile(path.join(evidence,'session-browser.json'),JSON.stringify({scope:'Actual local inspection; persistent display ownership, not coding dispatch or live Codex conversation',owner,reload_restored:true,board_links_same_session:true,open_results_same_job:true,wrong_worker_rejected:true,fixtures:['Read-only runInfo response with explicitly fixture-wrong-worker; no persisted state changed'],explicit_detach:true,coding_requests:coding,axe_violations:axe.violations.map(v=>v.id)},null,2));
  177 | });
  178 | 
```