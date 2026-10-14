import {useEffect, useLayoutEffect, useRef, useState} from 'react';
import {bridge} from './bridge';
import {requireEvents, requireRun} from './RunActivity';
import PromptComposer from './PromptComposer';
import type {LocalDraft} from './local-drafts';
import type {OfficeSession, RunEventPage, RuntimeJob, RuntimeRun} from './types';
import './MonitorSession.css';

interface RecordedRead {job:RuntimeJob;run:RuntimeRun;page:RunEventPage}
export interface MonitorMemory {afterSeq:number;previous:number[];scrollTop:number;read?:RecordedRead;error?:string}
interface Props {owner?:OfficeSession;known:boolean;fixture:boolean;active:boolean;draft:LocalDraft;onDraft:(draft:LocalDraft)=>void;getDraft:()=>LocalDraft;operations:{pending:Promise<void>};memory:MonitorMemory;onProvider:()=>void;onAttach:()=>void}
const identity=(value:unknown):value is string=>typeof value==='string'&&/^[A-Za-z0-9][A-Za-z0-9_.:-]{0,119}$/.test(value);
export default function MonitorSession({owner,known,fixture,active,draft,onDraft,getDraft,operations,memory,onProvider,onAttach}:Props){
  const [read,setRead]=useState(memory.read),[error,setError]=useState(memory.error??''),[loading,setLoading]=useState(false),[refresh,setRefresh]=useState(0);
  const [afterSeq,setAfterSeq]=useState(memory.afterSeq);
  const body=useRef<HTMLDivElement>(null),generation=useRef(0),restored=useRef(false);
  const geometry=useRef({height:0,content:0});
  const ownerKey=owner?JSON.stringify([owner.job_id,owner.project_id,owner.run_id,owner.worker_id]):'';
  useEffect(()=>{
    if(!owner||!active)return;
    let alive=true,timer:ReturnType<typeof setTimeout>|undefined;const request=++generation.current;
    async function load(){
      setLoading(true);setError('');let poll=true;
      try{
        const [jobReply,runReply,eventReply]=await Promise.all([bridge.runtime.job(owner!.job_id),bridge.runtime.runInfo(owner!.run_id),bridge.runtime.runEvents(owner!.run_id,afterSeq)]);
        const job=jobReply.job;
        if(jobReply.v!==1||!job||job.id!==owner!.job_id||job.project_id!==owner!.project_id||!identity(job.id)||typeof job.title!=='string'||job.title.length>200||!Array.isArray(job.run_ids)||job.run_ids.length>100||!job.run_ids.includes(owner!.run_id))throw new Error('Recorded task identity changed.');
        const run=requireRun(runReply,job,owner!.run_id);
        if(run.worker_id!==owner!.worker_id)throw new Error('Recorded session worker identity changed.');
        const page=requireEvents(eventReply,run,afterSeq);
        if(!alive||request!==generation.current)return;
        const next={job,run,page};memory.read=next;memory.error='';setRead(next);setLoading(false);poll=run.state==='running'&&run.ended_at===null;
      }catch(reason){if(!alive||request!==generation.current)return;const message=reason instanceof Error?reason.message:'Recorded trace unavailable.';memory.error=message;setError(message);setLoading(false);}
      if(alive&&request===generation.current&&poll)timer=setTimeout(()=>void load(),5000);
    }
    void load();return()=>{alive=false;generation.current++;clearTimeout(timer);};
  },[ownerKey,active,afterSeq,refresh,memory]);
  useLayoutEffect(()=>{
    const node=body.current;if(!node)return;
    const restore=()=>{geometry.current={height:node.clientHeight,content:node.scrollHeight};node.scrollTop=Math.min(memory.scrollTop,Math.max(0,node.scrollHeight-node.clientHeight));node.dataset.scrollTop=String(node.scrollTop);node.dataset.desiredScrollTop=String(memory.scrollTop);};
    if(read&&!restored.current){restore();restored.current=true;}
    const resize=new ResizeObserver(restore);resize.observe(node);return()=>resize.disconnect();
  },[read,memory]);
  const page=(next:number)=>{if(body.current)memory.scrollTop=0;memory.afterSeq=next;memory.read=undefined;restored.current=false;setRead(undefined);setAfterSeq(next);};
  const state=read?.job.state==='verifying'?'Checking':read&&['failed','blocked','needs_approval','paused','cancelled'].includes(read.job.state)?read.job.state.replaceAll('_',' '):read?.run.state?.replaceAll('_',' ')??'Recorded session';
  const local=read?.job.execution_profile==='local_git_inspection';
  return <section className="monitor-session" aria-label="Session execution trace" data-session-run={owner?.run_id??''}>
    <div className="monitor-trace-toolbar"><span>{fixture?'Test fixture · ':''}{owner?(local?'Local Git inspection':'Recorded session'):'Session'}{owner&&<> <span aria-hidden="true">·</span> <strong>{state}</strong></>}</span>{owner&&<button disabled={!active||loading} onClick={()=>setRefresh(value=>value+1)} aria-label="Refresh trace" title="Refresh trace">↻</button>}</div>
    <div ref={body} className="monitor-trace-body" tabIndex={0} aria-label="Recorded output" data-scroll-top={memory.scrollTop} onScroll={event=>{const node=event.currentTarget;const changed=geometry.current.height!==node.clientHeight||geometry.current.content!==node.scrollHeight;const expected=Math.min(memory.scrollTop,Math.max(0,node.scrollHeight-node.clientHeight));if(!changed&&Math.abs(node.scrollTop-expected)>.5)memory.scrollTop=node.scrollTop;geometry.current={height:node.clientHeight,content:node.scrollHeight};node.dataset.scrollTop=String(node.scrollTop);node.dataset.desiredScrollTop=String(memory.scrollTop);}}>
      {!known?<p className="monitor-empty" role="status">Reading session ownership…</p>:!owner?<div className="monitor-empty"><h3>No recorded session</h3><p>This computer has no attached run.</p><div><button onClick={onAttach}>Attach a recorded session</button><button onClick={onProvider}>Choose provider</button></div></div>:<>
        {read&&<><h3 className="monitor-task-title">{read.job.title}</h3><details className="monitor-record-details"><summary>Run details</summary><p>{local?'Local inspection. No model call.':'Recorded output; provider connectivity is not established by this view.'}</p><p>Recorded usage: {read.run.usage.total_tokens===null?'tokens unknown':`${read.run.usage.total_tokens} tokens`} · {read.run.usage.cost_usd===null?'cost unknown':`$${read.run.usage.cost_usd}`}</p><p>Run {read.run.id} · Worker {read.run.worker_id}</p>{typeof (read.job as RuntimeJob&{source?:{text?:string}}).source?.text==='string'&&<pre>{(read.job as RuntimeJob&{source:{text:string}}).source.text.slice(0,2000)}</pre>}</details></>}
        {loading&&!read&&<p role="status">Reading recorded output…</p>}
        {error&&<p className="monitor-read-error" role="alert">{error}{read?' Showing the last validated read.':''}</p>}
        {read&&<ol className="monitor-events">{read.page.items.map(event=><li key={event.seq} data-event-seq={event.seq} data-event-type={event.type}><span className="monitor-event-mark" aria-hidden="true">{event.type==='warning'?'!':event.type==='tool_finished'?'✓':event.type==='output'?'›':'·'}</span><pre>{event.message}</pre></li>)}</ol>}
        {read&&!read.page.items.length&&<p className="monitor-empty">No output recorded on this page.</p>}
        {read&&(memory.previous.length>0||read.page.has_more)&&<div className="monitor-page"><button disabled={!memory.previous.length||loading} onClick={()=>page(memory.previous.pop()??0)}>Previous events</button><button disabled={!read.page.has_more||loading} onClick={()=>{memory.previous.push(afterSeq);page(read.page.next_after_seq);}}>More events</button></div>}
      </>}
    </div>
    <PromptComposer draft={draft} onChange={onDraft} getCurrentDraft={getDraft} operations={operations} canSubmit={false} label="Message this session" disabledReason="Sending is unavailable. The current runtime has no session message or attachment transport, and this host has not passed the native dispatch gates."/>
  </section>;
}
