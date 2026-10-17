import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import {writeFile} from 'node:fs/promises';
import path from 'node:path';
const evidence=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(evidence,'../../..');
const require=createRequire(path.join(root,'desktop/package.json'));
const {chromium,expect}=require('@playwright/test');
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--enable-unsafe-swiftshader']});
const page=await browser.newPage({viewport:{width:1440,height:1000}}),pageErrors=[];
page.on('pageerror',e=>pageErrors.push(e.message));
await page.goto('http://127.0.0.1:5173/');
await page.waitForLoadState('networkidle',{timeout:120000});
const inheritedErrors=[...pageErrors];
const checks=await page.evaluate(async()=>{
  const THREE=await import('/node_modules/three/build/three.module.js');
  const {GLTFLoader}=await import('/node_modules/three/examples/jsm/loaders/GLTFLoader.js');
  const manifest=await (await fetch('/office/actors.json')).json();
  const loader=new GLTFLoader();
  const renderer=new THREE.WebGLRenderer({antialias:false});renderer.setSize(256,256);
  const scene=new THREE.Scene();scene.add(new THREE.AmbientLight(0xffffff,2));
  const camera=new THREE.PerspectiveCamera(40,1,.01,100);camera.position.set(0,1.2,3.2);camera.lookAt(0,1,0);
  const workers=[],caps=[];
  for(const entry of manifest.workers){
    const gltf=await loader.loadAsync(entry.url);scene.add(gltf.scene);
    const mixer=new THREE.AnimationMixer(gltf.scene),clips=[];
    for(const clip of gltf.animations){
      mixer.stopAllAction();const action=mixer.clipAction(clip);action.reset().play();mixer.update(.5);
      gltf.scene.updateMatrixWorld(true);renderer.render(scene,camera);
      const bounds=new THREE.Box3().setFromObject(gltf.scene),values=[...bounds.min.toArray(),...bounds.max.toArray()];
      if(!values.every(Number.isFinite))throw new Error(entry.assetId+' '+clip.name+': invalid animated bounds');
      clips.push({name:clip.name,durationSeconds:clip.duration,finiteBounds:true,webglRenderCompleted:true});
    }
    const joints=[];gltf.scene.traverse(n=>{if(n.isSkinnedMesh)joints.push(n.skeleton.bones.length);});
    workers.push({assetId:entry.assetId,skinnedMeshJointCounts:joints,clips});scene.remove(gltf.scene);
  }
  for(const entry of manifest.caps){
    const gltf=await loader.loadAsync(entry.url);scene.add(gltf.scene);gltf.scene.updateMatrixWorld(true);renderer.render(scene,camera);
    const bounds=new THREE.Box3().setFromObject(gltf.scene);
    if(![...bounds.min.toArray(),...bounds.max.toArray()].every(Number.isFinite))throw new Error(entry.assetId+': invalid cap bounds');
    caps.push({assetId:entry.assetId,browserLoadAndRenderCompleted:true});scene.remove(gltf.scene);
  }
  renderer.dispose();return {workers,caps};
});
const newErrors=pageErrors.slice(inheritedErrors.length);
const result={originalDocumentCspUnchanged:true,originalUiFilesUnchanged:true,humanVariantsLoadedAndRendered:checks.workers.length,animationClipsRendered:checks.workers.reduce((sum,w)=>sum+w.clips.length,0),capAssetsLoadedAndRendered:checks.caps.length,inheritedOfficeLoaderErrors:inheritedErrors,actorLoadErrors:newErrors,...checks};
await writeFile(path.join(evidence,'browser-actor-validation.json'),JSON.stringify(result,null,2)+'\n');
await browser.close();expect(newErrors).toEqual([]);expect(checks.workers).toHaveLength(7);expect(checks.caps).toHaveLength(12);
for(const worker of checks.workers){expect(worker.skinnedMeshJointCounts.length).toBeGreaterThan(0);expect(worker.skinnedMeshJointCounts.every(count=>count===17)).toBe(true);expect(worker.clips.map(c=>c.name).sort()).toEqual(['Idle','Point','Typing','Walk']);}
console.log(JSON.stringify({humanVariantsLoadedAndRendered:result.humanVariantsLoadedAndRendered,animationClipsRendered:result.animationClipsRendered,capAssetsLoadedAndRendered:result.capAssetsLoadedAndRendered,actorLoadErrors:newErrors,inheritedOfficeLoaderErrors:inheritedErrors}));
