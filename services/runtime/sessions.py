"""Durable local inputs and explicit follow-up intents. No provider calls here."""
from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path
import re
import stat
from datetime import datetime, timezone
from uuid import UUID, uuid4

from .models import is_codex_job_from_stored
from .policy import ErrorCode, RuntimeFault, PolicyEngine

MAX_ATTACHMENT_BYTES = 10 * 1024 * 1024
MAX_STAGED_BYTES = 25 * 1024 * 1024
MAX_SEND_BYTES = 1024 * 1024
RASTER_TYPES = {'image/png', 'image/jpeg', 'image/gif', 'image/webp'}
TEXT_TYPES = {'text/plain', 'text/markdown', 'text/csv', 'text/tab-separated-values',
              'text/x-python', 'text/javascript', 'text/typescript', 'text/css', 'text/yaml', 'text/x-yaml',
              'application/javascript', 'application/typescript',
              'application/json', 'application/x-ndjson', 'application/yaml', 'application/x-yaml',
              'application/toml', 'application/xml', 'text/xml'}
TEXT_EXTENSIONS = {'.txt','.md','.markdown','.csv','.tsv','.json','.jsonl','.yaml','.yml','.toml',
                   '.xml','.log','.ts','.tsx','.js','.jsx','.mjs','.cjs','.py','.rb','.rs','.go',
                   '.java','.c','.h','.cpp','.hpp','.cs','.css','.scss','.sql','.vue','.svelte',
                   '.swift','.kt','.diff','.patch'}


def _id(value):
    try:
        if not isinstance(value, str) or str(UUID(value)) != value:
            raise ValueError()
        return value
    except (ValueError, AttributeError):
        raise RuntimeFault(ErrorCode.INVALID_INPUT, 'A canonical UUID is required.') from None


def _now():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')


def _directory(path: Path) -> int:
    """Walk every component without following symlinks, including trusted roots."""
    path = Path(os.path.abspath(path))
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    fd = os.open('/', flags)
    try:
        for component in path.parts[1:]:
            try:
                os.mkdir(component, 0o700, dir_fd=fd)
            except FileExistsError:
                pass
            child = os.open(component, flags, dir_fd=fd)
            os.close(fd)
            fd = child
        return fd
    except OSError:
        os.close(fd)
        raise RuntimeFault(ErrorCode.POLICY_DENIED, 'Local attachment storage is unavailable or contains a symlink.') from None


def validate_bytes(name: str, media_type: str, data: bytes):
    if (not isinstance(name, str) or not name or len(name) > 240 or len(name.encode('utf-8')) > 255 or name in {'.','..'}
        or re.search(r'[\\/\x00-\x1f\x7f]', name)):
        raise RuntimeFault(ErrorCode.INVALID_INPUT, 'Attachment name must be a bounded file name.')
    if not isinstance(media_type, str) or len(data) > MAX_ATTACHMENT_BYTES:
        raise RuntimeFault(ErrorCode.INVALID_INPUT, 'Attachment exceeds the supported local file limit.')
    extension = Path(name).suffix.lower()
    media_type = _effective_type(name, media_type)
    raster = (media_type == 'image/png' and extension == '.png' and data.startswith(b'\x89PNG\r\n\x1a\n')) or (
        media_type == 'image/jpeg' and extension in {'.jpg','.jpeg'} and data.startswith(b'\xff\xd8\xff')) or (
        media_type == 'image/gif' and extension == '.gif' and data.startswith((b'GIF87a', b'GIF89a'))) or (
        media_type == 'image/webp' and extension == '.webp' and data[:4] == b'RIFF' and data[8:12] == b'WEBP')
    if media_type in RASTER_TYPES:
        if not raster:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, 'Attachment image bytes do not match its declared type.')
    elif media_type == 'application/pdf':
        if extension != '.pdf' or not data.startswith(b'%PDF-'):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, 'Attachment PDF bytes do not match its declared type.')
    elif extension in TEXT_EXTENSIONS and media_type in TEXT_TYPES | {''}:
        try:
            data.decode('utf-8', 'strict')
        except UnicodeError:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, 'Text attachments must contain UTF-8 text.') from None
        if b'\x00' in data:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, 'Binary data cannot be staged as text.')
    else:
        raise RuntimeFault(ErrorCode.INVALID_INPUT, 'This attachment type is not supported.')


