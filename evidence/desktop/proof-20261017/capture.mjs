import {chromium} from '/workspace/sidequest/desktop/node_modules/playwright-core/index.mjs';
import {expect} from '/workspace/sidequest/desktop/node_modules/@playwright/test/index.mjs';
import {PerspectiveCamera,Vector3,Euler} from '/workspace/sidequest/desktop/node_modules/three/build/three.module.js';
import fs from 'node:fs/promises';
import path from 'node:path';

const out=path.dirname(new URL(import.meta.url).pathname);
const started=Date.now(), steps=[], errors=[], methods=[], forbidden=[];
const save=async(name,value)=>fs.writeFile(path.join(out,name),JSON.stringify(value,null,2)+'\n');
const mark=async(name,screenshot)=>{
  const row={name,elapsed_seconds:Number(((Date.now()-started)/1000).toFixed(3)),screenshot};
  steps.push(row);console.log(JSON.stringify(row));await save('steps.json',steps);
  if(screenshot)await page.screenshot({path:path.join(out,screenshot)});
  await page.waitForTimeout(1200);
};
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--enable-unsafe-swiftshader']});
const context=await browser.newContext({viewport:{width:1440,height:900},recordVideo:{dir:path.join(out,'raw'),size:{width:1440,height:900},fps:12}});
const page=await context.newPage();page.setDefaultTimeout(30000);
const video=page.video();let result={status:'incomplete',scope:'Real browser UI and local Git inspection; software GPU. No native Electron or live coding/provider proof.'};
page.on('pageerror',error=>errors.push(error.message));
page.on('request',request=>{
  if(request.url().includes('/__sidequest/runtime/')){
    const method=request.url().split('/').at(-1);methods.push(method);
    if(['submitCoding','runCoding','enableCoding','sessionMessage','stageAttachment'].includes(method))forbidden.push(method);
  }
});
try{
  await page.goto('http://127.0.0.1:5173/');
  await expect(page.locator('.app-footer')).toHaveAttribute('data-actor-status','ready',{timeout:60000});
  const snapshot=await (await context.request.get('http://127.0.0.1:5173/__sidequest/snapshot')).json();
  expect(snapshot.mode).toBe('local-git');
  const canvas=page.locator('.office-canvas canvas');
  const graphics=await canvas.evaluate(node=>{
    const gl=node.getContext('webgl2'),ext=gl?.getExtension('WEBGL_debug_renderer_info');
    return {renderer:ext?gl.getParameter(ext.UNMASKED_RENDERER_WEBGL):null,actors:document.querySelector('.app-footer')?.dataset.actorCount,footer:document.querySelector('.app-footer')?.textContent};
  });
  await mark('Original office fully loaded','01-office.png');
  const box=await canvas.boundingBox();
  const office=await canvas.evaluate(node=>({position:JSON.parse(node.dataset.cameraPosition),target:JSON.parse(node.dataset.cameraTarget)}));
  const bindings=await (await context.request.get('http://127.0.0.1:5173/office/bindings.json')).json();
  const station=bindings.stations.find(row=>row.id==='parent_019');
  const camera=new PerspectiveCamera(35,box.width/box.height,.05,1000);
  camera.position.fromArray(office.position);camera.lookAt(new Vector3().fromArray(office.target));camera.updateMatrixWorld();
  const point=new Vector3(0,station.screenSize[1]*.3,.012).applyEuler(new Euler(...station.rotation)).add(new Vector3().fromArray(station.anchor)).project(camera);
  const physicalClick={x:box.x+(point.x+1)*box.width/2,y:box.y+(1-point.y)*box.height/2};
  await page.mouse.click(physicalClick.x,physicalClick.y);
  await expect(page.locator('main')).toHaveAttribute('data-mode','desk');
  await expect(page.locator('main')).toHaveAttribute('data-station','parent_019');
  const prompt=page.getByRole('textbox',{name:'Message this session'}),composer=page.getByRole('form',{name:'Local prompt composer'});
  await expect(prompt).toBeVisible();
  await prompt.fill('Review the local changes and check the saved results. Unsent draft; no provider is connected.');
  await composer.getByLabel('Select local files').setInputFiles([{name:'review-notes.txt',mimeType:'text/plain',buffer:Buffer.from('Please review the local Git changes. This attachment stays on this device.')},{name:'office-screenshot.png',mimeType:'image/png',buffer:await fs.readFile(path.join(out,'01-office.png'))}]);
  await expect(composer.getByRole('img',{name:'Preview of office-screenshot.png'})).toBeVisible();
  await expect(composer.getByRole('button',{name:'Remove review-notes.txt'})).toBeVisible();
  await expect(composer.getByRole('button',{name:'Send message'})).toBeDisabled();
  await mark('Physical monitor click; local text, file and image draft; send disabled','02-monitor-draft.png');
  await page.getByRole('button',{name:'Files',exact:true}).click();
  const source=snapshot.files.find(row=>row.path==='README.md');expect(source).toBeTruthy();
  await page.locator(`.file-list button[data-file-id="${source.id}"]`).click();
  const editor=page.getByTestId('diff-editor');await expect(editor.locator('.view-lines').last()).toBeVisible();
  await page.getByRole('button',{name:'Expand',exact:true}).click();
  await expect(page.getByRole('dialog',{name:'Computer work viewer'})).toBeVisible();
  await mark('Actual committed Git diff expanded in read-only viewer','03-git-diff.png');
  await page.keyboard.press('Escape');
  await page.getByRole('button',{name:'Jobs',exact:true}).click();
  const board=page.getByRole('region',{name:'Local jobs board'});await expect(board).toBeVisible();
  await board.getByRole('button',{name:'Register configured repository'}).click();
  await expect.poll(()=>board.locator('#job-project').inputValue()).not.toBe('');
  const title='Proof: inspect local Git — zero model calls';
  await board.getByLabel('Inspection title').fill(title);
  await board.getByRole('button',{name:'Submit inspection',exact:true}).click();
  await board.getByRole('button',{name:new RegExp('Proof: inspect local Git')}).click();
  await expect(board.getByRole('button',{name:'Run inspection',exact:true})).toBeEnabled();
  await mark('Fresh trusted repository registered; zero-budget inspection queued','04-inspection-queued.png');
  await board.getByRole('button',{name:'Run inspection',exact:true}).click();
  await expect(board.locator('.job-checks')).toContainText('pass',{timeout:90000});
  await expect(board).toContainText('Inspection results ready.');
  await board.locator('.artifact-files button[title="README.md"]').click();
  await expect(board.locator('.artifact-text')).toContainText('This file is real committed Git content');
  await mark('Real local inspection passed; immutable README artifact displayed','05-inspection-result.png');
  await board.locator('#job-artifact').selectOption({label:await board.locator('#job-artifact option').filter({hasText:'test_report'}).first().textContent()});
  await expect(board.locator('.artifact-text')).toContainText('candidate.frozen_identity');
  const report=JSON.parse(await board.locator('.artifact-text').textContent());expect(report.inference_calls).toBe(0);
  await mark('Frozen inspection check report: inference_calls = 0','06-check-report.png');
  await board.locator('.job-activity > summary').click();
  const activity=board.getByRole('region',{name:'Run activity'});
  await expect(activity).toContainText('No model call');await expect(activity.locator('.run-activity-state')).toHaveText('completed');
  await mark('Completed recorded inspection activity; no model call','07-run-activity.png');
  await board.locator('.job-activity > summary').click();
  await board.locator('.coding-readiness summary').click();
  await expect(board.locator('.coding-readiness')).toContainText('Coding tasks remain blocked.');
  await mark('Honest coding-unavailable explanation','08-coding-unavailable.png');
  await page.keyboard.press('Escape');
  await page.getByRole('button',{name:'Settings',exact:true}).click();
  const settings=page.getByRole('dialog',{name:'Provider settings dialog'});
  await expect(settings.getByText('Authentication',{exact:true})).toBeVisible();
  await expect(settings.getByText('Unknown',{exact:true})).toHaveCount(2);
  await mark('Actual provider discovery: executable detection, authentication unknown','09-provider-settings.png');
  await settings.getByRole('navigation',{name:'Settings view'}).getByRole('button',{name:'Usage',exact:true}).click();
  await expect(settings.getByText('No usage data reported',{exact:true})).toBeVisible();
  await mark('Actual usage page: telemetry unavailable','10-usage-unavailable.png');
  const runtimeRead=async(method)=>{
    const response=await context.request.post(`http://127.0.0.1:5173/__sidequest/runtime/${method}`,{headers:{Origin:'http://127.0.0.1:5173'},data:[]});expect(response.ok()).toBe(true);return response.json();
  };
  const state=await runtimeRead('snapshot'),caps=await runtimeRead('capabilities'),job=state.jobs.find(row=>row.title===title);
  expect(job.spent_usd).toBe(0);expect(forbidden).toEqual([]);expect(errors).toEqual([]);
  result={...result,status:'passed',browser:browser.version(),graphics,physical_monitor_click:physicalClick,source:{base:snapshot.baseRevision,candidate:snapshot.candidateRevision},job,frozen_check_report:report,capabilities:caps,page_errors:errors,prohibited_provider_requests:forbidden,runtime_methods:methods,local_draft_sent:false,network_mocks:false};
}catch(error){
  result={...result,status:'failed',error:String(error),page_errors:errors,runtime_methods:methods};
  await page.screenshot({path:path.join(out,'capture-failure.png')}).catch(()=>{});
  console.error(error);process.exitCode=1;
}finally{
  result.duration_seconds=(Date.now()-started)/1000;result.steps=steps;
  await context.close();await video.saveAs(path.join(out,'walkthrough-raw.webm'));await browser.close();
  await save('browser-verification.json',result);
}
