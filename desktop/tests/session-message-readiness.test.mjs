import test from 'node:test';
import assert from 'node:assert/strict';
import {sessionMessageReason,sessionAttachmentReason} from '../src/session-message-readiness.ts';
const caps={v:1,features:{coding:true,codex_session:true,session_messages:true,session_attachments:true},worker_model:{verified:true},codex:{host_enabled:true,state:'available',catalog_verified:true,usd_cost_enforced:true}};
const job={state:'verifying',execution_profile:'codex_session',spent_usd:0.01,budget_usd:0.03},run={state:'completed',ended_at:'2026-10-14T00:00:00Z',usage:{uncertain:false,cost_usd:0.01}};
test('protocol fixture: sending requires terminal coding identity, known remaining budget and every production readiness guard',()=>{
 assert.equal(sessionMessageReason(caps,job,run,true,true),null);
 for(const field of ['coding','codex_session','session_messages'])assert.ok(sessionMessageReason({...caps,features:{...caps.features,[field]:false}},job,run,true,true));
 for(const field of ['host_enabled','catalog_verified','usd_cost_enforced'])assert.ok(sessionMessageReason({...caps,codex:{...caps.codex,[field]:false}},job,run,true,true));
 assert.ok(sessionMessageReason(caps,{...job,spent_usd:null},run,true,true));assert.ok(sessionMessageReason(caps,{...job,spent_usd:0.03},run,true,true));assert.ok(sessionMessageReason(caps,job,{...run,state:'running'},true,true));assert.ok(sessionMessageReason(caps,job,{...run,usage:{...run.usage,uncertain:true}},true,true));assert.ok(sessionMessageReason(caps,job,run,false,true));assert.ok(sessionMessageReason(caps,job,run,true,false));
});
test('provider attachment bounds preserve local unsupported/large files rather than sending them',()=>{
 assert.equal(sessionAttachmentReason({text:'hello',attachments:[{name:'notes.txt',size:5}]},caps),null);
 assert.match(sessionAttachmentReason({text:'hello',attachments:[{name:'report.pdf',size:5}]},caps),/PDF/);
 assert.match(sessionAttachmentReason({text:'hello',attachments:[{name:'large.txt',size:1024*1024}]},caps),/1 MiB/);
 assert.match(sessionAttachmentReason({text:'hello',attachments:[{name:'notes.txt',size:5}]},{...caps,features:{...caps.features,session_attachments:false}}),/transport/);
});

test('protocol fixture: queued jobs and older task attempts cannot advertise send readiness',()=>{
 assert.ok(sessionMessageReason(caps,{...job,state:'queued'},run,true,true));
 assert.ok(sessionMessageReason(caps,{...job,tasks:[{id:'task-1',attempt_id:'new-run'}]},{...run,id:'old-run',task_id:'task-1'},true,true));
 assert.equal(sessionMessageReason(caps,{...job,state:'accepted',tasks:[{id:'task-1',attempt_id:'current-run'}]},{...run,id:'current-run',task_id:'task-1'},true,true),null);
});
