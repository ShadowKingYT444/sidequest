import { chromium } from '@playwright/test';
import { createRequire } from 'node:module';
import { spawn } from 'node:child_process';
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const require = createRequire(import.meta.url);
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const evidence = path.resolve(root, '../evidence/desktop');
await mkdir(evidence, { recursive: true });
let child, browser;
let output = '';
const startedAt = new Date().toISOString();
try {
  const executable = require('electron');
  // Launch the native executable directly. Playwright's Electron convenience
  // launcher disables the OS sandbox and cannot verify this production boundary.
  const args = ['.', '--remote-debugging-port=9223'];
  child = spawn(executable, args, {cwd:root, shell:false, detached:true, stdio:['ignore','pipe','pipe'],env:{...process.env,SIDEQUEST_REPO:process.env.SIDEQUEST_REPO ?? path.resolve(root,'..'),SIDEQUEST_BASE:process.env.SIDEQUEST_BASE ?? 'HEAD~1'}});
  await new Promise((resolve,reject)=>{
    const timer=setTimeout(()=>reject(new Error('Native Electron startup timed out. '+output)),15_000);
    const read=data=>{output=(output+data.toString()).slice(-8000);if(output.includes('DevTools listening')){clearTimeout(timer);resolve();}};
    child.stdout.on('data',read);child.stderr.on('data',read);
    child.on('error',error=>{clearTimeout(timer);reject(error)});
    child.on('exit',(code,signal)=>{clearTimeout(timer);reject(new Error(`Native Electron exited (${code ?? signal}). ${output}`));});
  });
  browser=await chromium.connectOverCDP('http://127.0.0.1:9223');
  const context=browser.contexts()[0];
  const page=context.pages()[0] ?? await context.waitForEvent('page');
  await page.waitForLoadState('domcontentloaded');
  const boundary=await page.evaluate(async()=>({bridgeKeys:Object.keys(window.sidequest ?? {}).sort(),nodeAccess:typeof window.require,snapshot:await window.sidequest?.snapshot()}));
  if(boundary.nodeAccess!=='undefined'||boundary.bridgeKeys.join(',')!=='diff,snapshot'||boundary.snapshot?.mode!=='local-git')throw new Error('Desktop boundary smoke check failed.');
  await page.screenshot({path:path.join(evidence,'electron-window.png')});
  await writeFile(path.join(evidence,'electron-smoke.json'),JSON.stringify({status:'passed',startedAt,bridgeKeys:boundary.bridgeKeys,nodeAccess:false,mode:boundary.snapshot.mode,args},null,2)+'\n');
  console.log('Native Electron window and real Git IPC passed.');
}catch(error){
  const reason=error instanceof Error?error.message:String(error);
  const status=/sandbox|display|X server|install|ENOENT/i.test(reason)?'blocked':'failed';
  await writeFile(path.join(evidence,'electron-smoke.json'),JSON.stringify({status,startedAt,reason:reason.slice(0,4000),sandboxDisabled:false},null,2)+'\n');
  console.error(`Native Electron smoke ${status}: ${reason.slice(0,1000)}`);process.exitCode=2;
}finally{await browser?.close();if(child?.pid){try{process.kill(-child.pid,'SIGTERM')}catch{}}}
