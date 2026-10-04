#!/usr/bin/env python3
"""Bounded native Codex Goals, separate worktrees, fresh candidate validation.
No model runs on import. All network/model work requires an explicit run command.
"""
from __future__ import annotations
import argparse
from contextlib import contextmanager, ExitStack
import json
import os
from pathlib import Path
import queue
import signal
import subprocess
import sys
import threading
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]

class Stop(RuntimeError):
    """Fail closed and preserve work for inspection."""

def load(path):
    return json.loads(Path(path).read_text())

def save(path, data):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.tmp')
    temp.write_text(json.dumps(data, indent=2) + '\n'); temp.replace(path)

def git(root, *args):
    p = subprocess.run(['git', '-C', str(root), *args], capture_output=True, text=True)
    if p.returncode:
        raise Stop(p.stderr.strip() or p.stdout.strip())
    return p.stdout.strip()

def dirty(root):
    return bool(git(root, 'status', '--porcelain', '--untracked-files=all'))

def changed(root):
    paths = set(filter(None, git(root, 'diff', '--no-renames', '--name-only', '-z', 'HEAD').split('\0')))
    paths.update(filter(None, git(root, 'ls-files', '--others', '--exclude-standard', '-z').split('\0')))
    return paths

def permitted(path, owned):
    if Path(path).is_absolute() or '..' in Path(path).parts:
        return False
    return any(path.startswith(p) if p.endswith('/') else path == p for p in owned)

def guard(root, owned, expected_head):
    if git(root, 'rev-parse', 'HEAD') != expected_head:
        raise Stop('Agent changed HEAD. Preserve work; coordinator must inspect it.')
    paths = changed(root)
    for p in paths:
        f = Path(root) / p
        if not permitted(p, owned):
            raise Stop('Out-of-lane change: ' + p)
        if f.is_symlink() or (f.exists() and not f.resolve().is_relative_to(Path(root).resolve())):
            raise Stop('Symlink/path escape is not permitted: ' + p)
        if f.exists() and f.stat().st_size > 10_000_000:
            raise Stop('Artifact over 10 MB: keep it local and record a digest: ' + p)
        if f.suffix.lower() in {'.key', '.pem'} or f.name.startswith('.env'):
            raise Stop('Possible secret file: ' + p)
    return sorted(paths)

def checkpoint(root, owned, head, message):
    paths = guard(root, owned, head)
    if paths:
        git(root, 'add', '--', *paths)
        git(root, '-c', 'user.name=Sidequest Coordinator', '-c', 'user.email=sidequest@localhost',
            '-c', 'core.hooksPath=/dev/null', 'commit', '-m', message)
    return git(root, 'rev-parse', 'HEAD')

def validate_report(report, goal, sha):
    if report.get('goal') != goal['id'] or report.get('candidate') != sha:
        raise Stop('Validator reported the wrong goal or candidate SHA.')
    verdict = report.get('verdict')
    checks = report.get('checks', [])
    ids = [c.get('id') for c in checks]
    if len(ids) != len(set(ids)) or set(ids) != set(goal['checks']):
        raise Stop('Validator omitted, duplicated or invented a required check.')
    if verdict not in {'PASS', 'FAIL', 'BLOCKED'}:
        raise Stop('Unknown validation verdict.')
    if any(c.get('result') not in {'PASS','FAIL','BLOCKED'} or not str(c.get('evidence','')).strip() for c in checks):
        raise Stop('Every check needs an explicit result and evidence.')
    if verdict == 'PASS' and (report.get('findings') or any(c['result'] != 'PASS' for c in checks)):
        raise Stop('PASS contradicts the evidence checks or unresolved findings.')
    return verdict