def _effective_type(name, media_type):
    return media_type.lower() if media_type else {
        '.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.gif':'image/gif',
        '.webp':'image/webp','.pdf':'application/pdf',
    }.get(Path(name).suffix.lower(), 'text/plain')


class AttachmentStore:
    def __init__(self, config, store):
        self.store = store
        self.root = config.adapter_output_dir / 'session-attachments'

    @staticmethod
    def public(record):
        return {key: record[key] for key in ('id','run_id','name','media_type','size_bytes','sha256')}

    def stage(self, body):
        if not isinstance(body, dict) or set(body) != {'run_id','attachment_key','name','media_type','data_base64'}:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, 'Attachment staging fields do not match the local protocol.')
        run_id, key = _id(body['run_id']), _id(body['attachment_key'])
        self.store.get_run(run_id)
        encoded = body['data_base64']
        if not isinstance(encoded, str) or len(encoded) > ((MAX_ATTACHMENT_BYTES + 2) // 3) * 4:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, 'Attachment exceeds the supported local file limit.')
        try:
            data = base64.b64decode(encoded, validate=True)
        except (ValueError, TypeError):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, 'Attachment encoding is invalid.') from None
        if base64.b64encode(data).decode() != encoded:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, 'Attachment encoding must be canonical.')
        validate_bytes(body['name'], body['media_type'], data)
        digest = hashlib.sha256(data).hexdigest()
        fd = _directory(self.root)
        attachment_id = str(uuid4())
        try:
            with self.store.transaction() as connection:
                prior = connection.execute('SELECT * FROM session_attachments WHERE run_id=? AND attachment_key=?', (run_id,key)).fetchone()
                if prior:
                    if (prior['name'],prior['media_type'],prior['sha256']) != (body['name'],body['media_type'],digest):
                        raise RuntimeFault(ErrorCode.VERSION_CONFLICT, 'Attachment key was already used for different content.')
                    self._read(dict(prior), fd)
                    return self.public(dict(prior))
                count, total = connection.execute('SELECT COUNT(*),COALESCE(SUM(size_bytes),0) FROM session_attachments WHERE run_id=?', (run_id,)).fetchone()
                if count >= 10 or total + len(data) > MAX_STAGED_BYTES:
                    raise RuntimeFault(ErrorCode.INVALID_INPUT, 'Local session staging permits 10 files and 25 MiB total.')
                target = os.open(attachment_id, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=fd)
                try:
                    with os.fdopen(target, 'wb') as stream:
                        stream.write(data); stream.flush(); os.fsync(stream.fileno())
                    record = dict(id=attachment_id,run_id=run_id,attachment_key=key,name=body['name'],
                                  media_type=body['media_type'],size_bytes=len(data),sha256=digest,
                                  storage_key=attachment_id,created_at=_now())
                    connection.execute('INSERT INTO session_attachments VALUES (?,?,?,?,?,?,?,?,?)', tuple(record.values()))
                    self.store._bump_revision(connection)
                    os.fsync(fd)
                    return self.public(record)
                except Exception:
                    os.unlink(attachment_id, dir_fd=fd)
                    raise
        finally:
            os.close(fd)

    def _read(self, record, directory_fd=None):
        owned = directory_fd is None
        directory_fd = _directory(self.root) if owned else directory_fd
        fd = None
        try:
            _id(record['storage_key'])
            fd = os.open(record['storage_key'], os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory_fd)
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size != record['size_bytes']:
                raise RuntimeFault(ErrorCode.POLICY_DENIED, 'Staged attachment identity changed.')
            with os.fdopen(fd, 'rb') as stream:
                fd = None
                data = stream.read(MAX_ATTACHMENT_BYTES + 1)
            if len(data) != record['size_bytes'] or hashlib.sha256(data).hexdigest() != record['sha256']:
                raise RuntimeFault(ErrorCode.POLICY_DENIED, 'Staged attachment failed its digest check.')
            validate_bytes(record['name'],record['media_type'],data)
            return data
        except OSError:
            raise RuntimeFault(ErrorCode.POLICY_DENIED, 'Staged attachment cannot be read safely.') from None
        finally:
            if fd is not None: os.close(fd)
            if owned: os.close(directory_fd)

    def resolve(self, run_id, ids):
        if not isinstance(ids,list) or len(ids)>10 or any(not isinstance(i,str) for i in ids) or len(set(ids)) != len(ids):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, 'Attachment IDs must be unique and bounded.')
        records = []
        total = 0
        for attachment_id in ids:
            record = self.store.get_session_attachment(_id(attachment_id))
            if record['run_id'] != run_id:
                raise RuntimeFault(ErrorCode.POLICY_DENIED, 'Attachment belongs to a different recorded run.')
            data = self._read(record)
            effective_type = _effective_type(record['name'],record['media_type'])
            if effective_type == 'application/pdf':
                raise RuntimeFault(ErrorCode.INVALID_INPUT, 'The current provider supports raster images and UTF-8 files; PDF sending is unavailable.')
            total += len(data)
            if total > MAX_SEND_BYTES:
                raise RuntimeFault(ErrorCode.INVALID_INPUT, 'Provider attachments must total at most 1 MiB per message.')
            records.append({'attachment_id':record['id'],'name':record['name'],
                'media_type':effective_type if effective_type in RASTER_TYPES else 'text/plain',
                'size_bytes':record['size_bytes'],'sha256':record['sha256'],
                'path':str(self.root / record['storage_key'])})
        return records


