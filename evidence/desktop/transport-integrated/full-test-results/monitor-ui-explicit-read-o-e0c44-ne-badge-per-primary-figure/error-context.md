# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: monitor-ui.spec.ts >> explicit read-only fixture shows distinct notifications and one badge per primary figure
- Location: tests/browser/monitor-ui.spec.ts:77:1

# Error details

```
Error: expect(received).toHaveLength(expected)

Expected length: 2
Received length: 1
Received array:  [{"allowed_actions": ["read_repo", "run_checks"], "artifact_ids": ["art_13d534c556ab405ba8e0f2746aefa6cc", "art_17b5c39e7f4b4ad186d73dd4963e9034", "art_da28bdbe39b64c6cb78d02439728d071", "sha256:1ba35f964707623cd27295f53a28758a478d2a0635e63ed749004b2d435f8780", "2c2020f7-54ce-4abd-86cd-534f50570b6b", "556e685c-8920-4c6d-8723-6a300257a81c", "83d13572-2948-432b-96a0-38b9ee9a0d49", "ad4ac5db-2692-43a8-889e-0009a78132bb", "285927d8-335f-49b6-b7ea-3da7ec598a32", "2d48f4da-417b-46f9-a16d-fff8a50580ac", …], "blocked_reason": null, "budget_usd": 0, "candidate_id": "cand_d43916a138e34ed38ae5549fa86509df", "checks": [{"evidence_artifact_id": "sha256:1ba35f964707623cd27295f53a28758a478d2a0635e63ed749004b2d435f8780", "id": "candidate.frozen_identity", "state": "pass"}], "delivery_state": "disabled", "events": [{"artifact_id": null, "at": "2026-10-14T20:36:29.048Z", "id": 8, "message": "Immutable candidate artifacts frozen.", "type": "status"}, {"artifact_id": null, "at": "2026-10-14T20:36:29.375Z", "id": 9, "message": "Attempt result recorded.", "type": "status"}, {"artifact_id": "art_13d534c556ab405ba8e0f2746aefa6cc", "at": "2026-10-14T20:36:29.376Z", "id": 10, "message": "Candidate recorded.", "type": "status"}, {"artifact_id": "sha256:1ba35f964707623cd27295f53a28758a478d2a0635e63ed749004b2d435f8780", "at": "2026-10-14T20:36:29.378Z", "id": 11, "message": "Frozen identity check passed.", "type": "tool_finished"}, {"artifact_id": null, "at": "2026-10-14T20:36:29.378Z", "id": 12, "message": "Local Git inspection completed; the frozen candidate identity check passed. No model inference or delivery ran.", "type": "status"}], "execution_profile": "local_git_inspection", "id": "56706593-07c4-4b98-845e-c11b2578251e", "project_id": "bd2bb2ef-8252-4386-b699-d8dc740f6148", "run_ids": ["d3460454-49c7-4a47-9a6d-61b3158a5027"], "source": {"kind": "typed", "text": "Inspect the registered Git repository and produce immutable read-only artifacts with a frozen-identity check. No coding model, source mutation or delivery.", "uri": "sidequest:local-git-inspection"}, "spent_usd": 0, "state": "verifying", "tasks": [{"attempt_id": "d3460454-49c7-4a47-9a6d-61b3158a5027", "depends_on": [], "id": "9679fcb7-e7f7-49a4-a759-7feb8a1ce021", "state": "completed", "worker_id": "13cfe4e0-f18b-43b7-bb83-54cf43312a26"}], "title": "Browser inspection 2026-10-14T20:36:25.717Z", "worker_id": null, "workflow_version": 1}]
```

# Test source

