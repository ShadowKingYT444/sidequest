'use strict';
const { randomUUID } = require('node:crypto');
const path = require('node:path');
const fs = require('node:fs');
const ID = /^[A-Za-z0-9][A-Za-z0-9_.:-]{0,119}$/;
function opaque(value) {
  if (typeof value !== 'string' || !ID.test(value) || value === '.' || value === '..') throw new Error('Invalid object identifier.');
  return encodeURIComponent(value);
}
function revision(value) { if (!Number.isSafeInteger(value) || value < 0) throw new Error('Invalid revision.'); return value; }
function station(value) {if(typeof value!=='string'||!/^parent_(?:00[1-9]|01[0-9]|02[0-4])$/.test(value))throw new Error('Invalid office station.');return value;}
function createRuntimeClient({ url, token, tokenFile, repo, baseRef = 'HEAD' } = {}) {
  let origin;
  if (url) {
    const parsed = new URL(url);
    if (parsed.protocol !== 'http:' || !['127.0.0.1','[::1]'].includes(parsed.hostname) || parsed.username || parsed.password || parsed.pathname !== '/' || parsed.search || parsed.hash) throw new Error('Runtime must use a literal loopback HTTP origin.');
    origin = parsed.origin;
  }
  if (!token && tokenFile) {
    const fd = fs.openSync(tokenFile, fs.constants.O_RDONLY | fs.constants.O_NOFOLLOW);
    try { const info = fs.fstatSync(fd); if (!info.isFile() || info.size > 512 || info.nlink !== 1 || (info.mode & 0o077)) throw new Error('Invalid local session file.'); token = fs.readFileSync(fd, 'utf8').trim(); } finally { fs.closeSync(fd); }
  }
  if (token && (typeof token !== 'string' || token.length > 512 || /[\r\n]/.test(token))) throw new Error('Invalid local session configuration.');
  async function request(route, body) {
    if (!origin || !token) throw new Error('Local runtime is not configured.');
    const response = await fetch(origin + route, { method:body ? 'POST':'GET',
      headers:{Authorization:`Bearer ${token}`,Accept:'application/json',...(body ? {'Content-Type':'application/json'}:{})},
      body:body ? JSON.stringify(body):undefined, redirect:'error', signal:AbortSignal.timeout(10_000) });
    const declared = Number(response.headers.get('content-length'));
    if (declared > 1024*1024) { await response.body?.cancel(); throw new Error('Runtime response exceeds the read limit.'); }
    const reader = response.body?.getReader(); const parts=[]; let length=0;
    if (reader) for (;;) { const {value,done}=await reader.read();if(done)break;length+=value.length;if(length>1024*1024){await reader.cancel();throw new Error('Runtime response exceeds the read limit.');}parts.push(value); }
    const text=Buffer.concat(parts.map(part=>Buffer.from(part))).toString('utf8');
    if (!response.ok) {
      let code='UNAVAILABLE';try { const value=JSON.parse(text);if(typeof value.error?.code==='string' && /^[A-Z_]+$/.test(value.error.code))code=value.error.code; }catch{}
      throw Object.assign(new Error(`Local runtime request failed (${response.status}, ${code}).`),{code,status:response.status});
    }
    return JSON.parse(text);
  }
  const command = (type,payload,expectedRevision) => request('/v1/commands',{v:1,command_id:randomUUID(),type,expected_revision:revision(expectedRevision),payload});
  async function inspectionOnly() {
    const capabilities = await request('/v1/capabilities');
    if (capabilities.features?.local_git_inspection !== true) throw new Error('This runtime does not support the safe local inspection profile.');
  }
  async function codingReady() {
    const capabilities=await request('/v1/capabilities');
    if(capabilities.features?.coding!==true||capabilities.features?.codex_session!==true||capabilities.worker_model?.verified!==true||capabilities.codex?.usd_cost_enforced!==true)throw new Error('Coding execution requires fresh host readiness, consent and an enforced USD ceiling.');
  }
  return Object.freeze({
    snapshot:()=>request('/v1/snapshot'), capabilities:()=>request('/v1/capabilities'),
    job:id=>request(`/v1/jobs/${opaque(id)}`),
    runInfo:id=>request(`/v1/runs/${opaque(id)}`),
    runEvents:(id,afterSeq=0)=>{revision(afterSeq);return request(`/v1/runs/${opaque(id)}/events?after_seq=${afterSeq}&limit=200`);},
    assignSession:async(stationId,jobId,runId,expectedRevision)=>{
      station(stationId);opaque(jobId);opaque(runId);revision(expectedRevision);
      const [job,run]=await Promise.all([request(`/v1/jobs/${opaque(jobId)}`),request(`/v1/runs/${opaque(runId)}`)]);
      if(job.v!==1||job.job?.id!==jobId||!job.job.run_ids?.includes(runId)||run.v!==1||run.run?.id!==runId||run.run.job_id!==jobId||typeof run.run.worker_id!=='string'||!ID.test(run.run.worker_id))throw new Error('Recorded session ownership is unavailable.');
      return command('office.assign_session',{station_id:stationId,job_id:jobId,run_id:runId},expectedRevision);
    },
    clearSession:(stationId,expectedRevision)=>command('office.clear_session',{station_id:station(stationId)},expectedRevision),
    artifact:id=>request(`/v1/artifacts/${opaque(id)}`),
    artifacts:(id,cursor='')=>{
      if(typeof cursor!=='string'||cursor.length>2048)throw new Error('Invalid artifact cursor.');
      return request(`/v1/jobs/${opaque(id)}/artifacts?limit=100&cursor=${encodeURIComponent(cursor)}`);
    },
    files:(id,cursor='')=>{
      if(typeof cursor!=='string'||cursor.length>2048)throw new Error('Invalid file cursor.');
      return request(`/v1/artifacts/${opaque(id)}/files?limit=100&cursor=${encodeURIComponent(cursor)}`);
    },
    text:(artifact,file,startLine=1)=>{
      if(!Number.isSafeInteger(startLine)||startLine<1)throw new Error('Invalid text page.');
      return request(`/v1/artifacts/${opaque(artifact)}/text?file_id=${opaque(file)}&start_line=${startLine}&limit=200`);
    },
    diff:(artifact,file,cursor='')=>{
      if(typeof cursor!=='string'||cursor.length>2048)throw new Error('Invalid diff cursor.');
      return request(`/v1/artifacts/${opaque(artifact)}/diff?file_id=${opaque(file)}&cursor=${encodeURIComponent(cursor)}&limit=200`);
    },
    register:expectedRevision=>{
      if(!repo || !path.isAbsolute(repo)) throw new Error('A host repository must be configured.');
      return command('project.register',{name:path.basename(repo),repo_path:repo,base_ref:baseRef,policy:{allowed_actions:['read_repo','run_checks']}},expectedRevision);
    },
    refreshReadiness:expectedRevision=>command('system.codex.refresh',{},expectedRevision),
    enableCoding:async(projectId,expectedRevision)=>{opaque(projectId);revision(expectedRevision);await codingReady();return command('project.enable_coding',{project_id:projectId},expectedRevision);},
    submitCoding:async(projectId,title,objective,writePrefix,budget,expectedRevision)=>{
      opaque(projectId);revision(expectedRevision);
      if(typeof title!=='string'||!title.trim()||title.length>200||/[\u0000-\u001f]/.test(title))throw new Error('Coding title must contain 1–200 readable characters.');
      if(typeof objective!=='string'||!objective.trim()||objective.length>2000||/[\u0000-\u0008\u000b\u000c\u000e-\u001f]/.test(objective))throw new Error('Coding objective must contain 1–2000 readable characters.');
      if(typeof writePrefix!=='string'||writePrefix.length>240||!writePrefix.split('/').every(part=>/^[A-Za-z0-9_][A-Za-z0-9_.-]*$/.test(part))||writePrefix.split('/').some(part=>['.git','.codex'].includes(part)))throw new Error('Choose a safe relative write prefix.');
      if(typeof budget!=='string'||!/^\d{1,6}(?:\.\d{1,6})?$/.test(budget)||Number(budget)<=0)throw new Error('Choose a positive USD budget with at most six decimal places.');
      await codingReady();
      return command('job.create',{project_id:projectId,title,source:{kind:'typed',uri:'sidequest:manual-coding',text:objective},checks:['candidate.frozen_identity'],allowed_actions:['read_repo','propose_patch','run_checks'],budget_usd:budget,plan:{tasks:[{id:'coding',objective,depends_on:[],write_paths:[writePrefix],check_ids:['candidate.frozen_identity']}]}},expectedRevision);
    },
    runCoding:async(jobId,expectedRevision)=>{
      const id=decodeURIComponent(opaque(jobId));revision(expectedRevision);await codingReady();
      const result=await request(`/v1/jobs/${opaque(jobId)}`);
      if(result.job?.id!==id||result.job.execution_profile!=='codex_session'||result.job.state!=='queued'||!(result.job.budget_usd>0))throw new Error('This job is not a queued host-verified coding task.');
      return command('job.run',{job_id:id},expectedRevision);
    },
    submitInspection:async(projectId,title,expectedRevision)=>{
      opaque(projectId);
      revision(expectedRevision);
      if(typeof title!=='string'||title.trim().length<1||title.length>200||/[\u0000-\u001f]/.test(title))throw new Error('Inspection title must contain 1–200 readable characters.');
      await inspectionOnly();
      return command('job.create',{project_id:projectId,title,source:{kind:'typed',uri:'sidequest:local-git-inspection',text:'Inspect the registered Git repository and produce immutable read-only artifacts with a frozen-identity check. No coding model, source mutation or delivery.'},checks:['candidate.frozen_identity'],allowed_actions:['read_repo','run_checks'],budget_usd:0},expectedRevision);
    },
    run:async(jobId,expectedRevision)=>{
      const id=decodeURIComponent(opaque(jobId)); revision(expectedRevision); await inspectionOnly();
      const result=await request(`/v1/jobs/${opaque(jobId)}`);
      if(result.job?.id!==id||result.job.execution_profile!=='local_git_inspection'||result.job.state!=='queued'||result.job.budget_usd!==0)throw new Error('This job is not a queued zero-budget local inspection.');
      return command('job.run',{job_id:id},expectedRevision);
    },
    stop:expectedRevision=>command('system.stop',{},expectedRevision),
  });
}
const METHOD_ARITY = Object.freeze({snapshot:[0,0],capabilities:[0,0],job:[1,1],runInfo:[1,1],runEvents:[1,2],assignSession:[4,4],clearSession:[2,2],artifact:[1,1],artifacts:[1,2],files:[1,2],text:[2,3],diff:[2,3],register:[1,1],submitInspection:[3,3],run:[2,2],stop:[1,1],refreshReadiness:[1,1],enableCoding:[2,2],submitCoding:[6,6],runCoding:[2,2]});
async function dispatchRuntime(client,method,args) {
  const arity = typeof method === 'string' && Object.hasOwn(METHOD_ARITY,method) && METHOD_ARITY[method];
  if (!arity || !Array.isArray(args) || args.length < arity[0] || args.length > arity[1] || args.some(value => !['string','number'].includes(typeof value))) throw new Error('Invalid local runtime request.');
  if (JSON.stringify(args).length > 4096) throw new Error('Local runtime request exceeds the input limit.');
  return client[method](...args);
}
module.exports = {createRuntimeClient,dispatchRuntime,METHOD_ARITY};
