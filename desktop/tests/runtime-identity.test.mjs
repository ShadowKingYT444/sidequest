import test from 'node:test';
import assert from 'node:assert/strict';
import {requireFrozenArtifact,requireFilePage,requireTextPage,requireDiffPage,requireOfficeSessions} from '../src/runtime-identity.ts';
const hash='a'.repeat(64);
const artifact={id:'manifest-1',job_id:'job-1',kind:'file_manifest',candidate_id:'candidate-1',sha256:hash,immutable:true};
const file={file_id:'file-1',sha256:hash};
test('office session identities reject duplicate station, run and worker ownership',()=>{
  const row={station_id:'parent_019',job_id:'job-1',run_id:'run-1',worker_id:'worker-1',project_id:'project-1',assigned_at:'2026-10-14T09:00:00Z'};
  const snapshot={v:1,revision:3,jobs:[],office_sessions:[row]};
  assert.deepEqual(requireOfficeSessions(snapshot),[row]);
  for(const patch of [{station_id:'parent_099'},{run_id:'../secret'},{worker_id:null},{assigned_at:'yesterday'}])assert.throws(()=>requireOfficeSessions({...snapshot,office_sessions:[{...row,...patch}]}));
  for(const patch of [{station_id:'parent_020'},{run_id:'run-2'},{worker_id:'worker-2'}])assert.throws(()=>requireOfficeSessions({...snapshot,office_sessions:[row,{...row,...patch}]}));
});

test('office session validation bounds supplemental jobs independently from twenty recent jobs',()=>{
  const recent=Array.from({length:20},(_,index)=>({id:`recent-${index}`,title:'Recent task'}));
  const supplemental=Array.from({length:124},(_,index)=>({id:`older-${index}`,title:'Older office task'}));
  const snapshot={v:1,revision:3,jobs:recent,office_jobs:supplemental,office_jobs_truncated:true,office_sessions:[]};
  assert.deepEqual(requireOfficeSessions(snapshot),[]);
  assert.throws(()=>requireOfficeSessions({...snapshot,jobs:[...recent,{id:'recent-20',title:'Extra recent task'}]}));
  for(const office_jobs of [null,{},[null],[[]],[{id:'../outside',title:'Task'}],[{id:'older-1',title:'x'.repeat(201)}],
    [supplemental[0],supplemental[0]],[...supplemental,{id:'older-124',title:'Extra supplemental task'}]]) {
    assert.throws(()=>requireOfficeSessions({...snapshot,office_jobs}));
  }
});

test('supplemental overflow metadata is explicit boolean state and never accepts unknown coverage as verified',()=>{
  const snapshot={v:1,revision:3,jobs:[],office_jobs:[],office_sessions:[]};
  for(const office_jobs_truncated of [true,false,undefined])assert.deepEqual(requireOfficeSessions({...snapshot,office_jobs_truncated}),[]);
  for(const office_jobs_truncated of [null,0,1,'false',{},[]])assert.throws(()=>requireOfficeSessions({...snapshot,office_jobs_truncated}));
  assert.throws(()=>requireOfficeSessions({v:1,revision:3,jobs:[],office_jobs_truncated:true,office_sessions:[]}));
});

test('frozen display requires explicit immutability, digest and selected job ownership',()=>{
  assert.doesNotThrow(()=>requireFrozenArtifact(artifact,'job-1'));
  for(const patch of [{immutable:false},{immutable:undefined},{job_id:'other'},{sha256:'not-a-hash'}])assert.throws(()=>requireFrozenArtifact({...artifact,...patch},'job-1'));
});
test('file, text and diff pages are bound to the selected frozen artifact and file',()=>{
  const files={v:1,artifact_id:'manifest-1',candidate_id:'candidate-1',files:[]};
  assert.doesNotThrow(()=>requireFilePage(files,artifact));
  for(const patch of [{artifact_id:'other'},{candidate_id:'other'},{files:Array(101).fill({})}])assert.throws(()=>requireFilePage({...files,...patch},artifact));
  const text={v:1,artifact_id:'manifest-1',file_id:'file-1',sha256:hash,immutable:true,lines:[]};
  assert.doesNotThrow(()=>requireTextPage(text,artifact,file));
  for(const patch of [{file_id:'other'},{sha256:'b'.repeat(64)},{immutable:false},{artifact_id:'other'}])assert.throws(()=>requireTextPage({...text,...patch},artifact,file));
  const diffArtifact={...artifact,id:'diff-1',kind:'diff'};
  const diff={v:1,artifact_id:'diff-1',candidate_id:'candidate-1',rows:[]};
  assert.doesNotThrow(()=>requireDiffPage(diff,diffArtifact,artifact));
  assert.throws(()=>requireDiffPage({...diff,candidate_id:'other'},diffArtifact,artifact));
  assert.throws(()=>requireDiffPage({...diff,artifact_id:'manifest-1'},diffArtifact,artifact));
});
