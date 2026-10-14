import {test,expect,type Page} from '@playwright/test';
import {mkdir} from 'node:fs/promises';
import AxeBuilder from '@axe-core/playwright';

// Explicit protocol fake: real Chromium IndexedDB/File reload, real React composer,
// fake authenticated runtime receipts. No provider startup or model turn occurs.
const captures=`../evidence/desktop/transport/${process.env.SIDEQUEST_TRANSPORT_EVIDENCE_RUN??'captures'}`;
async function composerFixture(page:Page,{lostReply=false,usd=true,rejectedBeforeStart=false}={}){
 page.on('pageerror',error=>console.error('Composer fixture page error:',error.message));
 await page.addInitScript(({lostReply,usd,rejectedBeforeStart})=>{
  const caps={v:1,features:{coding:true,codex_session:true,session_messages:true,session_attachments:true},worker_model:{verified:true},codex:{host_enabled:true,state:'available',catalog_verified:true,usd_cost_enforced:usd}};
  const record=(kind:string,id:string)=>{const calls=JSON.parse(localStorage.getItem('fixture:calls')??'[]');calls.push({kind,id});localStorage.setItem('fixture:calls',JSON.stringify(calls));};
  (window as any).sidequest={runtime:{
   capabilities:async()=>caps,snapshot:async()=>({v:1,revision:7}),
   stageAttachment:async(run:string,key:string,name:string,mime:string,base64:string)=>{record('stage',key);return {v:1,attachment:{id:'attachment-'+key,run_id:run,name,media_type:mime,size_bytes:atob(base64).length,sha256:'a'.repeat(64)}};},
   sessionMessage:async(run:string,id:string)=>{record('send',id);const command={v:1,accepted:true,command_id:id,revision:8,result:{run_id:'follow-up-run'}};localStorage.setItem('fixture:receipt:'+id,JSON.stringify(command));if(lostReply)throw Error('Protocol fake: response lost after acceptance');return command;},
   commandStatus:async(id:string)=>{record('status',id);const receipt=localStorage.getItem('fixture:receipt:'+id);return {v:1,found:!!receipt,...(receipt?{command:JSON.parse(receipt),message:{id,state:rejectedBeforeStart?'rejected':'completed',run_id:rejectedBeforeStart?null:'follow-up-run'}}:{})};},
  }};
 },{lostReply,usd,rejectedBeforeStart});
 await page.route('**/transport-fixture',route=>route.fulfill({contentType:'text/html',body:`<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Protocol-fake session composer</title><meta name="viewport" content="width=device-width, initial-scale=1"></head><body style="margin:0;background:#111;color:#eee;font:14px system-ui"><p style="margin:16px">Protocol-fake session transport · no model calls</p><div id="fixture-root" style="max-width:720px;margin:16px;border:1px solid #333"></div><script type="module">
 import RefreshRuntime from '/@react-refresh';
 RefreshRuntime.injectIntoGlobalHook(window);window.$RefreshReg$=()=>{};window.$RefreshSig$=()=>type=>type;window.__vite_plugin_react_preamble_installed__=true;
 </script><script type="module">
 import '/src/style.css';
 import React from '/node_modules/.vite/deps/react.js';
 import ReactDOMClient from '/node_modules/.vite/deps/react-dom_client.js';
 const {createRoot}=ReactDOMClient;
 import SessionComposer from '/src/SessionComposer.tsx';
 import {SessionDraftStore} from '/src/session-drafts.ts';
 import {createDraftOperations} from '/src/local-drafts.ts';
 const store=new SessionDraftStore('fixture-conversation');window.fixtureStore=store;
 const job={id:'job-1',state:'verifying',execution_profile:'codex_session',spent_usd:0.01,budget_usd:0.03};
 const run={id:'run-1',state:'completed',ended_at:'2026-10-14T00:00:00Z',usage:{uncertain:false,cost_usd:0.01}};
 createRoot(document.getElementById('fixture-root')).render(React.createElement(SessionComposer,{store,operations:createDraftOperations(),job,run,known:true,active:true,onAccepted:()=>{window.fixtureAccepted=true;}}));
 </script></body></html>`}));
 await page.goto('/transport-fixture');await expect(page.getByRole('textbox',{name:'Message this session'})).toBeEditable();
}

