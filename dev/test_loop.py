"""Offline launch-kit tests. Fakes here are not product acceptance evidence."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import loop
import check

FAKE_SERVER = r'''
import json,sys,uuid,os
status=os.environ.get('FAKE_GOAL_STATUS','complete'); ident='thread-'+uuid.uuid4().hex
for line in sys.stdin:
 m=json.loads(line)
 if 'id' not in m: continue
 method=m['method']; result={}
 if method=='thread/start': result={'thread':{'id':ident}}
 elif method=='thread/goal/set': result={'goal':{'status':'active'}}
 elif method=='turn/start':
  print(json.dumps({'method':'item/agentMessage/delta','params':{'delta':'test notification'}}),flush=True)
  result={'turn':{'id':'t1'}}
 elif method=='thread/goal/get': result={'goal':{'status':status,'tokensUsed':4}}
 elif method=='thread/read': result={'thread':{'status':{'type':'idle'}}}
 print(json.dumps({'id':m['id'],'result':result}),flush=True)
'''
class PureTests(unittest.TestCase):
    def test_launch_kit(self): check.check()
    def test_scope(self):
        self.assertTrue(loop.permitted('services/runtime/a.py',['services/runtime/']))
        for p in ['services/runtime2/a.py','../services/runtime/a.py','/services/runtime/a.py']:
            self.assertFalse(loop.permitted(p,['services/runtime/']))
    def test_report(self):
        goal={'id':'A1','checks':['A1-1']}; sha='a'*40
        r={'goal':'A1','candidate':sha,'verdict':'PASS','checks':[{'id':'A1-1','result':'PASS','evidence':'Executed fixture test'}],'findings':[]}
        self.assertEqual(loop.validate_report(r,goal,sha),'PASS')
        for field,value in [('candidate','b'*40),('checks',[]),('verdict','completed'),('findings',['unresolved'])]:
            bad=copy.deepcopy(r);bad[field]=value
            with self.subTest(field=field),self.assertRaises(loop.Stop):loop.validate_report(bad,goal,sha)
        bad=copy.deepcopy(r);bad['checks'][0]['result']='BLOCKED'
        with self.assertRaises(loop.Stop):loop.validate_report(bad,goal,sha)
    def test_duplicate_check(self):
        c={'id':'x','result':'PASS','evidence':'test'}
        with self.assertRaises(loop.Stop):
            loop.validate_report({'goal':'g','candidate':'h','verdict':'PASS','checks':[c,c]}, {'id':'g','checks':['x']},'h')
    def test_lock(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'lock'
            with loop.lock(p):
                with self.assertRaises(loop.Stop):
                    with loop.lock(p): pass
            self.assertFalse(p.exists())
    def test_real_jsonl_transport_fresh_threads(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);server=p/'fake.py';server.write_text(FAKE_SERVER)
            args=dict(cwd=p,objective='Test only',prompt='Test',tokens=20,seconds=5,
                      command=[sys.executable,str(server)],poll_seconds=0)
            a=loop.native_goal(**args,log=p/'one.jsonl')
            b=loop.native_goal(**args,log=p/'two.jsonl')
            self.assertNotEqual(a['thread_id'],b['thread_id'])
            self.assertIn('test notification',(p/'one.jsonl').read_text())
    def test_native_blocked_and_budget_stop(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);server=p/'fake.py';server.write_text(FAKE_SERVER)
            for state in ['blocked','paused','usageLimited','budgetLimited']:
                with self.subTest(state=state),patch.dict('os.environ',{'FAKE_GOAL_STATUS':state}),self.assertRaises(loop.Stop):
                    loop.native_goal(p,'Test','Test',20,5,p/(state+'.jsonl'),command=[sys.executable,str(server)],poll_seconds=0)

class GitTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.root=Path(self.temp.name)/'repo';self.root.mkdir()
        (self.root/'.gitignore').write_text('.sidequest/\n')
        (self.root/'dev').mkdir();shutil.copy(loop.ROOT/'dev/plan.json',self.root/'dev/plan.json')
        loop.git(self.root,'init','-b','main');loop.git(self.root,'add','.')
        loop.git(self.root,'-c','user.name=Test','-c','user.email=test@localhost','commit','-m','base')
        self.base=loop.git(self.root,'rev-parse','HEAD')
    def tearDown(self):self.temp.cleanup()
    def test_worktrees_same_base_and_refusal_to_overwrite(self):
        loop.prepare(self.root);setup=loop.load(self.root/'.sidequest/setup.json')
        for key,path in setup['lanes'].items():
            self.assertEqual(loop.git(Path(path),'rev-parse','HEAD'),self.base)
            self.assertEqual(loop.git(Path(path),'branch','--show-current'),'sidequest/'+key)
        with self.assertRaises(loop.Stop):loop.prepare(self.root)
    def test_scope_escape_and_head_change(self):
        (self.root/'outsider.txt').write_text('x')
        with self.assertRaises(loop.Stop):loop.guard(self.root,['services/runtime/'],self.base)
        (self.root/'outsider.txt').unlink();(self.root/'services/runtime').mkdir(parents=True)
        (self.root/'services/runtime/a.py').write_text('pass\n')
        new=loop.checkpoint(self.root,['services/runtime/'],self.base,'owned')
        self.assertNotEqual(new,self.base)
        with self.assertRaises(loop.Stop):loop.guard(self.root,['services/runtime/'],self.base)
    def test_symlink_rejected(self):
        (self.root/'services/runtime').mkdir(parents=True)
        (self.root/'services/runtime/escape').symlink_to('/tmp')
        with self.assertRaises(loop.Stop):loop.guard(self.root,['services/runtime/'],self.base)
    def test_rename_from_unowned_rejected(self):
        (self.root/'foreign.txt').write_text('original\n');loop.git(self.root,'add','foreign.txt')
        loop.git(self.root,'-c','user.name=Test','-c','user.email=test@localhost','commit','-m','foreign')
        head=loop.git(self.root,'rev-parse','HEAD');(self.root/'services/runtime').mkdir(parents=True)
        loop.git(self.root,'mv','foreign.txt','services/runtime/new.txt')
        with self.assertRaises(loop.Stop):loop.guard(self.root,['services/runtime/'],head)
    def fake_builder(self,cwd,objective,prompt,tokens,seconds,log,network=False):
        lane=Path(cwd).name;gid=objective.split()[1].strip(':')
        f=Path(cwd)/f'journals/{lane}.md';f.parent.mkdir(exist_ok=True)
        with f.open('a') as out:out.write(gid+'\n')
        loop.save(Path(cwd)/'.sidequest/handoff.json',{'status':'ready','evidence':[],'blockers':[]})
        return {'thread_id':'fake-builder-'+gid}
    def fake_review(self,root,cwd,goal,doc,sha,limits,label,network=False):
        return {'report':{'goal':goal['id'],'candidate':sha,'verdict':'PASS',
            'checks':[{'id':c,'result':'PASS','evidence':'OFFLINE CONTROLLER TEST ONLY'} for c in goal['checks']], 'findings':[]},
            'session':{'thread_id':'fake-review-'+label}}
    def test_all_lanes_and_assembly(self):
        loop.prepare(self.root)
        with patch.object(loop,'native_goal',side_effect=self.fake_builder),patch.object(loop,'review',side_effect=self.fake_review):
            for k in 'ABCD':loop.run_lane(self.root,k)
            loop.assemble(self.root)
        self.assertEqual(loop.git(self.root,'rev-parse','HEAD'),self.base)
        integrated=Path(loop.load(self.root/'.sidequest/setup.json')['parent'])/'integration'
        for k in 'ABCD':self.assertEqual(len((integrated/f'journals/{k}.md').read_text().splitlines()),3)
    def test_failed_review_never_advances_and_is_bounded(self):
        loop.prepare(self.root)
        def fail(*args,**kwargs):
            result=self.fake_review(*args,**kwargs);result['report']['verdict']='FAIL'
            result['report']['checks'][0]['result']='FAIL';return result
        with patch.object(loop,'native_goal',side_effect=self.fake_builder) as builds,patch.object(loop,'review',side_effect=fail):
            with self.assertRaises(loop.Stop):loop.run_lane(self.root,'A')
            self.assertEqual(builds.call_count,3)
        state=loop.load(self.root/'.sidequest/state/A.json')
        self.assertEqual(state['passed'],{});self.assertNotIn('A2',state['attempts'])
    def test_blocked_validation_reuses_candidate(self):
        loop.prepare(self.root)
        def blocked(*args,**kwargs):
            result=self.fake_review(*args,**kwargs);result['report']['verdict']='BLOCKED'
            result['report']['checks'][0]['result']='BLOCKED';return result
        with patch.object(loop,'native_goal',side_effect=self.fake_builder) as builds,patch.object(loop,'review',side_effect=blocked):
            with self.assertRaises(loop.Stop):loop.run_lane(self.root,'A')
            self.assertEqual(builds.call_count,1)
        old=loop.load(self.root/'.sidequest/state/A.json')['head']
        with patch.object(loop,'native_goal',side_effect=self.fake_builder) as builds,patch.object(loop,'review',side_effect=self.fake_review):
            loop.run_lane(self.root,'A');self.assertEqual(builds.call_count,2)
        self.assertEqual(loop.load(self.root/'.sidequest/state/A.json')['passed']['A1']['sha'],old)
    def test_merge_refuses_unvalidated_lane(self):
        loop.prepare(self.root)
        with self.assertRaises((loop.Stop,FileNotFoundError)):loop.assemble(self.root)

if __name__=='__main__':unittest.main()
