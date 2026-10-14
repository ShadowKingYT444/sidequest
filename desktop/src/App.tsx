import { Component, Suspense, lazy, useCallback, useEffect, useRef, useState, type ReactNode } from 'react';
import { bridge } from './bridge';
import type { GitDiff, Snapshot } from './types';
import { loadOfficeBindings, type OfficeBindings } from './office-bindings';
import type { EditorViews } from './DiffEditor';
const OfficeScene = lazy(() => import('./OfficeScene'));
const DiffEditor = lazy(() => import('./DiffEditor'));
const JobsBoard = lazy(() => import('./JobsBoard'));
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
  const jobsButton=useRef<HTMLButtonElement>(null);
  const views = useRef<EditorViews>(new Map());
  const requestId = useRef(0);
  const returnFocus = useRef<HTMLButtonElement | null>(null);
  const panel = useRef<HTMLDivElement>(null);
  const reducedMotion = useReducedMotion();
  const active = useVisible();
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
  const close = useCallback(() => { setMode('overview'); requestAnimationFrame(() => returnFocus.current?.focus()); }, []);
  const closeJobs=useCallback(()=>{setJobsOpen(false);requestAnimationFrame(()=>jobsButton.current?.focus());},[]);
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && mode !== 'overview') { event.preventDefault(); close(); }
      if (event.key === 'Tab' && mode === 'expanded' && panel.current) {
        const elements = Array.from(panel.current.querySelectorAll<HTMLElement>('button:not(:disabled), select, input, textarea, [tabindex="0"]')).filter(element => element.getClientRects().length);
        const first = elements[0], last = elements[elements.length - 1];
        if (event.shiftKey && (document.activeElement === first || !panel.current.contains(document.activeElement))) { event.preventDefault(); last?.focus(); }
        else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
      }
    };
    document.addEventListener('keydown', onKey); return () => document.removeEventListener('keydown', onKey);
  }, [mode, close]);
  useEffect(() => { if (mode !== 'overview') requestAnimationFrame(() => panel.current?.querySelector<HTMLButtonElement>('button')?.focus()); }, [mode]);
  const selectStation = (id: string) => { setSelectedStation(id); setMode('desk'); };
  const station = bindings?.stations.find(item => item.id === selectedStation);
  const failScene = useCallback((error: Error) => { setAssetFailure(true); setAssetStatus(`Office asset loading failed: ${error.message}`); }, []);
  const work = (
    <div className={`work-panel ${mode === 'expanded' ? 'expanded' : ''}`} ref={panel} role={mode === 'expanded' ? 'dialog' : 'region'} aria-modal={mode === 'expanded' ? true : undefined} aria-label="Computer work viewer">
      <header className="panel-header">
        <div><p className="eyebrow">{station?.label ?? 'Repository computer'} · Read-only</p><h2>{snapshot?.project.name ?? 'Local repository'}</h2></div>
        <div className="panel-actions">{mode !== 'expanded' && <button onClick={() => setMode('expanded')}>Expand</button>}<button onClick={close} aria-label="Return to office">Office <kbd>Esc</kbd></button></div>
      </header>
      <div className="revision-bar"><span>Git diff</span><span title={snapshot?.baseRevision}>{snapshot?.baseRevision.slice(0, 8)} <span aria-label="to">→</span> {snapshot?.candidateRevision.slice(0, 8)}</span><span>Committed revisions</span></div>
      <div className="work-body">
        <nav className="file-list" aria-label="Changed files"><p className="file-count">{snapshot?.files.length ?? 0} changed files</p>{snapshot?.files.map(file => <button key={file.id} className={selectedFile === file.id ? 'selected' : ''} onClick={() => setSelectedFile(file.id)} aria-pressed={selectedFile === file.id}><span className="file-status" title={file.status}>{({added: "+", deleted: "−", modified: "M", renamed: "R"} as Record<string,string>)[file.status] ?? file.status}</span><span className="file-path" title={file.path}>{file.path}</span>{file.binary && <span className="binary-tag">binary</span>}</button>)}</nav>
        <section className="editor-area" aria-label="Selected file diff">
          {selectedFile ? <div className="file-heading">{diff?.path ?? snapshot?.files.find(file => file.id === selectedFile)?.path}<span>Read-only</span></div> : null}
          {gitError ? <div className="message error" role="alert">{gitError}<button onClick={() => void refresh()}>Retry Git read</button></div> : !selectedFile ? <div className="message"><h3>No committed changes</h3><p>The selected revisions have no viewable text changes.</p></div> : diffError ? <div className="message error" role="alert">{diffError}<button onClick={() => void refresh()}>Refresh repository</button></div> : !diff ? <div className="message" role="status">Loading Git diff…</div> : diff.unavailableReason ? <div className="message"><h3>Content withheld</h3><p>{diff.unavailableReason}</p></div> : diff.binary ? <div className="message"><h3>Binary file</h3><p>This file is listed as a binary change. Its bytes are not rendered as text.</p></div> : <Suspense fallback={<div className="message" role="status">Loading diff editor…</div>}><DiffEditor diff={diff} views={views.current}/></Suspense>}
        </section>
      </div>
      <footer className="panel-footer">{snapshot?.agent.message ?? 'Agent service unavailable. No agent execution is connected.'}</footer>
    </div>
  );
  const officeReady = !!bindings && !assetFailure;
  return <main className="app-shell">
    <header className="app-header"><div className="brand">sidequest<span>local workspace</span></div><div className="project-label">{snapshot?.project.name ?? 'Connecting to Git…'}<span>{snapshot?.project.branch}</span></div><button ref={jobsButton} onClick={()=>{setMode('overview');setJobsMounted(true);setJobsOpen(true);}}>Jobs</button><button disabled={refreshing} onClick={() => void refresh()}>{refreshing ? 'Reading…' : 'Refresh Git'}</button></header>
    <div className="office-area">
      {officeReady ? <SceneBoundary onError={failScene}><Suspense fallback={<div className="scene-loading" role="status">Loading your office…</div>}><OfficeScene bindings={bindings} selectedStationId={mode === 'overview' ? null : selectedStation} onSelectStation={selectStation} childrenForStation={id => mode === 'desk' && id === selectedStation ? work : null} reducedMotion={reducedMotion} active={active} onError={failScene}/></Suspense></SceneBoundary> : <section className="asset-gate" aria-label="Office setup status"><div className="gate-marker">Office / pending assets</div><h1>{assetFailure ? 'Your office belongs here.' : 'Opening the office…'}</h1><p>{assetStatus}</p>{assetFailure && <><p className="gate-detail">Add the existing GLB export and map its monitor anchors. Blender originals stay untouched.</p><button className="primary" ref={returnFocus} onClick={() => selectStation('repository')} disabled={!snapshot || !!gitError}>Inspect local Git diff <span>→</span></button><span className="gate-note">Real repository data · no connected agent session</span></>}</section>}
      {gitError && mode === 'overview' && <div className="git-banner" role="alert">{gitError}</div>}
      {mode !== 'overview' && (mode === 'expanded' || !officeReady) && <div className={`panel-layer ${mode === 'expanded' ? 'is-expanded' : ''}`}>{work}</div>}
      {officeReady && mode === 'overview' && <nav className="station-nav" aria-label="Office computers">{bindings.stations.map(item => <button key={item.id} ref={item.id === selectedStation ? returnFocus : undefined} onClick={event => { returnFocus.current = event.currentTarget; selectStation(item.id); }}>Open {item.label}</button>)}</nav>}
      {jobsMounted&&<Suspense fallback={<div className="scene-loading" role="status">Loading jobs…</div>}><JobsBoard open={jobsOpen} active={active} onClose={closeJobs}/></Suspense>}
    </div>
    <footer className="app-footer"><span className="status-dot" aria-hidden="true"/><span>{officeReady ? 'Office ready' : 'Office assets unavailable'}</span><span className="footer-divider"/><span>Git read-only</span><span className="footer-right">Agent service unavailable · 0 UI model calls</span></footer>
  </main>;
}