test('protocol fake: real IndexedDB restores draft, File bytes, UUID, selection and a local image preview on reload',async({page})=>{
 await composerFixture(page);const input=page.getByRole('textbox',{name:'Message this session'});await input.fill('A thought worth retaining');
 const png=Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a1ioAAAAASUVORK5CYII=','base64');
 await page.getByLabel('Select local files').setInputFiles([{name:'notes.txt',mimeType:'text/plain',buffer:Buffer.from('Retained bytes')},{name:'pixel.png',mimeType:'image/png',buffer:png}]);
 await expect(page.getByRole('list',{name:'Local attachments'}).getByRole('listitem')).toHaveCount(2);await expect(page.getByAltText('Preview of pixel.png')).toBeVisible();
 await input.focus();await input.press('Control+Home');for(let i=0;i<3;i++)await input.press('ArrowRight');for(let i=0;i<5;i++)await input.press('Shift+ArrowRight');
 await expect.poll(()=>page.evaluate(()=>(window as any).fixtureStore.state.selection)).toEqual([3,8]);
 await page.evaluate(async()=>{await (window as any).fixtureStore.flush();});
 const before=await page.evaluate(()=>({ids:(window as any).fixtureStore.state.draft.attachments.map((a:any)=>a.id),url:(window as any).fixtureStore.state.draft.attachments[1].previewURL}));
 await page.reload();await expect(input).toHaveValue('A thought worth retaining');await expect(page.getByAltText('Preview of pixel.png')).toBeVisible();
 const restored=await page.evaluate(async()=>{const store=(window as any).fixtureStore;await store.ready;return {ids:store.state.draft.attachments.map((a:any)=>a.id),text:await store.state.draft.attachments[0].file.text(),url:store.state.draft.attachments[1].previewURL,selection:store.state.selection};});
 expect(restored.ids).toEqual(before.ids);expect(restored.text).toBe('Retained bytes');expect(restored.url).not.toBe(before.url);expect(restored.selection).toEqual([3,8]);expect(await input.evaluate((node:HTMLTextAreaElement)=>[node.selectionStart,node.selectionEnd])).toEqual([3,8]);
 await mkdir(captures,{recursive:true});await page.screenshot({path:captures+'/durable-composer.png'});
});

test('protocol fake: lost reply survives reload and reconciles exactly one send, keeping a subsequent draft',async({page})=>{
 await composerFixture(page,{lostReply:true});const input=page.getByRole('textbox',{name:'Message this session'});await input.fill('Follow up with the staged notes');
 await page.getByLabel('Select local files').setInputFiles({name:'notes.txt',mimeType:'text/plain',buffer:Buffer.from('Attached UTF-8 text')});
 await expect(page.getByRole('button',{name:'Send message'})).toBeEnabled();await page.getByRole('button',{name:'Send message'}).click();
 await expect(page.getByRole('button',{name:'Check send status'})).toBeEnabled();await expect(page.getByRole('button',{name:'Send message'})).toBeDisabled();
 await mkdir(captures,{recursive:true});await page.screenshot({path:captures+'/pending-composer.png'});
 await input.fill('My next thought');await page.evaluate(async()=>{await (window as any).fixtureStore.flush();});await page.reload();
 await expect(input).toHaveValue('My next thought');await expect(page.getByRole('button',{name:'Send message'})).toBeDisabled();
 await page.getByRole('button',{name:'Check send status'}).click();await expect(page.getByRole('button',{name:'Check send status'})).toHaveCount(0);await expect(input).toHaveValue('My next thought');await expect(page.getByRole('list',{name:'Local attachments'})).toHaveCount(0);
 const calls=await page.evaluate(()=>JSON.parse(localStorage.getItem('fixture:calls')??'[]'));expect(calls.map((call:any)=>call.kind)).toEqual(['stage','send','status']);expect(calls[1].id).toBe(calls[2].id);
 await page.setViewportSize({width:390,height:844});await mkdir(captures,{recursive:true});await page.screenshot({path:captures+'/reconciled-composer-mobile.png'});expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});

test('protocol fake: unknown spending authority keeps send disabled while durable local draft remains usable',async({page})=>{
 await composerFixture(page,{usd:false});await page.getByRole('textbox',{name:'Message this session'}).fill('No dispatch while authority is unknown');await expect(page.getByRole('button',{name:'Send message'})).toBeDisabled();
 await page.getByRole('textbox',{name:'Message this session'}).press('Control+Enter');expect(await page.evaluate(()=>localStorage.getItem('fixture:calls'))).toBeNull();
});

