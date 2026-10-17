# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: jobs-live.spec.ts >> recorded session ownership persists at a figure and renders real contextual events
- Location: tests/browser/jobs-live.spec.ts:142:1

# Error details

```
Error: locator.click: Test ended.
Call log:
  - waiting for getByRole('dialog', { name: 'Agent session' }).getByText('Attach recorded session', { exact: true })

```

# Test source

```ts
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
  136 |   await expect(result.locator('.artifact-files button[aria-pressed="true"]')).toHaveAttribute('title',selectedFile!);
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
> 153 |  let session=page.getByRole('dialog',{name:'Agent session'});await session.getByText('Attach recorded session',{exact:true}).click();
      |                                                                                                                              ^ Error: locator.click: Test ended.
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