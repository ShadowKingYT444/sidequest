# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: jobs-live.spec.ts >> genuine local inspection job produces immutable files and a check report
- Location: tests/browser/jobs-live.spec.ts:6:1

# Error details

```
Error: expect(locator).toHaveText(expected) failed

Locator:  getByRole('region', { name: 'Local jobs board' }).locator('.job-state')
Expected: "verifying"
Received: "failed"
Timeout:  20000ms

Call log:
  - Expect "toHaveText" getByRole('region', { name: 'Local jobs board' }).locator('.job-state') with timeout 20000ms
  - waiting for getByRole('region', { name: 'Local jobs board' }).locator('.job-state')
    - locator resolved to <span class="job-state">queued</span>
    - unexpected value "queued"
    7 × locator resolved to <span class="job-state">running</span>
      - unexpected value "running"
    35 × locator resolved to <span class="job-state">failed</span>
       - unexpected value "failed"

```

```yaml
- text: failed
```

# Test source

```ts
  1   | import {test,expect} from './timing';
  2   | import path from 'node:path';
  3   | import {writeFile} from 'node:fs/promises';
  4   | import AxeBuilder from '@axe-core/playwright';
  5   | 
  6   | test('genuine local inspection job produces immutable files and a check report',async({page,request})=>{
  7   |   test.setTimeout(120_000);
  8   |   test.skip(process.env.SIDEQUEST_TEST_INSPECTION!=='1','Opt in only against the configured real local inspection runtime. Never starts a coding model.');
  9   |   const errors:string[]=[];page.on('pageerror',error=>errors.push(error.message));
  10  |   const calls:{method:string;args:unknown[]}[]=[];
  11  |   page.on('request',req=>{if(req.url().includes('/__sidequest/runtime/'))calls.push({method:req.url().split('/').at(-1)!,args:req.postDataJSON()});});
  12  |   await page.goto('/');await expect(page.locator('.app-footer')).toHaveAttribute('data-actor-status','ready',{timeout:60000});await page.getByRole('button',{name:'Jobs',exact:true}).click();
  13  |   const board=page.getByRole('region',{name:'Local jobs board'});
  14  |   await expect(board).toBeVisible();await expect(board).toContainText('Local Git inspection');
  15  |   await expect(page.getByTestId('diff-editor')).toHaveCount(0);
  16  |   const projects=board.locator('#job-project');
  17  |   if(await projects.inputValue()===''){
  18  |     await board.getByRole('button',{name:'Register configured repository'}).click();
  19  |     await expect.poll(()=>projects.inputValue()).not.toBe('');
  20  |   }
  21  |   const title=`Browser inspection ${new Date().toISOString()}`;
  22  |   await board.getByLabel('Inspection title').fill(title);
  23  |   await board.getByRole('button',{name:'Submit inspection',exact:true}).click();
  24  |   await board.getByRole('button',{name:new RegExp(title.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'))}).click();
  25  |   await expect(board.getByRole('button',{name:'Run inspection',exact:true})).toBeEnabled();
  26  |   await page.screenshot({path:path.resolve('../evidence/desktop/job-queued.png')});
  27  |   await board.getByRole('button',{name:'Run inspection',exact:true}).click();
> 28  |   await expect(board.locator('.job-state')).toHaveText('verifying',{timeout:20_000});
      |                                             ^ Error: expect(locator).toHaveText(expected) failed
  29  |   await expect(board.locator('.job-checks')).toContainText('pass',{timeout:90_000});
  30  |   await expect(board).toContainText('Inspection results ready.');
  31  |   await expect(board.locator('.artifact-files>button').first()).toBeVisible();
  32  |   await expect(board.locator('.artifact-text')).not.toContainText('Loading file text…');
  33  |   await expect(board.locator('.artifact-files>button').first()).toBeVisible();
  34  |   await page.screenshot({path:path.resolve('../evidence/desktop/job-result.png')});
  35  |   await board.getByRole('button',{name:'Git diff',exact:true}).click();
  36  |   await expect(board.locator('.artifact-text')).toContainText('No textual changes in this inspected candidate.');
  37  |   await page.screenshot({path:path.resolve('../evidence/desktop/job-diff.png')});
  38  |   await board.locator('#job-artifact').selectOption({label:await board.locator('#job-artifact option').filter({hasText:'test_report'}).first().textContent()??''});
  39  |   await expect(board.locator('.artifact-text')).toContainText('candidate.frozen_identity');
  40  |   await expect.poll(async()=>JSON.parse(await board.locator('.artifact-text').textContent()??'{}').inference_calls).toBe(0);
  41  |   const report=JSON.parse(await board.locator('.artifact-text').textContent()??'{}');
  42  |   await page.screenshot({path:path.resolve('../evidence/desktop/job-check-report.png')});
  43  |   await board.locator('.job-activity > summary').click();
  44  |   const activity=board.getByRole('region',{name:'Run activity'});
  45  |   await expect(activity).toContainText('No model call');
  46  |   await expect(activity.locator('.run-activity-state')).toHaveText('completed');
  47  |   await expect.poll(()=>activity.locator('.run-activity-timeline>li').count()).toBeGreaterThan(0);
  48  |   await page.screenshot({path:path.resolve('../evidence/desktop/run-activity-actual.png')});
  49  |   await board.locator('.job-activity > summary').click();
  50  |   await board.locator('.coding-readiness summary').click();
  51  |   await expect(board.locator('.coding-readiness')).toContainText('Coding tasks remain blocked.');
  52  |   const refreshStart=calls.length;
  53  |   await board.getByRole('button',{name:'Refresh status',exact:true}).click();
  54  |   await expect.poll(()=>calls.slice(refreshStart).filter(call=>call.method==='capabilities').length).toBeGreaterThan(0);
  55  |   expect(calls.slice(refreshStart).every(call=>['snapshot','capabilities','artifacts','artifact','files','text','diff','runInfo','runEvents'].includes(call.method))).toBe(true);
  56  |   await page.screenshot({path:path.resolve('../evidence/desktop/job-readiness.png')});
  57  |   await board.locator('.coding-readiness summary').click();
  58  |   const responsiveAccessibility:{width:number;violations:unknown[]}[]=[];
  59  |   for(const width of [960,390]){
  60  |     await page.setViewportSize({width,height:780});
  61  |     await board.locator('.artifact-content').scrollIntoViewIfNeeded();
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
```