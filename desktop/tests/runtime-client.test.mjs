import test from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';
import {createRequire} from 'node:module';
import {chmodSync,mkdtempSync,writeFileSync,symlinkSync,linkSync,rmSync} from 'node:fs';
import os from 'node:os';
import path from 'node:path';
const require=createRequire(import.meta.url);
const {createRuntimeClient,dispatchRuntime}=require('../electron/runtime-client.cjs');

test('host runtime client uses fixed paths and secret authentication, and gates safe execution',async t=>{
  const requests=[];let enabled=false;let jobProfile=null;
  const server=http.createServer(async(req,res)=>{
    let body='';for await(const chunk of req)body+=chunk;
    requests.push({url:req.url,authorization:req.headers.authorization,body:body?JSON.parse(body):null});
    res.setHeader('Content-Type','application/json');
    res.end(JSON.stringify(req.url==='/v1/capabilities'?{v:1,features:{local_git_inspection:enabled}}:req.url==='/v1/jobs/job-1'?{v:1,job:{id:'job-1',state:'queued',execution_profile:jobProfile,budget_usd:0}}:{v:1,accepted:true,revision:2}));
  });
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));t.after(()=>server.close());
  const client=createRuntimeClient({url:`http://127.0.0.1:${server.address().port}`,token:'private-session',repo:'/configured/repo'});
  await assert.rejects(client.submitInspection('project-1','Inspect',1),/safe local inspection/);
  assert.equal(requests.length,1);enabled=true;
  await client.submitInspection('project-1','Inspect',1);
  const command=requests.at(-1).body;
  assert.equal(command.type,'job.create');assert.equal(command.payload.budget_usd,0);
  assert.deepEqual(command.payload.allowed_actions,['read_repo','run_checks']);
  assert.deepEqual(command.payload.checks,['candidate.frozen_identity']);
  assert.equal(requests.every(req=>req.authorization==='Bearer private-session'),true);
  assert.equal(JSON.stringify(command).includes('private-session'),false);
  const count=requests.length;
  for(const [method,args] of [['shell',['id']],['__proto__',[]],['job',['../secret']],['text',['artifact','file',0]],['run',['job',-1]],['submitInspection',['project','bad\ntext',1]],['snapshot',[1]],['runInfo',['../secret']],['runEvents',['run-1',-1]],['runEvents',['run-1',1.5]]])await assert.rejects(dispatchRuntime(client,method,args));
  assert.equal(requests.length,count,'invalid inputs produce no network calls');
  await client.register(2);assert.equal(requests.at(-1).body.payload.repo_path,'/configured/repo');
  assert.deepEqual(requests.at(-1).body.payload.policy,{allowed_actions:['read_repo','run_checks']});
  const beforeRun=requests.filter(item=>item.body?.type==='job.run').length;
  await assert.rejects(client.run('job-1',2),/not a queued zero-budget/);
  assert.equal(requests.filter(item=>item.body?.type==='job.run').length,beforeRun,'mixed-runtime coding job cannot launch through inspection capability');
  jobProfile='local_git_inspection';await client.run('job-1',2);
  assert.equal(requests.at(-1).body.type,'job.run');assert.equal(requests.at(-1).body.payload.job_id,'job-1');
});

