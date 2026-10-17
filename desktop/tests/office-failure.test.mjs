import test from 'node:test';
import assert from 'node:assert/strict';
import {describeOfficeFailure} from '../src/office-failure.ts';

test('WebGL creation and blocklist errors are graphics failures, not missing assets',()=>{
  for(const message of ['WebGL2 blocklisted','Error creating WebGL context.','Failed to create a WebGL2 rendering context','GPU unavailable']){
    const result=describeOfficeFailure(new Error(message));
    assert.equal(result.kind,'graphics');
    assert.equal(result.title,'3D graphics unavailable');
  }
});

test('loader failures retain their source and unknown rendering errors do not accuse assets',()=>{
  assert.equal(describeOfficeFailure(new Error('503'),'bindings').kind,'bindings');
  assert.equal(describeOfficeFailure(new Error('invalid JSON'),'bindings').kind,'bindings');
  assert.equal(describeOfficeFailure(new Error('model unavailable'),'assets').kind,'assets');
  assert.equal(describeOfficeFailure(new Error('Unexpected scene failure')).kind,'scene');
  assert.equal(describeOfficeFailure(null).kind,'scene');
});

test('user-facing diagnoses do not expose raw error paths or markup',()=>{
  const privateError=new Error('/private/example?token=private <img onerror=alert(1)>');
  for(const phase of ['bindings','assets','scene'])assert.doesNotMatch(JSON.stringify(describeOfficeFailure(privateError,phase)),/private|token|onerror/);
});
