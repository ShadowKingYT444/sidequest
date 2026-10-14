# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: jobs-live.spec.ts >> recorded session ownership persists at a figure and renders real contextual events
- Location: tests/browser/jobs-live.spec.ts:140:1

# Error details

```
Error: expect(received).toEqual(expected) // deep equality

- Expected  - 1
+ Received  + 3

- Array []
+ Array [
+   "target-size",
+ ]
```

# Page snapshot

```yaml
- main [ref=f1e3]:
  - generic [ref=f1e4]:
    - generic [ref=f1e5]: sidequest
    - button "Settings" [ref=f1e6] [cursor=pointer]
    - button "Jobs" [ref=f1e7] [cursor=pointer]
    - button "Refresh Git" [ref=f1e8] [cursor=pointer]
  - dialog "Agent session" [ref=f1e13]:
    - generic [ref=f1e14]:
      - heading "Computer 19" [level=2] [ref=f1e15]
      - button "Close agent session" [ref=f1e16] [cursor=pointer]: ×
    - generic [ref=f1e17]:
      - paragraph [ref=f1e18]: Recorded local inspection
      - paragraph [ref=f1e19]: Persisted worker ownership · original staged figure
      - generic [ref=f1e20]:
        - generic [ref=f1e21]:
          - term [ref=f1e22]: Task
          - definition [ref=f1e23]: Browser inspection 2026-10-14T09:44:26.540Z
        - generic [ref=f1e24]:
          - term [ref=f1e25]: Worker
          - definition [ref=f1e26]: 316ba303
        - generic [ref=f1e27]:
          - term [ref=f1e28]: Run
          - definition [ref=f1e29]: dcf89046
        - generic [ref=f1e30]:
          - term [ref=f1e31]: State
          - definition [ref=f1e32]: verifying
      - group [ref=f1e33]:
        - generic "Task request" [ref=f1e34]
      - group [ref=f1e35]:
        - generic "Conversation & events" [active] [ref=f1e36] [cursor=pointer]
        - region "Run activity" [ref=f1e37]:
          - generic [ref=f1e38]:
            - generic [ref=f1e39]:
              - heading "Conversation & events" [level=4] [ref=f1e40]
              - generic [ref=f1e41]: Local Git inspection
            - button "Refresh" [ref=f1e42] [cursor=pointer]
          - generic [ref=f1e43]:
            - generic [ref=f1e44]: Run
            - combobox "Run" [disabled] [ref=f1e45] [cursor=pointer]:
              - option "Run 1 · dcf89046" [selected]
            - generic [ref=f1e46]: completed
          - generic [ref=f1e47]:
            - generic [ref=f1e48]:
              - term [ref=f1e49]: Worker
              - definition [ref=f1e50]: 316ba303-4fbd-4a1b-ba4c-7dc080e8a478
            - generic [ref=f1e51]:
              - term [ref=f1e52]: Attempt
              - definition [ref=f1e53]: "1"
            - generic [ref=f1e54]:
              - term [ref=f1e55]: Model
              - definition [ref=f1e56]: No model call
            - generic [ref=f1e57]:
              - term [ref=f1e58]: Effort
              - definition [ref=f1e59]: —
          - paragraph [ref=f1e60]: "Recorded usage: Unknown tokens · $0"
          - group [ref=f1e61]:
            - generic "Run details" [ref=f1e62] [cursor=pointer]
          - generic [ref=f1e63]:
            - heading "Events" [level=5] [ref=f1e64]
            - generic [ref=f1e65]: 9 on this page
          - list "Persisted run events" [ref=f1e66]:
            - listitem [ref=f1e67]:
              - generic [ref=f1e68]:
                - generic [ref=f1e69]: status
                - time [ref=f1e70]: Oct 14, 2026, 9:44:26 AM
                - generic [ref=f1e71]: "#1"
              - paragraph [ref=f1e72]: Task dispatch reserved.
            - listitem [ref=f1e73]:
              - generic [ref=f1e74]:
                - generic [ref=f1e75]: status
                - time [ref=f1e76]: Oct 14, 2026, 9:44:26 AM
                - generic [ref=f1e77]: "#2"
              - paragraph [ref=f1e78]: Starting local Git inspection.
            - listitem [ref=f1e79]:
              - generic [ref=f1e80]:
                - generic [ref=f1e81]: status
                - time [ref=f1e82]: Oct 14, 2026, 9:44:27 AM
                - generic [ref=f1e83]: "#3"
              - paragraph [ref=f1e84]: Repository inspection completed.
            - listitem [ref=f1e85]:
              - generic [ref=f1e86]:
                - generic [ref=f1e87]: status
                - time [ref=f1e88]: Oct 14, 2026, 9:44:28 AM
                - generic [ref=f1e89]: "#4"
              - paragraph [ref=f1e90]: Independent repository clone prepared.
            - listitem [ref=f1e91]:
              - generic [ref=f1e92]:
                - generic [ref=f1e93]: status
                - time [ref=f1e94]: Oct 14, 2026, 9:44:28 AM
                - generic [ref=f1e95]: "#5"
              - paragraph [ref=f1e96]: Validating candidate scope and Git tree.
            - listitem [ref=f1e97]:
              - generic [ref=f1e98]:
                - generic [ref=f1e99]: status
                - time [ref=f1e100]: Oct 14, 2026, 9:44:30 AM
                - generic [ref=f1e101]: "#6"
              - paragraph [ref=f1e102]: Immutable candidate artifacts frozen.
            - listitem [ref=f1e103]:
              - generic [ref=f1e104]:
                - generic [ref=f1e105]: status
                - time [ref=f1e106]: Oct 14, 2026, 9:44:30 AM
                - generic [ref=f1e107]: "#7"
              - paragraph [ref=f1e108]: Attempt result recorded.
            - listitem [ref=f1e109]:
              - generic [ref=f1e110]:
                - generic [ref=f1e111]: status
                - time [ref=f1e112]: Oct 14, 2026, 9:44:30 AM
                - generic [ref=f1e113]: "#8"
              - paragraph [ref=f1e114]: Candidate recorded.
            - listitem [ref=f1e115]:
              - generic [ref=f1e116]:
                - generic [ref=f1e117]: tool finished
                - time [ref=f1e118]: Oct 14, 2026, 9:44:30 AM
                - generic [ref=f1e119]: "#9"
              - paragraph [ref=f1e120]: Frozen identity check passed.
          - generic [ref=f1e121]:
            - button "Previous events" [disabled] [ref=f1e122]
            - button "More events" [disabled] [ref=f1e123]
          - paragraph [ref=f1e124]: Deterministic local work. No provider inference.
      - generic [ref=f1e125]:
        - button "Open results" [ref=f1e126] [cursor=pointer]
        - button "Detach session" [ref=f1e127] [cursor=pointer]
      - button "Refresh session" [ref=f1e128] [cursor=pointer]
  - generic [ref=f1e129]:
    - combobox "Office navigation" [ref=f1e130]:
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
    - generic "Original staged poses; recorded runtime ownership is separate from provider connectivity." [ref=f1e131]: 26 staged · 1 recorded sessions
```

