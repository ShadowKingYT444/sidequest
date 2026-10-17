import assert from 'node:assert/strict';
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, symlinkSync, writeFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import os from 'node:os';
import path from 'node:path';
import vm from 'node:vm';
import test from 'node:test';

const require = createRequire(import.meta.url);
const security = require('../electron/security.cjs');
const { createStaticAssetHandler } = require('../electron/static-server.cjs');
const preloadSource = readFileSync(new URL('../electron/preload.cjs', import.meta.url), 'utf8');
const mainSource = readFileSync(new URL('../electron/main.cjs', import.meta.url), 'utf8');
const staticSource = readFileSync(new URL('../electron/static-server.cjs', import.meta.url), 'utf8');

test('preload exposes fixed read and validated local-runtime capabilities without shell or credentials', async () => {
  const calls = [];
  let exposed;
  const electron = {
    contextBridge: { exposeInMainWorld: (name, api) => { exposed = { name, api }; } },
    ipcRenderer: { invoke: (...args) => { calls.push(args); return Promise.resolve({ ok: true }); } },
  };
  vm.runInNewContext(preloadSource, {
    require: (name) => {
      assert.equal(name, 'electron');
      return electron;
    },
    Promise,
    Error,
    Object,
  });

  assert.equal(exposed.name, 'sidequest');
  assert.deepEqual(Object.keys(exposed.api), ['runtime', 'providers', 'snapshot', 'diff']);
  assert.equal(Object.isFrozen(exposed.api.runtime), true);
  assert.deepEqual(Object.keys(exposed.api.runtime), ['snapshot','capabilities','runInfo','runEvents','assignSession','clearSession','stageAttachment','sessionMessage','commandStatus','job','artifact','artifacts','files','text','diff','register','submitInspection','run','stop','refreshReadiness','enableCoding','submitCoding','runCoding']);
  assert.equal(Object.isFrozen(exposed.api), true);
  assert.deepEqual(await exposed.api.snapshot(), { ok: true });
  assert.deepEqual(calls, [['sidequest:snapshot']]);
  await exposed.api.diff('f_' + 'a'.repeat(32));
  assert.deepEqual(calls[1], ['sidequest:diff', 'f_' + 'a'.repeat(32)]);
  await assert.rejects(exposed.api.diff('../secret'), { code: 'INVALID_INPUT' });
  assert.equal(calls.length, 2, 'invalid identifiers never cross IPC');
  await exposed.api.runtime.run('job-1', 12);
  assert.equal(JSON.stringify(calls[2]), JSON.stringify(['sidequest:runtime', 'run', ['job-1', 12]]));
  await exposed.api.providers();assert.deepEqual(calls[3],['sidequest:providers']);
});

test('Electron security helpers trust only the app origin or configured loopback dev origin', () => {
  const devServer = security.normalizeDevServerUrl('http://127.0.0.1:5173');
  assert.equal(devServer.origin, 'http://127.0.0.1:5173');
  assert.equal(security.isTrustedRendererUrl('app://sidequest/index.html'), true);
  assert.equal(security.isTrustedRendererUrl('app://elsewhere/index.html'), false);
  assert.equal(security.isTrustedRendererUrl('file:///tmp/index.html'), false);
  assert.equal(security.isTrustedRendererUrl('http://127.0.0.1:5173/src/main.tsx', devServer.origin), true);
  assert.equal(security.isTrustedRendererUrl('http://127.0.0.1:5174/', devServer.origin), false);
  assert.equal(security.isTrustedRendererUrl('https://127.0.0.1:5173/', devServer.origin), false);
  assert.throws(() => security.normalizeDevServerUrl('https://example.com'));
  assert.throws(() => security.normalizeDevServerUrl('http://example.com:5173'));
  assert.throws(() => security.normalizeDevServerUrl('http://user@127.0.0.1:5173'));
});

test('IPC sender validation requires the current main frame and opaque file IDs', () => {
  const mainFrame = { url: 'app://sidequest/index.html' };
  const webContents = { mainFrame };
  const window = { webContents };
  assert.equal(security.isTrustedIpcSender({ sender: webContents, senderFrame: mainFrame }, window), true);
  assert.equal(security.isTrustedIpcSender({ sender: webContents, senderFrame: { url: mainFrame.url } }, window), false);
  assert.equal(security.isTrustedIpcSender({ sender: {}, senderFrame: mainFrame }, window), false);
  assert.equal(security.isTrustedIpcSender({ sender: webContents, senderFrame: { url: 'file:///tmp/evil' } }, window), false);
  assert.equal(security.isValidFileId('f_' + 'b'.repeat(32)), true);
  for (const invalid of ['../file', 'f_' + 'b'.repeat(31), 'f_' + 'b'.repeat(33), null, 7]) {
    assert.equal(security.isValidFileId(invalid), false);
  }
});

