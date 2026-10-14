"""Deterministic protocol/store fixtures. These tests never call a real provider."""
from __future__ import annotations

import base64
import asyncio
import json
import hashlib
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
from uuid import uuid4

import httpx

from services.runtime.api import create_app
from services.runtime.artifacts import ArtifactStore
from services.runtime.scheduler import Scheduler
from services.runtime.config import codex_configuration_fingerprint
from services.runtime.policy import ErrorCode, RuntimeFault
from services.runtime.store import RuntimeStore, utc_now
from services.runtime.models import CandidateCreate, canonical_json
from services.runtime.tests.test_codex_lifecycle import CAPABILITY, FakeScheduler, codex_config, create_codex_job
from services.runtime.tests.test_support import open_fixture

TOKEN = 'session-transport-fixture-' + 'x' * 40


class SessionTransportTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='sidequest-session-fixture-')
        initial, config, self.project_id = open_fixture(Path(self.temp.name))
        initial.close()
        self.config = codex_config(config)
        self.store = RuntimeStore(self.config)
        self.job_id = create_codex_job(self.store, self.project_id)
        self.store.set_job_command(str(uuid4()), self.store.revision, 'job.run', self.job_id, codex_ready=True)
        worker = self.store.create_worker('builder', configuration={'host_codex': True})
        claim = self.store.claim_ready_task(worker, 10_000, job_id=self.job_id)
        self.run_id = claim['attempt_id']
        self.task_id = claim['task_id']
        self.store.record_provider_session(self.run_id, provider_thread_id='thread-fixture',
                                          provider_turn_id='turn-fixture', model='fixture-model', effort='high')
        # Synthetic known usage for a fixture; native Codex always reports unknown USD today.
        self.store.settle_attempt(self.run_id, cost_micro=0, uncertain=False, state='completed')
        self.store.finalize_job(self.job_id, 'verifying', 'Protocol fixture completed.')
        self.store.assign_office_session(str(uuid4()), self.store.revision, 'parent_019', self.job_id, self.run_id)
        self.store.record_codex_readiness(str(uuid4()), self.store.revision,
            config_sha256=codex_configuration_fingerprint(self.config), capability=CAPABILITY, refreshed_at=utc_now())
        self.scheduler = FakeScheduler()
        self.app = create_app(self.config, token=TOKEN, store=self.store, scheduler=self.scheduler)
        self.http = httpx.AsyncClient(transport=httpx.ASGITransport(app=self.app), base_url='http://runtime')
        self.auth = {'Authorization': 'Bearer ' + TOKEN}

    async def asyncTearDown(self):
        await self.http.aclose()
        self.store.close()
        self.temp.cleanup()

    async def stage(self, **patch):
        body = {'run_id': self.run_id, 'attachment_key': str(uuid4()), 'name': 'notes.txt',
                'media_type': 'text/plain', 'data_base64': base64.b64encode(b'fixture notes').decode()}
        body.update(patch)
        return body, await self.http.post('/v1/session-attachments', headers=self.auth, json=body)

    def message(self, attachment_ids=None, **patch):
        result = {'v': 1, 'command_id': str(uuid4()), 'type': 'session.message',
                  'expected_revision': self.store.revision,
                  'payload': {'run_id': self.run_id, 'prompt': 'Continue the fixture goal.',
                              'attachment_ids': attachment_ids or []}}
        result.update(patch)
        return result

    async def test_attachment_staging_is_durable_idempotent_and_never_dispatches(self):
        body, response = await self.stage()
        self.assertEqual(response.status_code, 200, response.text)
        attachment = response.json()['attachment']
        self.assertEqual(attachment['run_id'], self.run_id)
        self.assertEqual(attachment['size_bytes'], len(b'fixture notes'))
        self.assertNotIn('path', attachment)
        replay = await self.http.post('/v1/session-attachments', headers=self.auth, json=body)
        self.assertEqual(replay.json(), response.json())
        reopened = RuntimeStore(self.config)
        self.assertEqual(reopened.get_session_attachment(attachment['id'])['sha256'], attachment['sha256'])
        reopened.close()
        changed = await self.http.post('/v1/session-attachments', headers=self.auth,
            json={**body, 'data_base64': base64.b64encode(b'changed').decode()})
        self.assertEqual(changed.status_code, 409)
        self.assertEqual(self.scheduler.enqueued, [])

    async def test_staging_rejects_auth_paths_binary_spoofing_and_bounds(self):
        self.assertEqual((await self.http.post('/v1/session-attachments', json={})).status_code, 403)
        for patch in [{'name': '../secret.txt'}, {'name': 'evil.svg', 'media_type': 'image/svg+xml'},
                      {'media_type': 'image/png'}, {'data_base64': '***'},
                      {'data_base64': base64.b64encode(b'\x00bad').decode()},
                      {'run_id': str(uuid4())}, {'path': '/credentials'}]:
            with self.subTest(patch=patch):
                _, response = await self.stage(**patch)
                self.assertIn(response.status_code, (400, 403, 404), response.text)
        self.assertEqual(self.scheduler.enqueued, [])

    async def test_empty_image_mime_and_code_types_preserve_receipt_and_map_supported_inputs(self):
        png = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+yRZkAAAAASUVORK5CYII=')
        _, response = await self.stage(name='reference.png',media_type='',data_base64=base64.b64encode(png).decode())
        self.assertEqual(response.status_code,200,response.text)
        attachment = response.json()['attachment']
        self.assertEqual(attachment['media_type'],'')
        from services.runtime.sessions import AttachmentStore
        self.assertEqual(AttachmentStore(self.config,self.store).resolve(self.run_id,[attachment['id']])[0]['media_type'],'image/png')
        for name,mime in [('config.yml','text/yaml'),('module.ts','application/typescript'),('module.js','application/javascript')]:
            _, response = await self.stage(name=name,media_type=mime)
            self.assertEqual(response.status_code,200,response.text)
            mapped = AttachmentStore(self.config,self.store).resolve(self.run_id,[response.json()['attachment']['id']])
            self.assertEqual(mapped[0]['media_type'],'text/plain')

    async def test_message_receipt_survives_lost_response_and_replay_never_enqueues_twice(self):
        _, staged = await self.stage()
        self.assertEqual(staged.status_code, 200, staged.text)
        command = self.message([staged.json()['attachment']['id']])
        sent = await self.http.post('/v1/commands', headers=self.auth, json=command)
        self.assertEqual(sent.status_code, 202, sent.text)
        self.assertEqual(sent.json()['result']['job_id'], self.job_id)
        receipt = await self.http.get('/v1/commands/' + command['command_id'], headers=self.auth)
        self.assertEqual(receipt.json()['command'], sent.json())
        self.assertEqual(receipt.json()['message']['state'], 'queued')
        replay = await self.http.post('/v1/commands', headers=self.auth, json=command)
        self.assertEqual(replay.json(), sent.json())
        self.assertEqual(self.scheduler.enqueued, [self.job_id])
        changed = {**command, 'payload': {**command['payload'], 'prompt': 'Different payload.'}}
        self.assertEqual((await self.http.post('/v1/commands', headers=self.auth, json=changed)).status_code, 409)
        self.assertNotIn('thread-fixture', receipt.text)
        self.assertNotIn('turn-fixture', receipt.text)

    async def test_message_keeps_production_readiness_scope_and_budget_checks(self):
        self.store.record_codex_readiness(str(uuid4()), self.store.revision,
            config_sha256=codex_configuration_fingerprint(self.config),
            capability={**CAPABILITY, 'usd_cost_enforced': False}, refreshed_at=utc_now())
        denied = await self.http.post('/v1/commands', headers=self.auth, json=self.message())
        self.assertEqual(denied.status_code, 403, denied.text)
        self.assertEqual(self.scheduler.enqueued, [])
        self.assertEqual((await self.http.get('/v1/commands/' + str(uuid4()), headers=self.auth)).json(),
                         {'v': 1, 'found': False})
        self.assertEqual((await self.http.get('/v1/commands/' + str(uuid4()))).status_code, 403)

    async def test_attachment_binding_and_provider_send_bounds_are_checked_before_queue(self):
        foreign_job = create_codex_job(self.store, self.project_id)
        foreign_worker = self.store.create_worker('builder')
        self.store.set_job_command(str(uuid4()), self.store.revision, 'job.run', foreign_job, codex_ready=True)
        foreign = self.store.claim_ready_task(foreign_worker, 10_000, job_id=foreign_job)['attempt_id']
        _, response = await self.stage(run_id=foreign)
        self.assertEqual(response.status_code, 200, response.text)
        denied = await self.http.post('/v1/commands', headers=self.auth,
                                     json=self.message([response.json()['attachment']['id']]))
        self.assertEqual(denied.status_code, 403, denied.text)
        _, oversized = await self.stage(data_base64=base64.b64encode(b'x' * (1024 * 1024 + 1)).decode())
        self.assertEqual(oversized.status_code, 200, oversized.text)
        denied = await self.http.post('/v1/commands', headers=self.auth,
                                     json=self.message([oversized.json()['attachment']['id']]))
        self.assertEqual(denied.status_code, 400, denied.text)
        self.assertEqual(self.scheduler.enqueued, [])

    async def test_claim_links_followup_anchor_and_rebinds_station_without_changing_goal(self):
        command = self.message()
        response = await self.http.post('/v1/commands', headers=self.auth, json=command)
        self.assertEqual(response.status_code, 202, response.text)
        original = self.store.get_job(self.job_id)['tasks'][0]
        claim = self.store.claim_ready_task(self.store.get_run(self.run_id)['worker_id'], 10_000, job_id=self.job_id)
        self.assertNotEqual(claim['attempt_id'], self.run_id)
        self.assertEqual(claim['followup']['message_id'], command['command_id'])
        self.assertEqual(claim['provider_thread_id'], 'thread-fixture')
        self.assertEqual(claim['provider_turn_id'], 'turn-fixture')
        task = self.store.get_job(self.job_id)['tasks'][0]
        self.assertEqual(task['objective'], original['objective'])
        self.assertEqual(task['write_paths'], original['write_paths'])
        self.assertEqual(self.store.list_office_sessions()[0]['run_id'], claim['attempt_id'])

    async def test_followup_keeps_the_recorded_worker_when_other_idle_builders_exist(self):
        command = self.message()
        self.assertEqual((await self.http.post('/v1/commands',headers=self.auth,json=command)).status_code,202)
        other = self.store.create_worker('builder',configuration={'host_codex':True})
        self.assertIsNone(self.store.claim_ready_task(other,10_000,job_id=self.job_id))
        original_worker = self.store.get_run(self.run_id)['worker_id']
        claim = self.store.claim_ready_task(original_worker,10_000,job_id=self.job_id)
        self.assertEqual(claim['worker_id'],original_worker)
        self.assertEqual(self.store.list_office_sessions()[0]['worker_id'],original_worker)

    async def test_interrupted_send_is_uncertain_and_cannot_start_a_fresh_turn(self):
        command = self.message()
        self.assertEqual((await self.http.post('/v1/commands', headers=self.auth, json=command)).status_code, 202)
        worker = self.store.get_run(self.run_id)['worker_id']
        claim = self.store.claim_ready_task(worker, 10_000, job_id=self.job_id)
        self.store.record_provider_session(claim['attempt_id'],provider_thread_id='thread-fixture',
            provider_turn_id='unseen-completion',model='fixture-model',effort='high')
        self.store.reconcile_interrupted_attempts()
        self.store.reconcile_interrupted_messages()
        receipt = self.store.command_receipt(command['command_id'])
        self.assertEqual(receipt['message']['state'], 'uncertain')
        self.assertEqual(receipt['message']['run_id'], claim['attempt_id'])
        denied = await self.http.post('/v1/commands', headers=self.auth, json=self.message())
        self.assertIn(denied.status_code, (403,429))
        self.assertEqual(self.scheduler.enqueued, [self.job_id])
        resume = {'v':1,'command_id':str(uuid4()),'type':'job.resume',
                  'expected_revision':self.store.revision,'payload':{'job_id':self.job_id}}
        response = await self.http.post('/v1/commands',headers=self.auth,json=resume)
        self.assertEqual(response.status_code,403,response.text)
        self.assertEqual(self.scheduler.enqueued,[self.job_id])

    async def test_latest_twenty_jobs_do_not_hide_an_assigned_old_run(self):
        for _ in range(21):
            create_codex_job(self.store, self.project_id)
        snapshot = (await self.http.get('/v1/snapshot', headers=self.auth)).json()
        self.assertEqual(len(snapshot['jobs']), 20)
        self.assertNotIn(self.job_id, [j['id'] for j in snapshot['jobs']])
        self.assertIn(self.job_id, [j['id'] for j in snapshot.get('office_jobs',[])])
        self.assertFalse(snapshot['office_jobs_truncated'])
        self.assertFalse(set(j['id'] for j in snapshot['jobs']) & set(j['id'] for j in snapshot['office_jobs']))

    async def test_runtime_pipeline_transports_exact_input_to_protocol_fake_and_completes_receipt(self):
        _, staged = await self.stage()
        command = self.message([staged.json()['attachment']['id']])
        queued = await self.http.post('/v1/commands', headers=self.auth, json=command)
        self.assertEqual(queued.status_code, 202, queued.text)
        goal = self.store.get_job(self.job_id)['tasks'][0]['objective']
        seen = []

        class ProtocolFakeAdapter:
            async def call(fake, lane, **request):
                seen.append((lane,request))
                if request['op']=='repo.inspect':
                    return {'data':{'revision':self.store.get_project(self.project_id)['base_revision'],
                                    'clean':True,'files':['README.md']},'artifacts':[]}
                if request['op']=='repo.prepare':
                    Path(request['workspace']).mkdir(parents=True)
                    return {'data':{'workspace':str(request['workspace'])},'artifacts':[]}
                self.assertEqual(request['op'],'agent.execute')
                self.assertEqual(request['payload']['objective'],goal)
                self.assertEqual(request['payload']['followup'],{'message_id':command['command_id'],
                                 'prompt':command['payload']['prompt']})
                self.assertEqual(request['context']['provider_thread_id'],'thread-fixture')
                self.assertEqual(request['context']['provider_turn_id'],'turn-fixture')
                attachment = request['context']['attachments'][0]
                self.assertEqual(set(attachment),{'attachment_id','name','media_type','size_bytes','sha256','path'})
                self.assertEqual(Path(attachment['path']).read_bytes(),b'fixture notes')
                self.assertNotIn('path',command['payload'])
                self.store.append_run_event(self.job_id,request['context']['run_id'],'output','Protocol fake: follow-up reply.')
                return {'data':{'status':'completed','message_id':command['command_id'],
                        'provider_thread_id':'thread-fixture','provider_turn_id':'next-turn-fixture',
                        'model':'fixture-model','effort':'high','model_verified':True,'effort_verified':True},
                        'artifacts':[], 'usage':{'cost_usd':None,'uncertain':True,
                        'input_tokens':10,'cached_input_tokens':0,'output_tokens':5,'total_tokens':15}}

        scheduler = Scheduler(self.store,self.config,ProtocolFakeAdapter(),ArtifactStore(self.config.artifacts_dir,self.store))
        scheduler.start()  # Saved explicit intent; no previous provider dispatch to repeat.
        try:
            await scheduler._tasks[self.job_id]
            receipt = self.store.command_receipt(command['command_id'])
            self.assertEqual(receipt['message']['state'],'completed', receipt)
            run = self.store.get_run(receipt['message']['run_id'])
            self.assertEqual(run['state'],'completed')
            self.assertEqual(run['provider_turn_id'],'next-turn-fixture')
            self.assertEqual(self.store.list_office_sessions()[0]['run_id'],run['id'])
            self.assertTrue(self.store.get_budget(self.job_id)['uncertain'])
            self.assertEqual([request['op'] for _,request in seen],['repo.inspect','repo.prepare','agent.execute'])
            self.assertTrue(any(event['message']=='Protocol fake: follow-up reply.' for event in self.store.list_run_events(run['id'])))
        finally:
            await scheduler.stop()

    async def test_assigned_jobs_are_retained_even_when_active_coverage_overflows(self):
        for _ in range(122): create_codex_job(self.store,self.project_id)
        snapshot = (await self.http.get('/v1/snapshot',headers=self.auth)).json()
        self.assertEqual(len(snapshot['jobs']),20)
        self.assertTrue(snapshot['office_jobs_truncated'])
        self.assertEqual(len(snapshot['office_jobs']),101)
        self.assertIn(self.job_id,[job['id'] for job in snapshot['office_jobs']])

    async def test_prior_candidate_restoration_keeps_verified_bytes_and_rejects_symlink_destinations(self):
        artifact_store = ArtifactStore(self.config.artifacts_dir,self.store)
        base = self.store.get_project(self.project_id)['base_revision']
        source = b'prior frozen candidate\n'
        digest = hashlib.sha256(source).hexdigest()
        tree = [{'path':'src/edit.txt','mode':'100644','size_bytes':len(source),'sha256':digest}]
        tree_digest = hashlib.sha256(canonical_json({'v':1,'files':tree}).encode()).hexdigest()
        candidate = {'id':'cand_transport_fixture','base_revision':base,'candidate_revision':'f'*40,
                     'tree_sha256':tree_digest,'patch_sha256':'a'*64}
        manifest = {'v':1,'candidate':candidate,'files':[dict(tree[0],status='added',old_path=None,
                    file_id='file_fixture',binary=False,added_lines=1,deleted_lines=0,media_type='text/plain')]}
        raw = canonical_json(manifest).encode()
        manifest_id = artifact_store._register_file_bytes(raw,expected_sha256=hashlib.sha256(raw).hexdigest(),
            job_id=self.job_id,run_id=self.run_id,kind='file_manifest',media_type='application/json',display_name='manifest.json')
        snapshot = Path(self.temp.name)/'frozen-input'
        (snapshot/'src').mkdir(parents=True);(snapshot/'src/edit.txt').write_bytes(source)
        ids,_,_ = artifact_store.import_candidate_snapshot(manifest,snapshot,job_id=self.job_id,
                    run_id=self.run_id,candidate_id=candidate['id'])
        self.store.create_candidate(CandidateCreate(candidate_id=candidate['id'],job_id=self.job_id,run_id=self.run_id,
                    source_revision=base,base_revision=base,candidate_revision=candidate['candidate_revision'],
                    tree_sha256=tree_digest,patch_sha256='a'*64,manifest_artifact_id=manifest_id))
        self.store.attach_artifacts_to_candidate(candidate['id'],ids)
        worker = Path(self.temp.name)/'worker'
        worker.mkdir();(worker/'README.md').write_text('unchanged baseline')
        actual = artifact_store.restore_candidate_for_followup(candidate['id'],self.run_id,worker,['src'])
        self.assertEqual(actual,tree_digest)
        self.assertEqual((worker/'src/edit.txt').read_bytes(),source)
        self.assertEqual((worker/'README.md').read_text(),'unchanged baseline')
        unsafe = Path(self.temp.name)/'unsafe-worker';unsafe.mkdir()
        untouched = Path(self.temp.name)/'outside';untouched.mkdir();(untouched/'edit.txt').write_text('keep')
        (unsafe/'src').symlink_to(untouched,target_is_directory=True)
        with self.assertRaises(RuntimeFault):
            artifact_store.restore_candidate_for_followup(candidate['id'],self.run_id,unsafe,['src'])
        self.assertEqual((untouched/'edit.txt').read_text(),'keep')

    async def test_candidate_directory_to_file_restores_deletions_before_writes(self):
        artifacts = ArtifactStore(self.config.artifacts_dir,self.store)
        data = b'replacement file\n';digest=hashlib.sha256(data).hexdigest()
        source_id=artifacts._register_file_bytes(data,expected_sha256=digest,job_id=self.job_id,run_id=self.run_id,
                    kind='source_file',media_type='text/plain',display_name='src/item')
        source=self.store.get_artifact(source_id)
        base=self.store.get_project(self.project_id)['base_revision']
        candidate={'id':'cand_directory_fixture','job_id':self.job_id,'run_id':self.run_id,
                   'base_revision':base,'candidate_revision':'f'*40,'tree_sha256':'a'*64,
                   'patch_sha256':'b'*64,'manifest_artifact_id':'fake-manifest'}
        manifest={'v':1,'candidate':candidate,'files':[
            {'path':'src/item','status':'added','sha256':digest,'size_bytes':len(data),'mode':'100644'},
            {'path':'src/item/nested/old.txt','status':'deleted','sha256':None,'size_bytes':0,'mode':'100644'}]}
        workspace=Path(self.temp.name)/'directory-worker';(workspace/'src/item/nested').mkdir(parents=True)
        (workspace/'src/item/nested/old.txt').write_text('old tree')
        with patch.object(self.store,'get_candidate',return_value=candidate), \
             patch.object(self.store,'get_job',return_value={'candidate_id':candidate['id']}), \
             patch.object(self.store,'get_artifact',return_value={'kind':'file_manifest'}), \
             patch.object(artifacts,'read_manifest',return_value=manifest), \
             patch.object(self.store,'list_candidate_artifacts',return_value=[source]):
            self.assertEqual(artifacts.restore_candidate_for_followup(candidate['id'],self.run_id,workspace,['src']),'a'*64)
        self.assertTrue((workspace/'src/item').is_file())
        self.assertEqual((workspace/'src/item').read_bytes(),data)

    async def test_readiness_expiry_before_claim_rejects_saved_intent_and_restores_parent(self):
        command=self.message()
        self.assertEqual((await self.http.post('/v1/commands',headers=self.auth,json=command)).status_code,202)
        self.store.record_codex_readiness(str(uuid4()),self.store.revision,
            config_sha256=codex_configuration_fingerprint(self.config),
            capability={**CAPABILITY,'usd_cost_enforced':False},refreshed_at=utc_now())
        class NeverDispatch:
            async def call(fake,*args,**kwargs): raise AssertionError('No provider/Git adapter may dispatch.')
        scheduler=Scheduler(self.store,self.config,NeverDispatch(),ArtifactStore(self.config.artifacts_dir,self.store))
        scheduler.start();scheduler.enqueue(self.job_id)
        try: await scheduler._tasks[self.job_id]
        finally: await scheduler.stop()
        self.assertEqual(self.store.command_receipt(command['command_id'])['message']['state'],'rejected')
        self.assertEqual(self.store.get_job(self.job_id)['state'],'verifying')
        self.assertEqual(self.store.get_job(self.job_id)['tasks'][0]['state'],'completed')
        self.assertEqual(len(self.store.list_job_runs(self.job_id)),1)
        self.store.record_codex_readiness(str(uuid4()),self.store.revision,
            config_sha256=codex_configuration_fingerprint(self.config),capability=CAPABILITY,refreshed_at=utc_now())
        self.assertEqual((await self.http.post('/v1/commands',headers=self.auth,json=self.message())).status_code,202)