# Test source

```ts
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
  123 |   await result.getByRole('button',{name:'Expand',exact:true}).click();
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
  154 |  await session.locator('.session-conversation>summary').click();await expect(session.getByRole('region',{name:'Run activity'}).locator('.run-activity-timeline>li').first()).toBeVisible();
  155 |  await expect(session).toContainText('No model call');await expect(session).toContainText('Recorded usage:');
  156 |  await page.screenshot({path:path.resolve('../evidence/desktop/recorded-session.png')});
  157 |  await session.getByRole('button',{name:'Open results',exact:true}).click();const results=page.getByRole('region',{name:'Computer job results'});await expect(results).toBeVisible();await expect(results.locator('.job-summary')).toContainText(job.title);await page.keyboard.press('Escape');
  158 |  await page.getByRole('combobox',{name:'Office navigation'}).selectOption('actor:parent_019');session=page.getByRole('dialog',{name:'Agent session'});await expect(session.locator('.session-records')).toHaveAttribute('data-session-run',runId);
  159 |  const saved=await read();const owner=saved.office_sessions.find((owner:{station_id:string})=>owner.station_id==='parent_019');expect(owner).toMatchObject({job_id:job.id,run_id:runId,worker_id:run.worker_id,project_id:job.project_id});
  160 |  await page.reload();await expect(page.locator('.app-footer')).toHaveAttribute('data-actor-status','ready',{timeout:60000});await page.getByRole('combobox',{name:'Office navigation'}).selectOption('actor:parent_019');session=page.getByRole('dialog',{name:'Agent session'});await expect(session.locator('.session-records')).toHaveAttribute('data-session-run',runId);
  161 |  await page.setViewportSize({width:390,height:780});await session.locator('.session-conversation>summary').click();await expect(session.getByRole('region',{name:'Run activity'}).locator('.run-activity-timeline>li').first()).toBeVisible();
> 162 |  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);const axe=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze();expect(axe.violations.map(v=>v.id)).toEqual([]);
      |                                                                                                                                                                                                                                         ^ Error: expect(received).toEqual(expected) // deep equality
  163 |  await page.screenshot({path:path.resolve('../evidence/desktop/recorded-session-390.png')});
  164 |  await page.route('**/__sidequest/runtime/runInfo',route=>route.fulfill({json:{v:1,run:{...run,worker_id:'fixture-wrong-worker'}}}));await session.getByRole('region',{name:'Run activity'}).getByRole('button',{name:'Refresh',exact:true}).click();await expect(session).toContainText('Recorded session worker identity changed.');await page.unroute('**/__sidequest/runtime/runInfo');
  165 |  await page.keyboard.press('Escape');await page.getByRole('combobox',{name:'Office navigation'}).selectOption('board');const detail=page.getByRole('region',{name:'Tasks board detail'});await detail.getByRole('combobox',{name:'Task',exact:true}).selectOption(job.id);await expect(detail).toContainText('Recorded worker at Computer 19');await detail.getByRole('button',{name:'Open session',exact:true}).click();
  166 |  session=page.getByRole('dialog',{name:'Agent session'});await expect(session.locator('.session-records')).toHaveAttribute('data-session-run',runId);
  167 |  await session.getByRole('button',{name:'Detach session',exact:true}).click();await expect(session).toContainText('No live session attached');expect((await read()).office_sessions.some((row:{station_id:string})=>row.station_id==='parent_019')).toBe(false);expect(coding).toEqual([]);
  168 |  await writeFile(path.resolve('../evidence/desktop/session-browser.json'),JSON.stringify({scope:'Actual local inspection; persistent display ownership, not coding dispatch or live Codex conversation',owner,reload_restored:true,board_links_same_session:true,open_results_same_job:true,wrong_worker_rejected:true,fixtures:['Read-only runInfo response with explicitly fixture-wrong-worker; no persisted state changed'],explicit_detach:true,coding_requests:coding,axe_violations:axe.violations.map(v=>v.id)},null,2));
  169 | });
  170 |
```
