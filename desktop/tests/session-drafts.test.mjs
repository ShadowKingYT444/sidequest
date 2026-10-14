import test from 'node:test';
import assert from 'node:assert/strict';
import {SessionDraftStore, createIndexedDraftStorage} from '../src/session-drafts.ts';
import {addLocalFiles} from '../src/local-drafts.ts';

// Protocol and durable-storage fakes only. These tests make no provider/model calls.
function protocolFixture(){
 const rows=new Map(), calls=[], receipts=new Map();
 const storage={async read(key){return rows.get(key);},async write(key,value){rows.set(key,structuredClone(value));}};
 const transport={async snapshot(){return {revision:2};},async stageAttachment(run,key,name,mime,bytes){calls.push(['stage',run,key]);return {v:1,attachment:{id:'attachment-1',run_id:run,name,media_type:mime,size_bytes:3,sha256:'a'.repeat(64)}};},async sessionMessage(run,id,prompt,ids,revision){calls.push(['send',run,id,prompt,ids,revision]);const reply={v:1,accepted:true,command_id:id,revision:revision+1,result:{run_id:run}};receipts.set(id,reply);return reply;},async commandStatus(id){calls.push(['status',id]);return {v:1,found:receipts.has(id),...(receipts.has(id)?{command:receipts.get(id)}:{})};}};
 return {storage,transport,rows,calls,receipts};
}
const urls=()=>({createObjectURL:()=>`blob:preview-${crypto.randomUUID()}`,revokeObjectURL(){}});
const target={runId:'run-1',revision:2};

test('protocol fixture: reload preserves File bytes, local identities and recreated image previews without storing URLs',async()=>{
 const fixture=protocolFixture(), first=new SessionDraftStore('session-1',fixture.storage,urls());await first.ready;
 const added=await addLocalFiles({text:'Keep this thought',attachments:[]},[new File(['abc'],'notes.txt',{type:'text/plain',lastModified:7})],urls());first.change(added.draft);await first.flush();
 const saved=fixture.rows.get('session-1');assert.equal(JSON.stringify(saved).includes('blob:preview'),false);
 const second=new SessionDraftStore('session-1',fixture.storage,urls());await second.ready;
 assert.equal(second.state.draft.text,'Keep this thought');assert.equal(second.state.draft.attachments[0].id,first.state.draft.attachments[0].id);assert.equal(await second.state.draft.attachments[0].file.text(),'abc');
 assert.equal(second.state.draft.attachments[0].file.lastModified,7);
});

test('protocol fixture: lost send reply stays locked across reload, reconciles original command ID and never sends twice',async()=>{
 const fixture=protocolFixture(),first=new SessionDraftStore('session-1',fixture.storage,urls());await first.ready;first.change({text:'Follow up',attachments:[]});
 const realSend=fixture.transport.sessionMessage;fixture.transport.sessionMessage=async(...args)=>{await realSend(...args);throw Error('Response lost after acceptance');};
 await first.send(target,fixture.transport);assert.equal(first.state.pending.state,'uncertain');const id=first.state.pending.commandId;
 const second=new SessionDraftStore('session-1',fixture.storage,urls());await second.ready;
 await second.send(target,fixture.transport);assert.equal(fixture.calls.filter(call=>call[0]==='send').length,1,'new command must not be issued while receipt is uncertain');
 await second.reconcile(fixture.transport);assert.equal(second.state.pending,undefined);assert.equal(second.state.draft.text,'');assert.equal(second.state.status,'Message accepted');
 assert.deepEqual(fixture.calls.at(-1),['status',id]);
});

test('protocol fixture: drafts edited during send are retained and only submitted attachment identities clear after acceptance',async()=>{
 const fixture=protocolFixture(),store=new SessionDraftStore('session-1',fixture.storage,urls());await store.ready;
 const added=await addLocalFiles({text:'Original',attachments:[]},[new File(['abc'],'notes.txt',{type:'text/plain'})],urls());store.change(added.draft);
 fixture.transport.sessionMessage=async(run,id)=>{store.change({...store.state.draft,text:'Next thought'});return {v:1,accepted:true,command_id:id,revision:3};};
 await store.send(target,fixture.transport);assert.equal(store.state.draft.text,'Next thought');assert.equal(store.state.draft.attachments.length,0);assert.equal(store.state.pending,undefined);
 assert.equal(fixture.calls.filter(call=>call[0]==='stage').length,1);
});

