import { useCallback, useEffect, useId, useRef, useState, type FormEvent } from 'react';
import { bridge } from './bridge';
import type { CommandReply, ProviderDiscovery, RuntimeCapabilities, RuntimeJob, RuntimeProject, RuntimeSnapshot, StationAssignment } from './types';
import ProviderTiles from './ProviderTiles';
import { PROVIDERS, providerReadiness } from './provider-readiness';
import './StationLauncher.css';

export interface StationLauncherProps {
  stationLabel: string;
  memory?: LauncherMemory;
  onUncertaintyChange?: (uncertain:boolean) => void;
  projectId?: string;
  onClose: () => void;
  onSettings: () => void;
  onQueued?: (assignment: StationAssignment) => void;
  onLaunched?: (assignment: StationAssignment) => void;
}

interface Setup { snapshot: RuntimeSnapshot; capabilities: RuntimeCapabilities; providers: ProviderDiscovery }
export interface LauncherMemory { inFlight:boolean; submissionUncertain:boolean; pendingTask:Omit<QueuedTask,'job'>|null; queued:QueuedTask|null; launchAccepted:boolean }
interface QueuedTask { assignment: StationAssignment; job: RuntimeJob; writePrefix: string; budget: string }
const jobStates=new Set(['queued','running','verifying','needs_approval','accepted','blocked','failed','paused','cancelled']);
const validJobText=(job:RuntimeJob)=>typeof job.title==='string'&&job.title.trim().length>0&&job.title.length<=200&&typeof job.state==='string'&&jobStates.has(job.state);
const validId = (value: unknown): value is string => typeof value === 'string' && /^[A-Za-z0-9][A-Za-z0-9_.:-]{0,119}$/.test(value);
const hasAction = (project: RuntimeProject | undefined, action: string) => Array.isArray(project?.policy?.allowed_actions) && project.policy.allowed_actions.includes(action);
const modelVerified = (caps: RuntimeCapabilities) => caps.worker_model?.verified === true &&
  typeof caps.worker_model.id === 'string' && !!caps.worker_model.id.trim() &&
  typeof caps.worker_model.effort === 'string' && !!caps.worker_model.effort.trim();
const codingReady = (setup: Setup) => setup.snapshot.stopped === false && setup.capabilities.features?.coding === true &&
  setup.capabilities.features.codex_session === true && modelVerified(setup.capabilities) && setup.capabilities.codex?.usd_cost_enforced === true;
const installedCodex = (setup: Setup) => setup.providers.providers.filter(provider => provider.id === 'codex' && provider.installed === true && typeof provider.binaryPath === 'string' && !!provider.binaryPath);

function assertSetup(setup: Setup) {
  const { snapshot, capabilities, providers } = setup;
  if (snapshot.v !== 1 || !Number.isSafeInteger(snapshot.revision) || snapshot.revision < 0 || typeof snapshot.stopped !== 'boolean' ||
      !Array.isArray(snapshot.projects) || !Array.isArray(snapshot.jobs) || capabilities.v !== 1 || providers.v !== 1 ||
      !Array.isArray(providers.providers) || providers.providers.length > 32) throw new Error('Local setup could not be verified.');
}

function requireProject(setup: Setup, id: string, proposals: boolean) {
  const project = setup.snapshot.projects.find(item => item.id === id);
  if (!validId(id) || !project || project.status !== 'active' || !hasAction(project, 'read_repo') || !hasAction(project, 'run_checks') || (proposals && !hasAction(project, 'propose_patch'))) {
    throw new Error('The registered repository does not permit this task.');
  }
  return project;
}

function requireReady(setup: Setup, provider: string) {
  if (provider !== 'codex' || !installedCodex(setup).length || !codingReady(setup)) throw new Error('Codex is unavailable on this host. Review agent settings.');
}

function acceptReply(reply: CommandReply) {
  if (reply.v !== 1 || reply.accepted !== true || !validId(reply.command_id) || !Number.isSafeInteger(reply.revision) || reply.revision < 0) throw new Error('The runtime did not accept this action.');
}

