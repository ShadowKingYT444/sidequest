import { Component, Suspense, lazy, useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from 'react';
import { bridge } from './bridge';
import type { GitDiff, JobView, ProviderDiscovery, RuntimeCapabilities, RuntimeJob, RuntimeSnapshot, Snapshot, StationAssignment } from './types';
import { loadOfficeBindings, type OfficeBindings } from './office-bindings';
import type { EditorViews } from './DiffEditor';
import type { OriginalActorState } from './OriginalActors';
import type { LauncherMemory } from './StationLauncher';
import {requireOfficeSessions} from './runtime-identity';
import './MonitorSession.css';
import NotificationTray from './NotificationTray';
import {deriveNotifications, notificationsByStation, type OfficeNotification} from './notifications';
import {createDraftOperations, type DraftOperations} from './local-drafts';
import {SessionDraftStore} from './session-drafts';
import type {MonitorMemory} from './MonitorSession';
import {describeOfficeFailure, type OfficeFailure} from './office-failure';
const MonitorSession=lazy(()=>import('./MonitorSession'));
const OfficeScene = lazy(() => import('./OfficeScene'));
const DiffEditor = lazy(() => {
  performance.mark('sidequest:editor-import-start');
  return import('./DiffEditor').then(module => {performance.mark('sidequest:editor-import-ready');return module;});
});
const JobsBoard = lazy(() => import('./JobsBoard'));
const ProviderSettings=lazy(()=>import('./ProviderSettings'));
const ProviderPicker=lazy(()=>import('./ProviderPicker'));
const StationLauncher=lazy(()=>import('./StationLauncher'));
const SessionCard=lazy(()=>import('./SessionCard'));
type Mode = 'overview' | 'desk' | 'expanded';
interface DiffRead {key:string;value:GitDiff}
class SceneBoundary extends Component<{ children: ReactNode; onError: (error: Error) => void }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  componentDidCatch(error: Error) { this.props.onError(error); }
  render() { return this.state.failed ? null : this.props.children; }
}
function useReducedMotion() {
  const [reduced, setReduced] = useState(() => matchMedia('(prefers-reduced-motion: reduce)').matches);
  useEffect(() => { const query = matchMedia('(prefers-reduced-motion: reduce)'); const update = () => setReduced(query.matches); query.addEventListener('change', update); return () => query.removeEventListener('change', update); }, []);
  return reduced;
}
function useVisible() {
  const [active, setActive] = useState(!document.hidden);
  useEffect(() => { const update = () => setActive(!document.hidden); document.addEventListener('visibilitychange', update); return () => document.removeEventListener('visibilitychange', update); }, []);
  return active;
}
function useCompact(){const [compact,setCompact]=useState(()=>innerWidth<600);useEffect(()=>{const update=()=>setCompact(innerWidth<600);addEventListener('resize',update);return()=>removeEventListener('resize',update);},[]);return compact;}
export default function App() {
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  const [gitError, setGitError] = useState<string | null>(null);
  const [readVersion, setReadVersion] = useState(0);
  const [refreshing, setRefreshing] = useState(false);
  const [bindings, setBindings] = useState<OfficeBindings | null>(null);
  const [officeFailure, setOfficeFailure] = useState<OfficeFailure|null>(null);
  const [officeAttempt, setOfficeAttempt] = useState(0);
  const assetFailure=officeFailure!==null;
  const [actorState, setActorState] = useState<OriginalActorState | null>(null);
  const updateActorState = useCallback((state: OriginalActorState) => setActorState(state), []);
  const [selectedStation, setSelectedStation] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const diffReadKey=snapshot&&selectedFile?JSON.stringify([readVersion,snapshot.baseRevision,snapshot.candidateRevision,selectedFile]):'';
  const [diffRead,setDiffRead]=useState<DiffRead|null>(null);
  const lastDiffRead=useRef<DiffRead|null>(null);
  const diff=diffRead?.key===diffReadKey?diffRead.value:null;
  const [diffError, setDiffError] = useState<string | null>(null);
  const [mode, setMode] = useState<Mode>('overview');
  const [jobsOpen,setJobsOpen]=useState(false);
  const [jobsMounted,setJobsMounted]=useState(false);
  const [settingsOpen,setSettingsOpen]=useState(false);
  const [launcherStation,setLauncherStation]=useState<string|null>(null);
  const [actorStation,setActorStation]=useState<string|null>(null);
  const [actorSceneId,setActorSceneId]=useState<string|null>(null);
  const [boardOpen,setBoardOpen]=useState(false);
  const [boardSnapshot,setBoardSnapshot]=useState<RuntimeSnapshot|null>(null);
  const [boardJobId,setBoardJobId]=useState('');
  const [boardError,setBoardError]=useState(false);
  const launcherAnchor=useRef<HTMLDivElement>(null);
  const launcherMemories=useRef(new Map<string,LauncherMemory>());
  const getLauncherMemory=(id:string)=>{let memory=launcherMemories.current.get(id);if(!memory){let uncertain=false;try{uncertain=sessionStorage.getItem('sidequest:uncertain-submit:'+id)==='1';}catch{}memory={inFlight:false,submissionUncertain:uncertain,pendingTask:null,queued:null,launchAccepted:false};launcherMemories.current.set(id,memory);}return memory;};
  const [sessionCount,setSessionCount]=useState<number|null>(null);
  const [officeSnapshot,setOfficeSnapshot]=useState<RuntimeSnapshot|null>(null);
  const [officeError,setOfficeError]=useState('');
  const [officeRevision,setOfficeRevision]=useState(0);
  const [notifications,setNotifications]=useState<OfficeNotification[]>([]);
  const stationBadges=useMemo(()=>notificationsByStation(notifications),[notifications]);
  const updateSessionCount=useCallback((count:number)=>{setSessionCount(count);setOfficeRevision(value=>value+1);},[]);
  const [monitorTab,setMonitorTab]=useState<'trace'|'files'|'task'>('trace');
  const monitorTabs=useRef(new Map<string,'trace'|'files'|'task'>());
  const drafts=useRef(new Map<string,SessionDraftStore>());
  const draftOperations=useRef(new Map<string,DraftOperations>());
  const traceMemories=useRef(new Map<string,MonitorMemory>());
  const computerPicker=useRef<HTMLSelectElement>(null);
  const sessionPanel=useRef<HTMLDivElement>(null);
  const [providers,setProviders]=useState<ProviderDiscovery|null>(null);
  const [runtimeCaps,setRuntimeCaps]=useState<RuntimeCapabilities|null>(null);
  const [settingsBusy,setSettingsBusy]=useState(false);
  const [stationJobs,setStationJobs]=useState<Record<string,StationAssignment>>(()=>{try{const raw=localStorage.getItem('sidequest:result-displays')??'{}';if(raw.length>65536)return {};const value=JSON.parse(raw);return Object.fromEntries(Object.entries(value).filter(([,item])=>typeof item==='object'&&item!==null&&typeof (item as StationAssignment).jobId==='string'&&typeof (item as StationAssignment).projectId==='string')) as Record<string,StationAssignment>;}catch{return {};}});
  const [showAssigned,setShowAssigned]=useState(true);
  const projectedWork=useRef<HTMLDivElement|null>(null);
  const [requestedJob,setRequestedJob]=useState<(StationAssignment&{requestId:number})|undefined>();
  const jobViews=useRef<Map<string,JobView>>(new Map());
  const settingsButton=useRef<HTMLButtonElement>(null);
  const jobsButton=useRef<HTMLButtonElement>(null);
  const views = useRef<EditorViews>(new Map());
  const requestId = useRef(0);
  const returnFocus = useRef<HTMLButtonElement | null>(null);
  const returnTarget=useRef('fallback');
  const panel = useRef<HTMLDivElement>(null);
  const reducedMotion = useReducedMotion();
  const active = useVisible();
  const compact=useCompact();
  useEffect(()=>{
    if(!active)return;let alive=true,timer:ReturnType<typeof setTimeout>|undefined;
    const read=async()=>{try{const state=await bridge.runtime.snapshot();const owners=requireOfficeSessions(state);const items=deriveNotifications(state);if(alive){setOfficeSnapshot(previous=>previous?.revision===state.revision&&previous.mode===state.mode?previous:state);setNotifications(previous=>JSON.stringify(previous)===JSON.stringify(items)?previous:items);setSessionCount(owners.length);setOfficeError('');}}catch(reason){if(alive){setSessionCount(null);setNotifications([]);setOfficeError(reason instanceof Error?reason.message:'Runtime unavailable.');}}if(alive)timer=setTimeout(()=>void read(),5000);};
    void read();return()=>{alive=false;clearTimeout(timer);};
  },[active,officeRevision]);
  const refreshProviders=useCallback(async()=>{setSettingsBusy(true);const results=await Promise.allSettled([bridge.providers(),bridge.runtime.capabilities()]);if(results[0].status==='fulfilled')setProviders(results[0].value);if(results[1].status==='fulfilled')setRuntimeCaps(results[1].value);else setRuntimeCaps(null);setSettingsBusy(false);},[]);
  useEffect(()=>{if(!settingsOpen)return;void refreshProviders();const escape=(event:KeyboardEvent)=>{if(event.key==='Escape'){event.preventDefault();setSettingsOpen(false);settingsButton.current?.focus();}if(event.key==='Tab'){const layer=document.querySelector('.settings-layer');const items=Array.from(layer?.querySelectorAll<HTMLElement>('button:not(:disabled),input,select,summary,[tabindex="0"]')??[]).filter(item=>item.getClientRects().length);const first=items[0],last=items.at(-1);if(event.shiftKey&&(document.activeElement===first||!layer?.contains(document.activeElement))){event.preventDefault();last?.focus();}else if(!event.shiftKey&&(document.activeElement===last||!layer?.contains(document.activeElement))){event.preventDefault();first?.focus();}}};document.addEventListener('keydown',escape);return()=>document.removeEventListener('keydown',escape);},[settingsOpen,refreshProviders]);
  const refresh = useCallback(async () => {
    setRefreshing(true); setGitError(null);
    try {
      const data = await bridge.snapshot(); setSnapshot(data); setReadVersion(version => version + 1);
      setSelectedFile(previous => data.files.some(file => file.id === previous) ? previous : data.files[0]?.id ?? null);
    } catch (error) { setGitError(error instanceof Error ? error.message : 'Could not read the configured Git repository.'); }
    finally { setRefreshing(false); }
  }, []);
  useEffect(() => { void refresh(); }, [refresh]);
  useEffect(() => {
    let alive = true;
    loadOfficeBindings().then(data => { if (alive) setBindings(data); }).catch(error => {
      if (alive) setOfficeFailure(describeOfficeFailure(error,'bindings'));
    });
    return () => { alive = false; };
  }, [officeAttempt]);
  useEffect(() => {
    if (!selectedFile || !diffReadKey || mode === 'overview' || monitorTab!=='files') return;
    // Reopening the same pinned read must not mount, clear, then mount Monaco.
    // Explicit refresh, either revision, or file selection invalidates this single entry.
    if(lastDiffRead.current?.key===diffReadKey){setDiffRead(lastDiffRead.current);setDiffError(null);return;}
    const generation = ++requestId.current; setDiffRead(null); setDiffError(null);
    bridge.diff(selectedFile).then(data => { if (generation === requestId.current) {
      const read={key:diffReadKey,value:data};lastDiffRead.current=read;setDiffRead(read);
    } }).catch(error => {
      if (generation === requestId.current) setDiffError(error instanceof Error ? error.message : 'Could not load this diff.');
    });
    return () => { ++requestId.current; };
  }, [selectedFile, diffReadKey, mode === 'overview' || monitorTab!=='files']);
  const close = useCallback(() => { setMode('overview'); requestAnimationFrame(() => computerPicker.current?.focus()); }, []);
  const closeJobs=useCallback(()=>{setJobsOpen(false);requestAnimationFrame(()=>jobsButton.current?.focus());},[]);
  const openJobs=useCallback(()=>{setBoardOpen(false);setLauncherStation(null);setActorStation(null);setSettingsOpen(false);setMode('overview');setJobsMounted(true);setJobsOpen(true);},[]);
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if(settingsOpen||jobsOpen||launcherStation||actorStation||boardOpen)return;
      if (event.key === 'Escape' && mode !== 'overview') { event.preventDefault(); close(); }
      if (event.key === 'Tab' && mode === 'expanded' && projectedWork.current) {
        const elements = Array.from(projectedWork.current.querySelectorAll<HTMLElement>('button:not(:disabled), select, input, textarea, [tabindex="0"]')).filter(element => element.getClientRects().length);
        const first = elements[0], last = elements[elements.length - 1];
        if (event.shiftKey && (document.activeElement === first || !projectedWork.current.contains(document.activeElement))) { event.preventDefault(); last?.focus(); }
        else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
      }
    };
    document.addEventListener('keydown', onKey); return () => document.removeEventListener('keydown', onKey);
  }, [mode, close,settingsOpen,jobsOpen,launcherStation,actorStation,boardOpen]);
  useEffect(() => { if (mode !== 'overview') requestAnimationFrame(() => projectedWork.current?.querySelector<HTMLButtonElement>('button')?.focus()); }, [mode]);
  const selectStation = useCallback((id: string,tab?:'trace'|'files'|'task') => {const selectedTab=tab??monitorTabs.current.get(id)??'trace';monitorTabs.current.set(id,selectedTab);setMonitorTab(selectedTab);setBoardOpen(false);setLauncherStation(null);setActorStation(null);setSettingsOpen(false);returnTarget.current=id;setShowAssigned(true); setSelectedStation(id);setJobsOpen(false); setMode('desk'); }, []);
  useEffect(()=>{if(mode==='expanded'||compact||!bindings||assetFailure)projectedWork.current?.removeAttribute('style');},[mode,compact,bindings,assetFailure]);
  const station = bindings?.stations.find(item => item.id === selectedStation);
  const stationLabel=station?.label??(selectedStation&&selectedStation!=='repository'?`Computer ${selectedStation.split('-').at(-1)?.padStart(2,'0')}`:'Repository computer');
  const openWorkstation=useCallback((id:string)=>{setBoardOpen(false);if(!bindings?.stations.some(item=>item.id===id))return;setJobsOpen(false);setSettingsOpen(false);setActorStation(null);setLauncherStation(id);},[bindings]);
  const openActor=useCallback((id:string,sceneId?:string)=>{setBoardOpen(false);setActorSceneId(sceneId??null);if(!bindings?.stations.some(item=>item.id===id))return;setJobsOpen(false);setSettingsOpen(false);setLauncherStation(null);setActorStation(id);},[bindings]);
  const openBoard=useCallback(()=>{setMode('overview');setSettingsOpen(false);setJobsOpen(false);setActorStation(null);setLauncherStation(null);setBoardOpen(true);},[]);
  useEffect(()=>{if(!boardOpen)return;let alive=true;setBoardError(false);bridge.runtime.snapshot().then(state=>{if(alive){setBoardSnapshot(state);setBoardJobId(previous=>state.jobs.some(job=>job.id===previous)?previous:state.jobs[0]?.id??'');}}).catch(()=>{if(alive)setBoardError(true);});const escape=(event:KeyboardEvent)=>{if(event.key==='Escape'){event.preventDefault();setBoardOpen(false);computerPicker.current?.focus();}};document.addEventListener('keydown',escape);return()=>{alive=false;document.removeEventListener('keydown',escape);};},[boardOpen]);
  const boardJob=boardSnapshot?.jobs.find(job=>job.id===boardJobId);
  useEffect(()=>{if(!actorStation)return;const panel=sessionPanel.current;panel?.querySelector<HTMLButtonElement>('button')?.focus();const key=(event:KeyboardEvent)=>{if(event.key==='Escape'){event.preventDefault();setActorStation(null);computerPicker.current?.focus();}if(event.key==='Tab'){const items=Array.from(panel?.querySelectorAll<HTMLElement>('button:not(:disabled),select,[tabindex="0"]')??[]).filter(item=>item.getClientRects().length);const first=items[0],last=items.at(-1);if(event.shiftKey&&document.activeElement===first){event.preventDefault();last?.focus();}else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first?.focus();}}};document.addEventListener('keydown',key);return()=>document.removeEventListener('keydown',key);},[actorStation]);
  const contextualCard=useMemo(()=>actorStation?{stationId:actorStation,sceneId:actorSceneId,kind:'actor' as const,element:sessionPanel}:launcherStation?{stationId:launcherStation,kind:'workstation' as const,element:launcherAnchor}:undefined,[actorStation,actorSceneId,launcherStation]);
  const failScene = useCallback((error: Error) => setOfficeFailure(describeOfficeFailure(error)), []);
  const failAssets = useCallback((error: Error) => setOfficeFailure(describeOfficeFailure(error,'assets')), []);
  const retryOffice=async()=>{
    if(officeFailure?.kind==='assets'){
      try{(await import('./OfficeScene')).clearOfficeModelCache();}catch(error){failScene(error instanceof Error?error:new Error('Office module unavailable'));return;}
    }
    setBindings(null);setOfficeFailure(null);setActorState(null);setOfficeAttempt(value=>value+1);
  };
  const selectedAssignment=selectedStation&&Object.hasOwn(stationJobs,selectedStation)?stationJobs[selectedStation]:undefined;
  const fileWork = selectedAssignment&&showAssigned?<Suspense fallback={<div className="message">Loading assigned job…</div>}><JobsBoard embedded open={!settingsOpen&&!jobsOpen} active={active&&!settingsOpen&&!jobsOpen} onClose={close} onExpand={mode==='expanded'?undefined:()=>setMode('expanded')} requestedJob={selectedAssignment} viewMemory={jobViews}/></Suspense>:(
    <div className={`work-panel ${mode === 'expanded' ? 'expanded' : ''}`} ref={panel} role={mode === 'expanded' ? 'dialog' : 'region'} aria-modal={mode === 'expanded' ? true : undefined} aria-label="Computer work viewer">
      <header className="panel-header">
        <div><p className="eyebrow">{stationLabel} · Read-only</p><h2>{snapshot?.project.name ?? 'Local repository'}</h2></div>
        <div className="panel-actions">{mode !== 'expanded' && <button onClick={() => setMode('expanded')}>Expand</button>}<button onClick={close} aria-label="Return to office">Office <kbd>Esc</kbd></button></div>
      </header>
      <div className="revision-bar"><span>Git diff</span><span title={snapshot?.baseRevision}>{snapshot?.baseRevision.slice(0, 8)} <span aria-label="to">→</span> {snapshot?.candidateRevision.slice(0, 8)}</span><span>Committed revisions</span></div>
      <div className="work-body">
        <nav className="file-list" aria-label="Changed files"><p className="file-count">{snapshot?.files.length ?? 0} changed files</p>{snapshot?.files.map(file => <button key={file.id} data-file-id={file.id} className={selectedFile === file.id ? 'selected' : ''} onClick={() => setSelectedFile(file.id)} aria-pressed={selectedFile === file.id}><span className="file-status" title={file.status}>{({added: "+", deleted: "−", modified: "M", renamed: "R"} as Record<string,string>)[file.status] ?? file.status}</span><span className="file-path" title={file.path}>{file.path}</span>{file.binary && <span className="binary-tag">binary</span>}</button>)}</nav>
        <section className="editor-area" aria-label="Selected file diff">
          {selectedFile ? <div className="file-heading">{diff?.path ?? snapshot?.files.find(file => file.id === selectedFile)?.path}<span>Read-only</span></div> : null}
          {gitError ? <div className="message error" role="alert">{gitError}<button onClick={() => void refresh()}>Retry Git read</button></div> : !selectedFile ? <div className="message"><h3>No committed changes</h3><p>The selected revisions have no viewable text changes.</p></div> : diffError ? <div className="message error" role="alert">{diffError}<button onClick={() => void refresh()}>Refresh repository</button></div> : !diff ? <div className="message" role="status">Loading Git diff…</div> : diff.unavailableReason ? <div className="message"><h3>Content withheld</h3><p>{diff.unavailableReason}</p></div> : diff.binary ? <div className="message"><h3>Binary file</h3><p>This file is listed as a binary change. Its bytes are not rendered as text.</p></div> : <Suspense fallback={<div className="message" role="status">Loading diff editor…</div>}><DiffEditor diff={diff} views={views.current}/></Suspense>}
        </section>
      </div>
    </div>
  );
  const selectedOwner=officeSnapshot?.office_sessions?.find(owner=>owner.station_id===selectedStation);
  const sessionKey=JSON.stringify([selectedStation,selectedOwner?.job_id??'',selectedOwner?.project_id??'',selectedOwner?.run_id??'unassigned',selectedOwner?.worker_id??'']);
  // Follow-up runs retain the same job conversation; the pending send itself remains tied to its exact run.
  const draftKey=JSON.stringify([selectedStation,selectedOwner?.job_id??'',selectedOwner?.project_id??'']);
  let draftStore=drafts.current.get(draftKey);if(!draftStore){draftStore=new SessionDraftStore(draftKey);drafts.current.set(draftKey,draftStore);}
  let operations=draftOperations.current.get(sessionKey);if(!operations){operations=createDraftOperations();draftOperations.current.set(sessionKey,operations);}
  let traceMemory=traceMemories.current.get(sessionKey);if(!traceMemory){traceMemory={afterSeq:0,previous:[],scrollTop:0};traceMemories.current.set(sessionKey,traceMemory);}
  const chooseMonitorTab=(tab:'trace'|'files'|'task')=>{setMonitorTab(tab);if(selectedStation)monitorTabs.current.set(selectedStation,tab);};
  const work=<div className="monitor-shell" role={mode==='expanded'&&monitorTab==='trace'?'dialog':undefined} aria-modal={mode==='expanded'&&monitorTab==='trace'?true:undefined} aria-label={monitorTab==='trace'?'Computer session viewer':monitorTab==='task'?'Computer task workspace':undefined} data-monitor-tab={monitorTab}>
    <header className="monitor-header"><span className="monitor-name">{stationLabel}</span><nav className="monitor-tabs" aria-label="Computer view"><button aria-pressed={monitorTab==='trace'} onClick={()=>chooseMonitorTab('trace')}>Trace</button><button aria-pressed={monitorTab==='files'} onClick={()=>chooseMonitorTab('files')}>Files</button><button aria-pressed={monitorTab==='task'} onClick={()=>chooseMonitorTab('task')}>Task setup</button></nav><div className="monitor-actions">{mode!=='expanded'&&<button onClick={()=>setMode('expanded')}>Expand</button>}<button onClick={close} aria-label="Return to office">Office <kbd>Esc</kbd></button></div></header>
    <div className="monitor-content">{monitorTab==='files'?fileWork:monitorTab==='task'&&selectedStation?<Suspense fallback={<p className="message">Opening task setup…</p>}><StationLauncher workspace key={selectedStation} memory={getLauncherMemory(selectedStation)} stationLabel={stationLabel} projectId={stationJobs[selectedStation]?.projectId} onClose={close} onSettings={()=>setSettingsOpen(true)} onUncertaintyChange={uncertain=>{try{const key='sidequest:uncertain-submit:'+selectedStation;if(uncertain)sessionStorage.setItem(key,'1');else sessionStorage.removeItem(key);}catch{}}} onQueued={assignment=>{setStationJobs(previous=>{const next={...previous,[selectedStation]:assignment};try{localStorage.setItem('sidequest:result-displays',JSON.stringify(next));}catch{}return next;});}} onLaunched={assignment=>assignResult(selectedStation,assignment)}/></Suspense>:<Suspense fallback={<p className="message" role="status">Opening session…</p>}><MonitorSession key={sessionKey} owner={selectedOwner} known={!!officeSnapshot&&!officeError} fixture={officeSnapshot?.mode==='fixture'} active={active&&!officeError&&!jobsOpen&&!settingsOpen&&!launcherStation&&!actorStation} store={draftStore} onAccepted={()=>setOfficeRevision(value=>value+1)} operations={operations} memory={traceMemory} onProvider={()=>selectedStation&&openWorkstation(selectedStation)} onAttach={()=>selectedStation&&openActor(selectedStation)}/></Suspense>}</div>
  </div>;
  const officeReady = !!bindings && !assetFailure;
  const displayStations=bindings?.stations??[{id:'repository',label:'Repository viewer'}];
  const assignResult=(id:string,assignment:StationAssignment)=>{if(!displayStations.some(item=>item.id===id))return;returnTarget.current=id;monitorTabs.current.set(id,'files');setMonitorTab('files');setShowAssigned(true);setStationJobs(previous=>{const next={...previous,[id]:assignment};try{localStorage.setItem('sidequest:result-displays',JSON.stringify(next));}catch{}return next;});setRequestedJob({...assignment,requestId:Date.now()});setJobsOpen(false);setSelectedStation(id);setMode('desk');};
  const openNotification=useCallback((item:OfficeNotification)=>{if(item.stationId){selectStation(item.stationId,'trace');}else{setRequestedJob({jobId:item.jobId,projectId:item.projectId,requestId:Date.now()});openJobs();}},[selectStation,openJobs]);
  return <main className="app-shell" data-mode={mode} data-station={selectedStation??""} data-actor-station={actorStation??""} data-launcher-station={launcherStation??""}>
    <header className="app-header"><div className="brand">sidequest<span>local workspace</span></div><div className="project-label">{snapshot?.project.name ?? 'Connecting to Git…'}<span>{snapshot?.project.branch}</span></div><NotificationTray items={notifications} onSelect={openNotification} loading={!officeSnapshot&&!officeError} error={officeError} disabled={settingsOpen||jobsOpen||!!launcherStation||!!actorStation}/><button ref={settingsButton} onClick={()=>{setBoardOpen(false);setLauncherStation(null);setActorStation(null);setJobsOpen(false);setSettingsOpen(true);}}>Settings</button><button ref={jobsButton} onClick={openJobs}>Jobs</button><button disabled={refreshing} onClick={() => void refresh()}>{refreshing ? 'Reading…' : 'Refresh Git'}</button></header>
    <div className="office-area">
      {officeReady ? <SceneBoundary key={officeAttempt} onError={failScene}><Suspense fallback={<div className="scene-loading" role="status">Loading your office…</div>}><OfficeScene bindings={bindings} selectedStationId={mode === 'overview' ? null : selectedStation} onSelectStation={selectStation} onSelectBoard={openBoard} boardSelected={boardOpen} onSelectWorkstation={openWorkstation} onSelectActor={openActor} stationBadges={stationBadges} onNotification={openNotification} workElement={mode==='desk'&&!compact&&!!bindings&&!assetFailure?projectedWork:undefined} reducedMotion={reducedMotion} active={active&&!jobsOpen&&!settingsOpen} contextualCard={contextualCard} onError={failAssets} onActorState={updateActorState}/></Suspense></SceneBoundary> : null}
      {!officeReady&&mode==='overview'&&<section className="asset-gate" aria-label={officeFailure?'Office unavailable':'Office loading'}><h1>{officeFailure?.title??'Opening your office…'}</h1><p role={officeFailure?'alert':'status'}>{officeFailure?.message??'Reading the original office layout.'}</p><div className="office-recovery-actions">{officeFailure&&<button onClick={()=>void retryOffice()}>Retry office</button>}<button className="primary" ref={returnFocus} onClick={()=>{selectStation('repository','files');returnTarget.current='fallback';setShowAssigned(false);}} disabled={!snapshot||!!gitError}>Inspect local Git diff <span>↗</span></button></div>{officeFailure&&<details className="office-recovery"><summary>Recovery help</summary>{officeFailure.kind==='graphics'?<><p>Use a desktop or browser with WebGL2 support, then retry.</p><p>Close this app, then run from the Sidequest folder:</p><code>python3 sidequest.py run --browser --repo /path/to/your/git-project</code><p>Open http://127.0.0.1:5173. Git, Settings and Jobs remain available without 3D.</p></>:<><p>Retry first. If office files still cannot load, close this app and run <code>python3 sidequest.py setup</code> from the Sidequest folder, then start again.</p></>}</details>}</section>}
      {gitError && mode === 'overview' && <div className="git-banner" role="alert">{gitError}</div>}
      {mode!=='overview'&&<div className={mode==='expanded'||compact||!officeReady?'panel-layer is-expanded':'projected-work'} ref={projectedWork} inert={settingsOpen||jobsOpen||boardOpen||!!launcherStation||!!actorStation} role={mode==='expanded'&&selectedAssignment&&showAssigned&&monitorTab==='files'?'dialog':undefined} aria-modal={mode==='expanded'&&selectedAssignment&&showAssigned&&monitorTab==='files'?true:undefined} aria-label={mode==='expanded'&&selectedAssignment&&showAssigned&&monitorTab==='files'?'Computer job viewer':undefined}>{work}</div>}

      {jobsMounted&&<Suspense fallback={<div className="scene-loading" role="status">Loading jobs…</div>}><JobsBoard open={jobsOpen} active={active} onClose={closeJobs} stations={displayStations} onAssign={assignResult} requestedJob={requestedJob} viewMemory={jobViews}/></Suspense>}
      {launcherStation&&<div className="context-card-anchor" ref={launcherAnchor}><Suspense fallback={<div className="scene-loading">Reading providers…</div>}><ProviderPicker key={launcherStation} stationLabel={bindings?.stations.find(item=>item.id===launcherStation)?.label??'Workstation'} projectId={stationJobs[launcherStation]?.projectId} onClose={()=>{setLauncherStation(null);computerPicker.current?.focus();}} onConnect={()=>{setLauncherStation(null);setSettingsOpen(true);}} onChoose={provider=>{const id=launcherStation;getLauncherMemory(id).selectedProvider=provider;selectStation(id,'task');}}/></Suspense></div>}
      {actorStation&&<div className="object-modal-layer"><div className="object-modal session-modal" role="dialog" aria-modal="true" aria-label="Agent session" ref={sessionPanel}><header><h2>{bindings?.stations.find(item=>item.id===actorStation)?.label??'Figure'}</h2><button onClick={()=>{setActorStation(null);computerPicker.current?.focus();}} aria-label="Close agent session">×</button></header><Suspense fallback={<p role="status">Reading recorded sessions…</p>}><SessionCard stationId={actorStation} active={active} onCount={updateSessionCount} onFiles={assignment=>{setActorStation(null);assignResult(actorStation,assignment);}} onBrowse={()=>selectStation(actorStation,'trace')} onProvider={()=>openWorkstation(actorStation)}/></Suspense></div></div>}
      {boardOpen&&<section className="board-detail-card" role="region" aria-label="Tasks board detail"><header><h2>Tasks</h2><button aria-label="Close task detail" onClick={()=>setBoardOpen(false)}>×</button></header>{boardError?<p>Runtime unavailable</p>:!boardSnapshot?<p>Reading tasks…</p>:boardSnapshot.jobs.length?<><label className="sr-only" htmlFor="board-task">Task</label><select id="board-task" value={boardJobId} onChange={event=>setBoardJobId(event.target.value)}>{boardSnapshot.jobs.map(job=><option value={job.id} key={job.id}>{job.title}</option>)}</select><p>{boardSnapshot.mode==='fixture'?'Test fixture · ':''}{boardJob?.state.replaceAll('_',' ')??'Unavailable'} · {boardJob?.execution_profile==='local_git_inspection'?'Local inspection':'Coding task'}</p>{boardSnapshot.office_sessions?.filter(owner=>owner.job_id===boardJob?.id).map(owner=><div key={owner.station_id}><p>Recorded worker at {bindings?.stations.find(station=>station.id===owner.station_id)?.label??owner.station_id}</p><button onClick={()=>openActor(owner.station_id)}>Open session</button></div>)}<button onClick={()=>{if(boardJob?.project_id){setRequestedJob({jobId:boardJob.id,projectId:boardJob.project_id,requestId:Date.now()});}openJobs();}}>Open task</button></>:<><p>No tasks yet</p><button onClick={openJobs}>Create a task</button></>}</section>}

      {settingsOpen&&<div className="settings-layer" role="dialog" aria-modal="true" aria-label="Provider settings dialog"><Suspense fallback={<div className="scene-loading">Opening settings…</div>}><ProviderSettings discovery={providers} capabilities={runtimeCaps} onClose={()=>{setSettingsOpen(false);settingsButton.current?.focus();}} onRefresh={()=>void refreshProviders()} busy={settingsBusy}/></Suspense></div>}
    </div>
    <footer className="app-footer" data-actor-status={officeFailure?'error':actorState?.status??'loading'} data-staged-actors={actorState?.loadedActorCount??0}><select className="computer-picker" ref={computerPicker} aria-label="Office navigation" value="" onChange={event=>{const value=event.target.value;if(value==='board')openBoard();else if(value.startsWith('work:'))openWorkstation(value.slice(5));else if(value.startsWith('actor:'))openActor(value.slice(6));else if(value.startsWith('monitor:'))selectStation(value.slice(8),'trace');else if(value)selectStation(value,'files');}}><option value="">Navigate…</option><option value="board">Tasks board</option><optgroup label="Computer sessions">{displayStations.map(item=><option key={item.id} value={'monitor:'+item.id}>{item.label}</option>)}</optgroup><optgroup label="Computer files">{displayStations.map(item=><option key={item.id} value={item.id}>{item.label}</option>)}</optgroup><optgroup label="Workstations">{displayStations.map(item=><option key={item.id} value={'work:'+item.id}>{item.label}</option>)}</optgroup><optgroup label="Staged figures">{displayStations.map(item=><option key={item.id} value={'actor:'+item.id}>{item.label}</option>)}</optgroup></select><span className="stage-status" title="Original staged poses; recorded runtime ownership is separate from provider connectivity.">{officeFailure?'Office unavailable':actorState?.status==='ready'?`${officeSnapshot?.mode==='fixture'?'Test fixture · ':''}${sessionCount===null?'Sessions unchecked':sessionCount?sessionCount+' recorded sessions':'No sessions'}`:actorState?.status==='error'?'Figures unavailable':'Loading figures…'}</span></footer>
  </main>;
}