test('protocol fixture: staging/readiness failure retains draft and ID; explicit retry after not-found reuses same send identity',async()=>{
 const fixture=protocolFixture(),store=new SessionDraftStore('session-1',fixture.storage,urls());await store.ready;store.change({text:'Keep me',attachments:[]});
 fixture.transport.sessionMessage=async(run,id)=>{fixture.calls.push(['send',run,id]);throw Error('Host unavailable');};await store.send(target,fixture.transport);
 const id=store.state.pending.commandId;await store.reconcile(fixture.transport);assert.equal(store.state.pending.state,'not_found');assert.equal(store.state.draft.text,'Keep me');
 await store.retry(target,fixture.transport);assert.equal(fixture.calls.filter(call=>call[0]==='send').length,2);assert.equal(fixture.calls.at(-1)[2],id);
});

test('protocol fixture: storage failure blocks sends before staging or message network mutation',async()=>{
 const fixture=protocolFixture(),store=new SessionDraftStore('session-1',{read:async()=>undefined,write:async()=>{throw Error('Quota exceeded');}},urls());await store.ready;store.change({text:'Keep me',attachments:[]});
 await store.send(target,fixture.transport);assert.equal(fixture.calls.length,0);assert.equal(store.state.draft.text,'Keep me');assert.match(store.state.error,/save|storage/i);
});

test('protocol fixture: malformed stored pending or mismatched receipts cannot clear a draft',async()=>{
 const fixture=protocolFixture(),store=new SessionDraftStore('session-1',fixture.storage,urls());await store.ready;store.change({text:'Keep me',attachments:[]});
 fixture.transport.sessionMessage=async()=>({v:1,accepted:true,command_id:'wrong-id',revision:3});await store.send(target,fixture.transport);assert.equal(store.state.pending.state,'uncertain');assert.equal(store.state.draft.text,'Keep me');
 fixture.transport.commandStatus=async()=>({v:1,found:true,command:{v:1,accepted:true,command_id:'wrong-id',revision:3}});await store.reconcile(fixture.transport);assert.equal(store.state.pending.state,'uncertain');assert.equal(store.state.draft.text,'Keep me');
 fixture.rows.set('bad',{v:1,text:'Unsafe',attachments:[],pending:{commandId:'bad',runId:'run-1',text:'Unsafe',attachmentIds:[],localIds:[],state:'uncertain'}});const bad=new SessionDraftStore('bad',fixture.storage,urls());await bad.ready;assert.match(bad.state.error,/restore/i);
});

test('protocol fixture: retry replays the exact saved revision even after staging and later runtime revision changes',async()=>{
 const fixture=protocolFixture(),store=new SessionDraftStore('session-1',fixture.storage,urls());await store.ready;store.change({text:'Keep exact identity',attachments:[]});let revision=20;fixture.transport.snapshot=async()=>({revision});
 fixture.transport.sessionMessage=async(...args)=>{fixture.calls.push(['send',...args]);throw Error('Lost response');};await store.send(target,fixture.transport);const original=fixture.calls.at(-1);
 assert.equal(original.at(-1),20);revision=21;await store.reconcile(fixture.transport);await store.retry(target,fixture.transport);assert.deepEqual(fixture.calls.at(-1),original);
});
test('protocol fixture: a definite revision rejection retains draft and requires explicit review before a new send identity',async()=>{
 const fixture=protocolFixture(),store=new SessionDraftStore('session-1',fixture.storage,urls());await store.ready;store.change({text:'Review me',attachments:[]});
 fixture.transport.sessionMessage=async()=>{throw Object.assign(Error('Revision conflict'),{code:'VERSION_CONFLICT',status:409});};await store.send(target,fixture.transport);assert.equal(store.state.pending.state,'rejected');const old=store.state.pending.commandId;
 await store.send(target,fixture.transport);assert.equal(store.state.pending.commandId,old);await store.reviewRejected();assert.equal(store.state.pending,undefined);assert.equal(store.state.draft.text,'Review me');
 await store.send(target,fixture.transport);assert.notEqual(store.state.pending.commandId,old);
});

test('protocol fixture: a corrupt pending record is never overwritten by edits or allowed to create another send',async()=>{
 const fixture=protocolFixture(),corrupt={v:1,text:'Possibly already sent',attachments:[],pending:{commandId:'corrupt',runId:'run-1',state:'uncertain'}};fixture.rows.set('session-1',corrupt);
 const store=new SessionDraftStore('session-1',fixture.storage,urls());await store.ready;store.change({text:'An unsent local thought',attachments:[]});store.setSelection([0,2]);await store.flush();await store.send(target,fixture.transport);
 assert.equal(fixture.calls.length,0);assert.deepEqual(fixture.rows.get('session-1'),corrupt);assert.match(store.state.error,/restore/);
});

