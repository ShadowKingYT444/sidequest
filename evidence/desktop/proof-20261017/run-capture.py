"""Real launcher + temporary trusted fixture; no persisted API credential."""
import hashlib,json,os,signal,socket,subprocess,tempfile,time,urllib.request
from pathlib import Path

ROOT=Path('/workspace/sidequest')
OUT=Path(__file__).resolve().parent
TEMP=Path(tempfile.mkdtemp(prefix='sidequest-video-proof-20261017-',dir='/tmp'))
PROJECT=TEMP/'proof-project';PROJECT.mkdir()
STATE=TEMP/'state'
def git(*args):
    return subprocess.check_output(['git','-C',str(PROJECT),*args],text=True).strip()
git('init','-q');git('config','user.name','Local Proof Fixture');git('config','user.email','proof@example.invalid')
(PROJECT/'README.md').write_text('# Local inspection proof\n\nThis file is real committed Git content.\n\nBaseline: the inspection reads a frozen commit.\n')
(PROJECT/'app.py').write_text('def greeting(name):\n    return f"Hello, {name}!"\n')
git('add','.');git('commit','-qm','Initial trusted local fixture');base=git('rev-parse','HEAD')
(PROJECT/'README.md').write_text('# Local inspection proof\n\nThis file is real committed Git content.\n\nThe desktop compares these commits without a model call.\nThe runtime freezes this candidate and stores immutable artifacts.\n\n## Review notes\n\n'+''.join(f'{n:03d}. Local review entry {n}: preserve the approved office and verify the saved result.\n' for n in range(1,181)))
(PROJECT/'app.py').write_text('def greeting(name):\n    cleaned = name.strip()\n    return f"Hello, {cleaned or \'friend\'}!"\n')
git('add','.');git('commit','-qm','Add review notes and normalize greeting')
cache=TEMP/'playwright-cache';(cache/'ffmpeg-1013').mkdir(parents=True)
(cache/'ffmpeg-1013/ffmpeg-linux').symlink_to('/usr/bin/ffmpeg')
prior=json.loads((ROOT/'evidence/desktop/startup-browser-20261017/final-full/run-context.json').read_text())['initial_source_hashes']
paths=sorted(set(prior)|{'sidequest.py'})
hashes={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in paths}
command=['python3','sidequest.py','run','--browser','--repo',str(PROJECT),'--base',base,'--state-dir',str(STATE)]
context={'application_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'command':command,'fixture_head':git('rev-parse','HEAD'),'fixture_base':base,'fixture_path':str(PROJECT),'state_directory':str(STATE),'source_hashes_before':hashes,'started_at_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'playwright_ffmpeg':'Temporary registry symlink to existing /usr/bin/ffmpeg; no package install'}
(OUT/'run-context.json').write_text(json.dumps(context,indent=2)+'\n')
log=(OUT/'launcher.log').open('w');launcher=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
try:
    for _ in range(120):
        if launcher.poll() is not None:raise RuntimeError('Launcher stopped before UI ready')
        try:
            with urllib.request.urlopen('http://127.0.0.1:5173',timeout=.5) as response:
                if response.status==200:break
        except OSError:time.sleep(.25)
    else:raise RuntimeError('Launcher UI readiness timed out')
    env=dict(os.environ,PLAYWRIGHT_BROWSERS_PATH=str(cache))
    code=subprocess.call(['node',str(OUT/'capture.mjs')],cwd=ROOT,env=env)
    context['capture_exit_code']=code
finally:
    launcher.send_signal(signal.SIGINT)
    context['launcher_exit_code']=launcher.wait(timeout=20);log.close()
    context['source_hashes_after']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in paths}
    context['source_hashes_unchanged']=context['source_hashes_after']==hashes
    context['state_files']=[str(p.relative_to(STATE)) for p in STATE.rglob('*') if p.is_file()]
    context['token_named_state_files']=[p for p in context['state_files'] if 'token' in Path(p).name.lower()]
    with socket.socket() as listener:context['vite_port_released']=listener.connect_ex(('127.0.0.1',5173))!=0
    context['completed_at_utc']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
    (OUT/'run-context.json').write_text(json.dumps(context,indent=2)+'\n')
raise SystemExit(code)
