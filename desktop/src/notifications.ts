/** Read-only notification projections. Ownership is never inferred from staged art. */
export interface OfficeNotification {
  id: string;
  kind: 'completed' | 'attention';
  label: string;
  title: string;
  detail: string;
  jobId: string;
  projectId: string;
  stationId: string | null;
  runId: string | null;
  owners: readonly { stationId: string; runId: string }[];
  occurredAt: string | null;
  fixture: boolean;
}

type Row = Record<string, unknown>;
const jobStates = new Set(['queued', 'running', 'verifying', 'needs_approval', 'accepted', 'completed', 'blocked', 'failed', 'paused', 'cancelled']);
const taskStates = new Set([...jobStates].filter(state => state !== 'accepted'));
const checkStates = new Set(['pass', 'fail', 'blocked', 'pending']);
const eventTypes = new Set(['status', 'tool_started', 'tool_finished', 'output', 'warning', 'usage']);
const attentionStates = new Set(['failed', 'blocked', 'needs_approval']);
const identity = (value: unknown): value is string => typeof value === 'string' && /^[A-Za-z0-9][A-Za-z0-9_.:-]{0,119}$/.test(value);
const station = (value: unknown): value is string => typeof value === 'string' && /^parent_(?:00[1-9]|01[0-9]|02[0-4])$/.test(value);
const text = (value: unknown, maximum: number): value is string => typeof value === 'string' && value.length <= maximum;
const timestamp = (value: unknown): value is string => text(value, 128) && Number.isFinite(Date.parse(value));
const nullableId = (value: unknown) => value === null || value === undefined || identity(value);
function fail(): never { throw new Error('Notification records are unavailable.'); }
function row(value: unknown): Row { if (!value || typeof value !== 'object' || Array.isArray(value)) fail(); return value as Row; }
function rows(value: unknown, maximum: number): Row[] { if (!Array.isArray(value) || value.length > maximum) fail(); return value.map(row); }
function uniqueIds(items: Row[]): void { const ids = new Set(); for (const item of items) { if (!identity(item.id) || ids.has(item.id)) fail(); ids.add(item.id); } }
function ids(value: unknown, maximum: number): string[] { if (!Array.isArray(value) || value.length > maximum || !value.every(identity) || new Set(value).size !== value.length) fail(); return value; }
const compare = (left: OfficeNotification, right: OfficeNotification) =>
  Number(right.kind === 'attention') - Number(left.kind === 'attention')
  || (right.occurredAt ? Date.parse(right.occurredAt) : 0) - (left.occurredAt ? Date.parse(left.occurredAt) : 0)
  || left.id.localeCompare(right.id);

