import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import { createRequire } from 'node:module';
import test from 'node:test';

const require = createRequire(import.meta.url);
const source = readFileSync(new URL('../electron/main.cjs', import.meta.url), 'utf8');

async function start({built = true, loadError = null} = {}) {
  const exits = [], messages = [], loads = [];
  let completion;
  const electron = {
    app: {isPackaged:false, on(){}, quit(){exits.push(0);}, exit(code){exits.push(code);},
      whenReady:()=>({then:callback=>({catch:handler=>{completion=Promise.resolve().then(callback).catch(handler);}})})},
    dialog: {showErrorBox:(_title,message)=>messages.push(message)},
    protocol: {registerSchemesAsPrivileged(){},handle(){}},
    ipcMain: {removeHandler(){},handle(){}},
    session: {defaultSession:{setPermissionRequestHandler(){},setPermissionCheckHandler(){},on(){}}},
    BrowserWindow: class {
      constructor(){this.webContents={setWindowOpenHandler(){},on(){}};}
      once(){} on(){}
      async loadURL(url){loads.push(url);if(loadError)throw loadError;}
    },
  };
  vm.runInNewContext(source, {__dirname:'/app/electron', process:{env:{},platform:'linux'}, console:{error:m=>messages.push(m)},
    require:name=>name==='electron'?electron:name==='node:fs'?{existsSync:()=>built}:name==='node:path'?path:
      name==='./git-reader.cjs'?{createGitReader(){}}:name==='./runtime-client.cjs'?{createRuntimeClient(){}}:
      name==='./provider-discovery.cjs'?{discoverProviders(){}}:name==='./static-server.cjs'?{createStaticAssetHandler(){}}:require('../electron/security.cjs'),
  });
  await completion;
  return {exits,messages,loads};
}

test('missing renderer build exits nonzero with setup instructions instead of opening a broken window', async()=>{
  const result=await start({built:false});
  assert.deepEqual(result.exits,[1]);
  assert.equal(result.loads.length,0);
  assert.match(result.messages.join('\n'),/sidequest\.py setup/);
});

test('native window startup rejection is visible, nonzero, and does not disclose raw errors', async()=>{
  const result=await start({loadError:new Error('secret-token /private/local/repo')});
  assert.deepEqual(result.exits,[1]);
  assert.match(result.messages.join('\n'),/doctor/);
  assert.doesNotMatch(result.messages.join('\n'),/secret-token|private\/local/);
});

test('built production renderer still loads through the restricted app protocol', async()=>{
  const result=await start();
  assert.deepEqual(result.exits,[]);
  assert.deepEqual(result.loads,['app://sidequest/index.html']);
});
