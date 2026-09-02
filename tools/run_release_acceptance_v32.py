from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def run(label: str, cmd: list[str], *, clear_pythonpath: bool = False) -> float:
    env = os.environ.copy()
    if clear_pythonpath:
        env.pop('PYTHONPATH', None)
    print(f'\n=== {label} ===', flush=True)
    print('$ ' + ' '.join(cmd), flush=True)
    t0 = time.perf_counter()
    subprocess.run(cmd, cwd=ROOT, env=env, check=True)
    dt = time.perf_counter() - t0
    print(f'=== {label}: OK ({dt:.1f}s) ===', flush=True)
    return dt


def main() -> int:
    timings: list[tuple[str, float]] = []
    steps = [
        ('editable install', [sys.executable, '-m', 'pip', 'install', '-e', '.', '--no-build-isolation'], False),
        ('v3.2 experiment suite', [sys.executable, 'tools/run_v32_suite.py'], False),
        ('full pytest', [sys.executable, '-m', 'pytest', '-q'], False),
        ('version/import path', [sys.executable, '-c',
            "import importlib.metadata,commlab; from pathlib import Path; "
            "assert importlib.metadata.version('commlab-ofdm')=='3.2.0'; "
            "assert commlab.__version__=='3.2.0'; "
            f"Path(commlab.__file__).resolve().relative_to(Path(r'{ROOT}').resolve()); "
            "print(importlib.metadata.version('commlab-ofdm'), commlab.__version__, Path(commlab.__file__).resolve())"], True),
        ('pytest without PYTHONPATH', [sys.executable, '-m', 'pytest', '-q'], True),
        ('compileall', [sys.executable, '-m', 'compileall', '-q', 'src', 'app', 'experiments', 'tools'], True),
        ('build manifest', [sys.executable, 'tools/build_manifest_v32.py'], True),
        ('verify manifest/release', [sys.executable, 'tools/verify_release_v32.py'], True),
    ]
    total_start = time.perf_counter()
    for label, cmd, clear in steps:
        timings.append((label, run(label, cmd, clear_pythonpath=clear)))
    total = time.perf_counter() - total_start
    print('\n=== CommLab v3.2 acceptance PASSED ===', flush=True)
    print(f'total={total:.1f}s', flush=True)
    print('; '.join(f'{label}={sec:.1f}s' for label, sec in timings), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
