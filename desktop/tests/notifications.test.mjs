import test from 'node:test';
import assert from 'node:assert/strict';
import { deriveNotifications, notificationsByStation } from '../src/notifications.ts';

const event = (id, type = 'status', message = 'Recorded result') => ({ id, type, message, at: '2026-10-14T10:00:00Z' });
const job = (patch = {}) => ({ id: 'job-1', project_id: 'project-1', title: 'Inspect source', state: 'accepted', artifact_ids: ['artifact-1'], run_ids: ['run-1'], worker_id: null,
  tasks: [{ id: 'task-1', state: 'completed', worker_id: 'worker-1', attempt_id: 'run-1' }], checks: [{ id: 'identity', state: 'pass' }], events: [event(1)], ...patch });
const owner = (patch = {}) => ({ station_id: 'parent_019', job_id: 'job-1', run_id: 'run-1', worker_id: 'worker-1', project_id: 'project-1', assigned_at: '2026-10-14T09:00:00Z', ...patch });
const snapshot = (patch = {}) => ({ v: 1, revision: 1, mode: 'local', stopped: false, projects: [{ id: 'project-1' }], jobs: [job()], office_sessions: [], ...patch });

test('completed jobs require every task completed and a nonempty passing check set; checking never means completed', () => {
  const ready = deriveNotifications(snapshot()); assert.equal(ready.length, 1); assert.equal(ready[0].kind, 'completed'); assert.equal(ready[0].label, 'Completed'); assert.equal(ready[0].stationId, null);
  for (const patch of [{ tasks: [] }, { tasks: [{ id: 'task-1', state: 'running' }] }, { checks: [] }, { checks: [{ id: 'identity', state: 'pending' }] }, { state: 'queued' }, { state: 'verifying' }]) assert.equal(deriveNotifications(snapshot({ jobs: [job(patch)] })).some(item => item.kind === 'completed'), false);
});

test('only validated persisted job/run/project/worker ownership receives a station badge', () => {
  const notifications = deriveNotifications(snapshot({ office_sessions: [owner()] })); assert.equal(notifications[0].stationId, 'parent_019'); assert.equal(notifications[0].runId, 'run-1'); assert.equal(notificationsByStation(notifications).get('parent_019').kind, 'completed');
  for (const patch of [{ project_id: 'other' }, { run_id: 'other' }, { worker_id: 'other' }, { station_id: 'parent_099' }]) assert.throws(() => deriveNotifications(snapshot({ office_sessions: [owner(patch)] })));
  const historical = deriveNotifications(snapshot({ office_sessions: [owner({ job_id: 'older-job' })] })); assert.equal(historical[0].stationId, null); assert.equal(notificationsByStation(historical).size, 0);
  for (const patch of [{ station_id: 'parent_020' }, { run_id: 'run-2' }, { worker_id: 'worker-2' }]) assert.throws(() => deriveNotifications(snapshot({ office_sessions: [owner(), owner(patch)] })));
});

test('failed, blocked, approval and warning events are attention with stable identities', () => {
  for (const state of ['failed', 'blocked', 'needs_approval']) { const items = deriveNotifications(snapshot({ jobs: [job({ state, blocked_reason: 'Review recorded state' })] })); assert.equal(items.length, 1); assert.equal(items[0].kind, 'attention'); assert.equal(items[0].id, 'job:job-1:attention'); assert.equal(items[0].detail, 'Review recorded state'); }
  const items = deriveNotifications(snapshot({ jobs: [job({ events: [event(1, 'warning', 'Retry needs review'), event(2, 'warning', 'Later warning')] })], office_sessions: [owner()] }));
  assert.deepEqual(items.map(item => item.kind), ['attention', 'completed']); assert.equal(items[0].id, 'job:job-1:warning:2'); assert.equal(notificationsByStation(items).get('parent_019').kind, 'attention');
  assert.deepEqual(deriveNotifications(snapshot({ jobs: [job({ events: [event(2, 'warning', 'Later warning'), event(1, 'warning', 'Retry needs review')] })], office_sessions: [owner()] })), items);
});

