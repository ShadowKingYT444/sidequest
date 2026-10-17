import test from 'node:test';
import assert from 'node:assert/strict';
import {PROVIDERS,providerReadiness} from '../src/provider-readiness.ts';

const project={id:'project-1',name:'Local repository',status:'active',base_revision:'a'.repeat(40),policy:{allowed_actions:['read_repo','run_checks','propose_patch']}};
const setup=()=>({
  discovery:{v:1,observedAt:'2026-10-14T09:00:00Z',providers:PROVIDERS.map(({id,name})=>({id,name,installed:true,binaryPath:'/usr/local/bin/'+id,version:null,homePath:null,runtime:'local',authentication:'unknown',reachability:'unknown'}))},
  capabilities:{v:1,features:{computer_artifacts:true,coding:true,codex_session:true},worker_model:{id:'verified-model',effort:'high',verified:true},reasons:[],codex:{state:'available',host_enabled:true,catalog_verified:true,usd_cost_enforced:true}},
  snapshot:{v:1,revision:4,stopped:false,mode:'local',projects:[project],jobs:[]},project,
});

test('six installed executables do not imply six connected adapters',()=>{
  assert.equal(PROVIDERS.length,6);
  const input=setup();
  assert.equal(providerReadiness('codex',input).available,true);
  for(const provider of PROVIDERS.filter(item=>item.id!=='codex')){
    const state=providerReadiness(provider.id,input);
    assert.equal(state.installed,true);assert.equal(state.available,false);assert.equal(state.status,'unsupported');
  }
});
test('Codex requires each verified execution, model, USD and repository gate',()=>{
  for(const change of [
    input=>{input.snapshot.stopped=true;},
    input=>{input.snapshot.revision=-1;},
    input=>{input.capabilities.codex.host_enabled=false;},
    input=>{input.capabilities.codex.catalog_verified=false;},
    input=>{input.capabilities.codex.state='unverified';},
    input=>{input.capabilities.codex.usd_cost_enforced=false;},
    input=>{input.capabilities.features.coding=false;},
    input=>{input.capabilities.features.codex_session=false;},
    input=>{input.capabilities.worker_model.verified=false;},
    input=>{input.capabilities.worker_model.id=' ';},
    input=>{input.capabilities.worker_model.effort=' ';},
    input=>{input.project={...project,status:'inactive'};},
    input=>{input.snapshot.projects=[];},
    input=>{input.project={...project,policy:{allowed_actions:['run_checks','propose_patch']}};},
    input=>{input.project={...project,policy:{allowed_actions:['read_repo','propose_patch']}};},
    input=>{input.project={...project,policy:{allowed_actions:['read_repo','run_checks']}};},
  ]){
    const input=setup();change(input);assert.equal(providerReadiness('codex',input).available,false);
  }
});
test('missing, malformed, duplicate and stale local metadata fail closed',()=>{
  assert.equal(providerReadiness('codex',{discovery:null,capabilities:null,snapshot:null}).status,'checking');
  const input=setup();assert.equal(providerReadiness('codex',{...input,failed:true}).available,false);
  for(const patch of [{installed:false},{binaryPath:null},{binaryPath:'codex'},{binaryPath:'/bad\npath'},{binaryPath:'/'+ 'a'.repeat(4096)}]){
    const current=setup();current.discovery.providers[0]={...current.discovery.providers[0],...patch};
    assert.equal(providerReadiness('codex',current).available,false);
  }
  input.discovery.providers.push({...input.discovery.providers[0]});assert.equal(providerReadiness('codex',input).available,false);
});
test('the current restricted host exposes an installed Codex as unavailable',()=>{
  const input=setup();input.capabilities.codex.host_enabled=false;input.capabilities.features.coding=false;input.capabilities.features.codex_session=false;
  input.capabilities.worker_model.verified=false;input.capabilities.codex.catalog_verified=false;input.capabilities.codex.usd_cost_enforced=false;
  const state=providerReadiness('codex',input);assert.equal(state.installed,true);assert.equal(state.available,false);assert.equal(state.label,'Unavailable');
});
