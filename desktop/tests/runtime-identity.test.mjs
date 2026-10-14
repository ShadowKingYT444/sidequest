import test from 'node:test';
import assert from 'node:assert/strict';
import {requireFrozenArtifact,requireFilePage,requireTextPage,requireDiffPage} from '../src/runtime-identity.ts';
const hash='a'.repeat(64);
const artifact={id:'manifest-1',job_id:'job-1',kind:'file_manifest',candidate_id:'candidate-1',sha256:hash,immutable:true};
const file={file_id:'file-1',sha256:hash};

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