test('one task notification supplies badges to each distinct validated recorded session', () => {
  const multiJob = job({ run_ids: ['run-1', 'run-2'], tasks: [{ id: 'task-1', state: 'completed', worker_id: 'worker-1', attempt_id: 'run-1' }, { id: 'task-2', state: 'completed', worker_id: 'worker-2', attempt_id: 'run-2' }] });
  const second = owner({ station_id: 'parent_020', run_id: 'run-2', worker_id: 'worker-2' });
  const items = deriveNotifications(snapshot({ jobs: [multiJob], office_sessions: [second, owner()] }));
  assert.equal(items.length, 1); assert.equal(items[0].stationId, 'parent_019');
  assert.deepEqual(items[0].owners, [{ stationId: 'parent_019', runId: 'run-1' }, { stationId: 'parent_020', runId: 'run-2' }]);
  const badges = notificationsByStation(items); assert.equal(badges.size, 2); assert.equal(badges.get('parent_020').runId, 'run-2');
});

test('released worker ownership requires the exact retained task attempt and rejects every known conflict', () => {
  const releasedTask = { id: 'task-1', state: 'completed', worker_id: null, attempt_id: 'run-1' };
  const released = snapshot({ jobs: [job({ worker_id: null, tasks: [releasedTask] })], office_sessions: [owner()] });
  const notifications = deriveNotifications(released); assert.equal(notificationsByStation(notifications).get('parent_019').runId, 'run-1');
  for (const patch of [{ attempt_id: null }, { attempt_id: 'other-run' }, { worker_id: undefined }, { worker_id: 'wrong-worker' }]) assert.throws(() => deriveNotifications(snapshot({ jobs: [job({ tasks: [{ ...releasedTask, ...patch }] })], office_sessions: [owner()] })));
  assert.throws(() => deriveNotifications(snapshot({ jobs: [job({ worker_id: 'wrong-worker', tasks: [releasedTask] })], office_sessions: [owner()] })));
  assert.throws(() => deriveNotifications(snapshot({ jobs: [job({ worker_id: 'worker-1', tasks: [{ ...releasedTask, worker_id: 'wrong-worker' }] })], office_sessions: [owner()] })));
  assert.throws(() => deriveNotifications(snapshot({ jobs: [job({ tasks: [releasedTask, { ...releasedTask, id: 'task-2' }] })], office_sessions: [owner()] })));
  const checking = deriveNotifications(snapshot({ jobs: [job({ state: 'verifying', worker_id: null, tasks: [releasedTask] })], office_sessions: [owner()] })); assert.deepEqual(checking, []);
});

test('task and failed-check attention outrank a completed result, without duplicated warning alerts', () => {
  const taskFailure = deriveNotifications(snapshot({ jobs: [job({ state: 'running', tasks: [{ id: 'task-1', state: 'failed' }] })] })); assert.equal(taskFailure[0].label, 'Failed');
  const checkFailure = deriveNotifications(snapshot({ jobs: [job({ checks: [{ id: 'identity', state: 'fail' }], events: [event(1, 'warning')] })] })); assert.equal(checkFailure.length, 1); assert.equal(checkFailure[0].label, 'Check needs attention');
});

test('fixture labels are explicit, unassigned notifications never invent station ownership', () => {
  const fixture = deriveNotifications(snapshot({ mode: 'fixture' })); assert.equal(fixture[0].fixture, true); assert.equal(notificationsByStation(fixture).size, 0); assert.equal(deriveNotifications(snapshot())[0].fixture, false);
});

test('malformed, overbound, duplicate and cross-identity records fail before projection', () => {
  for (const malformed of [null, [], {}, snapshot({ revision: -1 }), snapshot({ jobs: Array(21).fill(job()) }), snapshot({ jobs: [job(), job()] }), snapshot({ projects: [] }), snapshot({ jobs: [job({ title: 'x'.repeat(201) })] }), snapshot({ jobs: [job({ events: Array(51).fill(event(1)) })] }), snapshot({ jobs: [job({ checks: [{ id: 'identity', state: 'green' }] })] })]) assert.throws(() => deriveNotifications(malformed));
  for (const patch of [{ job_id: 'other' }, { project_id: 'other' }, { task_id: 'other' }, { at: 'yesterday' }, { id: 0 }, { type: 'script' }, { message: 'x'.repeat(16_385) }]) assert.throws(() => deriveNotifications(snapshot({ jobs: [job({ events: [{ ...event(1), ...patch }] })] })));
  assert.throws(() => deriveNotifications(snapshot({ jobs: [job({ events: [event(1), event('1')] })] })));
});

