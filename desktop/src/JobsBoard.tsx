import { useCallback, useEffect, useRef, useState } from 'react';
import { bridge } from './bridge';
import type { DiffPage, FilePage, RuntimeArtifact, RuntimeCapabilities, RuntimeSnapshot, TextPage } from './types';

const safeStates = new Set(['queued','running','verifying','needs_approval','accepted','blocked','failed','paused','cancelled']);
const stateLabel = (value:string) => safeStates.has(value) ? value.replaceAll('_',' ') : 'unavailable';
export default function JobsBoard({onClose,active,open}:{onClose:()=>void;active:boolean;open:boolean}) {
  const [snapshot,setSnapshot]=useState<RuntimeSnapshot|null>(null);
  const [caps,setCaps]=useState<RuntimeCapabilities|null>(null);
  const [error,setError]=useState('');
  const [busy,setBusy]=useState(false);
  const [notice,setNotice]=useState('');
  const [title,setTitle]=useState('Inspect current repository');
  const [projectId,setProjectId]=useState('');
  const [jobId,setJobId]=useState('');
  const [artifacts,setArtifacts]=useState<RuntimeArtifact[]>([]);
  const [artifactId,setArtifactId]=useState('');
  const [files,setFiles]=useState<FilePage|null>(null);
  const [fileId,setFileId]=useState('');
  const [fileCursors,setFileCursors]=useState<string[]>(['']);
  const [filePage,setFilePage]=useState(0);
  const [tab,setTab]=useState<'text'|'diff'>('text');
  const [text,setText]=useState<TextPage|null>(null);
  const [diff,setDiff]=useState<DiffPage|null>(null);
  const [preview,setPreview]=useState<string|null>(null);
  const [contentError,setContentError]=useState('');
  const [startLine,setStartLine]=useState(1);
  const [diffCursors,setDiffCursors]=useState<string[]>(['']);
  const [diffPage,setDiffPage]=useState(0);
  const request = useRef(0);
  const root = useRef<HTMLDivElement>(null);
  const job=snapshot?.jobs.find(item=>item.id===jobId);
  const artifact=artifacts.find(item=>item.id===artifactId);
  const manifest=artifact?.kind==='file_manifest';
  const localInspection=caps?.features.local_git_inspection===true;
  const refresh=useCallback(async()=>{
    try {
      const [state,capabilities]=await Promise.all([bridge.runtime.snapshot(),bridge.runtime.capabilities()]);
      setSnapshot(state);setCaps(capabilities);setError('');
      setProjectId(previous=>state.projects.some(item=>item.id===previous)?previous:state.projects[0]?.id??'');
      setJobId(previous=>state.jobs.some(item=>item.id===previous)?previous:state.jobs[0]?.id??'');
    } catch (reason) {setError(reason instanceof Error?reason.message:'Local runtime is unavailable.');}
  },[]);
  useEffect(()=>{void refresh();},[refresh]);
  useEffect(()=>{
    if(!active||!open)return;
    const timer=setInterval(()=>{void refresh();},1500);
    return()=>clearInterval(timer);
  },[refresh,active,open]);
  useEffect(()=>{
    if(!open)return;
    const close=(event:KeyboardEvent)=>{if(event.key==='Escape'){event.preventDefault();onClose();}};
    document.addEventListener('keydown',close);root.current?.querySelector<HTMLButtonElement>('button')?.focus();
    return()=>document.removeEventListener('keydown',close);
  },[onClose,open]);
  async function mutate(action:()=>Promise<unknown>,message:string) {
    setBusy(true);setError('');setNotice('');
    try {await action();setNotice(message);await refresh();}
    catch(reason){setError(reason instanceof Error?reason.message:'Command was not accepted. Refresh state before trying again.');}
    finally{setBusy(false);}
  }
  useEffect(()=>{
    let alive=true;setArtifacts([]);setArtifactId('');
    if(jobId)bridge.runtime.artifacts(jobId).then(result=>{if(alive){setArtifacts(result.artifacts);setArtifactId(result.artifacts.find(item=>item.kind==='file_manifest')?.id??result.artifacts[0]?.id??'');}}).catch(()=>{if(alive)setContentError('Artifact metadata is unavailable.');});
    return()=>{alive=false;};
  },[jobId,job?.artifact_ids.join(',')]);
  useEffect(()=>{setFileCursors(['']);setFilePage(0);setFileId('');setFiles(null);setPreview(null);setContentError('');},[artifactId]);
  useEffect(()=>{
    let alive=true;if(!artifactId)return;
    if(manifest)bridge.runtime.files(artifactId,fileCursors[filePage]??'').then(page=>{if(alive){setFiles(page);setFileId(previous=>page.files.some(item=>item.file_id===previous)?previous:page.files[0]?.file_id??'');}}).catch(()=>{if(alive)setContentError('File manifest read failed.');});
    else bridge.runtime.artifact(artifactId).then(result=>{if(alive)setPreview(result.preview_text??'This artifact has no text preview.');}).catch(()=>{if(alive)setContentError('Artifact preview read failed.');});
    return()=>{alive=false;};
  },[artifactId,manifest,filePage,fileCursors]);
  useEffect(()=>{setStartLine(1);setDiffCursors(['']);setDiffPage(0);},[fileId,artifactId]);
  useEffect(()=>{
    const generation=++request.current;setText(null);setDiff(null);setContentError('');
    if(!manifest||!fileId)return;
    const read=tab==='text'?bridge.runtime.text(artifactId,fileId,startLine):bridge.runtime.diff(artifactId,fileId,diffCursors[diffPage]??'');
    read.then(page=>{if(generation!==request.current)return;if(tab==='text')setText(page as TextPage);else setDiff(page as DiffPage);}).catch(()=>{if(generation===request.current)setContentError('This content is unavailable. Binary, deleted or restricted files may have no text preview.');});
    return()=>{++request.current;};
  },[artifactId,fileId,manifest,tab,startLine,diffPage,diffCursors]);
  return <div className="jobs-layer" hidden={!open}><div className="jobs-board" ref={root} role="region" aria-label="Local jobs board">
    <header className="panel-header"><div><p className="eyebrow">Local work · explicit execution</p><h2>Jobs</h2></div><div className="panel-actions"><button onClick={()=>void refresh()} disabled={busy}>Refresh status</button><button onClick={onClose}>Office <kbd>Esc</kbd></button></div></header>
    <div className="jobs-profile"><strong>{localInspection?'Local Git inspection':'Runtime unavailable'}</strong><span>Deterministic Git and identity checks · zero model calls · coding agent unavailable</span></div>
    {error&&<p className="jobs-alert" role="alert">{error}</p>}{notice&&<p className="jobs-notice" role="status">{notice}</p>}
    <div className="jobs-body"><aside className="jobs-sidebar">
      <form className="job-form" onSubmit={event=>{event.preventDefault();if(snapshot&&projectId)void mutate(()=>bridge.runtime.submitInspection(projectId,title,snapshot.revision),'Command queued. Review the job, then run it explicitly.');}}>
        <label htmlFor="job-project">Repository</label><select id="job-project" value={projectId} onChange={event=>setProjectId(event.target.value)} disabled={busy||!snapshot}>{snapshot?.projects.map(project=><option value={project.id} key={project.id}>{project.name}</option>)}{!projectId&&<option value="">No registered repository</option>}</select>
        <button type="button" disabled={busy||!snapshot||!localInspection} onClick={()=>snapshot&&void mutate(()=>bridge.runtime.register(snapshot.revision),'Repository registration queued. Refresh to review its resolved revision.')}>Register configured repository</button>
        <label htmlFor="job-title">Inspection title</label><input id="job-title" maxLength={200} value={title} onChange={event=>setTitle(event.target.value)} disabled={busy}/>
        <button className="primary" type="submit" disabled={busy||!projectId||!localInspection||!title.trim()||snapshot?.stopped}>Submit inspection</button>
        <p>Reads a committed repository into an isolated workspace. Checks its frozen bytes. Source changes and delivery are outside this job.</p>
      </form>
      <nav aria-label="Submitted jobs" className="job-list">{snapshot?.jobs.map(item=><button key={item.id} aria-pressed={item.id===jobId} className={item.id===jobId?'selected':''} onClick={()=>setJobId(item.id)}><span>{item.title}</span><small>{stateLabel(item.state)}</small></button>)}{snapshot?.jobs.length===0&&<p>No jobs submitted yet.</p>}</nav>
    </aside><section className="job-detail" aria-label="Selected job">
      {job?<><header className="job-summary"><div><h3>{job.title}</h3><p><span className="job-state">{stateLabel(job.state)}</span> · $0 inspection budget · {job.id}</p></div><button disabled={busy||!localInspection||job.state!=='queued'||snapshot?.stopped} onClick={()=>snapshot&&void mutate(()=>bridge.runtime.run(job.id,snapshot.revision),'Run command queued. Status and results will appear when execution completes.')}>Run inspection</button></header>
        {job.blocked_reason&&<p className="jobs-alert">{job.blocked_reason}</p>}
        <div className="job-checks" aria-label="Job checks">{job.checks.map(check=><span key={check.id}>{check.id} <strong>{check.state}</strong></span>)}</div>
        <details className="job-events"><summary>Run events ({job.events.length})</summary><ol>{job.events.slice(-50).map(event=><li key={event.id}><time>{event.at}</time> {event.message}</li>)}</ol></details>
        <div className="artifact-toolbar"><label htmlFor="job-artifact">Artifact</label><select id="job-artifact" value={artifactId} onChange={event=>setArtifactId(event.target.value)}>{artifacts.map(item=><option key={item.id} value={item.id}>{item.display_name??item.kind} · {item.kind}</option>)}{!artifacts.length&&<option value="">No result artifacts yet</option>}</select>{artifact&&<small title={artifact.sha256}>SHA256 {artifact.sha256.slice(0,12)} · immutable</small>}</div>
        <div className="artifact-body">{manifest&&<nav className="artifact-files" aria-label="Result files">{files?.files.map(file=><button key={file.file_id} aria-pressed={fileId===file.file_id} className={fileId===file.file_id?'selected':''} onClick={()=>setFileId(file.file_id)} title={file.path}>{file.path}<small>{file.status}{file.binary?' · binary':''}</small></button>)}<div className="page-controls"><button disabled={filePage===0} onClick={()=>setFilePage(page=>page-1)}>Previous files</button><button disabled={!files?.next_cursor} onClick={()=>{if(files?.next_cursor){setFileCursors(values=>[...values.slice(0,filePage+1),files.next_cursor!]);setFilePage(page=>page+1);}}}>More files</button></div></nav>}
          <section className="artifact-content" aria-label="Artifact content">{manifest&&<div className="artifact-tabs"><button aria-pressed={tab==='text'} onClick={()=>setTab('text')}>File text</button><button aria-pressed={tab==='diff'} onClick={()=>setTab('diff')}>Git diff</button><span>{files?.files.find(file=>file.file_id===fileId)?.path}</span></div>}
            {contentError?<p className="jobs-alert" role="alert">{contentError}</p>:!artifact?<p className="message">Run the inspection to produce immutable files and check results.</p>:!manifest?<pre className="artifact-text">{preview??'Loading artifact…'}</pre>:tab==='text'?<><pre className="artifact-text">{text?.lines.map(line=>`${String(line.line).padStart(5)}  ${line.text}${line.clipped?' [line clipped]':''}`).join('\n')??'Loading file text…'}</pre><div className="page-controls"><button disabled={startLine===1} onClick={()=>setStartLine(line=>Math.max(1,line-200))}>Previous lines</button><button disabled={!text?.next_start_line} onClick={()=>text?.next_start_line&&setStartLine(text.next_start_line)}>More lines</button></div></>:<><pre className="artifact-text diff-rows">{diff?(diff.rows.length?diff.rows.map((row,index)=><span key={index} className={`diff-row ${['add','remove','context'].includes(row.kind)?row.kind:'meta'}`}>{row.kind==='add'?'+':row.kind==='remove'?'-':' '} {row.text}{'\n'}</span>):'No textual changes in this inspected candidate.'): 'Loading Git diff…'}</pre><div className="page-controls"><button disabled={diffPage===0} onClick={()=>setDiffPage(page=>page-1)}>Previous diff</button><button disabled={!diff?.next_cursor} onClick={()=>{if(diff?.next_cursor){setDiffCursors(values=>[...values.slice(0,diffPage+1),diff.next_cursor!]);setDiffPage(page=>page+1);}}}>More diff</button></div></>}
          </section></div>
      </>:<div className="message"><h3>Inspect your repository</h3><p>Register the host-configured project, submit an inspection, and run it to read genuine local artifacts.</p>{!localInspection&&<p>The local runtime needs to be configured before jobs are available.</p>}</div>}
    </section></div>
    <footer className="panel-footer">{snapshot?`Runtime ${snapshot.mode} · revision ${snapshot.revision}${snapshot.stopped?' · dispatch stopped':''}`:'Runtime disconnected'} · No coding model configured</footer>
  </div></div>;
}
