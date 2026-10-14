import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import path from 'node:path';
import assert from 'node:assert/strict';
const evidence=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(evidence,'../../..');
const office=path.join(root,'desktop/public/office');
const require=createRequire(path.join(root,'desktop/package.json'));
const {Matrix4,Quaternion,Vector3}=require('three');
const {parseOfficeBindings,validateOfficeResourceUrl}=await import(pathToFileURL(path.join(root,'desktop/src/office-bindings.ts')).href);
const bindings=parseOfficeBindings(JSON.parse(await readFile(path.join(office,'bindings.json'),'utf8')));
assert.equal(bindings.stations.length,24);
const provenance=JSON.parse(await readFile(path.join(office,'provenance.json'),'utf8'));
const hash=b=>createHash('sha256').update(b).digest('hex');
const raw=await readFile(path.join(office,'office.glb'));
assert.equal(hash(raw),provenance.installed_glb_sha256);
const jsonSize=raw.readUInt32LE(12);
const gltf=JSON.parse(raw.subarray(20,20+jsonSize).toString('utf8'));
const binary=raw.subarray(28+jsonSize);
assert.equal(gltf.extensionsRequired,undefined);
const world=new Map();
function visit(index,parent){
  const n=gltf.nodes[index],local=n.matrix?new Matrix4().fromArray(n.matrix):new Matrix4().compose(new Vector3(...(n.translation??[0,0,0])),new Quaternion(...(n.rotation??[0,0,0,1])),new Vector3(...(n.scale??[1,1,1])));
  const matrix=parent.clone().multiply(local);world.set(index,matrix);
  for(const child of n.children??[])visit(child,matrix);
}
for(const index of gltf.scenes[gltf.scene??0].nodes)visit(index,new Matrix4());
const material=gltf.materials.findIndex(m=>m.name==='Display dark glass');assert.ok(material>=0);
const measured=JSON.parse(await readFile(path.join(evidence,'native-measurements.json'),'utf8'));
const checks=[];
for(const station of bindings.stations){
  const record=measured.meshes.find(r=>r.parent==='Desk_'+station.id&&r.name.startsWith('Left display screen'));
  const nodeIndex=gltf.nodes.findIndex(n=>n.mesh!==undefined&&n.extras?.scene_owner_id===station.id);
  assert.ok(nodeIndex>=0);const mesh=gltf.meshes[gltf.nodes[nodeIndex].mesh],points=[];
  for(const primitive of mesh.primitives.filter(p=>p.material===material)){
    const accessor=gltf.accessors[primitive.attributes.POSITION],view=gltf.bufferViews[accessor.bufferView];
    assert.equal(accessor.componentType,5126);assert.equal(accessor.type,'VEC3');
    const offset=(view.byteOffset??0)+(accessor.byteOffset??0),stride=view.byteStride??12;
    for(let i=0;i<accessor.count;i++)points.push(new Vector3(binary.readFloatLE(offset+i*stride),binary.readFloatLE(offset+i*stride+4),binary.readFloatLE(offset+i*stride+8)).applyMatrix4(world.get(nodeIndex)));
  }
  assert.ok(points.length>0);
  const maximumError=Math.max(...record.vertices_world_blender.map(v=>{const point=new Vector3(v[0],v[2],-v[1]);return Math.min(...points.map(p=>p.distanceTo(point)));}));
  assert.ok(maximumError<0.0001,`${station.id}: source surface differs by ${maximumError} metres`);
  checks.push({stationId:station.id,matchedOriginalScreenVertexCount:record.vertices_world_blender.length,maximumNativeToRuntimeErrorMetres:maximumError});
}
for(const resource of [...provenance.installed_local_resources,...provenance.additional_original_resources]){
  validateOfficeResourceUrl(resource.path,'http://127.0.0.1:5173/');
  assert.equal(hash(await readFile(path.join(office,resource.path))),resource.sha256);
}
for(const image of gltf.images)validateOfficeResourceUrl(image.uri,'http://127.0.0.1:5173/');
const result={bindingContractPassed:true,stationCount:24,allMonitorSurfacesMatchedOriginalRuntimeGeometry:true,surfaceToleranceMetres:0.0001,maximumErrorMetres:Math.max(...checks.map(c=>c.maximumNativeToRuntimeErrorMetres)),allRuntimeAndActorResourceHashesPassed:true,allResourcesLocal:true,meshCompressionRequired:false,checks};
await writeFile(path.join(evidence,'asset-validation.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({...result,checks:checks.length}));