```ts
  1  | import {test,expect,type Page} from './timing';
  2  | import {writeFile} from 'node:fs/promises';
  3  | import path from 'node:path';
  4  | import {PerspectiveCamera,Vector3,Euler} from 'three';
  5  | import AxeBuilder from '@axe-core/playwright';
  6  | const evidence=path.resolve('../evidence/desktop');
  7  | const origin={Origin:'http://127.0.0.1:5173'};
  8  | const png=Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aTioAAAAASUVORK5CYII=','base64');
  9  | const pose=async(page:Page)=>page.locator('.office-canvas canvas').evaluate(node=>({position:JSON.parse((node as HTMLElement).dataset.cameraPosition!),target:JSON.parse((node as HTMLElement).dataset.cameraTarget!)}));
  10 | async function paste(page:Page,text:string,image=false){await page.getByRole('textbox',{name:'Message this session'}).evaluate((node,payload)=>{const transfer=new DataTransfer();transfer.setData('text/plain',payload.text);transfer.setData('text/html','<img src=x onerror="window.__badPaste=true">');if(payload.image)transfer.items.add(new File([Uint8Array.from(payload.bytes)],'clipboard.png',{type:'image/png',lastModified:1}));node.dispatchEvent(new ClipboardEvent('paste',{clipboardData:transfer,bubbles:true,cancelable:true}));},{text,image,bytes:Array.from(png)});}
  11 | 
  12 | test('physical monitor POV restores orbited office camera through an interrupted return',async({page,request})=>{
  13 |   test.setTimeout(120_000);test.skip(process.env.SIDEQUEST_TEST_INSPECTION!=='1','Requires existing deterministic local inspection records; no coding job launches.');
  14 |   const marks:{phase:string;at:number}[]=[];const started=Date.now();const mark=async(phase:string)=>{marks.push({phase,at:Date.now()-started});await writeFile(path.join(evidence,'monitor-camera-timing.json'),JSON.stringify(marks,null,2));};
  15 |   const mutations:string[]=[],errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/__sidequest\/runtime\/(submitCoding|runCoding|enableCoding|submitInspection|run|register)$/.test(r.url())||/upload/i.test(r.url()))mutations.push(r.url());});
  16 |   const read=async()=>{const r=await request.post('/__sidequest/runtime/snapshot',{data:[],headers:origin});expect(r.ok()).toBe(true);return r.json();};
  17 |   let state=await read();const job=state.jobs.find((j:{execution_profile:string;run_ids:string[]})=>j.execution_profile==='local_git_inspection'&&j.run_ids?.length);expect(job).toBeTruthy();
  18 |   const runId=job.run_ids.at(-1),run=(await (await request.post('/__sidequest/runtime/runInfo',{data:[runId],headers:origin})).json()).run;
  19 |   const previous=state.office_sessions.filter((o:{station_id:string;worker_id:string})=>o.station_id==='parent_019'||o.worker_id===run.worker_id);
  20 |   for(const owner of previous){expect((await request.post('/__sidequest/runtime/clearSession',{data:[owner.station_id,state.revision],headers:origin})).ok()).toBe(true);state=await read();}
  21 |   expect((await request.post('/__sidequest/runtime/assignSession',{data:['parent_019',job.id,runId,state.revision],headers:origin})).ok()).toBe(true);
  22 |   await page.goto('/');await expect(page.locator('.app-footer')).toHaveAttribute('data-actor-status','ready',{timeout:60000});
  23 |   await mark('actors-ready');const canvas=page.locator('.office-canvas canvas'),box=(await canvas.boundingBox())!;const initial=await pose(page);
  24 |   await page.mouse.move(box.x+box.width*.9,box.y+box.height*.12);await page.mouse.wheel(0,-120);await expect.poll(async()=>JSON.stringify(await pose(page))).not.toBe(JSON.stringify(initial));
  25 |   await mark('office-orbit-changed');const office=await pose(page);
  26 |   const bindings=await (await request.get('/office/bindings.json')).json(),station=bindings.stations.find((s:{id:string})=>s.id==='parent_019');
  27 |   const camera=new PerspectiveCamera(35,box.width/box.height,.05,1000);camera.position.fromArray(office.position);camera.lookAt(new Vector3().fromArray(office.target));camera.updateMatrixWorld();
  28 |   const point=new Vector3(0,station.screenSize[1]*.3,.012).applyEuler(new Euler(...station.rotation as [number,number,number])).add(new Vector3().fromArray(station.anchor)).project(camera);
  29 |   const click={x:box.x+(point.x+1)*box.width/2,y:box.y+(1-point.y)*box.height/2};await page.mouse.click(click.x,click.y);
  30 |   await expect(page.locator('main')).toHaveAttribute('data-mode','desk');await expect(page.locator('main')).toHaveAttribute('data-station','parent_019');
  31 |   const trace=page.getByRole('region',{name:'Session execution trace'}),composer=page.getByRole('form',{name:'Local prompt composer'}),input=page.getByRole('textbox',{name:'Message this session'});
  32 |   await expect(trace).toHaveAttribute('data-session-run',runId);await expect(trace.locator('.monitor-events>li').first()).toBeVisible();await expect(trace).toContainText('Checking');await expect(page.getByTestId('diff-editor')).toHaveCount(0);await mark('physical-monitor-trace-visible');
  33 |   await page.evaluate(async()=>{document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}));await new Promise(requestAnimationFrame);const select=document.querySelector<HTMLSelectElement>('.computer-picker')!;select.value='monitor:parent_019';select.dispatchEvent(new Event('change',{bubbles:true}));});await expect(page.locator('main')).toHaveAttribute('data-mode','desk');await page.keyboard.press('Escape');await expect.poll(async()=>{const actual=await pose(page);return Math.max(...office.position.map((n:number,i:number)=>Math.abs(n-actual.position[i])));}).toBeLessThan(.01);await mark('interrupted-return-restored');
  34 |   await writeFile(path.join(evidence,'monitor-camera-browser.json'),JSON.stringify({scope:'Actual original monitor and recorded local inspection; no model calls',station:'parent_019',runId,office,physicalMonitorClick:click,interruptedReturnRestored:true,mutations,errors},null,2));expect(mutations).toEqual([]);expect(errors).toEqual([]);
  35 |   state=await read();expect((await request.post('/__sidequest/runtime/clearSession',{data:['parent_019',state.revision],headers:origin})).ok()).toBe(true);
  36 | });
  37 | 
  38 | test('local monitor drafts, attachments and scroll survive Escape, expansion, delayed reads and outages',async({page,request})=>{
  39 |   test.setTimeout(180_000);test.skip(process.env.SIDEQUEST_TEST_INSPECTION!=='1','Requires existing deterministic local inspection records; no coding job launches.');
  40 |   const marks:{phase:string;at:number}[]=[];const started=Date.now();const mark=async(phase:string)=>{marks.push({phase,at:Date.now()-started});await writeFile(path.join(evidence,'monitor-ui-timing.json'),JSON.stringify(marks,null,2));};
  41 |   const mutations:string[]=[],errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/__sidequest\/runtime\/(submitCoding|runCoding|enableCoding|submitInspection|run|register)$/.test(r.url())||/upload/i.test(r.url()))mutations.push(r.url());});
  42 |   const read=async()=>{const r=await request.post('/__sidequest/runtime/snapshot',{data:[],headers:origin});expect(r.ok()).toBe(true);return r.json();};
  43 |   let state=await read();const job=state.jobs.find((j:{execution_profile:string;run_ids:string[]})=>j.execution_profile==='local_git_inspection'&&j.run_ids?.length);expect(job).toBeTruthy();
  44 |   const runId=job.run_ids.at(-1),run=(await (await request.post('/__sidequest/runtime/runInfo',{data:[runId],headers:origin})).json()).run;
  45 |   const previous=state.office_sessions.filter((o:{station_id:string;worker_id:string})=>o.station_id==='parent_019'||o.worker_id===run.worker_id);
  46 |   for(const owner of previous){expect((await request.post('/__sidequest/runtime/clearSession',{data:[owner.station_id,state.revision],headers:origin})).ok()).toBe(true);state=await read();}
  47 |   expect((await request.post('/__sidequest/runtime/assignSession',{data:['parent_019',job.id,runId,state.revision],headers:origin})).ok()).toBe(true);
  48 |   await page.emulateMedia({reducedMotion:'reduce'});await page.goto('/');await expect(page.locator('.app-footer')).toHaveAttribute('data-actor-status','ready',{timeout:60000});await mark('actors-ready');const office=await pose(page);
  49 |   await page.getByRole('combobox',{name:'Office navigation'}).selectOption('monitor:parent_019');const trace=page.getByRole('region',{name:'Session execution trace'}),composer=page.getByRole('form',{name:'Local prompt composer'}),input=page.getByRole('textbox',{name:'Message this session'});await expect(trace).toHaveAttribute('data-session-run',runId);await expect(trace.locator('.monitor-events>li').first()).toBeVisible();await mark('trace-visible');
  50 |   await input.fill('Keep this draft. ');await input.evaluate(node=>(node as HTMLTextAreaElement).setSelectionRange(17,17));await paste(page,'Plain\r\n<script>literal</script>',true);
  51 |   await expect(input).toHaveValue('Keep this draft. Plain\n<script>literal</script>');await expect(composer.getByRole('img',{name:'Preview of clipboard.png'})).toBeVisible();
  52 |   await composer.getByLabel('Select local files').setInputFiles({name:'notes.txt',mimeType:'text/plain',buffer:Buffer.from('Local notes')});await expect(composer.getByRole('button',{name:'Remove notes.txt'})).toBeVisible();
  53 |   await composer.evaluate(node=>{const transfer=new DataTransfer();transfer.items.add(new File(['diff --git a/a b/a'],'review.diff',{type:'text/plain',lastModified:2}));node.dispatchEvent(new DragEvent('drop',{dataTransfer:transfer,bubbles:true,cancelable:true}));});await expect(composer.getByRole('button',{name:'Remove review.diff'})).toBeVisible();
  54 |   await composer.getByLabel('Select local files').setInputFiles({name:'bad.svg',mimeType:'image/svg+xml',buffer:Buffer.from('<svg onload="alert(1)"/>')});await expect(composer.getByRole('alert')).toContainText('use PNG');await expect(composer.getByRole('button',{name:'Remove bad.svg'})).toHaveCount(0);await composer.getByRole('button',{name:'Dismiss attachment errors'}).click();
  55 |   await composer.getByLabel('Select local files').setInputFiles({name:'huge.txt',mimeType:'text/plain',buffer:Buffer.alloc(10*1024*1024+1)});await expect(composer.getByRole('alert')).toContainText('10 MiB');await composer.getByRole('button',{name:'Dismiss attachment errors'}).click();
  56 |   await expect(composer.getByRole('button',{name:'Send message'})).toBeDisabled();await input.press('Control+Enter');expect(mutations).toEqual([]);expect(await page.evaluate(()=>Object.hasOwn(window,'__badPaste'))).toBe(false);
  57 |   const output=trace.getByLabel('Recorded output');await output.evaluate(node=>{node.scrollTop=node.scrollHeight;});await expect.poll(async()=>Number(await output.getAttribute('data-scroll-top'))).toBeGreaterThan(0);const scroll=Number(await output.getAttribute('data-scroll-top'));await mark('paste-drop-picker-errors-and-scroll');
  58 |   await page.screenshot({path:path.join(evidence,'monitor-pov-local-draft.png')});const focused=await pose(page);
  59 |   await page.keyboard.press('Escape');await expect(page.locator('main')).toHaveAttribute('data-mode','overview');await expect(trace).toHaveCount(0);
  60 |   await expect.poll(async()=>{const actual=await pose(page);return Math.max(...office.position.map((n:number,i:number)=>Math.abs(n-actual.position[i])),...office.target.map((n:number,i:number)=>Math.abs(n-actual.target[i])));}).toBeLessThan(.01);
  61 |   await page.getByRole('combobox',{name:'Office navigation'}).selectOption('monitor:parent_019');await expect(input).toHaveValue('Keep this draft. Plain\n<script>literal</script>');await expect(composer.getByRole('img',{name:'Preview of clipboard.png'})).toBeVisible();await expect.poll(async()=>Number(await output.getAttribute('data-scroll-top'))).toBeGreaterThan(0);
  62 |   await mark('reopen-retained');await page.getByRole('button',{name:'Files',exact:true}).click();await expect(page.getByTestId('diff-editor')).toHaveCount(1);await page.getByRole('button',{name:'Trace',exact:true}).click();await expect(page.getByTestId('diff-editor')).toHaveCount(0);await expect(input).toHaveValue('Keep this draft. Plain\n<script>literal</script>');
  63 |   await page.getByRole('button',{name:'Expand',exact:true}).click();await page.keyboard.press('Escape');await page.getByRole('combobox',{name:'Office navigation'}).selectOption('monitor:parent_019');await expect.poll(async()=>Number(await output.getAttribute('data-scroll-top'))).toBeGreaterThan(0);
  64 |   await mark('tabs-expand-and-escape-retained');await composer.getByRole('button',{name:'Remove notes.txt'}).click();await expect(composer.getByRole('button',{name:'Remove notes.txt'})).toHaveCount(0);
  65 |   await page.evaluate(()=>{const original=Blob.prototype.arrayBuffer;let release!:()=>void;const gate=new Promise<void>(resolve=>release=resolve);(window as unknown as {releaseDraftRead:()=>void}).releaseDraftRead=release;Blob.prototype.arrayBuffer=function(){return this.size===16?gate.then(()=>original.call(this)):original.call(this);};});
  66 |   await composer.getByLabel('Select local files').setInputFiles({name:'delayed.png',mimeType:'image/png',buffer:png});await expect(composer).toContainText('Reading local files');
  67 |   await page.keyboard.press('Escape');await page.getByRole('combobox',{name:'Office navigation'}).selectOption('monitor:parent_019');await input.fill('Newest reopened draft');await composer.getByLabel('Select local files').setInputFiles({name:'fresh.txt',mimeType:'text/plain',buffer:Buffer.from('latest file')});
  68 |   await page.evaluate(()=>(window as unknown as {releaseDraftRead:()=>void}).releaseDraftRead());await expect(composer.getByRole('button',{name:'Remove delayed.png'})).toBeVisible();await expect(composer.getByRole('button',{name:'Remove fresh.txt'})).toBeVisible();await expect(input).toHaveValue('Newest reopened draft');
  69 |   await page.route('**/__sidequest/runtime/snapshot',route=>route.fulfill({status:503,json:{error:'Test-only readonly snapshot outage'}}));await expect(page.locator('.stage-status')).toContainText('sessions unchecked');await expect(input).toHaveValue('Newest reopened draft');await input.fill('Newest reopened draft during outage');await page.unroute('**/__sidequest/runtime/snapshot');await expect(trace.locator('.monitor-events>li').first()).toBeVisible();await expect(input).toHaveValue('Newest reopened draft during outage');
  70 |   await mark('delayed-read-and-outage-retained');await page.setViewportSize({width:390,height:780});await expect(input).toBeVisible();expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  71 |   await page.screenshot({path:path.join(evidence,'monitor-local-draft-390.png')});const axe=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze();expect(axe.violations.map(v=>({id:v.id,impact:v.impact}))).toEqual([]);
  72 |   await writeFile(path.join(evidence,'monitor-ui-browser.json'),JSON.stringify({scope:'Real local Git inspection trace; native dispatch and OS clipboard are not established',station:'parent_019',runId,office,focused,traceScroll:scroll,returnCameraRestored:true,localAttachmentPaths:['synthetic clipboard event','browser file picker','browser drag/drop'],retainedAcrossEscapeAndTabs:true,delayedReadReopenRetained:true,outageDraftIdentityRetained:true,noSilentUpload:true,mutations,errors,axe:axe.violations.map(v=>v.id)},null,2));
  73 |   expect(errors).toEqual([]);await mark('mobile-accessibility-pass');
  74 |   state=await read();expect((await request.post('/__sidequest/runtime/clearSession',{data:['parent_019',state.revision],headers:origin})).ok()).toBe(true);
  75 | });
  76 | 
  77 | test('explicit read-only fixture shows distinct notifications and one badge per primary figure',async({page,request})=>{
  78 |   test.setTimeout(120_000);test.skip(process.env.SIDEQUEST_TEST_INSPECTION!=='1','Uses actual record identities in an explicitly labeled read-only fixture.');
> 79 |   const actual=await (await request.post('/__sidequest/runtime/snapshot',{data:[],headers:origin})).json();const jobs=actual.jobs.filter((j:{execution_profile:string;run_ids:string[]})=>j.execution_profile==='local_git_inspection'&&j.run_ids?.length).slice(0,2);expect(jobs).toHaveLength(2);
     |                                                                                                                                                                                                                                                                                    ^ Error: expect(received).toHaveLength(expected)
  80 |   const owners=[];for(const [i,job] of jobs.entries()){const run=(await (await request.post('/__sidequest/runtime/runInfo',{data:[job.run_ids.at(-1)],headers:origin})).json()).run;owners.push({station_id:i===0?'parent_019':'parent_020',job_id:job.id,project_id:job.project_id,run_id:run.id,worker_id:run.worker_id,assigned_at:new Date().toISOString()});}
  81 |   owners[1].worker_id='fixture-attention-worker';
  82 |   const fixture={...actual,mode:'fixture',jobs:jobs.map((job:any,i:number)=>({...job,state:i===0?'completed':'failed',title:`Test fixture · ${i===0?'Completed task':'Attention task'}`,blocked_reason:i===0?null:'Test fixture failure, no execution performed',tasks:job.tasks.map((task:any)=>({...task,state:i===0?'completed':'failed',worker_id:i===0?task.worker_id:'fixture-attention-worker'})),checks:job.checks.map((check:any)=>({...check,state:i===0?'pass':'fail'}))})),office_sessions:owners};
  83 |   const mutations:string[]=[];page.on('request',r=>{if(/__sidequest\/runtime\/(submitCoding|runCoding|enableCoding|assignSession|clearSession)$/.test(r.url()))mutations.push(r.url());});
  84 |   await page.route('**/__sidequest/runtime/snapshot',route=>route.fulfill({json:fixture}));await page.goto('/');await expect(page.locator('.app-footer')).toHaveAttribute('data-actor-status','ready',{timeout:60000});await expect(page.locator('.app-footer')).toContainText('Test fixture');
  85 |   const canvas=page.locator('.office-canvas canvas');await expect.poll(async()=>JSON.parse(await canvas.getAttribute('data-agent-badges')??'[]').length).toBe(2);
  86 |   const badges=JSON.parse((await canvas.getAttribute('data-agent-badges'))!);expect(badges).toEqual(expect.arrayContaining([{sceneId:'worker_parent_019',stationId:'parent_019',kind:'completed',jobId:jobs[0].id},{sceneId:'worker_parent_020',stationId:'parent_020',kind:'attention',jobId:jobs[1].id}]));expect(badges.some((b:{sceneId:string})=>b.sceneId==='child_019_01')).toBe(false);
  87 |   await page.getByRole('button',{name:/^Notifications/}).click();const tray=page.getByRole('region',{name:'Notifications',exact:true});await expect(tray.locator('[data-notification-kind=completed]')).toHaveCount(1);await expect(tray.locator('[data-notification-kind=attention]')).toHaveCount(1);await expect(tray).toContainText('Test fixture');
  88 |   await page.screenshot({path:path.join(evidence,'notifications-badges-fixture.png')});const axe=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze();expect(axe.violations.map(v=>({id:v.id,impact:v.impact}))).toEqual([]);
  89 |   await tray.getByRole('button',{name:/Completed task/}).click();await expect(page.locator('main')).toHaveAttribute('data-station','parent_019');await expect(page.getByRole('region',{name:'Session execution trace'})).toHaveAttribute('data-session-run',owners[0].run_id);expect(mutations).toEqual([]);
  90 |   await writeFile(path.join(evidence,'notifications-browser.json'),JSON.stringify({scope:'Explicit read-only fixture of completion/attention; not real successful worker dispatch',fixture:true,badges,duplicateChildBadge:false,mutations,axe:axe.violations.map(v=>v.id)},null,2));
  91 | });
  92 | 
```