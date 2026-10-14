import { useEffect, useId, useRef, useState } from 'react';
import { bridge } from './bridge';
import type { RunEventPage, RuntimeJob, RuntimeRun } from './types';
import './RunActivity.css';

interface Props { job: RuntimeJob; active: boolean; selectedRunId?:string; expectedWorkerId?:string; contextual?:boolean }
interface RunRead { run: RuntimeRun; page: RunEventPage; readAt: string }
interface ReadState { key: string; data?: RunRead; loading: boolean; error: string }
const runStates = new Set(['running', 'completed', 'failed', 'cancelled', 'ambiguous']);
const eventTypes = new Set(['status', 'tool_started', 'tool_finished', 'output', 'warning', 'usage']);
const label = (value: string) => value.replaceAll('_', ' ');
const boundedString = (value: unknown, limit = 200): value is string => typeof value === 'string' && value.length > 0 && value.length <= limit;
const nullableString = (value: unknown): value is string | null => value === null || boundedString(value);
const tokenCount = (value: unknown): value is number | null => value === null || (typeof value === 'number' && Number.isSafeInteger(value) && value >= 0);

export function requireRun(value: unknown, job: RuntimeJob, runId: string): RuntimeRun {
  const reply = value as { v?: number; run?: RuntimeRun } | null;
  const run = reply?.run;
  if (reply?.v !== 1 || !run || run.id !== runId || run.job_id !== job.id || !boundedString(run.task_id)
    || (job.tasks?.length && !job.tasks.some(task => task.id === run.task_id))
    || !nullableString(run.worker_id) || !Number.isSafeInteger(run.attempt) || run.attempt < 1
    || !runStates.has(run.state) || !nullableString(run.model) || !nullableString(run.effort)
    || !boundedString(run.started_at, 128) || !(run.ended_at === null || boundedString(run.ended_at, 128))
    || !run.usage || typeof run.usage.uncertain !== 'boolean'
    || ![run.usage.input_tokens, run.usage.cached_input_tokens, run.usage.output_tokens, run.usage.total_tokens].every(tokenCount)
    || !(run.usage.cost_usd === null || (typeof run.usage.cost_usd === 'number' && Number.isFinite(run.usage.cost_usd) && run.usage.cost_usd >= 0))) {
    throw new Error('The run response does not match the selected job.');
  }
  return run;
}

export function requireEvents(value: unknown, run: RuntimeRun, afterSeq: number): RunEventPage {
  const page = value as RunEventPage | null;
  if (!page || page.v !== 1 || page.run_id !== run.id || !Array.isArray(page.items) || page.items.length > 200
    || typeof page.has_more !== 'boolean' || !Number.isSafeInteger(page.next_after_seq)) {
    throw new Error('The event response does not match the selected run.');
  }
  let previous = afterSeq;
  for (const event of page.items) {
    if (!event || !Number.isSafeInteger(event.seq) || event.seq <= previous || event.job_id !== run.job_id
      || event.task_id !== run.task_id || !boundedString(event.at, 128) || !eventTypes.has(event.type)
      || typeof event.message !== 'string' || event.message.length > 16_384 || !nullableString(event.artifact_id)) {
      throw new Error('The event page has an invalid identity or sequence.');
    }
    previous = event.seq;
  }
  if (page.next_after_seq !== previous || (page.has_more && previous === afterSeq)) {
    throw new Error('The event page has an invalid continuation.');
  }
  return page;
}

function timestamp(value: string | null) {
  if (!value) return '—';
  const date = new Date(value);
  return Number.isFinite(date.getTime()) ? date.toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'medium' }) : 'Unavailable';
}
function count(value: number | null) { return value === null ? 'Unknown' : value.toLocaleString(); }
function cost(value: number | string | null) { return typeof value !== 'number' ? 'Unknown' : `$${value.toLocaleString(undefined, { maximumFractionDigits: 6 })}`; }

