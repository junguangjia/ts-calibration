"""Bounded local runner. Every invocation writes into a fresh result directory."""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import importlib.metadata as meta
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
THREAD_KEYS = ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS',
               'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS')


def source_hashes() -> dict[str, str]:
    """Hash the local research code/config without traversing private snapshots."""
    paths = [ROOT / name for name in ('pilot.py', 'theory_checks.py',
             'pyproject.toml', 'uv.lock', 'Makefile')]
    for directory in ('src', 'scripts', 'tests'):
        paths.extend((ROOT / directory).rglob('*.py'))
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(paths)}


def source_revision() -> str | None:
    completed = subprocess.run(['git', 'rev-parse', '--verify', 'HEAD'], cwd=ROOT,
                               capture_output=True, text=True, timeout=5, check=False)
    return completed.stdout.strip() if completed.returncode == 0 else None

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('task', choices=['test', 'smoke', 'reproduce', 'info'])
    args = parser.parse_args()
    expected = ROOT / '.venv'
    if Path(sys.prefix).resolve() != expected.resolve():
        parser.error('Use this project .venv/bin/python; do not run with a global interpreter.')
    env = os.environ.copy()
    for key in THREAD_KEYS:
        env[key] = '1'
    env.update(PYTHONNOUSERSITE='1', PYTHONHASHSEED='0', MPLBACKEND='Agg',
               MPLCONFIGDIR=str(ROOT / '.cache/matplotlib'),
               XDG_CACHE_HOME=str(ROOT / '.cache'))
    stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    destination = ROOT / 'results' / (stamp + '-' + args.task + '-' + uuid.uuid4().hex[:8])
    destination.mkdir(parents=True, exist_ok=False)
    report = {
        'run_id': destination.name, 'task': args.task, 'started_utc': stamp,
        'workspace': str(ROOT), 'experiment_status': 'development',
        'python_executable': sys.executable, 'python': platform.python_version(),
        'machine': platform.machine(), 'platform': platform.platform(),
        'packages': {n: meta.version(n) for n in ('numpy', 'scipy', 'pytest')},
        'threads': {k: env[k] for k in THREAD_KEYS}, 'workers': 1,
        'purpose': 'Environment acceptance / reference reproduction, NOT research confirmation',
        'source_revision': source_revision(), 'source_sha256': source_hashes(),
        'steps': [], 'status': 'running',
    }
    commands: list[tuple[str, list[str], int]] = []
    if args.task == 'test':
        commands = [('pytest', [sys.executable, '-m', 'pytest', '-q'], 120)]
    elif args.task == 'smoke':
        commands = [('pilot_smoke', [sys.executable, 'pilot.py', '--out',
                     str(destination/'pilot'), '--reps', '2'], 120)]
    elif args.task == 'reproduce':
        commands = [
            ('pilot_200', [sys.executable, 'pilot.py', '--out',
                          str(destination/'pilot'), '--reps', '200'], 900),
            ('theory_reference', [sys.executable, 'theory_checks.py', '--out',
                                 str(destination/'theory')], 900),
        ]
    configuration = {
        'run_id': destination.name, 'task': args.task,
        'experiment_status': 'development',
        'reference_seed_sources': {
            'pilot': 'pilot.py:SEED (actual value in pilot/environment.json)',
            'theory': 'theory_checks.py:monte_carlo (seed rule in theory/checks.json)',
        },
        'commands': [{'name': label, 'argv': command, 'timeout_seconds': timeout}
                     for label, command, timeout in commands],
        'python': report['python'], 'packages': report['packages'],
        'threads': report['threads'], 'workers': 1,
        'source_revision': report['source_revision'],
        'source_sha256': report['source_sha256'],
    }
    config_bytes = (json.dumps(configuration, indent=2) + '\n').encode()
    (destination / 'config.json').write_bytes(config_bytes)
    report['config_sha256'] = hashlib.sha256(config_bytes).hexdigest()
    print('Run directory:', destination, flush=True)
    record_path = destination/'run.json'
    record_path.write_text(json.dumps(report, indent=2)+chr(10))
    exitcode = 0
    for label, command, timeout in commands:
        step = {'name': label, 'command': command, 'timeout_seconds': timeout}
        started = time.monotonic()
        logfile = destination/(label+'.log')
        print('Running:', label, flush=True)
        try:
            with logfile.open('x') as stream:
                result = subprocess.run(command, cwd=ROOT, env=env, stdout=stream,
                                        stderr=subprocess.STDOUT, timeout=timeout, check=False)
            step['returncode'] = result.returncode
            if result.returncode:
                exitcode = result.returncode
        except subprocess.TimeoutExpired:
            step.update(returncode=124, error='Bounded task timed out; child terminated')
            exitcode = 124
        except OSError as exc:
            step.update(returncode=1, error=str(exc))
            exitcode = 1
        step.update(elapsed_seconds=round(time.monotonic()-started, 3), log=logfile.name)
        report['steps'].append(step)
        if label.startswith('pilot_'):
            metadata = destination / 'pilot' / 'environment.json'
            if metadata.exists():
                report['pilot_seed'] = json.loads(metadata.read_text())['seed']
        if label == 'theory_reference':
            metadata = destination / 'theory' / 'checks.json'
            if metadata.exists():
                report['theory_monte_carlo_seed_rule'] = json.loads(metadata.read_text())['mc_seed_rule']
        record_path.write_text(json.dumps(report, indent=2)+chr(10))
        if logfile.exists():
            print(logfile.read_text()[-18000:], flush=True)
        if exitcode:
            break
    report['status'] = 'passed' if exitcode == 0 else 'failed'
    report['finished_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
    record_path.write_text(json.dumps(report, indent=2)+chr(10))
    if args.task == 'info':
        print(json.dumps(report, indent=2))
    print('Status:', report['status'], flush=True)
    return exitcode

if __name__ == '__main__':
    raise SystemExit(main())
