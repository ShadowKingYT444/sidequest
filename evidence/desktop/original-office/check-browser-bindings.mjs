import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import {readFile,writeFile} from 'node:fs/promises';
import path from 'node:path';
const evidence=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(evidence,'../../..');
const require=createRequire(path.join(root,'desktop/package.json'));
const {chromium,expect}=require('@playwright/test');
const {PerspectiveCamera,Vector3,Matrix4,Quaternion,Euler}=require('three');
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--enable-unsafe-swiftshader']});
const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[];
page.on('pageerror',e=>errors.push({message:e.message,stack:e.stack}));
await page.emulateMedia({reducedMotion:'reduce'});
await page.goto('http://127.0.0.1:5173/');
await expect(page.locator('.office-canvas canvas')).toBeVisible({timeout:120000});
await page.waitForLoadState('networkidle',{timeout:120000});
await expect(page.locator('.app-footer')).toHaveAttribute('data-actor-status','ready',{timeout:120000});
const bindings=JSON.parse(await readFile(path.join(root,'desktop/public/office/bindings.json'),'utf8'));
const canvas=await page.locator('.office-canvas canvas').boundingBox();
const camera=new PerspectiveCamera(40,canvas.width/canvas.height,.05,1000);
camera.position.set(11.5,8.5,12);camera.lookAt(new Vector3(1,-.3,-3.8));camera.updateMatrixWorld();
const clickPoint=async point=>{const p=point.clone().project(camera);await page.mouse.click(canvas.x+(p.x+1)*canvas.width/2,canvas.y+(1-p.y)*canvas.height/2);};
let physicalMonitor=null;
for(const id of ['parent_017','parent_018','parent_005','parent_006','parent_013','parent_014','parent_020']){
  const monitor=bindings.stations.find(station=>station.id===id);
  for(const offset of [[.3,.1],[-.3,.1],[.3,-.3]]){
    const point=new Vector3(monitor.screenSize[0]*offset[0],monitor.screenSize[1]*offset[1],.004).applyEuler(new Euler(...monitor.rotation)).add(new Vector3(...monitor.anchor));
    await clickPoint(point);await page.waitForTimeout(500);
    if(await page.locator('.app-shell').getAttribute('data-station')===id&&await page.locator('.app-shell').getAttribute('data-mode')==='desk'){
      await expect(page.getByTestId('diff-editor')).toHaveCount(1,{timeout:30000});physicalMonitor={stationId:id,screenOffset:offset};break;
    }
    await page.keyboard.press('Escape');await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  }
  if(physicalMonitor)break;
}
expect(physicalMonitor).not.toBeNull();
await page.keyboard.press('Escape');await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
const actors=JSON.parse(await readFile(path.join(root,'desktop/public/office/actors.json'),'utf8'));
const actor=actors.stagedReferenceInstances.find(instance=>instance.sceneId==='worker_parent_019');
const m=actor.worldMatrixGltfRows;
await clickPoint(new Vector3(0,1.1,0).applyMatrix4(new Matrix4().set(...m.flat())));
await expect(page.getByRole('dialog',{name:'Agent session'})).toContainText('No live session attached',{timeout:30000});
await page.screenshot({path:path.join(evidence,'original-actor-context-card.png')});
await page.keyboard.press('Escape');await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
// Reuse the verified authored GLB transforms, including original PickBounds.
const bytes=await readFile(path.join(root,'desktop/public/office/office.glb'));
const document=JSON.parse(bytes.subarray(20,20+bytes.readUInt32LE(12)).toString('utf8'));
const parents=new Map();document.nodes.forEach((node,index)=>node.children?.forEach(child=>parents.set(child,index)));
const worlds=new Map();
const world=index=>{if(worlds.has(index))return worlds.get(index);const node=document.nodes[index];const local=node.matrix?new Matrix4().fromArray(node.matrix):new Matrix4().compose(new Vector3(...(node.translation??[0,0,0])),new Quaternion(...(node.rotation??[0,0,0,1])),new Vector3(...(node.scale??[1,1,1])));const result=parents.has(index)?world(parents.get(index)).clone().multiply(local):local;worlds.set(index,result);return result;};
const pickIndex=document.nodes.findIndex(node=>node.name==='Desk_parent_019__PickBounds.001');
let workstationClicked=false;
for(const offset of [[-.8,0,.2],[.8,0,.2],[-.8,-.5,.5],[.8,-.5,.5]]){
  await clickPoint(new Vector3(...offset).applyMatrix4(world(pickIndex)));
  await page.waitForTimeout(500);
  if(await page.getByRole('dialog',{name:'New task'}).count()){workstationClicked=true;break;}
  await page.keyboard.press('Escape');await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
}
expect(workstationClicked).toBe(true);
const launcher=page.getByRole('dialog',{name:'New task'});
const physicalWorkstationId=await page.locator('.app-shell').getAttribute('data-launcher-station');
await expect(launcher.getByRole('combobox',{name:'Agent',exact:true})).toHaveValue('codex',{timeout:30000});
await expect(launcher.getByRole('button',{name:'Submit task',exact:true})).toBeDisabled();
await page.screenshot({path:path.join(evidence,'original-workstation-context-card.png')});
await page.keyboard.press('Escape');await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
const samples=[];
for(const label of ['Computer 01','Computer 03','Computer 19','Computer 24']){
  await page.getByRole('combobox',{name:'Office navigation'}).selectOption('parent_'+label.slice(-2).padStart(3,'0'));
  await expect(page.getByTestId('diff-editor')).toHaveCount(1,{timeout:30000});
  const element=page.locator('.projected-work');
  await expect(element).toBeVisible();
  const box=await element.boundingBox();
  expect(box.width).toBeGreaterThan(400);expect(box.height).toBeGreaterThan(200);
  samples.push({label,projectedMonitorBox:box});
  await page.keyboard.press('Escape');await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  await expect(page.getByTestId('diff-editor')).toHaveCount(0);
}
const point=new Vector3(...bindings.board.anchor).project(camera);
await page.mouse.click(canvas.x+(point.x+1)*canvas.width/2,canvas.y+(1-point.y)*canvas.height/2);
await expect(page.getByRole('region',{name:'Tasks board detail'})).toBeVisible({timeout:15000});
await page.screenshot({path:path.join(evidence,'original-board-task-detail.png')});
const result={stations:samples,physicalMonitorClick:physicalMonitor,physicalActorClick:true,physicalWorkstationClick:{clicked:workstationClicked,stationId:physicalWorkstationId},boardHitOpenedTaskDetail:true,errors,cleanConsolePassed:errors.length===0};
await writeFile(path.join(evidence,'browser-binding-validation.json'),JSON.stringify(result,null,2)+'\n');
await browser.close();
console.log(JSON.stringify(result));
