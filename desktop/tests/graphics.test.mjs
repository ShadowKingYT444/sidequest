import test from 'node:test';
import assert from 'node:assert/strict';
import {isSoftwareRenderer} from '../src/graphics.ts';

function context(renderer, extension = true) {
  return {RENDERER:1, getExtension:()=>extension?{UNMASKED_RENDERER_WEBGL:2}:null, getParameter:()=>renderer};
}

test('known software renderers skip expensive camera animation without changing the scene',()=>{
  for(const renderer of ['ANGLE (Google, Vulkan 1.3.0 (SwiftShader Device (Subzero)), SwiftShader driver)', 'llvmpipe (LLVM 15.0.6, 256 bits)', 'softpipe', 'Microsoft Basic Render Driver']) {
    assert.equal(isSoftwareRenderer(context(renderer)),true,renderer);
  }
});

test('hardware and unknown renderer metadata keep camera animation available',()=>{
  for(const renderer of ['ANGLE (NVIDIA GeForce RTX 4070)', 'Apple M2', 'AMD Radeon RX 6800', 'WebKit WebGL', null]) {
    assert.equal(isSoftwareRenderer(context(renderer)),false);
  }
  assert.equal(isSoftwareRenderer(context('WebKit WebGL',false)),false);
  assert.equal(isSoftwareRenderer({getExtension(){throw new Error('unavailable context');}}),false);
});