test('BrowserWindow and main process keep Node access disabled and deny navigation, windows, downloads, and capture', () => {
  const prefs = security.secureWebPreferences('/app/electron/preload.cjs');
  assert.equal(prefs.preload, '/app/electron/preload.cjs');
  assert.equal(prefs.sandbox, true);
  assert.equal(prefs.contextIsolation, true);
  assert.equal(prefs.nodeIntegration, false);
  assert.equal(prefs.webSecurity, true);
  assert.equal(prefs.allowRunningInsecureContent, false);
  assert.equal(prefs.webviewTag, false);

  assert.match(mainSource, /contents\.setWindowOpenHandler\(\(\) => \(\{ action: 'deny' \}\)\)/);
  assert.match(mainSource, /setPermissionRequestHandler\([^\n]+callback\(false\)/);
  assert.match(mainSource, /setPermissionCheckHandler\(\(\) => false\)/);
  assert.match(mainSource, /setDisplayMediaRequestHandler\([^\n]+callback\(\{\}\)/);
  assert.match(mainSource, /will-download/);
  assert.match(mainSource, /will-navigate/);
  assert.match(mainSource, /will-redirect/);
  assert.match(mainSource, /will-attach-webview/);
  assert.match(mainSource, /protocol\.handle\('app', serveAppRequest\)/);
  assert.match(staticSource, /path\.resolve\(root, 'public', relative\)/);
  assert.match(staticSource, /model\/gltf-binary/);
  assert.match(staticSource, /worker-src 'self' blob:/);
  assert.match(staticSource, /frame-src 'none'/);
  assert.match(mainSource, /SIDEQUEST_DEV_SERVER_URL/);
  assert.match(mainSource, /SIDEQUEST_REPO/);
  assert.match(mainSource, /SIDEQUEST_BASE/);
  assert.doesNotMatch(mainSource, /--no-sandbox/);
  assert.doesNotMatch(preloadSource, /ipcRenderer\.(?:send|on|once|sendSync)\s*\(/);
});

test('app protocol serves dist assets and root office URLs from copied public assets safely', async (t) => {
  const temp = mkdtempSync(path.join(os.tmpdir(), 'sidequest-app-protocol-'));
  const dist = path.join(temp, 'dist');
  const publicDir = path.join(dist, 'public');
  mkdirSync(publicDir, { recursive: true });
  writeFileSync(path.join(dist, 'index.html'), '<main>Sidequest</main>');
  writeFileSync(path.join(publicDir, 'room.glb'), Buffer.from([0, 1, 2, 3]));
  const outside = path.join(temp, 'outside.txt');
  writeFileSync(outside, 'private');
  symlinkSync(outside, path.join(publicDir, 'escape.txt'));
  t.after(() => rmSync(temp, { recursive: true, force: true }));
  const serve = createStaticAssetHandler(dist);

  const root = await serve({ method: 'GET', url: 'app://sidequest/' });
  assert.equal(root.status, 200);
  assert.equal(await root.text(), '<main>Sidequest</main>');

  const officeAsset = await serve({ method: 'GET', url: 'app://sidequest/room.glb' });
  assert.equal(officeAsset.status, 200);
  assert.equal(officeAsset.headers.get('content-type'), 'model/gltf-binary');
  assert.equal(new Uint8Array(await officeAsset.arrayBuffer()).length, 4);
  assert.match(officeAsset.headers.get('content-security-policy'), /worker-src 'self' blob:/);
  assert.match(officeAsset.headers.get('content-security-policy'), /frame-src 'none'/);

  for (const url of [
    'app://sidequest/a%2f..%2foutside.txt',
    'app://sidequest/%5c..%5coutside.txt',
    'app://other/index.html',
    'file:///etc/passwd',
  ]) {
    assert.equal((await serve({ method: 'GET', url })).status, 404, url);
  }
  assert.equal((await serve({ method: 'GET', url: 'app://sidequest/escape.txt' })).status, 404);
  assert.equal((await serve({ method: 'POST', url: 'app://sidequest/' })).status, 405);
  assert.equal(existsSync(path.join(dist, 'outside.txt')), false);
});


test('provider discovery uses fixed executable metadata and never infers authentication', async t => {
  const temporaryRoot=mkdtempSync(path.join(os.tmpdir(),'sidequest-provider-metadata-'));t.after(()=>rmSync(temporaryRoot,{recursive:true,force:true}));
  const binaryDirectory=path.join(temporaryRoot,'bin'),fixtureHome=path.join(temporaryRoot,'host');
  mkdirSync(binaryDirectory);mkdirSync(path.join(fixtureHome,'.local','bin'),{recursive:true});mkdirSync(path.join(fixtureHome,'.opencode','bin'),{recursive:true});
  writeFileSync(path.join(binaryDirectory,'agent'),'This executable fixture must never run.',{mode:0o755});
  writeFileSync(path.join(binaryDirectory,'antigravity'),'IDE launcher fixture',{mode:0o755});
  mkdirSync(path.join(binaryDirectory,'codex'));symlinkSync(path.join(temporaryRoot,'missing'),path.join(binaryDirectory,'claude'));
  writeFileSync(path.join(fixtureHome,'.local','bin','claude'),'metadata only',{mode:0o755});
  writeFileSync(path.join(fixtureHome,'.opencode','bin','opencode'),'metadata only',{mode:0o755});
  const inspected=[];const realFs=require('node:fs/promises');const module={exports:{}};
  const fakeEnvironment={PATH:['.',binaryDirectory,binaryDirectory,'/invalid\nentry'].join(path.delimiter),HOME:fixtureHome,CODEX_HOME:path.join(fixtureHome,'.codex')};
  vm.runInNewContext(readFileSync(new URL('../electron/provider-discovery.cjs',import.meta.url),'utf8'),{module,process:{platform:'linux',env:fakeEnvironment},require:name=>{
    if(name==='node:path')return path;if(name==='node:fs')return {constants:require('node:fs').constants};
    if(name==='node:fs/promises')return {access:async(file,mode)=>{inspected.push(file);return realFs.access(file,mode);},stat:realFs.stat};
    throw new Error('Discovery must not import process execution or credential-reading tools.');
  }});
  const result=JSON.parse(JSON.stringify(await module.exports.discoverProviders()));
  const find=id=>result.providers.find(provider=>provider.id===id);
  assert.equal(find('codex').installed,false,'an executable directory is not a CLI');
  assert.equal(find('cursor').binaryPath,path.join(binaryDirectory,'agent'));assert.equal(find('cursor').discoverySource,'path');
  assert.equal(find('claude').binaryPath,path.join(fixtureHome,'.local','bin','claude'));assert.equal(find('claude').discoverySource,'known-install');
  assert.equal(find('opencode').installed,true);assert.equal(find('antigravity').installed,false,'IDE launcher is not the coding CLI');
  assert.equal(result.providers.every(provider=>provider.authentication==='unknown'&&provider.reachability==='unknown'&&provider.version===null),true);
  assert.equal(inspected.every(file=>['codex','claude','cursor-agent','agent','grok','opencode','agy'].includes(path.basename(file))),true);
  const directories=Array.from({length:65},(_,index)=>path.join(temporaryRoot,'path-'+index));directories.forEach(directory=>mkdirSync(directory));
  writeFileSync(path.join(directories[64],'codex'),'out of bounded search',{mode:0o755});fakeEnvironment.PATH=directories.join(path.delimiter);
  assert.equal((await module.exports.discoverProviders()).providers.find(provider=>provider.id==='codex').installed,false,'PATH search is capped at 64 directories');
  const configuredExecutable=path.join(temporaryRoot,'configured-codex');writeFileSync(configuredExecutable,'metadata-only explicit host locator',{mode:0o755});fakeEnvironment.SIDEQUEST_CODEX_EXECUTABLE=configuredExecutable;
  const configured=(await module.exports.discoverProviders()).providers.find(provider=>provider.id==='codex');assert.equal(configured.binaryPath,configuredExecutable);assert.equal(configured.discoverySource,'host-setting');assert.equal(configured.authentication,'unknown');assert.equal(configured.reachability,'unknown');
});

test('protocol fixture: preload retains sanitized definite send rejection code across Electron IPC',async()=>{
 let api;vm.runInNewContext(preloadSource,{require:()=>({contextBridge:{exposeInMainWorld:(_name,value)=>{api=value;}},ipcRenderer:{invoke:async()=>({v:1,error:{code:'VERSION_CONFLICT',status:409,message:'Local runtime request failed.'}})}}),Promise,Error,Object});
 await assert.rejects(api.runtime.sessionMessage('run-1','12345678-1234-1234-1234-123456789012','Prompt','[]',2),{code:'VERSION_CONFLICT',status:409});
});