function validateFields(prompt: string, writePrefix: string, budget: string) {
  if (!prompt.trim() || prompt.length > 2000 || /[\u0000-\u0008\u000b\u000c\u000e-\u001f]/.test(prompt)) return 'Enter a task prompt.';
  if (!writePrefix || writePrefix.length > 240 || !writePrefix.split('/').every(part => /^[A-Za-z0-9_][A-Za-z0-9_.-]*$/.test(part)) ||
      writePrefix.split('/').some(part => ['.git', '.codex'].includes(part))) return 'Enter an allowed relative folder, such as src/components.';
  if (!/^\d{1,6}(?:\.\d{1,6})?$/.test(budget) || Number(budget) <= 0) return 'Enter a positive USD limit with up to six decimal places.';
  return '';
}

async function verifiedJob(id: string, projectId: string, budget: string): Promise<RuntimeJob> {
  if (!validId(id) || !validId(projectId)) throw new Error('Task identity was not confirmed.');
  const result = await bridge.runtime.job(id);
  if (result.v !== 1 || result.job?.id !== id || result.job.project_id !== projectId || result.job.execution_profile !== 'codex_session' || !validJobText(result.job) ||
      typeof result.job.budget_usd !== 'number' || !Number.isFinite(result.job.budget_usd) || result.job.budget_usd <= 0 || result.job.budget_usd !== Number(budget)) {
    throw new Error('Task identity, execution profile or budget was not confirmed.');
  }
  return result.job;
}