/** Reject malformed/cross-project records before displaying any notification or badge. */
export function deriveNotifications(value: unknown): OfficeNotification[] {
  const snapshot = row(value);
  if (snapshot.v !== 1 || !Number.isSafeInteger(snapshot.revision) || (snapshot.revision as number) < 0
    || !text(snapshot.mode, 64) || typeof snapshot.stopped !== 'boolean') fail();
  const projects = rows(snapshot.projects, 100), jobs = rows(snapshot.jobs, 20);
  uniqueIds(projects); uniqueIds(jobs);
  const projectIds = new Set(projects.map(project => project.id));
  const owners = rows(snapshot.office_sessions ?? [], 24);
  const ownedStations = new Set(), ownedRuns = new Set(), ownedWorkers = new Set();
  for (const owner of owners) {
    if (!station(owner.station_id) || ![owner.job_id, owner.project_id, owner.run_id, owner.worker_id].every(identity)
      || !timestamp(owner.assigned_at) || ownedStations.has(owner.station_id) || ownedRuns.has(owner.run_id) || ownedWorkers.has(owner.worker_id)) fail();
    ownedStations.add(owner.station_id); ownedRuns.add(owner.run_id); ownedWorkers.add(owner.worker_id);
  }
  const notifications: OfficeNotification[] = [];
  const validatedJobs = new Map<string, { job: Row; tasks: Row[]; runIds: string[]; checks: Row[]; events: Row[] }>();
  for (const job of jobs) {
    if (!identity(job.project_id) || !projectIds.has(job.project_id) || !text(job.title, 200) || !job.title.trim()
      || !jobStates.has(job.state as string) || !nullableId(job.worker_id)
      || !(job.blocked_reason === undefined || job.blocked_reason === null || text(job.blocked_reason, 4096))) fail();
    ids(job.artifact_ids, 100);
    const runIds = ids(job.run_ids ?? [], 100), tasks = rows(job.tasks ?? [], 100), checks = rows(job.checks, 100), events = rows(job.events, 50);
    uniqueIds(tasks); uniqueIds(checks);
    for (const task of tasks) {
      if (!taskStates.has(task.state as string) || !nullableId(task.worker_id) || !nullableId(task.attempt_id)
        || (task.job_id !== undefined && task.job_id !== job.id)) fail();
    }
    for (const check of checks) if (!checkStates.has(check.state as string) || !nullableId(check.evidence_artifact_id)
      || (check.job_id !== undefined && check.job_id !== job.id)) fail();
    const eventIds = new Set();
    for (const event of events) {
      // SQLite job-event IDs are integers; fixture adapters may expose bounded strings.
      const eventId = typeof event.id === 'number' && Number.isSafeInteger(event.id) && event.id > 0 ? String(event.id) : identity(event.id) ? event.id : null;
      if (eventId === null || eventIds.has(eventId) || !timestamp(event.at) || !eventTypes.has(event.type as string)
        || !text(event.message, 16_384) || (event.job_id !== undefined && event.job_id !== job.id)
        || (event.project_id !== undefined && event.project_id !== job.project_id)
        || (event.task_id !== undefined && !tasks.some(task => task.id === event.task_id))
        || (event.artifact_id !== undefined && event.artifact_id !== null && !identity(event.artifact_id))) fail();
      eventIds.add(eventId);
    }
    validatedJobs.set(job.id as string, { job, tasks, runIds, checks, events });
  }
  for (const owner of owners) {
    const selected = validatedJobs.get(owner.job_id as string);
    // The public snapshot contains only the latest 20 jobs. An older recorded
    // owner is not an invalid record, but cannot supply a badge without its job.
    if (!selected) continue;
    const matchingTasks = selected.tasks.filter(task => task.attempt_id === owner.run_id);
    const knownWorkerConflict = (selected.job.worker_id != null && selected.job.worker_id !== owner.worker_id)
      || matchingTasks.some(task => task.worker_id != null && task.worker_id !== owner.worker_id);
    const knownWorker = selected.job.worker_id === owner.worker_id || matchingTasks.some(task => task.worker_id === owner.worker_id);
    // A settled task can release its worker while retaining the exact attempt.
    // The persisted owner remains valid; missing linkage or a known conflict does not.
    const releasedWorker = selected.job.worker_id == null && matchingTasks.length === 1 && matchingTasks[0].worker_id === null;
    if (selected.job.project_id !== owner.project_id || !selected.runIds.includes(owner.run_id as string)
      || matchingTasks.length > 1 || knownWorkerConflict || !(knownWorker || releasedWorker)) fail();
  }
  for (const { job, tasks, checks, events } of validatedJobs.values()) {
    const jobOwners = owners.filter(item => item.job_id === job.id).sort((a, b) => (a.station_id as string).localeCompare(b.station_id as string));
    const owner = jobOwners[0];
    const sortedEvents = [...events].sort((a, b) => Date.parse(b.at as string) - Date.parse(a.at as string)
      || (typeof a.id === 'number' && typeof b.id === 'number' ? b.id - a.id : String(b.id).localeCompare(String(a.id))));
    const warning = sortedEvents.find(event => event.type === 'warning');
    const taskAttention = tasks.find(task => attentionStates.has(task.state as string));
    const attentionState = attentionStates.has(job.state as string) ? job.state : taskAttention?.state;
    const failedCheck = checks.some(check => check.state === 'fail' || check.state === 'blocked');
    const common = {
      title: job.title as string, jobId: job.id as string, projectId: job.project_id as string,
      stationId: owner?.station_id as string ?? null, runId: owner?.run_id as string ?? null,
      owners: jobOwners.map(item => ({ stationId: item.station_id as string, runId: item.run_id as string })),
      fixture: snapshot.mode === 'fixture',
    };
    const ready = tasks.length > 0 && tasks.every(task => task.state === 'completed') && checks.length > 0 && checks.every(check => check.state === 'pass');
    // Passing run/check evidence does not finalize a job that is still checking.
    if (ready && ['accepted', 'completed'].includes(job.state as string)) {
      notifications.push({ ...common, id: `job:${job.id}:completed`, kind: 'completed', label: 'Completed',
        detail: 'Tasks completed and checks passed.', occurredAt: sortedEvents[0]?.at as string ?? null });
    }
    if (attentionState || failedCheck) {
      const label = attentionState === 'needs_approval' ? 'Approval needed' : attentionState === 'blocked' ? 'Blocked' : attentionState === 'failed' ? 'Failed' : 'Check needs attention';
      notifications.push({ ...common, id: `job:${job.id}:attention`, kind: 'attention', label,
        detail: typeof job.blocked_reason === 'string' && job.blocked_reason ? job.blocked_reason : label === 'Approval needed' ? 'Review this task before it can continue.' : 'Open this task to review its recorded state.',
        occurredAt: sortedEvents[0]?.at as string ?? null });
    } else if (warning) {
      notifications.push({ ...common, id: `job:${job.id}:warning:${warning.id}`, kind: 'attention', label: 'Needs attention', detail: warning.message as string,
        occurredAt: warning.at as string });
    }
  }
  return notifications.sort(compare);
}

/** One status per explicitly owned station; attention takes precedence over completion. */
export function notificationsByStation(items: readonly OfficeNotification[]): ReadonlyMap<string, OfficeNotification> {
  const result = new Map<string, OfficeNotification>();
  for (const item of [...items].sort(compare)) for (const owner of item.owners) {
    if (station(owner.stationId) && identity(owner.runId) && !result.has(owner.stationId)) result.set(owner.stationId, { ...item, stationId: owner.stationId, runId: owner.runId });
  }
  return result;
}
