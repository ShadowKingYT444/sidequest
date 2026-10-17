# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: jobs-live.spec.ts >> genuine local inspection job produces immutable files and a check report
- Location: tests/browser/jobs-live.spec.ts:8:1

# Error details

```
Error: expect(locator).toHaveText(expected) failed

Locator:  getByRole('region', { name: 'Local jobs board' }).locator('.job-state')
Expected: "verifying"
Received: "blocked"
Timeout:  20000ms

Call log:
  - Expect "toHaveText" getByRole('region', { name: 'Local jobs board' }).locator('.job-state') with timeout 20000ms
  - waiting for getByRole('region', { name: 'Local jobs board' }).locator('.job-state')
    - locator resolved to <span class="job-state">queued</span>
    - unexpected value "queued"
    5 × locator resolved to <span class="job-state">running</span>
      - unexpected value "running"
    37 × locator resolved to <span class="job-state">blocked</span>
       - unexpected value "blocked"

```

```yaml
- text: blocked
```

# Test source

```ts
  1   | import {evidenceDirectory} from './evidence';
  2   | import {test,expect} from './timing';
  3   | import path from 'node:path';
  4   | import {writeFile} from 'node:fs/promises';
  5   | import AxeBuilder from '@axe-core/playwright';
  6   | const evidence=evidenceDirectory();
  7   | 
  8   | test('genuine local inspection job produces immutable files and a check report',async({page,request})=>{
  9   |   test.setTimeout(120_000);
  10  |   test.skip(process.env.SIDEQUEST_TEST_INSPECTION!=='1','Opt in only against the configured real local inspection runtime. Never starts a coding model.');
  11  |   const errors:string[]=[];page.on('pageerror',error=>errors.push(error.message));
  12  |   const calls:{method:string;args:unknown[]}[]=[];
  13  |   page.on('request',req=>{if(req.url().includes('/__sidequest/runtime/'))calls.push({method:req.url().split('/').at(-1)!,args:req.postDataJSON()});});
  14  |   await page.goto('/');await expect(page.locator('.app-footer')).toHaveAttribute('data-actor-status','ready',{timeout:60000});await page.getByRole('button',{name:'Jobs',exact:true}).click();
  15  |   const board=page.getByRole('region',{name:'Local jobs board'});
  16  |   await expect(board).toBeVisible();await expect(board).toContainText('Local Git inspection');
  17  |   await expect(page.getByTestId('diff-editor')).toHaveCount(0);
  18  |   const projects=board.locator('#job-project');
  19  |   if(await projects.inputValue()===''){
  20  |     await board.getByRole('button',{name:'Register configured repository'}).click();
  21  |     await expect.poll(()=>projects.inputValue()).not.toBe('');
  22  |   }
  23  |   const title=`Browser inspection ${new Date().toISOString()}`;
  24  |   await board.getByLabel('Inspection title').fill(title);
  25  |   await board.getByRole('button',{name:'Submit inspection',exact:true}).click();
  26  |   await board.getByRole('button',{name:new RegExp(title.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'))}).click();
  27  |   await expect(board.getByRole('button',{name:'Run inspection',exact:true})).toBeEnabled();
  28  |   await page.screenshot({path:path.join(evidence,'job-queued.png')});
  29  |   await board.getByRole('button',{name:'Run inspection',exact:true}).click();
> 30  |   await expect(board.locator('.job-state')).toHaveText('verifying',{timeout:20_000});
      |                                             ^ Error: expect(locator).toHaveText(expected) failed
  31  |   await expect(board.locator('.job-checks')).toContainText('pass',{timeout:90_000});
  32  |   await expect(board).toContainText('Inspection results ready.');
  33  |   await expect(board.locator('.artifact-files>button').first()).toBeVisible();
  34  |   await expect(board.locator('.artifact-text')).not.toContainText('Loading file text…');
  35  |   await expect(board.locator('.artifact-files>button').first()).toBeVisible();
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
```