test('runtime origin and session file reject redirects, remote hosts, links and loose permissions',async t=>{
  for(const url of ['https://127.0.0.1:4317','http://localhost:4317','http://example.com','http://user@127.0.0.1:4317','http://127.0.0.1:4317/path'])assert.throws(()=>createRuntimeClient({url,token:'private'}));
  const temp=mkdtempSync(path.join(os.tmpdir(),'sidequest-runtime-auth-'));t.after(()=>rmSync(temp,{recursive:true,force:true}));
  const token=path.join(temp,'token');writeFileSync(token,'private-session',{mode:0o600});
  assert.doesNotThrow(()=>createRuntimeClient({url:'http://127.0.0.1:4317',tokenFile:token}));
  chmodSync(token,0o644);assert.throws(()=>createRuntimeClient({tokenFile:token}));chmodSync(token,0o600);
  const symlink=path.join(temp,'symlink');symlinkSync(token,symlink);assert.throws(()=>createRuntimeClient({tokenFile:symlink}));
  const hardlink=path.join(temp,'hardlink');linkSync(token,hardlink);assert.throws(()=>createRuntimeClient({tokenFile:hardlink}));
  const server=http.createServer((req,res)=>{res.writeHead(302,{Location:'http://example.com'});res.end();});
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));t.after(()=>server.close());
  await assert.rejects(createRuntimeClient({url:`http://127.0.0.1:${server.address().port}`,token:'private'}).snapshot());
});

test('runtime response bound limits untrusted artifact output',async t=>{
  const server=http.createServer((_req,res)=>{res.writeHead(200,{'Content-Type':'application/json','Content-Length':2*1024*1024});res.end('x');});
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));t.after(()=>server.close());
  await assert.rejects(createRuntimeClient({url:`http://127.0.0.1:${server.address().port}`,token:'private'}).artifact('artifact-1'),/read limit/);
});

test('coding methods require verified capability and USD enforcement before mutations',async t=>{
  const requests=[];let usd=false;let profile='local_git_inspection';
  const server=http.createServer(async(req,res)=>{
    let body='';for await(const chunk of req)body+=chunk;requests.push({method:req.method,url:req.url,body:body?JSON.parse(body):null});
    res.setHeader('Content-Type','application/json');
    res.end(JSON.stringify(req.url==='/v1/capabilities'?{features:{coding:true,codex_session:true},worker_model:{verified:true},codex:{usd_cost_enforced:usd}}:req.url==='/v1/jobs/job-1'?{job:{id:'job-1',state:'queued',execution_profile:profile,budget_usd:'0.01'}}:{accepted:true}));
  });
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));t.after(()=>server.close());
  const client=createRuntimeClient({url:`http://127.0.0.1:${server.address().port}`,token:'test-session'});
  await assert.rejects(client.enableCoding('project-1',1),/USD ceiling/);
  await assert.rejects(client.submitCoding('project-1','Change','Add a scoped change','src','0.01',1),/USD ceiling/);
  await assert.rejects(client.runCoding('job-1',1),/USD ceiling/);
  assert.equal(requests.some(req=>req.method==='POST'),false);
  const before=requests.length;
  for(const prefix of ['../secret','/absolute','.git/hooks','.codex/config'])await assert.rejects(client.submitCoding('project-1','Change','Task',prefix,'0.01',1));
  for(const budget of ['0','-1','NaN','1e9'])await assert.rejects(client.submitCoding('project-1','Change','Task','src',budget,1));
  assert.equal(requests.length,before,'invalid coding inputs make no network request');
  usd=true;await assert.rejects(client.runCoding('job-1',1),/queued host-verified/);
  assert.equal(requests.some(req=>req.method==='POST'),false,'inspection profiles cannot enter coding execution');
  profile='codex_session';await client.runCoding('job-1',1);
  assert.deepEqual(requests.at(-1).body.payload,{job_id:'job-1'});
});

test('office session commands validate station and recorded run ownership without launching work',async t=>{
 const requests=[];let runJob='job-1';
 const server=http.createServer(async(req,res)=>{
  let body='';for await(const chunk of req)body+=chunk;requests.push({url:req.url,body:body?JSON.parse(body):null});res.setHeader('Content-Type','application/json');
  res.end(JSON.stringify(req.url==='/v1/jobs/job-1'?{v:1,job:{id:'job-1',run_ids:['run-1']}}:req.url==='/v1/runs/run-1'?{v:1,run:{id:'run-1',job_id:runJob,worker_id:'worker-1'}}:{v:1,accepted:true}));
 });await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));t.after(()=>server.close());
 const client=createRuntimeClient({url:`http://127.0.0.1:${server.address().port}`,token:'test-session'});
 await assert.rejects(dispatchRuntime(client,'assignSession',['parent_099','job-1','run-1',1]));assert.equal(requests.length,0);
 runJob='other';await assert.rejects(client.assignSession('parent_019','job-1','run-1',1),/ownership/);assert.equal(requests.some(r=>r.body),false);
 runJob='job-1';await client.assignSession('parent_019','job-1','run-1',1);assert.equal(requests.at(-1).body.type,'office.assign_session');
 await client.clearSession('parent_019',2);assert.equal(requests.at(-1).body.type,'office.clear_session');
 assert.equal(requests.some(r=>r.body?.type==='job.run'||r.url==='/v1/capabilities'),false);
});