/** A desk queues one scoped task. Every grant and launch is a separate user action. */
export default function StationLauncher({ stationLabel, memory, onUncertaintyChange, projectId: initialProjectId, onClose, onSettings, onQueued, onLaunched }: StationLauncherProps) {
  const id = useId();
  const retained=useRef<LauncherMemory>(memory??{inFlight:false,submissionUncertain:false,pendingTask:null,queued:null,launchAccepted:false}).current;
  const dialog = useRef<HTMLElement>(null);
  const mounted = useRef(false);
  const locked = useRef(false);
  const close = useRef(onClose); close.current = onClose;
  const [setup, setSetup] = useState<Setup | null>(null);
  const [provider, setProvider] = useState('');
  const [projectId, setProjectId] = useState(initialProjectId ?? '');
  const [prompt, setPrompt] = useState('');
  const [writePrefix, setWritePrefix] = useState('');
  const [budget, setBudget] = useState('');
  const [queued, setQueued] = useState<QueuedTask | null>(retained.queued);
  const [pendingTask, setPendingTask] = useState<Omit<QueuedTask, 'job'> | null>(retained.pendingTask);
  const [submissionUncertain, setSubmissionUncertain] = useState(retained.submissionUncertain);
  const [launchAccepted, setLaunchAccepted] = useState(retained.launchAccepted);
  const [busy, setBusy] = useState(true);
  const [connectionFailed, setConnectionFailed] = useState(false);
  const [error, setError] = useState('');

  const readSetup = useCallback(async () => {
    const [snapshot, capabilities, providers] = await Promise.all([bridge.runtime.snapshot(), bridge.runtime.capabilities(), bridge.providers()]);
    const current = { snapshot, capabilities, providers }; assertSetup(current);
    if (mounted.current) {
      setSetup(current); setConnectionFailed(false);setPendingTask(retained.pendingTask);setSubmissionUncertain(retained.submissionUncertain);setLaunchAccepted(retained.launchAccepted);
      setProjectId(previous => current.snapshot.projects.some(project => project.id === previous) ? previous : current.snapshot.projects[0]?.id ?? '');
      setQueued(previous => {
        previous=retained.queued??previous;
        if (!previous) return previous;
        const job = current.snapshot.jobs.find(item => item.id === previous.assignment.jobId && item.project_id === previous.assignment.projectId &&
          item.execution_profile === 'codex_session' && validJobText(item) && item.budget_usd === Number(previous.budget));
        return job ? { ...previous, job } : previous;
      });
    }
    return current;
  }, []);

  useEffect(() => {
    mounted.current = true;
    void readSetup().catch(() => { if (mounted.current) { setConnectionFailed(true); setSetup(null); } }).finally(() => { if (mounted.current) setBusy(false); });
    return () => { mounted.current = false; };
  }, [readSetup]);

  useEffect(() => {
    dialog.current?.focus();
    const keyboard = (event: KeyboardEvent) => {
      if (event.key === 'Escape') { event.preventDefault(); event.stopPropagation(); close.current(); }
      if (event.key !== 'Tab') return;
      const controls = [...(dialog.current?.querySelectorAll<HTMLElement>('button:not(:disabled),input:not(:disabled),select:not(:disabled),textarea:not(:disabled),summary,[tabindex="0"]') ?? [])]
        .filter(element => !element.hidden && element.getClientRects().length > 0);
      if (!controls.length) { event.preventDefault(); dialog.current?.focus(); return; }
      const first = controls[0], last = controls[controls.length - 1], focused = document.activeElement;
      if (!dialog.current?.contains(focused) || (event.shiftKey && focused === first) || (!event.shiftKey && focused === last) || focused === dialog.current) {
        event.preventDefault(); (event.shiftKey ? last : first).focus();
      }
    };
    document.addEventListener('keydown', keyboard, true);
    return () => { document.removeEventListener('keydown', keyboard, true); };
  }, []);

  const act = async (action: () => Promise<void>) => {
    if (locked.current) return;
    locked.current = true; setBusy(true); setError('');
    try { await action(); }
    catch (failure) {
      if (mounted.current) {
        setError(failure instanceof Error ? failure.message : 'This action could not be confirmed.');
        try { await readSetup(); } catch { setConnectionFailed(true); setSetup(null); }
      }
    } finally { locked.current = false; if (mounted.current) setBusy(false); }
  };

  const selectedProjectId = queued?.assignment.projectId ?? pendingTask?.assignment.projectId ?? projectId;
  const project = setup?.snapshot.projects.find(item => item.id === selectedProjectId);
  const readiness = { discovery: setup?.providers ?? null, capabilities: setup?.capabilities ?? null, snapshot: setup?.snapshot ?? null, project, failed: connectionFailed };
  const providerStates = PROVIDERS.map(item => ({ ...item, readiness: providerReadiness(item.id, readiness) }));
  const codexState = providerStates.find(item => item.id === 'codex')!.readiness;
  const ready = !!setup && !connectionFailed && codingReady(setup) && provider === 'codex' && installedCodex(setup).length > 0 && codexState.available;
  const canPropose = hasAction(project, 'propose_patch');
  const basePolicy = project?.status === 'active' && hasAction(project, 'read_repo') && hasAction(project, 'run_checks');
  const fieldError = validateFields(prompt, writePrefix, budget);
  const scopeError = validateFields('Task', writePrefix, budget);
  const message = connectionFailed ? 'Setup unavailable' : !setup ? 'Checking providers…' : providerStates.some(item => item.readiness.available) ? 'Provider ready' : 'No providers ready';

  useEffect(() => {
    const available = PROVIDERS.filter(item => providerReadiness(item.id, {
      discovery: setup?.providers ?? null, capabilities: setup?.capabilities ?? null, snapshot: setup?.snapshot ?? null,
      project: setup?.snapshot.projects.find(item => item.id === selectedProjectId), failed: connectionFailed,
    }).available);
    setProvider(previous => available.some(item => item.id === previous) ? previous : available[0]?.id ?? '');
  }, [setup, connectionFailed, selectedProjectId]);

  const rememberUncertainty=(value:boolean)=>{
    retained.submissionUncertain=value;
    onUncertaintyChange?.(value);
    if(mounted.current)setSubmissionUncertain(value);
  };
  const submit = (event: FormEvent) => {
    event.preventDefault();
    if (locked.current || retained.inFlight || retained.submissionUncertain || retained.pendingTask || retained.queued ||
        !ready || !basePolicy || !canPropose || !projectId || fieldError || queued || pendingTask || submissionUncertain) return;
    // Reserve the shared attempt before the first await, including close/reopen.
    retained.inFlight=true;
    rememberUncertainty(true);
    const attempt = { projectId, provider, prompt, writePrefix, budget };
    const queuedCallback = onQueued;
    void act(async () => {
      let transportStarted=false;
      try {
        const current = await readSetup();
        requireReady(current, attempt.provider);
        requireProject(current, attempt.projectId, true);
        if(retained.pendingTask || retained.queued)throw new Error('Review the existing submitted task in Jobs.');
        const title = attempt.prompt.trim().split(/[\r\n]/, 1)[0].replaceAll('\t', ' ').slice(0, 120);
        transportStarted=true;
        const reply = await bridge.runtime.submitCoding(attempt.projectId, title, attempt.prompt, attempt.writePrefix, attempt.budget, current.snapshot.revision);
        if(reply?.v===1&&reply.accepted===false&&validId(reply.command_id)&&Number.isSafeInteger(reply.revision)&&reply.revision>=0)rememberUncertainty(false);
        acceptReply(reply);
        const jobId = reply.result?.job_id;
        if (!validId(jobId)) throw new Error('Submission accepted, but its task identity is unavailable. Review Jobs.');
        retained.pendingTask={assignment:{jobId,projectId:attempt.projectId},writePrefix:attempt.writePrefix,budget:attempt.budget};
        if(mounted.current)setPendingTask(retained.pendingTask);
        await readSetup();
        const job = await verifiedJob(jobId, attempt.projectId, attempt.budget);
        const assignment = { jobId, projectId: attempt.projectId };
        retained.queued={assignment,job,writePrefix:attempt.writePrefix,budget:attempt.budget};
        rememberUncertainty(false);
        if(mounted.current)setQueued(retained.queued);
        queuedCallback?.(assignment);
      } finally {
        retained.inFlight=false;
        if(!transportStarted)rememberUncertainty(false);
      }
    });
  };

  const refresh = () => void act(async () => {
    await readSetup();
    const pending=retained.pendingTask??pendingTask;
    if (pending && !queued) {
      const job = await verifiedJob(pending.assignment.jobId, pending.assignment.projectId, pending.budget);
      retained.queued={...pending,job};rememberUncertainty(false);if(mounted.current){setQueued(retained.queued);setSubmissionUncertain(false);}
      onQueued?.(pending.assignment);
    } else if (queued) {
      const job = await verifiedJob(queued.assignment.jobId, queued.assignment.projectId, queued.budget);
      if (mounted.current) setQueued({ ...queued, job });
    }
  });

  const launch = () => {
    if (!queued || launchAccepted || !ready || !canPropose || !basePolicy || queued.job.state !== 'queued') return;
    const task = queued, launchedCallback = onLaunched;
    void act(async () => {
      const current = await readSetup(); requireReady(current, 'codex'); requireProject(current, task.assignment.projectId, true);
      const job = await verifiedJob(task.assignment.jobId, task.assignment.projectId, task.budget);
      if (job.state !== 'queued') { if (mounted.current) setQueued({ ...task, job }); throw new Error('This task is no longer queued.'); }
      const reply = await bridge.runtime.runCoding(job.id, current.snapshot.revision); acceptReply(reply);
      retained.launchAccepted=true;if(mounted.current)setLaunchAccepted(true);
      launchedCallback?.(task.assignment);
      await readSetup();
      const updated = await verifiedJob(job.id, task.assignment.projectId, task.budget);
      if (mounted.current) setQueued({ ...task, job: updated });
    });
  };

  return <div className="station-launcher-backdrop" onPointerDown={event => { if (event.target === event.currentTarget) onClose(); }}>
    <section className="station-launcher" ref={dialog} tabIndex={-1} role="dialog" aria-modal="true" aria-labelledby={`${id}-title`} aria-describedby={`${id}-status`} aria-busy={busy}>
      <header className="station-launcher-header"><div><h2 id={`${id}-title`}>{launchAccepted ? 'Launch accepted' : queued ? queued.job.state === 'queued' ? 'Task queued' : 'Task status' : 'New task'}</h2><span>{stationLabel}</span></div><button type="button" className="station-launcher-close" aria-label="Close task launcher" onClick={onClose}>×</button></header>
      <div className="station-launcher-content">
        <div className="station-launcher-status"><p id={`${id}-status`} role="status">{message}</p></div>
        {error && <p className="station-launcher-error" role="alert">{error}</p>}
        {submissionUncertain && <p className="station-launcher-error" role="alert">Submission was not confirmed. Review Jobs before submitting again.</p>}
        {pendingTask && !queued && <p role="status" className="station-launcher-note">Task accepted. Refresh to verify its current state.</p>}
        {queued ? <div className="station-launcher-queued"><h3>{queued.job.title}</h3><p><span>{queued.job.state.replaceAll('_', ' ')}</span> · ${queued.budget} limit</p><div><span>Write scope</span><code>{queued.writePrefix}</code></div><div><span>Task ID</span><code>{queued.assignment.jobId}</code></div><p className="station-launcher-note">{launchAccepted ? 'Launch accepted. Follow its real status in Jobs.' : 'Queued only. Launch is a separate action.'}</p></div> : <form id={`${id}-form`} onSubmit={submit}>
          <ProviderTiles {...readiness} value={provider} onChange={setProvider} disabled={busy || !!pendingTask || submissionUncertain} />
          <details className="station-launcher-options station-launcher-setup"><summary>Provider availability</summary><dl>{providerStates.map(item => <div key={item.id}><dt>{item.name}</dt><dd>{item.readiness.reason}{item.readiness.installed && <small>Executable found · discovery does not verify a connection.</small>}</dd></div>)}</dl><button type="button" disabled={busy} onClick={() => { onClose(); onSettings(); }}>Agent settings</button></details>
          <div className="station-launcher-pickers"><label htmlFor={`${id}-project`}>Repository<select id={`${id}-project`} value={projectId} onChange={event => setProjectId(event.target.value)} disabled={busy || !!pendingTask || submissionUncertain}>{!projectId && <option value="">No registered repository</option>}{setup?.snapshot.projects.map(item => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label></div>
          <label htmlFor={`${id}-prompt`}>Prompt<textarea id={`${id}-prompt`} placeholder="What should this agent work on?" rows={2} maxLength={2000} value={prompt} onChange={event => setPrompt(event.target.value)} disabled={busy || !!pendingTask || submissionUncertain} required /></label>
          <details className="station-launcher-options"><summary>Scope and spending<span>{scopeError ? 'Required' : 'Review'}</span></summary><div className="station-launcher-scope"><label htmlFor={`${id}-scope`}>Allowed folder<input id={`${id}-scope`} placeholder="src/components" maxLength={240} value={writePrefix} onChange={event => setWritePrefix(event.target.value)} disabled={busy || !!pendingTask || submissionUncertain} required /></label><label htmlFor={`${id}-budget`}>USD limit<input id={`${id}-budget`} placeholder="0.00" inputMode="decimal" maxLength={13} value={budget} onChange={event => setBudget(event.target.value)} disabled={busy || !!pendingTask || submissionUncertain} required /></label></div>{scopeError && (writePrefix || budget) && <p className="station-launcher-field-note">{scopeError}</p>}</details>
          {!canPropose && codexState.status === 'permission_needed' && basePolicy && <div className="station-launcher-permission"><button type="button" disabled={busy || !projectId || !!pendingTask || submissionUncertain} onClick={() => void act(async () => { const current = await readSetup(); requireReady(current, 'codex'); requireProject(current, projectId, false); const reply = await bridge.runtime.enableCoding(projectId, current.snapshot.revision); acceptReply(reply); await readSetup(); })}>Allow candidate proposals</button></div>}
          <p className="station-launcher-note">Submit queues this task. Launch it separately.</p>
        </form>}
      </div>
      <footer className="station-launcher-footer"><button type="button" disabled={busy} onClick={refresh}>Refresh setup</button>{queued ? <button type="button" className="station-launcher-primary" disabled={busy || !ready || !basePolicy || !canPropose || launchAccepted || queued.job.state !== 'queued'} onClick={launch}>{launchAccepted ? 'Launch accepted' : 'Launch task'}</button> : <button type="submit" form={`${id}-form`} className="station-launcher-primary" disabled={busy || !ready || !basePolicy || !canPropose || !!fieldError || !!pendingTask || submissionUncertain}>Submit task</button>}</footer>
    </section>
  </div>;
}