const newerJobs = () => Array.from({ length: 20 }, (_, index) => job({
  id: `newer-job-${index}`, state: 'queued', run_ids: [], tasks: [], checks: [], events: [],
}));

test('assigned runs older than the latest twenty retain completion and attention badges after worker release', () => {
  const released = job({ tasks: [{ id: 'task-1', state: 'completed', worker_id: null, attempt_id: 'run-1' }] });
  const state = snapshot({ jobs: newerJobs(), office_jobs: [released], office_sessions: [owner()] });
  const items = deriveNotifications(state);
  assert.equal(items.length, 1);
  assert.equal(items[0].jobId, 'job-1');
  assert.equal(notificationsByStation(items).get('parent_019')?.kind, 'completed');
  const attention = deriveNotifications({ ...state, office_jobs: [{ ...released, state: 'blocked', blocked_reason: 'Review this older run' }] });
  assert.equal(attention[0]?.detail, 'Review this older run');
  assert.equal(notificationsByStation(attention).get('parent_019')?.kind, 'attention');
});

test('older active unassigned jobs retain attention without inventing station ownership', () => {
  const items = deriveNotifications(snapshot({ jobs: newerJobs(), office_jobs: [job({
    state: 'running', tasks: [{ id: 'task-1', state: 'running', worker_id: 'worker-1', attempt_id: 'run-1' }],
    checks: [], events: [event(1, 'warning', 'Older active run needs input')],
  })] }));
  assert.equal(items.length, 1);
  assert.equal(items[0].detail, 'Older active run needs input');
  assert.equal(notificationsByStation(items).size, 0);
});

test('recent and supplemental job projections deduplicate equivalent records and reject conflicting state', () => {
  // Property order is not identity. Runtime fields unrelated to notifications may differ.
  const copy = { events: [event(1)], ...job(), budget_usd: 5 };
  const items = deriveNotifications(snapshot({ office_jobs: [copy], office_sessions: [owner()] }));
  assert.equal(items.length, 1);
  assert.equal(notificationsByStation(items).size, 1);
  for (const patch of [{ state: 'blocked' }, { worker_id: 'other-worker' }, { run_ids: [] }, { events: [event(1, 'warning')] }]) {
    assert.throws(() => deriveNotifications(snapshot({ office_jobs: [job(patch)] })));
  }
});

test('supplemental records are bounded and validated before any notification is projected', () => {
  for (const malformed of [null, {}, [job(), job()], Array.from({ length: 125 }, (_, index) => job({ id: `old-${index}` })),
    [job({ project_id: 'other-project' })], [job({ checks: [{ id: 'identity', state: 'green' }] })],
    [job({ events: [{ ...event(1), project_id: 'other-project' }] })]]) {
    assert.throws(() => deriveNotifications(snapshot({ office_jobs: malformed })));
  }
  const atBound = Array.from({ length: 124 }, (_, index) => job({ id: `old-${index}`, state: 'queued', tasks: [], checks: [], events: [] }));
  assert.equal(deriveNotifications(snapshot({ jobs: [], office_jobs: atBound })).length, 0);
});

test('supplemental snapshots require complete project, run, task and worker identities for every recorded owner', () => {
  const released = job({ tasks: [{ id: 'task-1', state: 'completed', worker_id: null, attempt_id: 'run-1' }] });
  const state = snapshot({ jobs: newerJobs(), office_jobs: [released], office_sessions: [owner()] });
  for (const patch of [{ job_id: 'missing-job' }, { project_id: 'other-project' }, { run_id: 'wrong-run' }]) {
    assert.throws(() => deriveNotifications({ ...state, office_sessions: [owner(patch)] }));
  }
  for (const patch of [{ tasks: [] }, { run_ids: [] }, { tasks: [{ ...released.tasks[0], worker_id: 'wrong-worker' }] },
    { tasks: [{ ...released.tasks[0], attempt_id: 'wrong-run' }] }, { worker_id: 'wrong-worker' },
    { worker_id: 'worker-1', tasks: [{ ...released.tasks[0], attempt_id: 'wrong-run' }] }]) {
    assert.throws(() => deriveNotifications({ ...state, office_jobs: [{ ...released, ...patch }] }));
  }
});