test('protocol fake: accepted command rejected before start retains file and next draft across reload until explicit review',async({page})=>{
 await composerFixture(page,{lostReply:true,rejectedBeforeStart:true});const input=page.getByRole('textbox',{name:'Message this session'});await input.fill('Original requested follow-up');
 await page.getByLabel('Select local files').setInputFiles({name:'notes.txt',mimeType:'text/plain',buffer:Buffer.from('Retain attachment')});await expect(page.getByRole('button',{name:'Send message'})).toBeEnabled();await page.getByRole('button',{name:'Send message'}).click();await expect(page.getByRole('button',{name:'Check send status'})).toBeEnabled();
 await input.fill('A concurrent next thought');await page.getByRole('button',{name:'Check send status'}).click();await expect(page.getByRole('button',{name:'Review retained draft'})).toBeVisible();await expect(page.getByRole('list',{name:'Local attachments'}).getByRole('listitem')).toHaveCount(1);await expect(input).toHaveValue('A concurrent next thought');await expect(page.getByRole('button',{name:'Send message'})).toBeDisabled();
 await page.evaluate(async()=>{await (window as any).fixtureStore.flush();});await page.reload();await expect(page.getByRole('button',{name:'Review retained draft'})).toBeVisible();await expect(page.getByText('Message did not start · review retained draft',{exact:true}).first()).toBeVisible();await expect(input).toHaveValue('A concurrent next thought');
 await mkdir(captures,{recursive:true});await page.screenshot({path:captures+'/rejected-before-start.png'});await page.getByRole('button',{name:'Review retained draft'}).click();await expect(page.getByRole('button',{name:'Review retained draft'})).toHaveCount(0);await expect(page.getByRole('button',{name:'Send message'})).toBeEnabled();await expect(page.getByRole('list',{name:'Local attachments'}).getByRole('listitem')).toHaveCount(1);await expect(input).toHaveValue('A concurrent next thought');
 const calls=await page.evaluate(()=>JSON.parse(localStorage.getItem('fixture:calls')??'[]'));expect(calls.map((call:any)=>call.kind)).toEqual(['stage','send','status']);expect(calls[1].id).toBe(calls[2].id);
});

test('protocol fake: successful 202 then rejected-before-start restores sent files without overwriting a newer draft',async({page})=>{
 await composerFixture(page,{rejectedBeforeStart:true});const input=page.getByRole('textbox',{name:'Message this session'});await input.fill('Successfully acknowledged original message');
 const png=Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a1ioAAAAASUVORK5CYII=','base64');
 await page.getByLabel('Select local files').setInputFiles([{name:'sent.txt',mimeType:'text/plain',buffer:Buffer.from('Original sent bytes')},{name:'sent.png',mimeType:'image/png',buffer:png}]);await expect(page.getByAltText('Preview of sent.png')).toBeVisible();await expect(page.getByRole('button',{name:'Send message'})).toBeEnabled();await page.getByRole('button',{name:'Send message'}).click();
 await expect(page.getByRole('button',{name:'Check send status'})).toBeEnabled();await input.fill('Separate newer thought');await page.getByLabel('Select local files').setInputFiles({name:'next.txt',mimeType:'text/plain',buffer:Buffer.from('Newer draft bytes')});await page.evaluate(async()=>{await (window as any).fixtureStore.flush();});await page.reload();
 await expect(input).toHaveValue('Separate newer thought');await expect(page.getByRole('button',{name:'Send message'})).toBeDisabled();await page.getByRole('button',{name:'Check send status'}).click();await expect(page.getByRole('button',{name:'Review retained draft'})).toBeVisible();
 await page.evaluate(async()=>{await (window as any).fixtureStore.flush();});await page.reload();await expect(page.getByRole('button',{name:'Review retained draft'})).toBeVisible();await page.getByRole('button',{name:'Review retained draft'}).click();await page.getByText('Retained draft',{exact:true}).click();await expect(page.locator('.prompt-retained-draft')).toContainText('Successfully acknowledged original message');await expect(page.locator('.prompt-retained-draft')).toContainText('sent.txt');await expect(input).toHaveValue('Separate newer thought');
 await page.getByRole('button',{name:'Restore retained draft'}).click();await expect(input).toHaveValue('Successfully acknowledged original message');await expect(page.getByRole('button',{name:'Remove sent.txt'})).toBeVisible();await expect(page.getByAltText('Preview of sent.png')).toBeVisible();await expect(page.locator('.prompt-retained-draft')).toContainText('Separate newer thought');await expect(page.locator('.prompt-retained-draft')).toContainText('next.txt');
 await page.evaluate(async()=>{await (window as any).fixtureStore.flush();});await page.reload();await expect(input).toHaveValue('Successfully acknowledged original message');await page.getByText('Retained draft',{exact:true}).click();await expect(page.locator('.prompt-retained-draft')).toContainText('Separate newer thought');
 const bytes=await page.evaluate(async()=>{const store=(window as any).fixtureStore;return {sent:await store.state.draft.attachments[0].file.text(),newer:await store.state.recovery.attachments[0].file.text()};});expect(bytes).toEqual({sent:'Original sent bytes',newer:'Newer draft bytes'});
 await expect(page.getByAltText('Preview of sent.png')).toBeVisible();const calls=await page.evaluate(()=>JSON.parse(localStorage.getItem('fixture:calls')??'[]'));expect(calls.map((call:any)=>call.kind)).toEqual(['stage','stage','send','status']);expect(calls[2].id).toBe(calls[3].id);
 await page.setViewportSize({width:390,height:844});expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);const axe=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze();expect(axe.violations.map(v=>({id:v.id,impact:v.impact}))).toEqual([]);await mkdir(captures,{recursive:true});await page.screenshot({path:captures+'/acknowledged-rejection-restored.png'});
});
