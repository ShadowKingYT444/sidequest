# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: monitor-ui.spec.ts >> local monitor drafts, attachments and scroll survive Escape, expansion, delayed reads and outages
- Location: tests/browser/monitor-ui.spec.ts:39:1

# Error details

```
Error: locator.evaluate: Test ended.
Call log:
  - waiting for locator('.office-canvas canvas')
    - locator resolved to visible <canvas width="1440" height="820" data-agent-badges="[]" data-shadow-passes="5" data-engine="three.js r186" data-render-frame-count="5" data-camera-target="[1,-0.3,-3.8]" data-office-controls-enabled="true" data-camera-position="[11.5,8.5,12]"></canvas>

```

# Test source

```ts
  1   | import {evidenceDirectory} from './evidence';
  2   | import {test,expect,type Page} from './timing';
  3   | import {writeFile} from 'node:fs/promises';
  4   | import path from 'node:path';
  5   | import {PerspectiveCamera,Vector3,Euler} from 'three';
  6   | import AxeBuilder from '@axe-core/playwright';
  7   | const evidence=evidenceDirectory();
  8   | const origin={Origin:'http://127.0.0.1:5173'};
  9   | const png=Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aTioAAAAASUVORK5CYII=','base64');
> 10  | const pose=async(page:Page)=>page.locator('.office-canvas canvas').evaluate(node=>({position:JSON.parse((node as HTMLElement).dataset.cameraPosition!),target:JSON.parse((node as HTMLElement).dataset.cameraTarget!)}));
      |                                                                    ^ Error: locator.evaluate: Test ended.
  11  | async function paste(page:Page,text:string,image=false){await page.getByRole('textbox',{name:'Message this session'}).evaluate((node,payload)=>{const transfer=new DataTransfer();transfer.setData('text/plain',payload.text);transfer.setData('text/html','<img src=x onerror="window.__badPaste=true">');if(payload.image)transfer.items.add(new File([Uint8Array.from(payload.bytes)],'clipboard.png',{type:'image/png',lastModified:1}));node.dispatchEvent(new ClipboardEvent('paste',{clipboardData:transfer,bubbles:true,cancelable:true}));},{text,image,bytes:Array.from(png)});}
  12  | 
  13  | test('physical monitor POV restores orbited office camera through an interrupted return',async({page,request})=>{
  14  |   test.setTimeout(120_000);test.skip(process.env.SIDEQUEST_TEST_INSPECTION!=='1','Requires existing deterministic local inspection records; no coding job launches.');
  15  |   const marks:{phase:string;at:number}[]=[];const started=Date.now();const mark=async(phase:string)=>{marks.push({phase,at:Date.now()-started});await writeFile(path.join(evidence,'monitor-camera-timing.json'),JSON.stringify(marks,null,2));};
  16  |   const mutations:string[]=[],errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/__sidequest\/runtime\/(submitCoding|runCoding|enableCoding|submitInspection|run|register)$/.test(r.url())||/upload/i.test(r.url()))mutations.push(r.url());});
  17  |   const read=async()=>{const r=await request.post('/__sidequest/runtime/snapshot',{data:[],headers:origin});expect(r.ok()).toBe(true);return r.json();};
  18  |   let state=await read();const job=state.jobs.find((j:{execution_profile:string;run_ids:string[]})=>j.execution_profile==='local_git_inspection'&&j.run_ids?.length);expect(job).toBeTruthy();
  19  |   const runId=job.run_ids.at(-1),run=(await (await request.post('/__sidequest/runtime/runInfo',{data:[runId],headers:origin})).json()).run;
  20  |   const previous=state.office_sessions.filter((o:{station_id:string;worker_id:string})=>o.station_id==='parent_019'||o.worker_id===run.worker_id);
  21  |   for(const owner of previous){expect((await request.post('/__sidequest/runtime/clearSession',{data:[owner.station_id,state.revision],headers:origin})).ok()).toBe(true);state=await read();}
  22  |   expect((await request.post('/__sidequest/runtime/assignSession',{data:['parent_019',job.id,runId,state.revision],headers:origin})).ok()).toBe(true);
  23  |   await page.goto('/');await expect(page.locator('.app-footer')).toHaveAttribute('data-actor-status','ready',{timeout:60000});
  24  |   await mark('actors-ready');const canvas=page.locator('.office-canvas canvas'),box=(await canvas.boundingBox())!;const initial=await pose(page);
  25  |   await page.mouse.move(box.x+box.width*.9,box.y+box.height*.12);await page.mouse.wheel(0,-120);await expect.poll(async()=>JSON.stringify(await pose(page))).not.toBe(JSON.stringify(initial));
  26  |   await mark('office-orbit-changed');const office=await pose(page);
  27  |   const bindings=await (await request.get('/office/bindings.json')).json(),station=bindings.stations.find((s:{id:string})=>s.id==='parent_019');
  28  |   const camera=new PerspectiveCamera(35,box.width/box.height,.05,1000);camera.position.fromArray(office.position);camera.lookAt(new Vector3().fromArray(office.target));camera.updateMatrixWorld();
  29  |   const point=new Vector3(0,station.screenSize[1]*.3,.012).applyEuler(new Euler(...station.rotation as [number,number,number])).add(new Vector3().fromArray(station.anchor)).project(camera);
  30  |   const click={x:box.x+(point.x+1)*box.width/2,y:box.y+(1-point.y)*box.height/2};await page.mouse.click(click.x,click.y);
  31  |   await expect(page.locator('main')).toHaveAttribute('data-mode','desk');await expect(page.locator('main')).toHaveAttribute('data-station','parent_019');
  32  |   const trace=page.getByRole('region',{name:'Session execution trace'}),composer=page.getByRole('form',{name:'Local prompt composer'}),input=page.getByRole('textbox',{name:'Message this session'});
  33  |   await expect(trace).toHaveAttribute('data-session-run',runId);await expect(trace.locator('.monitor-events>li').first()).toBeVisible();await expect(trace).toContainText('Checking');await expect(page.getByTestId('diff-editor')).toHaveCount(0);await mark('physical-monitor-trace-visible');
  34  |   await page.evaluate(async()=>{document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}));await new Promise(requestAnimationFrame);const select=document.querySelector<HTMLSelectElement>('.computer-picker')!;select.value='monitor:parent_019';select.dispatchEvent(new Event('change',{bubbles:true}));});await expect(page.locator('main')).toHaveAttribute('data-mode','desk');await page.keyboard.press('Escape');await expect.poll(async()=>{const actual=await pose(page);return Math.max(...office.position.map((n:number,i:number)=>Math.abs(n-actual.position[i])));}).toBeLessThan(.01);await mark('interrupted-return-restored');
  35  |   await writeFile(path.join(evidence,'monitor-camera-browser.json'),JSON.stringify({scope:'Actual original monitor and recorded local inspection; no model calls',station:'parent_019',runId,office,physicalMonitorClick:click,interruptedReturnRestored:true,mutations,errors},null,2));expect(mutations).toEqual([]);expect(errors).toEqual([]);
  36  |   state=await read();expect((await request.post('/__sidequest/runtime/clearSession',{data:['parent_019',state.revision],headers:origin})).ok()).toBe(true);
  37  | });
  38  | 
  39  | test('local monitor drafts, attachments and scroll survive Escape, expansion, delayed reads and outages',async({page,request})=>{
  40  |   test.setTimeout(180_000);test.skip(process.env.SIDEQUEST_TEST_INSPECTION!=='1','Requires existing deterministic local inspection records; no coding job launches.');
  41  |   const marks:{phase:string;at:number}[]=[];const started=Date.now();const mark=async(phase:string)=>{marks.push({phase,at:Date.now()-started});await writeFile(path.join(evidence,'monitor-ui-timing.json'),JSON.stringify(marks,null,2));};
  42  |   const mutations:string[]=[],errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/__sidequest\/runtime\/(submitCoding|runCoding|enableCoding|submitInspection|run|register)$/.test(r.url())||/upload/i.test(r.url()))mutations.push(r.url());});
  43  |   const read=async()=>{const r=await request.post('/__sidequest/runtime/snapshot',{data:[],headers:origin});expect(r.ok()).toBe(true);return r.json();};
  44  |   let state=await read();const job=state.jobs.find((j:{execution_profile:string;run_ids:string[]})=>j.execution_profile==='local_git_inspection'&&j.run_ids?.length);expect(job).toBeTruthy();
  45  |   const runId=job.run_ids.at(-1),run=(await (await request.post('/__sidequest/runtime/runInfo',{data:[runId],headers:origin})).json()).run;
  46  |   const previous=state.office_sessions.filter((o:{station_id:string;worker_id:string})=>o.station_id==='parent_019'||o.worker_id===run.worker_id);
  47  |   for(const owner of previous){expect((await request.post('/__sidequest/runtime/clearSession',{data:[owner.station_id,state.revision],headers:origin})).ok()).toBe(true);state=await read();}
  48  |   expect((await request.post('/__sidequest/runtime/assignSession',{data:['parent_019',job.id,runId,state.revision],headers:origin})).ok()).toBe(true);
  49  |   await page.emulateMedia({reducedMotion:'reduce'});await page.goto('/');await expect(page.locator('.app-footer')).toHaveAttribute('data-actor-status','ready',{timeout:60000});await mark('actors-ready');const office=await pose(page);
  50  |   await page.getByRole('combobox',{name:'Office navigation'}).selectOption('monitor:parent_019');const trace=page.getByRole('region',{name:'Session execution trace'}),composer=page.getByRole('form',{name:'Local prompt composer'}),input=page.getByRole('textbox',{name:'Message this session'});await expect(trace).toHaveAttribute('data-session-run',runId);await expect(trace.locator('.monitor-events>li').first()).toBeVisible();await mark('trace-visible');
  51  |   await input.fill('Keep this draft. ');await input.evaluate(node=>(node as HTMLTextAreaElement).setSelectionRange(17,17));await paste(page,'Plain\r\n<script>literal</script>',true);
  52  |   await expect(input).toHaveValue('Keep this draft. Plain\n<script>literal</script>');await expect(composer.getByRole('img',{name:'Preview of clipboard.png'})).toBeVisible();
  53  |   await composer.getByLabel('Select local files').setInputFiles({name:'notes.txt',mimeType:'text/plain',buffer:Buffer.from('Local notes')});await expect(composer.getByRole('button',{name:'Remove notes.txt'})).toBeVisible();
  54  |   await composer.evaluate(node=>{const transfer=new DataTransfer();transfer.items.add(new File(['diff --git a/a b/a'],'review.diff',{type:'text/plain',lastModified:2}));node.dispatchEvent(new DragEvent('drop',{dataTransfer:transfer,bubbles:true,cancelable:true}));});await expect(composer.getByRole('button',{name:'Remove review.diff'})).toBeVisible();
  55  |   await composer.getByLabel('Select local files').setInputFiles({name:'bad.svg',mimeType:'image/svg+xml',buffer:Buffer.from('<svg onload="alert(1)"/>')});await expect(composer.getByRole('alert')).toContainText('use PNG');await expect(composer.getByRole('button',{name:'Remove bad.svg'})).toHaveCount(0);await composer.getByRole('button',{name:'Dismiss attachment errors'}).click();
  56  |   await composer.getByLabel('Select local files').setInputFiles({name:'huge.txt',mimeType:'text/plain',buffer:Buffer.alloc(10*1024*1024+1)});await expect(composer.getByRole('alert')).toContainText('10 MiB');await composer.getByRole('button',{name:'Dismiss attachment errors'}).click();
  57  |   await expect(composer.getByRole('button',{name:'Send message'})).toBeDisabled();await input.press('Control+Enter');expect(mutations).toEqual([]);expect(await page.evaluate(()=>Object.hasOwn(window,'__badPaste'))).toBe(false);
  58  |   const output=trace.getByLabel('Recorded output');await output.evaluate(node=>{node.scrollTop=node.scrollHeight;});await expect.poll(async()=>Number(await output.getAttribute('data-scroll-top'))).toBeGreaterThan(0);const scroll=Number(await output.getAttribute('data-scroll-top'));await mark('paste-drop-picker-errors-and-scroll');
  59  |   await page.screenshot({path:path.join(evidence,'monitor-pov-local-draft.png')});const focused=await pose(page);
  60  |   await page.keyboard.press('Escape');await expect(page.locator('main')).toHaveAttribute('data-mode','overview');await expect(trace).toHaveCount(0);
  61  |   await expect.poll(async()=>{const actual=await pose(page);return Math.max(...office.position.map((n:number,i:number)=>Math.abs(n-actual.position[i])),...office.target.map((n:number,i:number)=>Math.abs(n-actual.target[i])));}).toBeLessThan(.01);
  62  |   await page.getByRole('combobox',{name:'Office navigation'}).selectOption('monitor:parent_019');await expect(input).toHaveValue('Keep this draft. Plain\n<script>literal</script>');await expect(composer.getByRole('img',{name:'Preview of clipboard.png'})).toBeVisible();await expect.poll(async()=>Number(await output.getAttribute('data-scroll-top'))).toBeGreaterThan(0);
  63  |   await mark('reopen-retained');await page.getByRole('button',{name:'Files',exact:true}).click();await expect(page.getByTestId('diff-editor')).toHaveCount(1);await page.getByRole('button',{name:'Trace',exact:true}).click();await expect(page.getByTestId('diff-editor')).toHaveCount(0);await expect(input).toHaveValue('Keep this draft. Plain\n<script>literal</script>');
  64  |   await page.getByRole('button',{name:'Expand',exact:true}).click();await page.keyboard.press('Escape');await page.getByRole('combobox',{name:'Office navigation'}).selectOption('monitor:parent_019');await expect.poll(async()=>Number(await output.getAttribute('data-scroll-top'))).toBeGreaterThan(0);
  65  |   await mark('tabs-expand-and-escape-retained');await composer.getByRole('button',{name:'Remove notes.txt'}).click();await expect(composer.getByRole('button',{name:'Remove notes.txt'})).toHaveCount(0);
  66  |   await page.evaluate(()=>{const original=Blob.prototype.arrayBuffer;let release!:()=>void;const gate=new Promise<void>(resolve=>release=resolve);(window as unknown as {releaseDraftRead:()=>void}).releaseDraftRead=release;Blob.prototype.arrayBuffer=function(){return this.size===16?gate.then(()=>original.call(this)):original.call(this);};});
  67  |   await composer.getByLabel('Select local files').setInputFiles({name:'delayed.png',mimeType:'image/png',buffer:png});await expect(composer).toContainText('Reading local files');
  68  |   await page.keyboard.press('Escape');await page.getByRole('combobox',{name:'Office navigation'}).selectOption('monitor:parent_019');await input.fill('Newest reopened draft');await composer.getByLabel('Select local files').setInputFiles({name:'fresh.txt',mimeType:'text/plain',buffer:Buffer.from('latest file')});
  69  |   await page.evaluate(()=>(window as unknown as {releaseDraftRead:()=>void}).releaseDraftRead());await expect(composer.getByRole('button',{name:'Remove delayed.png'})).toBeVisible();await expect(composer.getByRole('button',{name:'Remove fresh.txt'})).toBeVisible();await expect(input).toHaveValue('Newest reopened draft');
  70  |   await page.route('**/__sidequest/runtime/snapshot',route=>route.fulfill({status:503,json:{error:'Test-only readonly snapshot outage'}}));await expect(page.locator('.stage-status')).toContainText('sessions unchecked');await expect(input).toHaveValue('Newest reopened draft');await input.fill('Newest reopened draft during outage');await page.unroute('**/__sidequest/runtime/snapshot');await expect(trace.locator('.monitor-events>li').first()).toBeVisible();await expect(input).toHaveValue('Newest reopened draft during outage');
  71  |   await mark('delayed-read-and-outage-retained');await page.setViewportSize({width:390,height:780});await expect(input).toBeVisible();expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  72  |   await page.screenshot({path:path.join(evidence,'monitor-local-draft-390.png')});const axe=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze();expect(axe.violations.map(v=>({id:v.id,impact:v.impact}))).toEqual([]);
  73  |   await writeFile(path.join(evidence,'monitor-ui-browser.json'),JSON.stringify({scope:'Real local Git inspection trace; native dispatch and OS clipboard are not established',station:'parent_019',runId,office,focused,traceScroll:scroll,returnCameraRestored:true,localAttachmentPaths:['synthetic clipboard event','browser file picker','browser drag/drop'],retainedAcrossEscapeAndTabs:true,delayedReadReopenRetained:true,outageDraftIdentityRetained:true,noSilentUpload:true,mutations,errors,axe:axe.violations.map(v=>v.id)},null,2));
  74  |   expect(errors).toEqual([]);await mark('mobile-accessibility-pass');
  75  |   state=await read();expect((await request.post('/__sidequest/runtime/clearSession',{data:['parent_019',state.revision],headers:origin})).ok()).toBe(true);
  76  | });
  77  | 
  78  | test('explicit read-only fixture shows distinct notifications and one badge per primary figure',async({page,request})=>{
  79  |   test.setTimeout(120_000);test.skip(process.env.SIDEQUEST_TEST_INSPECTION!=='1','Uses actual record identities in an explicitly labeled read-only fixture.');
  80  |   const read=async()=>{const response=await request.post('/__sidequest/runtime/snapshot',{data:[],headers:origin});expect(response.ok()).toBe(true);return response.json();};
  81  |   const inspected=(state:any)=>state.jobs.filter((j:{execution_profile:string;run_ids:string[]})=>j.execution_profile==='local_git_inspection'&&j.run_ids?.length);
  82  |   let actual=await read();const seeded:string[]=[];
  83  |   // Fresh runtime databases need two genuine record identities before the read-only UI fixture.
  84  |   // This opt-in setup uses only deterministic zero-budget Git inspection, never coding.
  85  |   while(inspected(actual).length<2){
  86  |     if(!actual.projects.length){const registered=await request.post('/__sidequest/runtime/register',{data:[actual.revision],headers:origin});expect(registered.ok()).toBe(true);expect((await registered.json()).accepted).toBe(true);actual=await read();}
  87  |     const submitted=await request.post('/__sidequest/runtime/submitInspection',{data:[actual.projects[0].id,`Notification fixture setup ${Date.now()}`,actual.revision],headers:origin});expect(submitted.ok()).toBe(true);const reply=await submitted.json();expect(reply.accepted).toBe(true);expect(reply.result?.job_id).toBeTruthy();seeded.push(reply.result.job_id);actual=await read();
  88  |     const started=await request.post('/__sidequest/runtime/run',{data:[reply.result.job_id,actual.revision],headers:origin});expect(started.ok()).toBe(true);expect((await started.json()).accepted).toBe(true);
  89  |     await expect.poll(async()=>{actual=await read();const job=actual.jobs.find((j:{id:string})=>j.id===reply.result.job_id);return !!job?.run_ids.length&&job.tasks.every((task:{state:string})=>task.state==='completed')&&job.checks.length>0&&job.checks.every((check:{state:string})=>check.state==='pass')&&job.spent_usd===0;},{timeout:20_000}).toBe(true);
  90  |   }
  91  |   const jobs=inspected(actual).slice(0,2);expect(jobs).toHaveLength(2);
  92  |   const owners=[];for(const [i,job] of jobs.entries()){const run=(await (await request.post('/__sidequest/runtime/runInfo',{data:[job.run_ids.at(-1)],headers:origin})).json()).run;owners.push({station_id:i===0?'parent_019':'parent_020',job_id:job.id,project_id:job.project_id,run_id:run.id,worker_id:run.worker_id,assigned_at:new Date().toISOString()});}
  93  |   owners[1].worker_id='fixture-attention-worker';
  94  |   const fixture={...actual,mode:'fixture',jobs:jobs.map((job:any,i:number)=>({...job,state:i===0?'completed':'failed',title:`Test fixture · ${i===0?'Completed task':'Attention task'}`,blocked_reason:i===0?null:'Test fixture failure, no execution performed',tasks:job.tasks.map((task:any)=>({...task,state:i===0?'completed':'failed',worker_id:i===0?task.worker_id:'fixture-attention-worker'})),checks:job.checks.map((check:any)=>({...check,state:i===0?'pass':'fail'}))})),office_jobs:[],office_jobs_truncated:false,office_sessions:owners};
  95  |   const mutations:string[]=[];page.on('request',r=>{if(/__sidequest\/runtime\/(submitCoding|runCoding|enableCoding|submitInspection|run|register|assignSession|clearSession)$/.test(r.url()))mutations.push(r.url());});
  96  |   await page.route('**/__sidequest/runtime/snapshot',route=>route.fulfill({json:fixture}));await page.goto('/');await expect(page.locator('.app-footer')).toHaveAttribute('data-actor-status','ready',{timeout:60000});await expect(page.locator('.app-footer')).toContainText('Test fixture');
  97  |   const canvas=page.locator('.office-canvas canvas');await expect.poll(async()=>JSON.parse(await canvas.getAttribute('data-agent-badges')??'[]').length).toBe(2);
  98  |   const badges=JSON.parse((await canvas.getAttribute('data-agent-badges'))!);expect(badges).toEqual(expect.arrayContaining([{sceneId:'worker_parent_019',stationId:'parent_019',kind:'completed',jobId:jobs[0].id},{sceneId:'worker_parent_020',stationId:'parent_020',kind:'attention',jobId:jobs[1].id}]));expect(badges.some((b:{sceneId:string})=>b.sceneId==='child_019_01')).toBe(false);
  99  |   await page.getByRole('button',{name:/^Notifications/}).click();const tray=page.getByRole('region',{name:'Notifications',exact:true});await expect(tray.locator('[data-notification-kind=completed]')).toHaveCount(1);await expect(tray.locator('[data-notification-kind=attention]')).toHaveCount(1);await expect(tray).toContainText('Test fixture');
  100 |   await page.screenshot({path:path.join(evidence,'notifications-badges-fixture.png')});const axe=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze();expect(axe.violations.map(v=>({id:v.id,impact:v.impact}))).toEqual([]);
  101 |   await tray.getByRole('button',{name:/Completed task/}).click();await expect(page.locator('main')).toHaveAttribute('data-station','parent_019');await expect(page.getByRole('region',{name:'Session execution trace'})).toHaveAttribute('data-session-run',owners[0].run_id);expect(mutations).toEqual([]);
  102 |   await writeFile(path.join(evidence,'notifications-browser.json'),JSON.stringify({scope:'Explicit read-only fixture of completion/attention; not real successful worker dispatch',fixture:true,zeroBudgetSetupJobs:seeded,badges,duplicateChildBadge:false,mutations,axe:axe.violations.map(v=>v.id)},null,2));
  103 | });
  104 | 
```