test('protocol fixture: session transport keeps idempotency identity, validates opaque attachments and retains production USD guard',async t=>{
 const requests=[];let usd=false;
 const server=http.createServer(async(req,res)=>{let body='';for await(const chunk of req)body+=chunk;requests.push({url:req.url,body:body?JSON.parse(body):null});res.setHeader('Content-Type','application/json');res.end(JSON.stringify(req.url==='/v1/capabilities'?{features:{coding:true,codex_session:true,session_messages:true,session_attachments:true},worker_model:{verified:true},codex:{usd_cost_enforced:usd}}:{v:1,accepted:true}));});
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));t.after(()=>server.close());
 const client=createRuntimeClient({url:`http://127.0.0.1:${server.address().port}`,token:'fixture-token'}),id='12345678-1234-1234-1234-123456789012';
 await assert.rejects(client.sessionMessage('run-1',id,'Follow up','[]',2),/USD ceiling/);assert.equal(requests.some(item=>item.body),false);
 const before=requests.length;
 for(const [method,args] of [['stageAttachment',['run-1',id,'../notes.txt','text/plain','YWJj']],['stageAttachment',['run-1',id,'notes.txt','text/html','YWJj']],['stageAttachment',['run-1',id,'notes.txt','text/plain','not-base64']],['sessionMessage',['run-1',id,'Prompt','["../host"]',2]],['sessionMessage',['run-1','not-uuid','Prompt','[]',2]],['commandStatus',['not-uuid']]])await assert.rejects(dispatchRuntime(client,method,args));
 assert.equal(requests.length,before,'invalid IPC inputs never reach the runtime');
 await dispatchRuntime(client,'stageAttachment',['run-1',id,'notes.txt','text/plain','YWJj']);assert.equal(requests.at(-1).url,'/v1/session-attachments');assert.deepEqual(requests.at(-1).body,{run_id:'run-1',attachment_key:id,name:'notes.txt',media_type:'text/plain',data_base64:'YWJj'});
 usd=true;await client.sessionMessage('run-1',id,'Follow up','["attachment-1"]',2);assert.deepEqual(requests.at(-1).body,{v:1,command_id:id,type:'session.message',expected_revision:2,payload:{run_id:'run-1',prompt:'Follow up',attachment_ids:['attachment-1']}});
 await client.commandStatus(id);assert.equal(requests.at(-1).url,`/v1/commands/${id}`);
 await assert.rejects(dispatchRuntime(client,'snapshot',['a'.repeat(4097)]));
});

test('protocol fixture: native IPC fault envelope never exposes provider messages, paths or credentials',async()=>{
 const {dispatchRuntimeReply}=require('../electron/runtime-client.cjs');const client={sessionMessage:async()=>{throw Object.assign(Error('Do not expose /private/host or secret-token'),{code:'POLICY_DENIED',status:403});}};
 const reply=await dispatchRuntimeReply(client,'sessionMessage',['run-1','12345678-1234-1234-1234-123456789012','Prompt','[]',2]);assert.deepEqual(reply,{v:1,error:{code:'POLICY_DENIED',status:403,message:'Local runtime request failed (403, POLICY_DENIED).'}});assert.doesNotMatch(JSON.stringify(reply),/private|secret/);
});
