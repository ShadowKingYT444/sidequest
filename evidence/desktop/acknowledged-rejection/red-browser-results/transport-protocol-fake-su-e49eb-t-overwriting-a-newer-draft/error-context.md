# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: transport.spec.ts >> protocol fake: successful 202 then rejected-before-start restores sent files without overwriting a newer draft
- Location: tests/browser/transport.spec.ts:80:1

# Error details

```
Error: expect(locator).toBeEnabled() failed

Locator: getByRole('button', { name: 'Check send status' })
Expected: enabled
Timeout: 15000ms
Error: element(s) not found

Call log:
  - Expect "toBeEnabled" getByRole('button', { name: 'Check send status' }) with timeout 15000ms
  - waiting for getByRole('button', { name: 'Check send status' })
    - locator resolved to <button disabled type="button">Check send status</button>
    - unexpected value "disabled"

```

```yaml
- paragraph: Protocol-fake session transport · no model calls
- form "Local prompt composer":
  - button "Attach files"
  - text: Message this session
  - textbox "Message this session":
    - /placeholder: Write a local draft…
  - button "Send message" [disabled]
  - button "Select local files"
  - group: Message accepted ⌄
  - text: 0/2,000
```

# Test source

```ts
  1  | import {test,expect,type Page} from '@playwright/test';
  2  | import {mkdir} from 'node:fs/promises';
  3  | 
  4  | // Explicit protocol fake: real Chromium IndexedDB/File reload, real React composer,
  5  | // fake authenticated runtime receipts. No provider startup or model turn occurs.
  6  | const captures=`../evidence/desktop/transport/${process.env.SIDEQUEST_TRANSPORT_EVIDENCE_RUN??'captures'}`;
  7  | async function composerFixture(page:Page,{lostReply=false,usd=true,rejectedBeforeStart=false}={}){
  8  |  page.on('pageerror',error=>console.error('Composer fixture page error:',error.message));
  9  |  await page.addInitScript(({lostReply,usd,rejectedBeforeStart})=>{
  10 |   const caps={v:1,features:{coding:true,codex_session:true,session_messages:true,session_attachments:true},worker_model:{verified:true},codex:{host_enabled:true,state:'available',catalog_verified:true,usd_cost_enforced:usd}};
  11 |   const record=(kind:string,id:string)=>{const calls=JSON.parse(localStorage.getItem('fixture:calls')??'[]');calls.push({kind,id});localStorage.setItem('fixture:calls',JSON.stringify(calls));};
  12 |   (window as any).sidequest={runtime:{
  13 |    capabilities:async()=>caps,snapshot:async()=>({v:1,revision:7}),
  14 |    stageAttachment:async(run:string,key:string,name:string,mime:string,base64:string)=>{record('stage',key);return {v:1,attachment:{id:'attachment-'+key,run_id:run,name,media_type:mime,size_bytes:atob(base64).length,sha256:'a'.repeat(64)}};},
  15 |    sessionMessage:async(run:string,id:string)=>{record('send',id);const command={v:1,accepted:true,command_id:id,revision:8,result:{run_id:'follow-up-run'}};localStorage.setItem('fixture:receipt:'+id,JSON.stringify(command));if(lostReply)throw Error('Protocol fake: response lost after acceptance');return command;},
  16 |    commandStatus:async(id:string)=>{record('status',id);const receipt=localStorage.getItem('fixture:receipt:'+id);return {v:1,found:!!receipt,...(receipt?{command:JSON.parse(receipt),...(rejectedBeforeStart?{message:{id,state:'rejected',run_id:null}}:{})}:{})};},
  17 |   }};
  18 |  },{lostReply,usd,rejectedBeforeStart});
  19 |  await page.route('**/transport-fixture',route=>route.fulfill({contentType:'text/html',body:`<!doctype html><html><head><meta charset="utf-8"><title>Protocol-fake session composer</title><meta name="viewport" content="width=device-width, initial-scale=1"></head><body style="margin:0;background:#111;color:#eee;font:14px system-ui"><p style="margin:16px">Protocol-fake session transport · no model calls</p><div id="fixture-root" style="max-width:720px;margin:16px;border:1px solid #333"></div><script type="module">
  20 |  import RefreshRuntime from '/@react-refresh';
  21 |  RefreshRuntime.injectIntoGlobalHook(window);window.$RefreshReg$=()=>{};window.$RefreshSig$=()=>type=>type;window.__vite_plugin_react_preamble_installed__=true;
  22 |  </script><script type="module">
  23 |  import '/src/style.css';
  24 |  import React from '/node_modules/.vite/deps/react.js';
  25 |  import ReactDOMClient from '/node_modules/.vite/deps/react-dom_client.js';
  26 |  const {createRoot}=ReactDOMClient;
  27 |  import SessionComposer from '/src/SessionComposer.tsx';
  28 |  import {SessionDraftStore} from '/src/session-drafts.ts';
  29 |  import {createDraftOperations} from '/src/local-drafts.ts';
  30 |  const store=new SessionDraftStore('fixture-conversation');window.fixtureStore=store;
  31 |  const job={id:'job-1',state:'verifying',execution_profile:'codex_session',spent_usd:0.01,budget_usd:0.03};
  32 |  const run={id:'run-1',state:'completed',ended_at:'2026-10-14T00:00:00Z',usage:{uncertain:false,cost_usd:0.01}};
  33 |  createRoot(document.getElementById('fixture-root')).render(React.createElement(SessionComposer,{store,operations:createDraftOperations(),job,run,known:true,active:true,onAccepted:()=>{window.fixtureAccepted=true;}}));
  34 |  </script></body></html>`}));
  35 |  await page.goto('/transport-fixture');await expect(page.getByRole('textbox',{name:'Message this session'})).toBeEditable();
  36 | }
  37 | 
  38 | test('protocol fake: real IndexedDB restores draft, File bytes, UUID, selection and a local image preview on reload',async({page})=>{
  39 |  await composerFixture(page);const input=page.getByRole('textbox',{name:'Message this session'});await input.fill('A thought worth retaining');
  40 |  const png=Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a1ioAAAAASUVORK5CYII=','base64');
  41 |  await page.getByLabel('Select local files').setInputFiles([{name:'notes.txt',mimeType:'text/plain',buffer:Buffer.from('Retained bytes')},{name:'pixel.png',mimeType:'image/png',buffer:png}]);
  42 |  await expect(page.getByRole('list',{name:'Local attachments'}).getByRole('listitem')).toHaveCount(2);await expect(page.getByAltText('Preview of pixel.png')).toBeVisible();
  43 |  await input.focus();await input.press('Control+Home');for(let i=0;i<3;i++)await input.press('ArrowRight');for(let i=0;i<5;i++)await input.press('Shift+ArrowRight');
  44 |  await expect.poll(()=>page.evaluate(()=>(window as any).fixtureStore.state.selection)).toEqual([3,8]);
  45 |  await page.evaluate(async()=>{await (window as any).fixtureStore.flush();});
  46 |  const before=await page.evaluate(()=>({ids:(window as any).fixtureStore.state.draft.attachments.map((a:any)=>a.id),url:(window as any).fixtureStore.state.draft.attachments[1].previewURL}));
  47 |  await page.reload();await expect(input).toHaveValue('A thought worth retaining');await expect(page.getByAltText('Preview of pixel.png')).toBeVisible();
  48 |  const restored=await page.evaluate(async()=>{const store=(window as any).fixtureStore;await store.ready;return {ids:store.state.draft.attachments.map((a:any)=>a.id),text:await store.state.draft.attachments[0].file.text(),url:store.state.draft.attachments[1].previewURL,selection:store.state.selection};});
  49 |  expect(restored.ids).toEqual(before.ids);expect(restored.text).toBe('Retained bytes');expect(restored.url).not.toBe(before.url);expect(restored.selection).toEqual([3,8]);expect(await input.evaluate((node:HTMLTextAreaElement)=>[node.selectionStart,node.selectionEnd])).toEqual([3,8]);
  50 |  await mkdir(captures,{recursive:true});await page.screenshot({path:captures+'/durable-composer.png'});
  51 | });
  52 | 
  53 | test('protocol fake: lost reply survives reload and reconciles exactly one send, keeping a subsequent draft',async({page})=>{
  54 |  await composerFixture(page,{lostReply:true});const input=page.getByRole('textbox',{name:'Message this session'});await input.fill('Follow up with the staged notes');
  55 |  await page.getByLabel('Select local files').setInputFiles({name:'notes.txt',mimeType:'text/plain',buffer:Buffer.from('Attached UTF-8 text')});
  56 |  await expect(page.getByRole('button',{name:'Send message'})).toBeEnabled();await page.getByRole('button',{name:'Send message'}).click();
  57 |  await expect(page.getByRole('button',{name:'Check send status'})).toBeEnabled();await expect(page.getByRole('button',{name:'Send message'})).toBeDisabled();
  58 |  await mkdir(captures,{recursive:true});await page.screenshot({path:captures+'/pending-composer.png'});
  59 |  await input.fill('My next thought');await page.evaluate(async()=>{await (window as any).fixtureStore.flush();});await page.reload();
  60 |  await expect(input).toHaveValue('My next thought');await expect(page.getByRole('button',{name:'Send message'})).toBeDisabled();
  61 |  await page.getByRole('button',{name:'Check send status'}).click();await expect(page.getByRole('button',{name:'Check send status'})).toHaveCount(0);await expect(input).toHaveValue('My next thought');await expect(page.getByRole('list',{name:'Local attachments'})).toHaveCount(0);
  62 |  const calls=await page.evaluate(()=>JSON.parse(localStorage.getItem('fixture:calls')??'[]'));expect(calls.map((call:any)=>call.kind)).toEqual(['stage','send','status']);expect(calls[1].id).toBe(calls[2].id);
  63 |  await page.setViewportSize({width:390,height:844});await mkdir(captures,{recursive:true});await page.screenshot({path:captures+'/reconciled-composer-mobile.png'});expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  64 | });
  65 | 
  66 | test('protocol fake: unknown spending authority keeps send disabled while durable local draft remains usable',async({page})=>{
  67 |  await composerFixture(page,{usd:false});await page.getByRole('textbox',{name:'Message this session'}).fill('No dispatch while authority is unknown');await expect(page.getByRole('button',{name:'Send message'})).toBeDisabled();
  68 |  await page.getByRole('textbox',{name:'Message this session'}).press('Control+Enter');expect(await page.evaluate(()=>localStorage.getItem('fixture:calls'))).toBeNull();
  69 | });
  70 | 
  71 | test('protocol fake: accepted command rejected before start retains file and next draft across reload until explicit review',async({page})=>{
  72 |  await composerFixture(page,{lostReply:true,rejectedBeforeStart:true});const input=page.getByRole('textbox',{name:'Message this session'});await input.fill('Original requested follow-up');
  73 |  await page.getByLabel('Select local files').setInputFiles({name:'notes.txt',mimeType:'text/plain',buffer:Buffer.from('Retain attachment')});await expect(page.getByRole('button',{name:'Send message'})).toBeEnabled();await page.getByRole('button',{name:'Send message'}).click();await expect(page.getByRole('button',{name:'Check send status'})).toBeEnabled();
  74 |  await input.fill('A concurrent next thought');await page.getByRole('button',{name:'Check send status'}).click();await expect(page.getByRole('button',{name:'Review retained draft'})).toBeVisible();await expect(page.getByRole('list',{name:'Local attachments'}).getByRole('listitem')).toHaveCount(1);await expect(input).toHaveValue('A concurrent next thought');await expect(page.getByRole('button',{name:'Send message'})).toBeDisabled();
  75 |  await page.evaluate(async()=>{await (window as any).fixtureStore.flush();});await page.reload();await expect(page.getByRole('button',{name:'Review retained draft'})).toBeVisible();await expect(page.getByText('Message did not start · review retained draft',{exact:true}).first()).toBeVisible();await expect(input).toHaveValue('A concurrent next thought');
  76 |  await mkdir(captures,{recursive:true});await page.screenshot({path:captures+'/rejected-before-start.png'});await page.getByRole('button',{name:'Review retained draft'}).click();await expect(page.getByRole('button',{name:'Review retained draft'})).toHaveCount(0);await expect(page.getByRole('button',{name:'Send message'})).toBeEnabled();await expect(page.getByRole('list',{name:'Local attachments'}).getByRole('listitem')).toHaveCount(1);await expect(input).toHaveValue('A concurrent next thought');
  77 |  const calls=await page.evaluate(()=>JSON.parse(localStorage.getItem('fixture:calls')??'[]'));expect(calls.map((call:any)=>call.kind)).toEqual(['stage','send','status']);expect(calls[1].id).toBe(calls[2].id);
  78 | });
  79 | 
  80 | test('protocol fake: successful 202 then rejected-before-start restores sent files without overwriting a newer draft',async({page})=>{
  81 |  await composerFixture(page,{rejectedBeforeStart:true});const input=page.getByRole('textbox',{name:'Message this session'});await input.fill('Successfully acknowledged original message');
  82 |  await page.getByLabel('Select local files').setInputFiles({name:'sent.txt',mimeType:'text/plain',buffer:Buffer.from('Original sent bytes')});await expect(page.getByRole('button',{name:'Send message'})).toBeEnabled();await page.getByRole('button',{name:'Send message'}).click();
> 83 |  await expect(page.getByRole('button',{name:'Check send status'})).toBeEnabled();await input.fill('Separate newer thought');await page.getByLabel('Select local files').setInputFiles({name:'next.txt',mimeType:'text/plain',buffer:Buffer.from('Newer draft bytes')});await page.evaluate(async()=>{await (window as any).fixtureStore.flush();});await page.reload();
     |                                                                    ^ Error: expect(locator).toBeEnabled() failed
  84 |  await expect(input).toHaveValue('Separate newer thought');await expect(page.getByRole('button',{name:'Send message'})).toBeDisabled();await page.getByRole('button',{name:'Check send status'}).click();await expect(page.getByRole('button',{name:'Review retained draft'})).toBeVisible();
  85 |  await page.evaluate(async()=>{await (window as any).fixtureStore.flush();});await page.reload();await expect(page.getByRole('button',{name:'Review retained draft'})).toBeVisible();await page.getByRole('button',{name:'Review retained draft'}).click();await page.getByText('Retained draft',{exact:true}).click();await expect(page.locator('.prompt-retained-draft')).toContainText('Successfully acknowledged original message');await expect(page.locator('.prompt-retained-draft')).toContainText('sent.txt');await expect(input).toHaveValue('Separate newer thought');
  86 |  await page.getByRole('button',{name:'Restore retained draft'}).click();await expect(input).toHaveValue('Successfully acknowledged original message');await expect(page.getByRole('button',{name:'Remove sent.txt'})).toBeVisible();await expect(page.locator('.prompt-retained-draft')).toContainText('Separate newer thought');await expect(page.locator('.prompt-retained-draft')).toContainText('next.txt');
  87 |  await page.evaluate(async()=>{await (window as any).fixtureStore.flush();});await page.reload();await expect(input).toHaveValue('Successfully acknowledged original message');await page.getByText('Retained draft',{exact:true}).click();await expect(page.locator('.prompt-retained-draft')).toContainText('Separate newer thought');
  88 |  const bytes=await page.evaluate(async()=>{const store=(window as any).fixtureStore;return {sent:await store.state.draft.attachments[0].file.text(),newer:await store.state.recovery.attachments[0].file.text()};});expect(bytes).toEqual({sent:'Original sent bytes',newer:'Newer draft bytes'});
  89 |  const calls=await page.evaluate(()=>JSON.parse(localStorage.getItem('fixture:calls')??'[]'));expect(calls.map((call:any)=>call.kind)).toEqual(['stage','send','status']);expect(calls[1].id).toBe(calls[2].id);
  90 |  await page.setViewportSize({width:390,height:844});expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);await mkdir(captures,{recursive:true});await page.screenshot({path:captures+'/acknowledged-rejection-restored.png'});
  91 | });
  92 | 
```