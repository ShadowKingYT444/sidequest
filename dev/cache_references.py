#!/usr/bin/env python3
"""Download third-party reference images for local inspection, never game assets."""
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__':
    target=ROOT/'docs/design/cache'; target.mkdir(parents=True,exist_ok=True)
    failures=[]; records=[]
    for ref in json.loads((ROOT/'dev/references.json').read_text()):
        path=target/(ref['id']+'.jpg')
        try:
            request=urllib.request.Request(ref['image'],headers={'User-Agent':'Sidequest-reference-cache/1.0'})
            with urllib.request.urlopen(request,timeout=30) as r:
                data=r.read(12_000_001)
            if len(data)>12_000_000 or not data.startswith(b'\xff\xd8'):
                raise ValueError('Expected a JPEG reference under 12 MB')
            path.write_bytes(data)
            records.append({'id':ref['id'],'source':ref['image'],'sha256':hashlib.sha256(data).hexdigest()})
            print(path)
        except Exception as e:
            failures.append(ref['id']); print(ref['id']+': FAILED: '+str(e))
    (target/'manifest.json').write_text(json.dumps(records,indent=2)+'\n')
    raise SystemExit(1 if failures else 0)
