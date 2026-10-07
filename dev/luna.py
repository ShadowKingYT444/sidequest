#!/usr/bin/env python3
"""Luna/max preflight and pinned launcher for the existing development loop.
No model turn is started by `check`. Live model/Unity execution is not simulated.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import functools
import os
from pathlib import Path
import sys
import uuid

import loop

ROOT = Path(__file__).resolve().parents[1]
MODEL = 'gpt-6-luna'
EFFORT = 'max'
COMMAND = ['codex', '-c', 'model="gpt-6-luna"',
           '-c', 'model_reasoning_effort="max"',
           '-c', 'model_reasoning_summary="concise"',
           '-c', 'features.goals=true', '-c', 'features.multi_agent=false',
           'app-server']


def verify_selection(rpc, require_images=False):
    """Only configuration/catalog reads; no thread or inference request."""
    config = rpc.request('config/read', {'includeLayers': False}).get('config', {})
    if config.get('model') != MODEL or config.get('model_reasoning_effort') != EFFORT:
        raise loop.Stop('Effective Codex configuration is not Luna/max. Inspect local or managed settings; no fallback was selected.')
    seen = set()
    cursor = None
    for _ in range(20):
        params = {'limit': 100, 'includeHidden': False}
        if cursor is not None:
            params['cursor'] = cursor
        result = rpc.request('model/list', params)
        rows = result.get('data')
        if not isinstance(rows, list):
            raise loop.Stop('Model catalog has an unsupported response shape.')
        for row in rows:
            if not isinstance(row, dict) or row.get('model', row.get('id')) != MODEL:
                continue
            efforts = {item.get('reasoningEffort') for item in row.get('supportedReasoningEfforts', []) if isinstance(item, dict)}
            if EFFORT not in efforts:
                raise loop.Stop('This account/client does not advertise max for Luna. No silent effort downgrade.')
            # Official app-server backward compatibility: missing modalities means text+image.
            modalities = row.get('inputModalities', ['text', 'image'])
            if require_images and 'image' not in modalities:
                raise loop.Stop('The selected model does not advertise image input required for visual validation.')
            return {'model': MODEL, 'effort': EFFORT, 'input_modalities': modalities,
                    'inference_started': False}
        cursor = result.get('nextCursor')
        if cursor is None:
            raise loop.Stop('Luna is not in this account model catalog. No Sol or other provider fallback.')
        if not isinstance(cursor, str) or not cursor or cursor in seen:
            raise loop.Stop('Invalid or repeated model-catalog cursor.')
        seen.add(cursor)
    raise loop.Stop('Model catalog page limit exceeded; no inference started.')


def preflight(cwd, require_images=False):
    if os.getenv('SIDEQUEST_MODEL') not in (None, '', MODEL):
        raise loop.Stop('SIDEQUEST_MODEL conflicts with the Luna launcher. Escalation requires a separate deliberate run.')
    cwd = Path(cwd).resolve()
    if not (cwd / '.codex/config.toml').is_file():
        raise loop.Stop('This checkout lacks the 0.3 Codex configuration. Reconcile old worktrees before running.')
    logs = ROOT / '.sidequest/preflight'
    logs.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(logs, 0o700)
    path = logs / (uuid.uuid4().hex + '.jsonl')
    rpc = loop.RPC(list(COMMAND), str(cwd), path, 30)
    try:
        # Effective config may contain sensitive provider settings. Do not persist
        # raw config/catalog responses; save only the small allowlisted result.
        rpc.log.close()
        rpc.log = open(os.devnull, 'w', encoding='utf8')
        os.chmod(str(path) + '.stderr', 0o600)
        rpc.request('initialize', {'clientInfo': {'name': 'sidequest-preflight', 'title': 'Sidequest preflight', 'version': '0.3.0'}})
        rpc.send({'method': 'initialized', 'params': {}})
        result = verify_selection(rpc, require_images)
        loop.save(str(path) + '.result.json', result)
        print('Luna/max configuration and account catalog verified. No model turn started.', flush=True)
        return result
    finally:
        rpc.close()


def run_root(action, lane):
    if action == 'check':
        return ROOT
    setup = loop.load(ROOT / '.sidequest/setup.json')
    plan = loop.load(ROOT / 'dev/plan.json')
    if plan.get('spec_revision') != '0.3':
        raise loop.Stop('Expected the 0.3 implementation plan.')
    paths = [Path(setup['lanes'][lane])] if action == 'run' else [Path(p) for p in setup['lanes'].values()]
    for path in paths:
        if loop.load(path / 'dev/plan.json') != plan:
            raise loop.Stop('Worktree plan differs from the coordinator. Preserve work and reconcile; do not reset automatically.')
        if not (path / '.codex/config.toml').is_file():
            raise loop.Stop('Prepared worktree predates the model configuration.')
    return paths[0] if action == 'run' else ROOT


@contextmanager
def pinned_goals():
    """Inject explicit config flags into every app-server process, not just preflight.
    Keep the tested controller lifecycle intact. Restore the function on exit.
    """
    original = loop.native_goal
    loop.native_goal = functools.partial(original, command=list(COMMAND))
    try:
        yield
    finally:
        loop.native_goal = original


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['check', 'run', 'assemble'])
    parser.add_argument('lane', nargs='?', choices=list('ABCD'))
    parser.add_argument('--allow-network', action='store_true')
    args = parser.parse_args()
    if args.action == 'run' and not args.lane:
        parser.error('run requires a lane A, B, C or D')
    if args.action != 'run' and args.lane:
        parser.error('a lane is accepted only with run')
    try:
        cwd = run_root(args.action, args.lane)
        preflight(cwd, require_images=args.lane == 'C' or args.action == 'assemble')
        if args.action == 'check':
            return 0
        with pinned_goals():
            if args.action == 'run':
                loop.run_lane(ROOT, args.lane, args.allow_network)
            else:
                loop.assemble(ROOT, args.allow_network)
    except (loop.Stop, OSError, ValueError, KeyError, TypeError) as error:
        print('STOP: ' + str(error), file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print('Interrupted. Work is preserved; inspect before retrying.', file=sys.stderr)
        return 130
    return 0


if __name__ == '__main__':
    sys.exit(main())