export default function RunActivity({ job, active, selectedRunId, expectedWorkerId, contextual=false }: Props) {
  const controlId = useId();
  const ids = [...new Set(job.run_ids ?? [])].slice(-100);
  const [selection, setSelection] = useState({ jobId: job.id, runId: ids.at(-1) ?? '' });
  const runId = selectedRunId ? (ids.includes(selectedRunId)?selectedRunId:'') : selection.jobId === job.id && ids.includes(selection.runId) ? selection.runId : ids.at(-1) ?? '';
  const selectionKey = `${job.id}:${runId}`;
  const [cursor, setCursor] = useState({ key: selectionKey, afterSeq: 0, previous: [] as number[] });
  const afterSeq = cursor.key === selectionKey ? cursor.afterSeq : 0;
  const previousPages = cursor.key === selectionKey ? cursor.previous : [];
  const readKey = `${selectionKey}:${afterSeq}`;
  const [read, setRead] = useState<ReadState>({ key: '', loading: false, error: '' });
  const [refresh, setRefresh] = useState(0);
  const [visible, setVisible] = useState(!document.hidden);
  const generation = useRef(0);
  const currentJob = useRef(job);
  currentJob.current = job;
  const current = read.key === readKey ? read : undefined;
  const data = current?.data;
  const run = data?.run;
  const localInspection = job.execution_profile === 'local_git_inspection';
  const codexProfile = job.execution_profile === 'codex_session';

  useEffect(() => {
    const changed = () => setVisible(!document.hidden);
    document.addEventListener('visibilitychange', changed);
    return () => document.removeEventListener('visibilitychange', changed);
  }, []);

  useEffect(() => {
    if (!runId || !active || !visible) return;
    const request = ++generation.current;
    let alive = true;
    let timer: ReturnType<typeof setTimeout> | undefined;
    const selectedJob = currentJob.current;
    async function load() {
      setRead(previous => ({ key: readKey, data: previous.key === readKey ? previous.data : undefined, loading: true, error: '' }));
      let poll = true;
      try {
        const [runReply, eventReply] = await Promise.all([
          bridge.runtime.runInfo(runId), bridge.runtime.runEvents(runId, afterSeq),
        ]);
        if (!alive || request !== generation.current) return;
        const selectedRun = requireRun(runReply, selectedJob, runId);
        if(expectedWorkerId&&selectedRun.worker_id!==expectedWorkerId)throw new Error('Recorded session worker identity changed.');
        const page = requireEvents(eventReply, selectedRun, afterSeq);
        setRead({ key: readKey, data: { run: selectedRun, page, readAt: new Date().toISOString() }, loading: false, error: '' });
        poll = selectedRun.state === 'running' && selectedRun.ended_at === null;
      } catch (reason) {
        if (!alive || request !== generation.current) return;
        setRead(previous => ({ key: readKey, data: previous.key === readKey ? previous.data : undefined, loading: false,
          error: reason instanceof Error ? reason.message : 'Run activity is unavailable.' }));
      }
      if (alive && request === generation.current && poll) timer = setTimeout(() => void load(), 5000);
    }
    void load();
    return () => { alive = false; generation.current++; clearTimeout(timer); };
  }, [runId, readKey, afterSeq, active, visible, refresh, expectedWorkerId]);

  const chooseRun = (id: string) => {
    setSelection({ jobId: job.id, runId: id });
    setCursor({ key: `${job.id}:${id}`, afterSeq: 0, previous: [] });
  };

  return <section className={'run-activity'+(contextual?' is-contextual':'')} aria-label="Run activity" data-run-id={runId || undefined}>
    <header className="run-activity-heading">
      <div><h4>{contextual?'Conversation & events':'Run activity'}</h4><span className="run-activity-profile">{localInspection ? 'Local Git inspection' : codexProfile ? 'Codex worker profile' : 'Execution profile unavailable'}</span></div>
      {runId && <button type="button" className="run-activity-refresh" disabled={!active || !visible || current?.loading} onClick={() => setRefresh(value => value + 1)}>Refresh</button>}
    </header>
    {!runId ? <p className="run-activity-empty">No run attempts recorded yet.</p> : <>
      <div className="run-activity-toolbar">
        <label htmlFor={controlId}>Run</label>
        <select id={controlId} value={runId} disabled={!!selectedRunId} onChange={event => chooseRun(event.target.value)}>
          {ids.map((id, index) => <option key={id} value={id}>Run {index + 1} · {id.slice(0, 8)}</option>)}
        </select>
        {run && <span className="run-activity-state" data-state={run.state}>{label(run.state)}</span>}
        {current?.loading && <span className="run-activity-loading" role="status">{data ? 'Refreshing…' : 'Loading run…'}</span>}
        {!active || !visible ? <span className="run-activity-loading">Updates paused</span> : null}
      </div>
      {current?.error && <div className="run-activity-error" role="alert"><span>{current.error}</span>{data && <small>Last known activity · {timestamp(data.readAt)}</small>}</div>}
      {run && <>
        <dl className="run-activity-summary">
          <div><dt>Worker</dt><dd title={run.worker_id ?? undefined}>{run.worker_id ?? 'Unassigned'}</dd></div>
          <div><dt>Attempt</dt><dd>{run.attempt}</dd></div>
          <div><dt>Model</dt><dd>{localInspection ? 'No model call' : run.model ?? 'Not recorded'}</dd></div>
          <div><dt>Effort</dt><dd>{localInspection ? '—' : run.effort ?? 'Not recorded'}</dd></div>
        </dl>
        <p className="run-activity-note">Recorded usage: {count(run.usage.total_tokens)} tokens · {cost(run.usage.cost_usd)}{run.usage.uncertain?' · uncertain':''}</p>
        <details className="run-activity-details"><summary>Run details</summary><dl>
          <div><dt>Run</dt><dd>{run.id}</dd></div><div><dt>Task</dt><dd>{run.task_id}</dd></div>
          <div><dt>Recorded model</dt><dd>{run.model ?? 'Not recorded'}</dd></div><div><dt>Recorded effort</dt><dd>{run.effort ?? 'Not recorded'}</dd></div>
          <div><dt>Started</dt><dd><time dateTime={run.started_at ?? undefined}>{timestamp(run.started_at)}</time></dd></div>
          <div><dt>Ended</dt><dd>{run.ended_at ? <time dateTime={run.ended_at}>{timestamp(run.ended_at)}</time> : 'Not recorded'}</dd></div>
          <div><dt>Input tokens</dt><dd>{count(run.usage.input_tokens)}</dd></div><div><dt>Cached input</dt><dd>{count(run.usage.cached_input_tokens)}</dd></div>
          <div><dt>Output tokens</dt><dd>{count(run.usage.output_tokens)}</dd></div><div><dt>Total tokens</dt><dd>{count(run.usage.total_tokens)}</dd></div>
          <div><dt>Cost</dt><dd>{cost(run.usage.cost_usd)}{run.usage.uncertain ? ' · uncertain' : ''}</dd></div>
        </dl></details>
        <div className="run-activity-events-header"><h5>Events</h5><small>{data!.page.items.length} on this page</small></div>
        {data!.page.items.length ? <ol className="run-activity-timeline" aria-label="Persisted run events" tabIndex={0}>
          {data!.page.items.map(event => <li key={event.seq} data-event-seq={event.seq}>
            <div className="run-activity-event-meta"><span>{label(event.type)}</span><time dateTime={event.at} title={event.at}>{timestamp(event.at)}</time><span>#{event.seq}</span></div>
            <p>{event.message}</p>
          </li>)}
        </ol> : <p className="run-activity-empty">No events recorded on this page.</p>}
        <div className="run-activity-pages">
          <button type="button" disabled={!previousPages.length || current?.loading || !active || !visible} onClick={() => setCursor({ key: selectionKey, afterSeq: previousPages.at(-1)!, previous: previousPages.slice(0, -1) })}>Previous events</button>
          <button type="button" disabled={!data!.page.has_more || current?.loading || !active || !visible} onClick={() => setCursor({ key: selectionKey, afterSeq: data!.page.next_after_seq, previous: [...previousPages, afterSeq] })}>More events</button>
        </div>
      </>}
      <p className="run-activity-note">{localInspection ? 'Deterministic local work. No provider inference.' : codexProfile ? 'Persisted runtime records. Provider turns are not verified in this view.' : 'Persisted runtime records. Provider execution is unverified.'}</p>
    </>}
  </section>;
}