class SessionStoreMixin:
    def get_session_attachment(self, attachment_id):
        with self.read_connection() as connection:
            row = connection.execute('SELECT * FROM session_attachments WHERE id=?', (_id(attachment_id),)).fetchone()
            if not row: raise RuntimeFault(ErrorCode.NOT_FOUND, 'Staged attachment was not found.')
            return dict(row)

    def command_receipt(self, command_id):
        with self.read_connection() as connection:
            row = connection.execute('SELECT response_json FROM command_results WHERE command_id=?', (_id(command_id),)).fetchone()
            if not row: return {'v':1,'found':False}
            result = {'v':1,'found':True,'command':json.loads(row['response_json'])}
            message = connection.execute('SELECT id,state,run_id FROM session_messages WHERE id=?', (command_id,)).fetchone()
            if message: result['message'] = dict(message)
            return result

    def queue_session_message(self, command_id, expected_revision, payload, *, codex_ready):
        command_id = _id(str(command_id))
        if not isinstance(payload,dict) or set(payload) != {'run_id','prompt','attachment_ids'}:
            raise RuntimeFault(ErrorCode.INVALID_INPUT, 'Session message fields do not match the protocol.')
        run_id = _id(payload['run_id'])
        prompt, attachment_ids = payload['prompt'], payload['attachment_ids']
        if not isinstance(prompt,str) or not prompt.strip() or len(prompt)>2000 or re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]',prompt):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, 'A follow-up prompt must contain 1–2000 readable characters.')
        if not isinstance(attachment_ids,list) or len(attachment_ids)>10 or any(not isinstance(i,str) for i in attachment_ids) or len(set(attachment_ids))!=len(attachment_ids):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, 'Attachment IDs must be unique and bounded.')
        for item in attachment_ids: _id(item)

        def write(connection):
            if not codex_ready or self.get_setting('stopped', False):
                raise RuntimeFault(ErrorCode.POLICY_DENIED, 'Fresh host execution readiness, consent and enforced USD limits are required.')
            row = connection.execute('SELECT a.*,t.job_id,t.objective,t.current_attempt_id,t.state AS task_state,'
                'j.project_id,j.state AS job_state,j.budget_micro,j.allowed_actions_json,'
                'p.base_revision AS project_revision,p.status AS project_status,p.policy_json '
                'FROM attempts a JOIN tasks t ON t.id=a.task_id JOIN jobs j ON j.id=t.job_id '
                'JOIN projects p ON p.id=j.project_id WHERE a.id=?', (run_id,)).fetchone()
            if not row: raise RuntimeFault(ErrorCode.NOT_FOUND, 'Recorded run was not found.')
            job = self.get_job(row['job_id'])
            if not is_codex_job_from_stored(job, job['tasks']):
                raise RuntimeFault(ErrorCode.POLICY_DENIED, 'Only a scoped coding session accepts follow-up messages.')
            for action in ('read_repo','propose_patch','run_checks'):
                PolicyEngine.assert_action_allowed(action,json.loads(row['policy_json']),json.loads(row['allowed_actions_json']))
            if (row['state']!='completed' or row['task_state']!='completed' or row['current_attempt_id']!=run_id
                or row['job_state'] not in {'verifying','accepted'} or not row['provider_thread_id'] or not row['provider_turn_id']
                or row['project_status']!='active' or row['base_revision']!=row['project_revision']):
                raise RuntimeFault(ErrorCode.POLICY_DENIED, 'Follow-up requires the current completed run, saved provider identity and unchanged source.')
            budget = self.get_budget(row['job_id'])
            if budget['uncertain'] or budget['spent_micro'] is None or budget['budget_micro']-budget['spent_micro']-budget['reserved_micro']<=0:
                raise RuntimeFault(ErrorCode.BUDGET_LIMIT, 'Known positive remaining budget is required; uncertain usage cannot authorize a new turn.')
            for attachment_id in attachment_ids:
                attachment = connection.execute('SELECT run_id FROM session_attachments WHERE id=?',(attachment_id,)).fetchone()
                if not attachment or attachment['run_id']!=run_id:
                    raise RuntimeFault(ErrorCode.POLICY_DENIED, 'Attachment is not staged for this recorded run.')
            connection.execute('INSERT INTO session_messages '
                '(id,job_id,task_id,parent_run_id,prompt,attachment_ids_json,state,created_at,previous_job_state) '
                'VALUES (?,?,?,?,?,?,?,?,?)',
                (command_id,row['job_id'],row['task_id'],run_id,prompt,json.dumps(attachment_ids),'queued',_now(),row['job_state']))
            connection.execute("UPDATE tasks SET state='queued',resume_requested=0 WHERE id=?",(row['task_id'],))
            connection.execute("UPDATE approvals SET state='stale' WHERE job_id=? AND state IN ('pending','approved')",(row['job_id'],))
            connection.execute("UPDATE jobs SET state='running',blocked_reason=NULL,updated_at=? WHERE id=?",(_now(),row['job_id']))
            self._insert_event(connection,row['job_id'],run_id,None,'status','Follow-up message queued explicitly.',None)
            self._insert_event(connection,row['job_id'],run_id,None,'output','User follow-up: '+prompt,None)
            return {'job_id':row['job_id'],'message_id':command_id}
        return self.execute_command(command_id,'session.message',payload,expected_revision,write)

    def _claim_session_message(self, connection, task_id, run_id, worker_id):
        message = connection.execute("SELECT m.*,a.provider_thread_id,a.provider_turn_id FROM session_messages m "
            "JOIN attempts a ON a.id=m.parent_run_id WHERE m.task_id=? AND m.state='queued'",(task_id,)).fetchone()
        if not message: return {}
        connection.execute("UPDATE session_messages SET state='dispatching',run_id=? WHERE id=?",(run_id,message['id']))
        self._insert_event(connection,message['job_id'],run_id,None,'output','User follow-up: '+message['prompt'],None)
        owners = connection.execute('SELECT * FROM office_sessions WHERE run_id=?', (message['parent_run_id'],)).fetchall()
        # Preserve the immutable-identity trigger: explicit follow-up clears and
        # reassigns the station atomically through the same recorded-run checks.
        connection.execute('DELETE FROM office_sessions WHERE run_id=?', (message['parent_run_id'],))
        for owner in owners:
            connection.execute('INSERT INTO office_sessions VALUES (?,?,?,?,?,?)',
                (owner['station_id'],owner['job_id'],run_id,worker_id,owner['project_id'],_now()))
        return {'followup':{'message_id':message['id'],'prompt':message['prompt']},
                'parent_run_id':message['parent_run_id'],'attachment_ids':json.loads(message['attachment_ids_json']),
                'provider_thread_id':message['provider_thread_id'],'provider_turn_id':message['provider_turn_id']}

    def settle_session_message(self, run_id):
        with self.transaction() as connection:
            run = connection.execute('SELECT state FROM attempts WHERE id=?',(run_id,)).fetchone()
            if not run: return
            changed = connection.execute("UPDATE session_messages SET state=? WHERE run_id=? AND state='dispatching'",
                ('completed' if run['state']=='completed' else 'uncertain',run_id)).rowcount
            if changed: self._bump_revision(connection)

    def reconcile_interrupted_messages(self):
        with self.transaction() as connection:
            changed = connection.execute("UPDATE session_messages SET state='uncertain' WHERE state='dispatching'").rowcount
            if changed: self._bump_revision(connection)

    def reject_unstarted_messages(self, job_id):
        """Release known undispatched intents after a failure; never touch uncertain turns."""
        with self.transaction() as connection:
            job=connection.execute('SELECT state,blocked_reason FROM jobs WHERE id=?',(job_id,)).fetchone()
            if not job or job['state'] not in {'blocked','failed','cancelled'}: return
            messages=connection.execute("SELECT m.* FROM session_messages m JOIN tasks t ON t.id=m.task_id "
                "JOIN attempts a ON a.id=m.parent_run_id WHERE m.job_id=? AND m.state='queued' "
                "AND t.current_attempt_id=m.parent_run_id AND a.state='completed'",(job_id,)).fetchall()
            for message in messages:
                connection.execute("UPDATE session_messages SET state='rejected' WHERE id=?",(message['id'],))
                if job['state']!='cancelled':
                    connection.execute("UPDATE tasks SET state='completed',worker_id=NULL,resume_requested=0 WHERE id=?",(message['task_id'],))
                    explanation='Follow-up was not dispatched. Prior task and candidate were retained. '+(job['blocked_reason'] or '')
                    connection.execute('UPDATE jobs SET state=?,outcome=?,blocked_reason=NULL,updated_at=? WHERE id=?',
                        (message['previous_job_state'],explanation,_now(),job_id))
                self._insert_event(connection,job_id,message['parent_run_id'],None,'warning',
                    'Follow-up was rejected before provider dispatch; review the retained input before sending again.',None)
            if messages: self._bump_revision(connection)

    def queued_message_jobs(self):
        with self.read_connection() as connection:
            return [row['job_id'] for row in connection.execute(
                "SELECT DISTINCT m.job_id FROM session_messages m JOIN jobs j ON j.id=m.job_id "
                "WHERE m.state='queued' AND j.state='running'").fetchall()]

    def queued_message_worker(self, task_id):
        with self.read_connection() as connection:
            row = connection.execute("SELECT a.worker_id FROM session_messages m JOIN attempts a ON a.id=m.parent_run_id "
                "WHERE m.task_id=? AND m.state='queued'",(task_id,)).fetchone()
            return row['worker_id'] if row else None
