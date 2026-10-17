import test from 'node:test';
import assert from 'node:assert/strict';
import { parseOfficeBindings, validateOfficeResourceUrl } from '../src/office-bindings.ts';
const station={id:'desk-a',label:'Repository',anchor:[0,0,0],rotation:[0,0,0],screenSize:[1,1],focus:{position:[1,1,1],target:[0,0,0]}};
const bindings={modelUrl:'/office/office.glb',overview:{position:[1,1,1],target:[0,0,0]},stations:[station]};
test('bindings preserve stable monitor IDs and reject duplicate or invalid geometry',()=>{
  assert.equal(parseOfficeBindings(bindings).stations[0].id,'desk-a');
  assert.throws(()=>parseOfficeBindings({...bindings,stations:[station,station]}),/duplicate/);
  assert.throws(()=>parseOfficeBindings({...bindings,stations:[{...station,anchor:[Infinity,0,0]}]}),/finite/);
  assert.throws(()=>parseOfficeBindings({...bindings,stations:[{...station,screenSize:[0,1]}]}),/greater/);
  assert.throws(()=>parseOfficeBindings({...bindings,modelUrl:'https://example.com/art.glb'}));
});
test('embedded image blobs work while model resource URLs stay local',()=>{
  const page='http://127.0.0.1:5173/';
  assert.equal(validateOfficeResourceUrl('/office/textures/desk.png',page),'http://127.0.0.1:5173/office/textures/desk.png');
  assert.equal(validateOfficeResourceUrl('blob:http://127.0.0.1:5173/image-id',page),'blob:http://127.0.0.1:5173/image-id');
  assert.equal(validateOfficeResourceUrl('data:image/png;base64,AA==',page),'data:image/png;base64,AA==');
  assert.equal(validateOfficeResourceUrl('/office/office.glb','app://sidequest/index.html'),'app://sidequest/office/office.glb');
  assert.equal(validateOfficeResourceUrl('blob:app://sidequest/image','app://sidequest/index.html'),'blob:app://sidequest/image');
  assert.throws(()=>validateOfficeResourceUrl('app://other/office/image.png','app://sidequest/index.html'));
  assert.throws(()=>validateOfficeResourceUrl('file:///office/image.png','app://sidequest/index.html'));
  assert.throws(()=>validateOfficeResourceUrl('blob:app://other/image','app://sidequest/index.html'));
  for(const url of ['https://example.com/office/file.png','blob:https://example.com/image','/office/%2e%2e/private.env','/outside/file.png','file:///etc/passwd','/office/a.png?token=secret'])assert.throws(()=>validateOfficeResourceUrl(url,page));
});
