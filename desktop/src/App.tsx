import { Component, Suspense, lazy, useCallback, useEffect, useRef, useState, type ReactNode } from 'react';
import { bridge } from './bridge';
import type { GitDiff, JobView, ProviderDiscovery, RuntimeCapabilities, Snapshot, StationAssignment } from './types';
import { loadOfficeBindings, type OfficeBindings } from './office-bindings';
import type { EditorViews } from './DiffEditor';
const OfficeScene = lazy(() => import('./OfficeScene'));
const DiffEditor = lazy(() => import('./DiffEditor'));
const JobsBoard = lazy(() => import('./JobsBoard'));
const ProviderSettings=lazy(()=>import('./ProviderSettings'));
type Mode = 'overview' | 'desk' | 'expanded';
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
  const [assetStatus, setAssetStatus] = useState('Loading office bindings…');
  const [assetFailure, setAssetFailure] = useState(false);
  const [selectedStation, setSelectedStation] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [diff, setDiff] = useState<GitDiff | null>(null);
  const [diffError, setDiffError] = useState<string | null>(null);
  const [mode, setMode] = useState<Mode>('overview');
  const [jobsOpen,setJobsOpen]=useState(false);
  const [jobsMounted,setJobsMounted]=useState(false);
  const [settingsOpen,setSettingsOpen]=useState(false);
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
  const refreshProviders=useCallback(async()=>{setSettingsBusy(true);const results=await Promise.allSettled([bridge.providers(),bridge.runtime.capabilities()]);if(results[0].status==='fulfilled')setProviders(results[0].value);if(results[1].status==='fulfilled')setRuntimeCaps(results[1].value);else setRuntimeCaps(null);setSettingsBusy(false);},[]);
  useEffect(()=>{if(!settingsOpen)return;void refreshProviders();const escape=(event:KeyboardEvent)=>{if(event.key==='Escape'){event.preventDefault();setSettingsOpen(false);settingsButton.current?.focus();}if(event.key==='Tab'){const layer=document.querySelector('.settings-layer');const items=Array.from(layer?.querySelectorAll<HTMLElement>('button:not(:disabled),input,select,[tabindex="0"]')??[]).filter(item=>item.getClientRects().length);const first=items[0],last=items.at(-1);if(event.shiftKey&&(document.activeElement===first||!layer?.contains(document.activeElement))){event.preventDefault();last?.focus();}else if(!event.shiftKey&&(document.activeElement===last||!layer?.contains(document.activeElement))){event.preventDefault();first?.focus();}}};document.addEventListener('keydown',escape);return()=>document.removeEventListener('keydown',escape);},[settingsOpen,refreshProviders]);
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
    loadOfficeBindings().then(data => { if (alive) { setBindings(data); setAssetStatus('Office bindings loaded'); } }).catch(() => {
      if (alive) { setAssetFailure(true); setAssetStatus('The completed office GLB and monitor bindings are not available in this checkout.'); }
    });
    return () => { alive = false; };
  }, []);
  useEffect(() => {
    if (!selectedFile || mode === 'overview') return;
    const generation = ++requestId.current; setDiff(null); setDiffError(null);
    bridge.diff(selectedFile).then(data => { if (generation === requestId.current) setDiff(data); }).catch(error => {
      if (generation === requestId.current) setDiffError(error instanceof Error ? error.message : 'Could not load this diff.');
    });
    return () => { ++requestId.current; };
  }, [selectedFile, readVersion, snapshot?.candidateRevision, mode === 'overview']);
  const close = useCallback(() => { setMode('overview'); requestAnimationFrame(() => {const target=returnTarget.current==='fallback'?returnFocus.current:Array.from(document.querySelectorAll<HTMLButtonElement>('.station-nav button')).find(item=>item.dataset.stationId===returnTarget.current);(target??returnFocus.current)?.focus();}); }, []);
  const closeJobs=useCallback(()=>{setJobsOpen(false);requestAnimationFrame(()=>jobsButton.current?.focus());},[]);
  const openJobs=useCallback(()=>{setMode('overview');setJobsMounted(true);setJobsOpen(true);},[]);
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if(settingsOpen||jobsOpen)return;
      if (event.key === 'Escape' && mode !== 'overview') { event.preventDefault(); close(); }
      if (event.key === 'Tab' && mode === 'expanded' && projectedWork.current) {
        const elements = Array.from(projectedWork.current.querySelectorAll<HTMLElement>('button:not(:disabled), select, input, textarea, [tabindex="0"]')).filter(element => element.getClientRects().length);
        const first = elements[0], last = elements[elements.length - 1];
        if (event.shiftKey && (document.activeElement === first || !projectedWork.current.contains(document.activeElement))) { event.preventDefault(); last?.focus(); }
        else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
      }
    };
    document.addEventListener('keydown', onKey); return () => document.removeEventListener('keydown', onKey);
  }, [mode, close,settingsOpen,jobsOpen]);
  useEffect(() => { if (mode !== 'overview') requestAnimationFrame(() => projectedWork.current?.querySelector<HTMLButtonElement>('button')?.focus()); }, [mode]);
  const selectStation = (id: string) => {returnTarget.current=id;setShowAssigned(true); setSelectedStation(id);setJobsOpen(false); setMode('desk'); };
  useEffect(()=>{if(mode==='expanded'||compact||!bindings||assetFailure)projectedWork.current?.removeAttribute('style');},[mode,compact,bindings,assetFailure]);
  const station = bindings?.stations.find(item => item.id === selectedStation);
  const stationLabel=station?.label??(selectedStation&&selectedStation!=='repository'?`Computer ${selectedStation.split('-').at(-1)?.padStart(2,'0')}`:'Repository computer');
  const failScene = useCallback((error: Error) => { setAssetFailure(true); setAssetStatus(`Office asset loading failed: ${error.message}`); }, []);
  const selectedAssignment=selectedStation&&Object.hasOwn(stationJobs,selectedStation)?stationJobs[selectedStation]:undefined;
  const work = selectedAssignment&&showAssigned?<Suspense fallback={<div className="message">Loading assigned job…</div>}><JobsBoard embedded open={!settingsOpen&&!jobsOpen} active={active&&!settingsOpen&&!jobsOpen} onClose={close} onExpand={mode==='expanded'?undefined:()=>setMode('expanded')} requestedJob={selectedAssignment} viewMemory={jobViews}/></Suspense>:(
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
      <footer className="panel-footer">{snapshot?.agent.message ?? 'Agent service unavailable. No agent execution is connected.'}</footer>
    </div>
  );
  const officeReady = !!bindings && !assetFailure;
  const displayStations=bindings?.stations??[{id:'repository',label:'Repository viewer'}];
  const assignResult=(id:string,assignment:StationAssignment)=>{if(!displayStations.some(item=>item.id===id))return;returnTarget.current=id;setShowAssigned(true);setStationJobs(previous=>{const next={...previous,[id]:assignment};try{localStorage.setItem('sidequest:result-displays',JSON.stringify(next));}catch{}return next;});setRequestedJob({...assignment,requestId:Date.now()});setJobsOpen(false);setSelectedStation(id);setMode('desk');};
  return <main className="app-shell" data-mode={mode} data-station={selectedStation??""}>
    <header className="app-header"><div className="brand">sidequest<span>local workspace</span></div><div className="project-label">{snapshot?.project.name ?? 'Connecting to Git…'}<span>{snapshot?.project.branch}</span></div><button ref={settingsButton} onClick={()=>{setJobsOpen(false);setSettingsOpen(true);}}>Settings</button><button ref={jobsButton} onClick={openJobs}>Jobs</button><button disabled={refreshing} onClick={() => void refresh()}>{refreshing ? 'Reading…' : 'Refresh Git'}</button></header>
    <div className="office-area">
      {officeReady ? <SceneBoundary onError={failScene}><Suspense fallback={<div className="scene-loading" role="status">Loading your office…</div>}><OfficeScene bindings={bindings} selectedStationId={mode === 'overview' ? null : selectedStation} onSelectStation={selectStation} onSelectBoard={openJobs} workElement={mode==='desk'&&!compact&&!!bindings&&!assetFailure?projectedWork:undefined} childrenForStation={()=>null} reducedMotion={reducedMotion} active={active&&!jobsOpen&&!settingsOpen} onError={failScene}/></Suspense></SceneBoundary> : null}
      {!officeReady&&mode==='overview'&&<section className="asset-gate" aria-label="Office asset pending"><p className="gate-marker">Original office assets pending</p><h1>Your office is waiting.</h1><p>The supplied office is required for desk navigation.<br/>Your local Git changes and job results are available below.</p><button className="primary" ref={returnFocus} onClick={()=>{selectStation('repository');returnTarget.current='fallback';setShowAssigned(false);}} disabled={!snapshot||!!gitError}>Inspect local Git diff <span>↗</span></button><small className="gate-note" title={assetStatus}>Original office assets have not been imported.</small></section>}
      {gitError && mode === 'overview' && <div className="git-banner" role="alert">{gitError}</div>}
      {mode!=='overview'&&<div className={mode==='expanded'||compact||!officeReady?'panel-layer is-expanded':'projected-work'} ref={projectedWork} role={mode==='expanded'&&selectedAssignment&&showAssigned?'dialog':undefined} aria-modal={mode==='expanded'&&selectedAssignment&&showAssigned?true:undefined} aria-label={mode==='expanded'&&selectedAssignment&&showAssigned?'Computer job viewer':undefined}>{work}</div>}
      {mode === 'overview' && <nav className="station-nav" aria-label="Office computers">{displayStations.map(item => <button key={item.id} data-station-id={item.id} onClick={()=>selectStation(item.id)}>Open {item.label}{Object.hasOwn(stationJobs,item.id)?' · result':''}</button>)}</nav>}
      {jobsMounted&&<Suspense fallback={<div className="scene-loading" role="status">Loading jobs…</div>}><JobsBoard open={jobsOpen} active={active} onClose={closeJobs} stations={displayStations} onAssign={assignResult} requestedJob={requestedJob} viewMemory={jobViews}/></Suspense>}
      {settingsOpen&&<div className="settings-layer" role="dialog" aria-modal="true" aria-label="Provider settings dialog"><Suspense fallback={<div className="scene-loading">Opening settings…</div>}><ProviderSettings discovery={providers} capabilities={runtimeCaps} onClose={()=>{setSettingsOpen(false);settingsButton.current?.focus();}} onRefresh={()=>void refreshProviders()} busy={settingsBusy}/></Suspense></div>}
    </div>
    <footer className="app-footer"><span className="status-dot" aria-hidden="true"/><span>{officeReady ? 'Original office' : 'Original office assets pending'}</span><span className="footer-divider"/><span>Git read-only</span><span className="footer-right">Usage unknown · 0 UI model calls</span></footer>
  </main>;
}
