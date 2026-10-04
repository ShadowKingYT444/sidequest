#!/usr/bin/env python3
"""Static checks for the launch kit, not product verification."""
import argparse
import ast
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
def check(root=ROOT):
    plan=json.loads((root/'dev/plan.json').read_text())
    assert set(plan['lanes'])==set('ABCD')
    prefixes=[]
    for key,lane in plan['lanes'].items():
        assert len(lane['goals'])==3
        text=(root/lane['doc']).read_text()
        for goal in lane['goals']:
            assert goal['id'] in text and 0<len(goal['objective'])<=4000
            assert len(set(goal['checks']))==len(goal['checks'])
            for cid in goal['checks']: assert cid in text
        for p in lane['owned']:
            assert '..' not in Path(p).parts and not Path(p).is_absolute()
            for other in prefixes:
                assert not (p.startswith(other) or other.startswith(p)), (p,other)
            prefixes.append(p)
    for f in [root/'README.md', root/'AGENTS.md', root/'SPEC.md', *(root/'docs').rglob('*.md')]:
        if '.sidequest' in f.parts: continue
        for link in re.findall(r'\]\(([^)]+)\)',f.read_text()):
            if '://' in link or link.startswith('#') or link.startswith('mailto:'): continue
            target=(f.parent/link.split('#')[0]).resolve()
            assert target.exists(), f'{f}: missing {link}'
    for f in (root/'dev').glob('*.py'): ast.parse(f.read_text(),filename=str(f))
    for f in (root/'docs/design').glob('*.svg'): ET.parse(f)
    fixture=json.loads((root/'contracts/snapshot.json').read_text())
    assert fixture['v']==1 and fixture['mode']=='fixture'
    print('PASS: static ownership, goal IDs, links, Python syntax, SVG XML and fixture labeling. Product not tested.')
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--setup',action='store_true');p.parse_args()
    check()