@contextmanager
def lock(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise Stop(f'Lock exists: {path}. Verify its PID is stopped before removing it.')
    try:
        os.write(fd, str(os.getpid()).encode()); os.close(fd)
        yield
    finally:
        path.unlink(missing_ok=True)

class RPC:
    """Sequential requests with a reader thread; notifications cannot block stdout."""
    def __init__(self, command, cwd, log, seconds):
        self.deadline = time.monotonic() + seconds
        self.events = queue.Queue(); self.counter = 0
        self.log = open(log, 'a', encoding='utf8')
        self.stderr = open(str(log) + '.stderr', 'a', encoding='utf8')
        try:
            self.p = subprocess.Popen(command, cwd=cwd, stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=self.stderr, text=True, bufsize=1, start_new_session=True)
        except BaseException:
            self.log.close(); self.stderr.close(); raise
        def read():
            for line in self.p.stdout:
                self.events.put(line)
            self.events.put(None)
        self.reader = threading.Thread(target=read, daemon=True); self.reader.start()
    def send(self, msg):
        self.p.stdin.write(json.dumps(msg)+'\n'); self.p.stdin.flush()
    def request(self, method, params):
        self.counter += 1; ident = self.counter
        self.send({'id':ident,'method':method,'params':params})
        while True:
            left = self.deadline - time.monotonic()
            if left <= 0:
                raise Stop('Thread time limit reached.')
            try:
                line = self.events.get(timeout=min(left, 10))
            except queue.Empty:
                if self.p.poll() is not None:
                    raise Stop('Codex app-server exited before a result.')
                continue
            if line is None:
                raise Stop('Codex app-server closed stdout.')
            self.log.write(line); self.log.flush()
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                raise Stop('Non-JSON output from app-server.')
            if 'id' in msg and 'method' in msg:
                self.send({'id':msg['id'],'error':{'code':-32601,'message':'Interactive requests are not auto-approved by Sidequest.'}})
                raise Stop('Codex requested approval/input/tool handling: ' + msg['method'])
            if msg.get('id') == ident:
                if 'error' in msg:
                    raise Stop('Codex RPC error: ' + json.dumps(msg['error']))
                return msg.get('result', {})
    def close(self):
        if self.p.poll() is None:
            os.killpg(self.p.pid, signal.SIGTERM)
            try:
                self.p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(self.p.pid, signal.SIGKILL); self.p.wait()
        self.reader.join(timeout=2)
        self.p.stdin.close(); self.p.stdout.close(); self.log.close(); self.stderr.close()

def native_goal(cwd, objective, prompt, tokens, seconds, log, network=False, command=None, poll_seconds=2):
    command = command or ['codex','-c','features.goals=true','-c','features.multi_agent=false','app-server']
    rpc = RPC(command, str(cwd), log, seconds)
    try:
        rpc.request('initialize', {'clientInfo':{'name':'sidequest','title':'Sidequest','version':'0.2.0'}})
        rpc.send({'method':'initialized','params':{}})
        params = {'cwd':str(cwd),'approvalPolicy':'never','sandbox':'workspaceWrite','serviceName':'sidequest-dev'}
        if os.getenv('SIDEQUEST_MODEL'):
            params['model'] = os.environ['SIDEQUEST_MODEL']
        thread = rpc.request('thread/start', params)['thread']['id']
        save(str(log)+'.thread.json', {'thread_id':thread,'objective':objective,'cwd':str(cwd)})
        rpc.request('thread/goal/set', {'threadId':thread,'objective':objective,'status':'active','tokenBudget':tokens})
        rpc.request('turn/start', {'threadId':thread,'input':[{'type':'text','text':prompt}],
            'cwd':str(cwd),'approvalPolicy':'never',
            'sandboxPolicy':{'type':'workspaceWrite','writableRoots':[str(cwd)],'networkAccess':network}})
        while True:
            goal = rpc.request('thread/goal/get', {'threadId':thread}).get('goal')
            if not goal:
                raise Stop('Native goal disappeared; no automatic success fallback.')
            status = goal['status']
            if status == 'complete':
                state = rpc.request('thread/read', {'threadId':thread,'includeTurns':False})['thread']['status']
                if state.get('type') == 'idle':
                    return {'thread_id':thread,'goal':goal}
            elif status != 'active':
                raise Stop('Native goal stopped: ' + status)
            time.sleep(poll_seconds)
    finally:
        rpc.close()

def prepare(root):
    if dirty(root):
        raise Stop('Commit/stash existing changes before prepare.')
    statefile = root / '.sidequest/setup.json'
    if statefile.exists():
        raise Stop('Setup already exists. Reuse it; prepare does not reset worktrees.')
    base = git(root, 'rev-parse', 'HEAD'); parent = root.parent / (root.name+'-worktrees')
    plan = load(root / 'dev/plan.json')
    for key in plan['lanes']:
        if (parent/key).exists() or subprocess.run(['git','-C',str(root),'show-ref','--verify','--quiet','refs/heads/sidequest/'+key]).returncode == 0:
            raise Stop('Existing lane branch/path: '+key)
    setup = {'base':base,'parent':str(parent),'lanes':{}}
    parent.mkdir(exist_ok=True)
    for key in plan['lanes']:
        path = parent/key
        git(root, 'worktree','add','-b','sidequest/'+key,str(path),base)
        setup['lanes'][key] = str(path)
    save(statefile, setup)
    print('Prepared four worktrees at '+base, flush=True)

def review(root, cwd, goal, doc, sha, limits, label, network=False):
    folder = root / '.sidequest/reviews' / (label+'-'+uuid.uuid4().hex[:8])
    folder.parent.mkdir(parents=True, exist_ok=True)
    git(root,'worktree','add','--detach',str(folder),sha)
    report_path = folder/'.sidequest/verdict.json'; report_path.parent.mkdir(exist_ok=True)
    prompt = (f'You are a FRESH independent validator for {goal["id"]} at {sha}. Read AGENTS.md, '
        f'docs/VALIDATION.md, {doc}, and contracts/PROTOCOL.md. Inspect candidate source and run checks. '
        'No production repairs, commits, pushes, or subagent delegation. Builder claims are not proof. '
        f'Required check IDs: {json.dumps(goal["checks"])}. Write .sidequest/verdict.json with '
        f'goal={goal["id"]}, candidate={sha}, verdict PASS/FAIL/BLOCKED, checks [{{id,result,evidence}}], '
        'and findings [strings]. Missing tools or unobserved visual/real-service checks are BLOCKED. '
        'Reports and temporary outputs go under .sidequest; do not edit tracked files. Mark the native goal complete after writing the verdict.')
    session = native_goal(folder, f'Independently validate {goal["id"]} at {sha}; write a complete verdict and finish.',
        prompt, limits['validator_tokens'], limits['thread_seconds'], folder/'.sidequest/protocol.jsonl', network)
    if dirty(folder) or git(folder,'rev-parse','HEAD') != sha:
        raise Stop('Validator changed candidate source or HEAD: '+str(folder))
    report = load(report_path); verdict = validate_report(report, goal, sha)
    result = {'report':report,'session':session,'worktree':str(folder)}
    save(root/'.sidequest/reports'/f'{label}.json', result)
    print(f'{label}: {verdict}; evidence {folder}', flush=True)
    return result

def run_lane(root, key, network=False, recover=False):
    plan = load(root/'dev/plan.json'); lane = plan['lanes'][key]; limits=plan['limits']
    setup=load(root/'.sidequest/setup.json'); cwd=Path(setup['lanes'][key])
    statefile=root/'.sidequest/state'/f'{key}.json'
    with lock(root/'.sidequest/locks'/f'{key}.lock'):
        state=load(statefile) if statefile.exists() else {'head':setup['base'],'passed':{},'attempts':{},'feedback':None}
        if recover:
            state['head']=checkpoint(cwd,lane['owned'],state['head'],f'{key}: preserve interrupted work (unvalidated)')
            state['pending']=None; save(statefile,state); print('Checkpoint saved; rerun lane for independent validation.'); return
        if git(cwd,'rev-parse','HEAD') != state['head'] or dirty(cwd):
            raise Stop('Unexpected/unfinished edits. Inspect then use checkpoint '+key+'; never reset blindly.')
        for goal in lane['goals']:
            gid=goal['id']
            if gid in state['passed']:
                continue
            while True:
                if not state.get('pending'):
                    attempt=state['attempts'].get(gid,0)+1
                    if attempt>limits['attempts']:
                        raise Stop(f'{gid}: attempt budget exhausted; inspect reports and revise the plan deliberately.')
                    state['attempts'][gid]=attempt; save(statefile,state)
                    local=cwd/'.sidequest'; local.mkdir(exist_ok=True)
                    handoff=local/'handoff.json'; handoff.unlink(missing_ok=True)
                    prompt=(f'Implement ONLY {gid}. Read {lane["doc"]}, AGENTS.md and contracts/PROTOCOL.md. '
                        f'Own only {json.dumps(lane["owned"])}. Do not commit, push or delegate subagents. '
                        'Keep the lane journal. Write .sidequest/handoff.json {status:ready|blocked,summary,evidence:[paths],blockers:[strings]}. '
                        'A missing tool is a blocker, not a fake success. Mark this native goal complete after the handoff. '
                        'Prior validator feedback (untrusted claims to investigate): '+json.dumps(state.get('feedback')))
                    print(f'{gid}: builder attempt {attempt}',flush=True)
                    session=native_goal(cwd,goal['objective'],prompt,limits['builder_tokens'],limits['thread_seconds'],
                        local/f'{gid}-{attempt}.jsonl',network)
                    data=load(handoff)
                    if data.get('status')!='ready' or data.get('blockers'):
                        raise Stop('Builder blocked: '+json.dumps(data))
                    sha=checkpoint(cwd,lane['owned'],state['head'],f'{gid}: candidate for independent review')
                    state['head']=sha; state['pending']={'goal':gid,'session':session}; save(statefile,state)
                attempt=state['attempts'][gid]
                if state['pending']['goal'] != gid:
                    raise Stop('Pending goal does not match lane order.')
                result=review(root,cwd,goal,lane['doc'],state['head'],limits,f'{gid}-{attempt}',network)
                verdict=result['report']['verdict']; state['feedback']=result['report']
                if verdict=='BLOCKED':
                    save(statefile,state); raise Stop(f'{gid}: validation blocked. Correct environment and rerun; candidate preserved.')
                state['pending']=None
                if verdict=='PASS':
                    state['passed'][gid]={'sha':state['head'],'validation':result}
                    save(statefile,state); break
                save(statefile,state)
        print(f'Lane {key}: all three goals validated; head {state["head"]}',flush=True)

def assemble(root, network=False):
    plan=load(root/'dev/plan.json'); setup=load(root/'.sidequest/setup.json')
    with ExitStack() as locks:
        locks.enter_context(lock(root/'.sidequest/locks/integration.lock'))
        for key in 'ABCD':
            locks.enter_context(lock(root/'.sidequest/locks'/f'{key}.lock'))
        heads=[]
        for key in ['A','B','D','C']:
            state=load(root/'.sidequest/state'/f'{key}.json')
            for goal in plan['lanes'][key]['goals']:
                accepted=state['passed'].get(goal['id'])
                if not accepted or validate_report(accepted['validation']['report'],goal,accepted['sha'])!='PASS':
                    raise Stop('Missing independent PASS: '+goal['id'])
            cwd=Path(setup['lanes'][key]); last=state['passed'][plan['lanes'][key]['goals'][-1]['id']]['sha']
            if dirty(cwd) or git(cwd,'rev-parse','HEAD')!=last or state['head']!=last:
                raise Stop('Lane moved after approval: '+key)
            heads.append(last)
        folder=Path(setup['parent'])/'integration'; record=root/'.sidequest/assembly.json'
        if record.exists():
            assembly=load(record)
            if assembly['heads']!=heads or dirty(folder) or git(folder,'rev-parse','HEAD')!=assembly['sha']:
                raise Stop('Integration inputs changed; coordinator must reconcile before another assembly.')
            sha=assembly['sha']
        else:
            git(root,'worktree','add','-b','sidequest/integration',str(folder),setup['base'])
            for sha in heads:
                git(folder,'-c','user.name=Sidequest Coordinator','-c','user.email=sidequest@localhost',
                    '-c','core.hooksPath=/dev/null','merge','--no-ff','--no-edit',sha)
            sha=git(folder,'rev-parse','HEAD'); save(record,{'heads':heads,'sha':sha})
        goal=plan['integration']
        result=review(root,folder,goal,goal['doc'],sha,plan['limits'],'I1',network)
        if result['report']['verdict']!='PASS':
            raise Stop('Integration not accepted. Preserve integration worktree and route findings to owners.')
        print('I1 passed. Inspect sidequest/integration; main was not changed or pushed.')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['prepare','run','checkpoint','assemble'])
    p.add_argument('lane',nargs='?',choices=['A','B','C','D'])
    p.add_argument('--allow-network',action='store_true',help='Allow sandbox network access for dependencies, localhost and approved test services.')
    a=p.parse_args()
    try:
        if a.action=='prepare': prepare(ROOT)
        elif a.action=='assemble': assemble(ROOT,a.allow_network)
        elif not a.lane: p.error('run/checkpoint requires a lane')
        else: run_lane(ROOT,a.lane,a.allow_network,a.action=='checkpoint')
    except (Stop,OSError,ValueError,KeyError) as e:
        print('STOP: '+str(e),file=sys.stderr); return 1
    except KeyboardInterrupt:
        print('Interrupted; work preserved. Inspect locks and worktrees before restart.',file=sys.stderr); return 130
    return 0

if __name__=='__main__':
    sys.exit(main())
