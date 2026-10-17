import {useEffect,useRef,useState} from 'react';
import {bridge} from './bridge';
import {requireOfficeSessions} from './runtime-identity';
import type {RuntimeJob,RuntimeSnapshot} from './types';

const id=(value:unknown):value is string=>typeof value==='string'&&/^[A-Za-z0-9][A-Za-z0-9_.:-]{0,119}$/.test(value);
interface Props {stationId:string;active:boolean;onFiles:(assignment:{jobId:string;projectId:string})=>void;onCount:(count:number)=>void;onBrowse:()=>void;onProvider:()=>void}
export default function SessionCard({stationId,active,onFiles,onCount,onBrowse,onProvider}:Props){
  const [state,setState]=useState<RuntimeSnapshot|null>(null),[job,setJob]=useState<RuntimeJob|null>(null),[jobId,setJobId]=useState(''),[runId,setRunId]=useState(''),[error,setError]=useState(''),[busy,setBusy]=useState(false),[revision,setRevision]=useState(0);
  const generation=useRef(0),mounted=useRef(false),locked=useRef(false);
  const owner=state?.office_sessions?.find(row=>row.station_id===stationId);
  useEffect(()=>{mounted.current=true;return()=>{mounted.current=false;generation.current++;};},[]);
  useEffect(()=>{
    if(!active)return;
    const request=++generation.current;setBusy(true);setError('');
    bridge.runtime.snapshot().then(snapshot=>{
      const owners=requireOfficeSessions(snapshot);if(request!==generation.current||!mounted.current)return;
      setState(snapshot);onCount(owners.length);const assigned=owners.find(row=>row.station_id===stationId);
      setJobId(previous=>assigned?.job_id??(snapshot.jobs.some(job=>job.id===previous)?previous:snapshot.jobs.find(job=>job.run_ids?.length)?.id??''));
    }).catch(reason=>{if(request===generation.current&&mounted.current)setError(reason instanceof Error?reason.message:'Session state is unavailable.');}).finally(()=>{if(request===generation.current&&mounted.current)setBusy(false);});
    return()=>{generation.current++;};
  },[stationId,active,revision,onCount]);
  useEffect(()=>{
    let alive=true;setJob(null);if(!jobId)return;
    bridge.runtime.job(jobId).then(reply=>{
      if(reply.v!==1||reply.job?.id!==jobId||!id(reply.job.project_id)||!Array.isArray(reply.job.run_ids)||reply.job.run_ids.length>100||!reply.job.run_ids.every(id)||typeof reply.job.title!=='string'||reply.job.title.length>200)throw new Error('Recorded task identity is unavailable.');
      if(owner&&(reply.job.project_id!==owner.project_id||!reply.job.run_ids.includes(owner.run_id)))throw new Error('The assigned session no longer matches this task.');
      if(alive){setJob(reply.job);setRunId(previous=>owner?.run_id??(reply.job.run_ids?.includes(previous)?previous:reply.job.run_ids?.at(-1)??''));}
    }).catch(reason=>{if(alive)setError(reason instanceof Error?reason.message:'Recorded task is unavailable.');});
    return()=>{alive=false;};
  },[jobId,owner?.run_id,owner?.project_id,revision]);
  const change=async(clear:boolean)=>{
    if(locked.current||!active)return;locked.current=true;setBusy(true);setError('');
    try{
      const fresh=await bridge.runtime.snapshot();requireOfficeSessions(fresh);
      const reply=clear?await bridge.runtime.clearSession(stationId,fresh.revision):await bridge.runtime.assignSession(stationId,jobId,runId,fresh.revision);
      if(reply.v!==1||reply.accepted!==true||!id(reply.command_id)||!Number.isSafeInteger(reply.revision))throw new Error('Assignment outcome is unconfirmed. Refresh session state before retrying.');
      if(mounted.current)setRevision(value=>value+1);
    }catch(reason){if(mounted.current)setError(reason instanceof Error?reason.message:'The recorded assignment could not be changed.');}
    finally{locked.current=false;if(mounted.current)setBusy(false);}
  };
  return <div className="session-records" data-session-run={owner?.run_id??''}>
    {state?.mode==='fixture'&&<p className="session-note">Test fixture session state</p>}
    {busy&&!state&&<p role="status">Reading session state…</p>}
    {error&&<p role="alert" className="session-error">{error}</p>}
    <p className="session-status">{owner?(job?.execution_profile==='local_git_inspection'?'Recorded local inspection':'Recorded session'):'No live session attached'}</p>
    {owner&&<><h3 className="session-task-title">{job?.title??'Reading task…'}</h3><p className="session-compact-state">{job?.state==='verifying'?'Checking':job?.state.replaceAll('_',' ')??'State unavailable'}</p><div className="object-actions"><button onClick={onBrowse}>Open monitor</button><button disabled={!job} onClick={()=>onFiles({jobId:owner.job_id,projectId:owner.project_id})}>Open results</button></div><details className="session-ownership"><summary>Session details</summary><p className="session-note">Recorded display ownership · original staged figure</p><p className="session-note">Run {owner.run_id}<br/>Worker {owner.worker_id}</p><button disabled={busy||!active} onClick={()=>void change(true)}>Detach session</button></details></>}
    {!owner&&<details className="session-assign"><summary>Attach recorded session</summary><p className="session-note">Assign an existing run to this figure. This does not start or move worker execution.</p><label>Recorded task<select value={jobId} disabled={busy||!active} onChange={event=>{setError('');setJobId(event.target.value);}}><option value="">Choose a task</option>{state?.jobs.filter(job=>job.run_ids?.length).map(job=><option key={job.id} value={job.id}>{job.title}</option>)}</select></label><label>Recorded run<select value={runId} disabled={busy||!job||!active} onChange={event=>setRunId(event.target.value)}><option value="">Choose a run</option>{job?.run_ids?.map((run,index)=><option key={run} value={run}>Run {index+1} · {run.slice(0,8)}</option>)}</select></label><button disabled={busy||!!error||!job||!runId||!active} onClick={()=>void change(false)}>Assign session</button></details>}
    {!owner&&<div className="object-actions"><button onClick={onBrowse}>Open monitor</button><button onClick={onProvider}>Choose provider</button></div>}
    <button className="session-read-refresh" disabled={busy||!active} onClick={()=>setRevision(value=>value+1)}>Refresh session</button>
  </div>;
}
