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
  for(const [method,args] of [['shell',['id']],['__proto__',[]],['job',['../secret']],['text',['artifact','file',0]],['run',['job',-1]],['submitInspection',['project','bad\ntext',1]],['snapshot',[1]]])await assert.rejects(dispatchRuntime(client,method,args));
  assert.equal(requests.length,count,'invalid inputs produce no network calls');
  await client.register(2);assert.equal(requests.at(-1).body.payload.repo_path,'/configured/repo');
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