test('protocol fixture: an accepted receipt rejected before provider start retains attachments and the concurrent next thought until explicit review',async()=>{
 const fixture=protocolFixture(),store=new SessionDraftStore('session-1',fixture.storage,urls());await store.ready;
 const added=await addLocalFiles({text:'Original request',attachments:[]},[new File(['abc'],'notes.txt',{type:'text/plain'})],urls());store.change(added.draft);
 const realSend=fixture.transport.sessionMessage;fixture.transport.sessionMessage=async(...args)=>{await realSend(...args);throw Error('Lost acceptance reply');};await store.send(target,fixture.transport);
 const pending=store.state.pending;store.change({...store.state.draft,text:'My next thought'});await store.flush();
 fixture.transport.commandStatus=async(id)=>({v:1,found:true,command:fixture.receipts.get(id),message:{id,state:'rejected',run_id:null}});
 await store.reconcile(fixture.transport);assert.equal(store.state.pending.state,'rejected');assert.equal(store.state.pending.commandId,pending.commandId);assert.equal(store.state.draft.text,'My next thought');assert.equal(store.state.draft.attachments.length,1);assert.match(store.state.status,/did not start/i);
 const reloaded=new SessionDraftStore('session-1',fixture.storage,urls());await reloaded.ready;assert.equal(reloaded.state.pending.state,'rejected');assert.equal(reloaded.state.draft.text,'My next thought');assert.equal(await reloaded.state.draft.attachments[0].file.text(),'abc');
 await reloaded.send(target,fixture.transport);assert.equal(fixture.calls.filter(call=>call[0]==='send').length,1);await reloaded.reviewRejected();assert.equal(reloaded.state.pending,undefined);assert.equal(reloaded.state.draft.text,'My next thought');assert.equal(reloaded.state.draft.attachments.length,1);
});

test('protocol fixture: conflicting or malformed message status never clears a pending draft or offers a fresh send identity',async()=>{
 for(const metadata of [{id:'other-command',state:'rejected',run_id:null},{id:'same',state:'invented',run_id:null},{id:'same',state:'rejected',run_id:'provider-run'},{id:'same',state:'dispatching',run_id:null},{id:'same',state:'completed',run_id:'../host'}]){
  const fixture=protocolFixture(),store=new SessionDraftStore('session-1',fixture.storage,urls());await store.ready;store.change({text:'Retain exact thought',attachments:[]});
  const realSend=fixture.transport.sessionMessage;fixture.transport.sessionMessage=async(...args)=>{await realSend(...args);throw Error('Lost reply');};await store.send(target,fixture.transport);const id=store.state.pending.commandId;
  fixture.transport.commandStatus=async()=>({v:1,found:true,command:fixture.receipts.get(id),message:{...metadata,id:metadata.id==='same'?id:metadata.id}});
  await store.reconcile(fixture.transport);assert.equal(store.state.pending.state,'uncertain');assert.equal(store.state.pending.commandId,id);assert.equal(store.state.draft.text,'Retain exact thought');assert.match(store.state.error,/message.*(identity|status)/i);
 }
});

test('protocol fixture: a contradictory later status cannot erase a known not-started rejection',async()=>{
 const fixture=protocolFixture(),store=new SessionDraftStore('session-1',fixture.storage,urls());await store.ready;store.change({text:'Retain rejected draft',attachments:[]});const realSend=fixture.transport.sessionMessage;fixture.transport.sessionMessage=async(...args)=>{await realSend(...args);throw Error('Lost reply');};await store.send(target,fixture.transport);const id=store.state.pending.commandId;
 fixture.transport.commandStatus=async()=>({v:1,found:true,command:fixture.receipts.get(id),message:{id,state:'rejected',run_id:null}});await store.reconcile(fixture.transport);
 for(const message of [undefined,{id,state:'queued',run_id:null}]){fixture.transport.commandStatus=async()=>({v:1,found:true,command:fixture.receipts.get(id),...(message?{message}:{})});await store.reconcile(fixture.transport);assert.equal(store.state.pending.state,'rejected');assert.equal(store.state.draft.text,'Retain rejected draft');assert.match(store.state.error,/rejected message status/i);}
});
