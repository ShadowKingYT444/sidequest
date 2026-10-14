import { useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react';
import RunActivity from './RunActivity';
import { bridge } from './bridge';
import type { CommandReply, DiffPage, FilePage, JobView, RuntimeArtifact, RuntimeCapabilities, RuntimeSnapshot, StationAssignment, TextPage } from './types';
import {requireDiffPage,requireFilePage,requireFrozenArtifact,requireTextPage} from './runtime-identity';

const safeStates = new Set(['queued','running','verifying','needs_approval','accepted','blocked','failed','paused','cancelled']);
const stateLabel = (value:string) => safeStates.has(value) ? value.replaceAll('_',' ') : 'unavailable';
function readablePreview(value:string|null) {
  if(value===null)return 'This artifact has no text preview.';
  try {const formatted=JSON.stringify(JSON.parse(value),null,2);return formatted.length<=256*1024?formatted:value;}catch{return value;}
}
interface Props {onClose:()=>void;active:boolean;open:boolean;embedded?:boolean;onExpand?:()=>void;requestedJob?:StationAssignment&{requestId?:number};stations?:{id:string;label:string}[];onAssign?:(station:string,assignment:StationAssignment)=>void;viewMemory?:{current:Map<string,JobView>}}
function copyView(view:JobView|undefined):JobView|undefined{return view?{...view,artifactCursors:[...(view.artifactCursors??[''])],fileCursors:[...(view.fileCursors??[''])],diffCursors:[...(view.diffCursors??[''])]}:undefined;}
export default function JobsBoard({onClose,active,open,embedded=false,onExpand,requestedJob,stations=[],onAssign,viewMemory}:Props) {
  const initialView=useRef(requestedJob?copyView(viewMemory?.current.get(requestedJob.jobId)):undefined).current;
  const pendingRestore=useRef(initialView?{jobId:requestedJob!.jobId,view:initialView}:null);
  const [snapshot,setSnapshot]=useState<RuntimeSnapshot|null>(null);
  const [caps,setCaps]=useState<RuntimeCapabilities|null>(null);
  const [error,setError]=useState('');
  const [connectionError,setConnectionError]=useState('');
  const [busy,setBusy]=useState(false);
  const [notice,setNotice]=useState('');
  const [activityOpen,setActivityOpen]=useState(false);
  const [title,setTitle]=useState('Inspect current repository');
  const [jobKind,setJobKind]=useState<'inspection'|'coding'>('inspection');
  const [objective,setObjective]=useState('');
  const [writePrefix,setWritePrefix]=useState('src');
  const [budget,setBudget]=useState('0.01');
  const [displayStation,setDisplayStation]=useState(stations[0]?.id??'');
  const [projectId,setProjectId]=useState('');
  const [jobId,setJobId]=useState(requestedJob?.jobId??'');
  const [artifacts,setArtifacts]=useState<RuntimeArtifact[]>([]);
  const [artifactId,setArtifactId]=useState(initialView?.artifactId??'');
  const [artifactCursors,setArtifactCursors]=useState<string[]>(initialView?.artifactCursors??['']);
  const [artifactPage,setArtifactPage]=useState(initialView?.artifactPage??0);
  const [nextArtifact,setNextArtifact]=useState<string|null>(null);
  const [files,setFiles]=useState<FilePage|null>(null);
  const [fileId,setFileId]=useState(initialView?.fileId??'');
  const [fileCursors,setFileCursors]=useState<string[]>(initialView?.fileCursors??['']);
  const [filePage,setFilePage]=useState(initialView?.filePage??0);
  const [tab,setTab]=useState<'text'|'diff'>(initialView?.tab??'text');
  const [text,setText]=useState<TextPage|null>(null);
  const [diff,setDiff]=useState<DiffPage|null>(null);
  const [preview,setPreview]=useState<string|null>(null);
  const [contentError,setContentError]=useState('');
  const [startLine,setStartLine]=useState(initialView?.startLine??1);
  const [diffCursors,setDiffCursors]=useState<string[]>(initialView?.diffCursors??['']);
  const [diffPage,setDiffPage]=useState(initialView?.diffPage??0);
  const [loadedContentKey,setLoadedContentKey]=useState('');
  const previousJob=useRef(jobId);
  const previousArtifact=useRef(artifactId);
  const previousFile=useRef(fileId);
  const request = useRef(0);
  const snapshotRequest=useRef(0);
  const root = useRef<HTMLDivElement>(null);
  const openedOnce=useRef(false);
  const requested=useRef(requestedJob);requested.current=requestedJob;
  const appliedRequest=useRef('');
  const connectionLost=useRef(false);
  const [readEpoch,setReadEpoch]=useState(0);
  const job=snapshot?.jobs.find(item=>item.id===jobId);
  const project=snapshot?.projects.find(item=>item.id===projectId);
  const artifact=artifacts.find(item=>item.id===artifactId);
  const manifest=artifact?.kind==='file_manifest';
  const diffArtifact=artifacts.find(item=>item.kind==='diff'&&!!artifact?.candidate_id&&item.candidate_id===artifact.candidate_id);
  const contentKey=JSON.stringify(manifest?[jobId,artifactId,artifactPage,artifactCursors[artifactPage]??'',fileId,filePage,fileCursors[filePage]??'',tab,startLine,diffPage,diffCursors[diffPage]??'']:[jobId,artifactId,artifactPage,artifactCursors[artifactPage]??'']);
  const localInspection=caps?.features.local_git_inspection===true;
  const connected=!!snapshot&&!connectionError;
  const codingReady=caps?.features.coding===true&&caps.features.codex_session===true&&caps.worker_model.verified===true&&caps.codex?.usd_cost_enforced===true;
  const codingPolicy=project?.policy?.allowed_actions.includes('propose_patch')===true;
  const resultsReady=job?.execution_profile==='local_git_inspection'&&job.tasks?.length&&job.tasks.every(task=>task.state==='completed')&&job.checks.length>0&&job.checks.every(check=>check.state==='pass');
  const refresh=useCallback(async()=>{
    const generation=++snapshotRequest.current;
    try {
      const [state,capabilities]=await Promise.all([bridge.runtime.snapshot(),bridge.runtime.capabilities()]);
      const target=requested.current;
      if(target&&!state.jobs.some(item=>item.id===target.jobId)){
        try {const result=await bridge.runtime.job(target.jobId);if(result.job.id===target.jobId&&result.job.project_id===target.projectId)state.jobs.push(result.job);}catch{/* An unavailable assignment remains unavailable. */}
      }
      if(generation!==snapshotRequest.current)return;
      setSnapshot(state);setCaps(capabilities);setConnectionError('');
      if(connectionLost.current){connectionLost.current=false;setReadEpoch(value=>value+1);}
      setProjectId(previous=>state.projects.some(item=>item.id===previous)?previous:state.projects[0]?.id??'');
      setJobId(previous=>{
        const key=target?`${target.jobId}:${target.projectId}:${target.requestId??0}`:'';
        if(target&&(embedded||appliedRequest.current!==key)){appliedRequest.current=key;return state.jobs.find(item=>item.id===target.jobId&&item.project_id===target.projectId)?.id??'';}
        return state.jobs.some(item=>item.id===previous)?previous:state.jobs[0]?.id??'';
      });
    } catch (reason) {if(generation===snapshotRequest.current){connectionLost.current=true;setCaps(null);setNotice('');setConnectionError(reason instanceof Error?reason.message:'Local runtime is unavailable.');}}
  },[embedded]);
  useEffect(()=>{void refresh();},[refresh]);
  useEffect(()=>{if(requestedJob)void refresh();},[requestedJob?.jobId,requestedJob?.requestId,refresh]);
  useEffect(()=>{setNotice('');setError('');},[jobId,job?.state]);
  useEffect(()=>{
    if(previousJob.current===jobId)return;
    previousJob.current=jobId;
    const saved=copyView(viewMemory?.current.get(jobId));pendingRestore.current=saved?{jobId,view:saved}:null;
    setArtifactId(saved?.artifactId??'');setFileId(saved?.fileId??'');setTab(saved?.tab??'text');setStartLine(saved?.startLine??1);
    setArtifactCursors(saved?.artifactCursors??['']);setArtifactPage(saved?.artifactPage??0);
    setFileCursors(saved?.fileCursors??['']);setFilePage(saved?.filePage??0);
    setDiffCursors(saved?.diffCursors??['']);setDiffPage(saved?.diffPage??0);
    setFiles(null);setPreview(null);setText(null);setDiff(null);setLoadedContentKey('');
  },[jobId,viewMemory]);
  useEffect(()=>{
    if(!active||!open)return;
    const timer=setInterval(()=>{void refresh();},1500);
    return()=>clearInterval(timer);
  },[refresh,active,open]);
  useEffect(()=>{
    if(!open){if(!embedded)openedOnce.current=false;return;}
    const close=(event:KeyboardEvent)=>{if(event.key==='Escape'){event.preventDefault();onClose();}};
    document.addEventListener('keydown',close);if(!openedOnce.current){openedOnce.current=true;root.current?.querySelector<HTMLButtonElement>('button')?.focus();}
    return()=>document.removeEventListener('keydown',close);
  },[onClose,open,embedded]);
  async function mutate(action:()=>Promise<CommandReply>,message:string) {
    setBusy(true);setError('');setNotice('');
    try {const reply=await action();if(reply.result?.job_id)setJobId(reply.result.job_id);if(reply.result?.project_id)setProjectId(reply.result.project_id);setNotice(message);await refresh();}
    catch(reason){setError(reason instanceof Error?reason.message:'Command was not accepted. Refresh state before trying again.');}
    finally{setBusy(false);}
  }
  useEffect(()=>{
    let alive=true;setArtifacts([]);setContentError('');
    if(jobId)bridge.runtime.artifacts(jobId,artifactCursors[artifactPage]??'').then(result=>{if(alive){result.items.forEach(item=>requireFrozenArtifact(item,jobId));setArtifacts(result.items);setNextArtifact(result.next_cursor);setArtifactId(previous=>result.items.some(item=>item.id===previous)?previous:result.items.find(item=>item.id===pendingRestore.current?.view.artifactId)?.id??result.items.find(item=>item.kind==='file_manifest')?.id??result.items[0]?.id??'');}}).catch(()=>{if(alive)setContentError('Frozen artifact metadata is unavailable.');});
    return()=>{alive=false;};
  },[jobId,job?.artifact_ids.join(','),job?.events.length,artifactPage,artifactCursors,readEpoch]);
  useEffect(()=>{
    if(previousArtifact.current===artifactId)return;previousArtifact.current=artifactId;
    if(pendingRestore.current?.jobId===jobId&&pendingRestore.current.view.artifactId===artifactId)return;
    setFileCursors(['']);setFilePage(0);setFileId('');setFiles(null);setPreview(null);setContentError('');
  },[artifactId,jobId]);
  useEffect(()=>{
    let alive=true;if(!artifact||artifact.job_id!==jobId)return;
    if(manifest)bridge.runtime.files(artifactId,fileCursors[filePage]??'').then(page=>{if(alive){requireFilePage(page,artifact);setFiles(page);setFileId(previous=>page.files.some(item=>item.file_id===previous)?previous:page.files.find(item=>item.file_id===pendingRestore.current?.view.fileId)?.file_id??page.files[0]?.file_id??'');}}).catch(()=>{if(alive)setContentError('Frozen file manifest identity is unavailable.');});
    else bridge.runtime.artifact(artifactId).then(result=>{if(alive){requireFrozenArtifact(result.artifact,jobId);if(result.artifact.id!==artifactId||result.artifact.sha256!==artifact.sha256)throw new Error('Artifact identity mismatch.');setPreview(readablePreview(result.preview_text));setLoadedContentKey(contentKey);}}).catch(()=>{if(alive)setContentError('Frozen artifact preview identity is unavailable.');});
    return()=>{alive=false;};
  },[artifactId,artifact?.candidate_id,artifact?.sha256,jobId,manifest,filePage,fileCursors,readEpoch]);
  useEffect(()=>{
    const changed=previousFile.current!==fileId;previousFile.current=fileId;
    if(!changed)return;
    if(pendingRestore.current?.jobId===jobId&&pendingRestore.current.view.artifactId===artifactId&&pendingRestore.current.view.fileId===fileId)return;
    setStartLine(1);setDiffCursors(['']);setDiffPage(0);
  },[fileId,artifactId,jobId]);
  useEffect(()=>{
    const generation=++request.current;setText(null);setDiff(null);setLoadedContentKey('');setContentError('');
    if(!manifest||!fileId||!files?.files.some(file=>file.file_id===fileId))return;
    if(tab==='diff'&&!diffArtifact){setContentError('A frozen Git diff artifact is unavailable on this artifact page.');return;}
    const read=tab==='text'?bridge.runtime.text(artifactId,fileId,startLine):bridge.runtime.diff(diffArtifact!.id,fileId,diffCursors[diffPage]??'');
    read.then(page=>{
      if(generation!==request.current)return;
      if(tab==='text') {const result=page as TextPage;const file=files?.files.find(item=>item.file_id===fileId);requireTextPage(result,artifact!,file);setText(result);}
      else {const result=page as DiffPage;requireDiffPage(result,diffArtifact!,artifact!);setDiff(result);}
      setLoadedContentKey(contentKey);
    }).catch(()=>{if(generation===request.current)setContentError('This content or its frozen identity is unavailable. Binary, deleted or restricted files may have no text preview.');});
    return()=>{++request.current;};
  },[artifactId,artifact?.candidate_id,fileId,files,manifest,tab,startLine,diffPage,diffCursors,diffArtifact?.id]);
  const currentView=(scrollTop:number):JobView=>({artifactId,fileId,tab,startLine,scrollTop,artifactCursors:[...artifactCursors],artifactPage,fileCursors:[...fileCursors],filePage,diffCursors:[...diffCursors],diffPage});
  const bodyReady=manifest?(tab==='text'?text!==null:diff!==null):preview!==null;
  const contentReady=bodyReady&&loadedContentKey===contentKey&&artifact?.job_id===jobId&&(!manifest||files?.files.some(file=>file.file_id===fileId));
  useEffect(()=>{
    if(!open||!active||!contentReady||!viewMemory||pendingRestore.current?.jobId===jobId)return;
    const previous=viewMemory.current.get(jobId);
    const samePage=previous?.artifactId===artifactId&&previous.fileId===fileId&&previous.tab===tab&&previous.startLine===startLine&&(previous.diffPage??0)===diffPage;
    viewMemory.current.set(jobId,currentView(samePage?previous.scrollTop:0));
  },[open,active,contentReady,artifactId,fileId,tab,startLine,jobId,viewMemory,artifactCursors,artifactPage,fileCursors,filePage,diffCursors,diffPage]);
  useLayoutEffect(()=>{
    if(!open||!active||!contentReady)return;
    const pending=pendingRestore.current?.jobId===jobId?pendingRestore.current:null;
    const saved=pending?.view??viewMemory?.current.get(jobId);
    const area=root.current?.querySelector<HTMLElement>('.artifact-text');
    if(area){const desired=saved?.artifactId===artifactId&&saved.fileId===fileId&&saved.tab===tab?saved.scrollTop:0;area.scrollTop=desired;if(viewMemory)viewMemory.current.set(jobId,currentView(desired));}
    if(pendingRestore.current===pending)pendingRestore.current=null;
  },[loadedContentKey,contentReady,open,active]);
  function rememberScroll(event:React.UIEvent<HTMLDivElement>){
    const target=event.target as HTMLElement;
    if(!open||!active||!target.classList.contains('artifact-text')||!viewMemory||!contentReady||pendingRestore.current?.jobId===jobId)return;
    const previous=viewMemory.current.get(jobId);
    const maximum=Math.max(0,target.scrollHeight-target.clientHeight);
    // Expanding a short file can clamp its DOM scroll to zero. Retain the
    // requested position for returning to the smaller in-world monitor.
    if(previous?.artifactId===artifactId&&previous.fileId===fileId&&previous.tab===tab&&previous.startLine===startLine&&previous.scrollTop>maximum&&Math.abs(target.scrollTop-maximum)<1)return;
    viewMemory.current.set(jobId,currentView(target.scrollTop));
  }
  function chooseArtifact(id:string){pendingRestore.current=null;setArtifactId(id);}
  function chooseFile(id:string){pendingRestore.current=null;setFileId(id);}
  function chooseView(action:()=>void){pendingRestore.current=null;action();}
  return <div className={embedded?'computer-jobs':'jobs-layer'} hidden={!open} onScrollCapture={rememberScroll}><div className="jobs-board" ref={root} role="region" aria-label={embedded?'Computer job results':'Local jobs board'}>
    <header className="panel-header"><div><p className="eyebrow">{embedded?'Assigned job · Read-only':'Local work · explicit execution'}</p><h2>{embedded?'Job results':'Jobs'}</h2></div><div className="panel-actions">{onExpand&&<button onClick={onExpand}>Expand</button>}<button onClick={()=>void refresh()} disabled={busy}>Refresh status</button><button onClick={onClose}>Office <kbd>Esc</kbd></button></div></header>
    {!embedded&&<><div className="jobs-profile"><strong>{snapshot?.mode==='fixture'?'Test fixture · no connected worker':localInspection?'Local Git inspection':'Runtime unavailable'}</strong><span>Inspection uses zero model calls · coding requires verified readiness</span></div>
    <details className="coding-readiness"><summary>Codex execution: {codingReady?'ready':'unavailable'}</summary><p>{caps?.reasons.join(' ')||'Host readiness has not been verified.'}</p><p>Model catalog: {caps?.codex?.catalog_verified===true?'verified':'unverified'}. Included subscription quota: {caps?.codex?.subscription_quota?.ordinary_usage_allowed===true?'available':caps?.codex?.subscription_quota?.ordinary_usage_allowed===false?'unavailable':'unverified'}. Purchased credits: {caps?.codex?.subscription_quota?.purchased_credits_available===true?'available':caps?.codex?.subscription_quota?.purchased_credits_available===false?'unavailable':'unverified'}.</p><p>{caps?.codex?.usd_cost_enforced===true?'The host reports an enforced USD ceiling.':'An enforced USD ceiling is unavailable. Coding tasks remain blocked.'} Status refresh reads cached host state and starts no model turn.</p><button disabled={busy||!connected||caps?.codex?.host_enabled!==true} onClick={()=>snapshot&&void mutate(()=>bridge.runtime.refreshReadiness(snapshot.revision),'Setup check recorded. Review the readiness result.')}>Check Codex setup</button></details></>}
    {(error||connectionError)&&<p className="jobs-alert" role="alert">{error||connectionError}</p>}{notice&&<p className="jobs-notice" role="status">{notice}</p>}
    <div className="jobs-body">{!embedded&&<aside className="jobs-sidebar">
      <form className="job-form" onSubmit={event=>{event.preventDefault();if(snapshot&&projectId)void mutate(()=>jobKind==='inspection'?bridge.runtime.submitInspection(projectId,title,snapshot.revision):bridge.runtime.submitCoding(projectId,title,objective,writePrefix,budget,snapshot.revision),'Job queued. Review the job, then run it explicitly.');}}>
        <label htmlFor="job-kind">Work type</label><select id="job-kind" value={jobKind} onChange={event=>setJobKind(event.target.value as 'inspection'|'coding')} disabled={busy}><option value="inspection">Local Git inspection</option><option value="coding">Codex coding task</option></select>
        <label htmlFor="job-project">Repository</label><select id="job-project" value={projectId} onChange={event=>setProjectId(event.target.value)} disabled={busy||!snapshot}>{snapshot?.projects.map(project=><option value={project.id} key={project.id}>{project.name}</option>)}{!projectId&&<option value="">No registered repository</option>}</select>
        <button type="button" disabled={busy||!connected||!localInspection||snapshot?.projects.length!==0} onClick={()=>snapshot&&void mutate(()=>bridge.runtime.register(snapshot.revision),'Repository registration accepted.')}>Register configured repository</button>
        <label htmlFor="job-title">{jobKind==='inspection'?'Inspection title':'Coding title'}</label><input id="job-title" maxLength={200} value={title} onChange={event=>setTitle(event.target.value)} disabled={busy}/>
        {jobKind==='coding'&&<><label htmlFor="coding-objective">Task objective</label><textarea id="coding-objective" maxLength={2000} value={objective} onChange={event=>setObjective(event.target.value)} disabled={busy}/><label htmlFor="coding-path">Allowed write prefix</label><input id="coding-path" value={writePrefix} onChange={event=>setWritePrefix(event.target.value)} maxLength={240}/><label htmlFor="coding-budget">USD budget</label><input id="coding-budget" inputMode="decimal" value={budget} onChange={event=>setBudget(event.target.value)}/><button type="button" disabled={busy||!connected||!projectId||!codingReady||codingPolicy||snapshot?.stopped} onClick={()=>snapshot&&void mutate(()=>bridge.runtime.enableCoding(projectId,snapshot.revision),'Local candidate proposals enabled for this project.')}>Allow candidate proposals</button><p>{codingPolicy?'Project permits proposals in an isolated clone.':'Project policy requires explicit permission for candidate proposals.'} {codingReady?'Review scope and budget before submitting.':'Coding unavailable. Review the setup and spend requirements above.'}</p></>}
        <button className="primary" type="submit" disabled={busy||!connected||!projectId||!title.trim()||snapshot?.stopped||(jobKind==='inspection'?!localInspection:!codingReady||!codingPolicy||!objective.trim())}>{jobKind==='inspection'?'Submit inspection':'Submit coding task'}</button>
        <p>{jobKind==='inspection'?'Reads a committed repository into an isolated workspace. Checks its frozen bytes. Source changes and delivery are outside this job.':'Submission queues one scoped task. Run it separately after reviewing readiness, project policy and the positive budget. Delivery remains disabled.'}</p>
      </form>
      <nav aria-label="Submitted jobs" className="job-list">{snapshot?.jobs.map(item=><button key={item.id} disabled={busy} aria-pressed={item.id===jobId} className={item.id===jobId?'selected':''} onClick={()=>setJobId(item.id)}><span>{item.title}</span><small>{stateLabel(item.state)}</small></button>)}{snapshot?.jobs.length===0&&<p>No jobs submitted yet.</p>}</nav>
    </aside>}<section className="job-detail" aria-label="Selected job">
      {job?<><header className="job-summary"><div><h3>{job.title}</h3><p><span className="job-state">{stateLabel(job.state)}</span> · ${job.budget_usd} budget · {job.id}</p></div>{!embedded&&<button disabled={busy||!connected||job.state!=='queued'||snapshot?.stopped||(job.execution_profile==='codex_session'?!codingReady||!(job.budget_usd>0):!localInspection||job.execution_profile!=='local_git_inspection'||job.budget_usd!==0)} onClick={()=>snapshot&&void mutate(()=>job.execution_profile==='codex_session'?bridge.runtime.runCoding(job.id,snapshot.revision):bridge.runtime.run(job.id,snapshot.revision),'Run accepted. Waiting for status.')}>{job.execution_profile==='codex_session'?'Run coding task':'Run inspection'}</button>}</header>
        {!embedded&&onAssign&&stations.length>0&&<div className="computer-assignment"><label htmlFor="result-computer">Show results on</label><select id="result-computer" value={displayStation} onChange={event=>setDisplayStation(event.target.value)}>{stations.map(item=><option key={item.id} value={item.id}>{item.label}</option>)}</select><button disabled={!job.project_id||!displayStation} onClick={()=>job.project_id&&onAssign(displayStation,{jobId:job.id,projectId:job.project_id})}>Assign result display</button></div>}
        {resultsReady&&<p className="jobs-notice" role="status">Inspection results ready. Source delivery is disabled; the backend retains the verifying state.</p>}
        {job.blocked_reason&&<p className="jobs-alert">{job.blocked_reason}</p>}
        <div className="job-checks" aria-label="Job checks">{job.checks.map(check=><span key={check.id}>{check.id} <strong>{check.state}</strong></span>)}</div>
        <details className="job-events job-activity" open={activityOpen} onToggle={event=>setActivityOpen(event.currentTarget.open)}><summary>Run activity ({job.run_ids?.length??0})</summary>{activityOpen&&<RunActivity job={job} active={active&&open&&connected}/>}</details>
        <div className="artifact-toolbar"><label htmlFor="job-artifact">Artifact</label><select id="job-artifact" value={artifactId} onChange={event=>chooseArtifact(event.target.value)}>{artifacts.map(item=><option key={item.id} value={item.id}>{item.display_name??item.kind} · {item.kind}</option>)}{!artifacts.length&&<option value="">No result artifacts yet</option>}</select><button disabled={artifactPage===0} onClick={()=>chooseView(()=>setArtifactPage(page=>page-1))}>Previous artifacts</button><button disabled={!nextArtifact} onClick={()=>chooseView(()=>{if(nextArtifact){setArtifactCursors(values=>[...values.slice(0,artifactPage+1),nextArtifact]);setArtifactPage(page=>page+1);}})}>More artifacts</button>{artifact&&<small title={artifact.sha256}>SHA256 {artifact.sha256.slice(0,12)} · {artifact.immutable?'immutable':'unavailable'}</small>}</div>
        <div className="artifact-body">{manifest&&<nav className="artifact-files" aria-label="Result files">{files?.files.map(file=><button key={file.file_id} aria-pressed={fileId===file.file_id} className={fileId===file.file_id?'selected':''} onClick={()=>chooseFile(file.file_id)} title={file.path}>{file.path}<small>{file.status}{file.binary?' · binary':''}</small></button>)}<div className="page-controls"><button disabled={filePage===0} onClick={()=>chooseView(()=>setFilePage(page=>page-1))}>Previous files</button><button disabled={!files?.next_cursor} onClick={()=>chooseView(()=>{if(files?.next_cursor){setFileCursors(values=>[...values.slice(0,filePage+1),files.next_cursor!]);setFilePage(page=>page+1);}})}>More files</button></div></nav>}
          <section className="artifact-content" aria-label="Artifact content">{manifest&&<div className="artifact-tabs"><button aria-pressed={tab==='text'} onClick={()=>chooseView(()=>setTab('text'))}>File text</button><button aria-pressed={tab==='diff'} onClick={()=>chooseView(()=>setTab('diff'))}>Git diff</button><span>{files?.files.find(file=>file.file_id===fileId)?.path}</span></div>}
            {contentError?<p className="jobs-alert" role="alert">{contentError}</p>:!artifact?<p className="message">Run the inspection to produce immutable files and check results.</p>:!manifest?<pre className="artifact-text" tabIndex={0} aria-label="Read-only artifact text">{preview??'Loading artifact…'}</pre>:tab==='text'?<><pre className="artifact-text" tabIndex={0} aria-label="Read-only artifact text">{text?.lines.map(line=>`${String(line.number).padStart(5)}  ${line.text}${line.clipped?' [line clipped]':''}`).join('\n')??'Loading file text…'}</pre><div className="page-controls"><button disabled={startLine===1} onClick={()=>chooseView(()=>setStartLine(line=>Math.max(1,line-200)))}>Previous lines</button><button disabled={!text?.next_line} onClick={()=>chooseView(()=>{if(text?.next_line)setStartLine(text.next_line);})}>More lines</button></div></>:<><pre className="artifact-text diff-rows" tabIndex={0} aria-label="Read-only Git diff rows">{diff?(diff.rows.length?diff.rows.map((row,index)=><span key={index} className={`diff-row ${['add','remove','context'].includes(row.kind)?row.kind:'meta'}`}>{row.kind==='add'?'+':row.kind==='remove'?'-':' '} {row.text}{row.clipped?' [row clipped]':''}{'\n'}</span>):'No textual changes in this inspected candidate.'): 'Loading Git diff…'}</pre><div className="page-controls"><button disabled={diffPage===0} onClick={()=>chooseView(()=>setDiffPage(page=>page-1))}>Previous diff</button><button disabled={!diff?.next_cursor} onClick={()=>chooseView(()=>{if(diff?.next_cursor){setDiffCursors(values=>[...values.slice(0,diffPage+1),diff.next_cursor!]);setDiffPage(page=>page+1);}})}>More diff</button></div></>}
          </section></div>
      </>:<div className="message"><h3>{embedded?'Assigned job unavailable':'Inspect your repository'}</h3><p>{embedded?'The assigned job is missing or does not belong to its recorded project. Open Jobs to choose an available result.':'Register the host-configured project, submit an inspection, and run it to read genuine local artifacts.'}</p>{!localInspection&&!embedded&&<p>The local runtime needs to be configured before jobs are available.</p>}</div>}
    </section></div>
    <footer className="panel-footer">{connectionError?'Runtime disconnected · last known snapshot':snapshot?`Runtime ${snapshot.mode} · revision ${snapshot.revision}${snapshot.stopped?' · dispatch stopped':''}`:'Runtime disconnected'} · {codingReady?'Coding readiness verified':'Coding execution unavailable'}</footer>
  </div></div>;
}
