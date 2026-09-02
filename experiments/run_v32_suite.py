from __future__ import annotations

from pathlib import Path
import os
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = [
    # Preserved earlier v3.2 branches.
    'v32_semantic_harq.py',
    'v32_mixed_service.py',
    'v32_failure_domains.py',
    'v32_service_migration.py',
    'v32_safety_bitalloc.py',
    # Predictive-resilience main line.
    'v32_predictive_failure_migration.py',
    'v32_failure_domain_risk.py',
    'v32_chance_inference.py',
    'v32_control_uep.py',
    'v32_multi_connectivity.py',
    'v32_multi_connectivity_frontier.py',
    'v32_multiconnectivity_safety_control.py',
]


def main() -> int:
    """Run every v3.2 experiment in an isolated child interpreter.

    Process isolation is intentional: the full historical dashboard imports a
    large scientific stack, and keeping all experiments in one interpreter can
    retain Matplotlib/NumPy state and make a long suite look stalled.  Each
    experiment remains deterministic because it owns explicit seeds.
    """
    env = os.environ.copy()
    env.setdefault('MPLCONFIGDIR', str(ROOT / '.mplcache' / 'v32_suite'))
    Path(env['MPLCONFIGDIR']).mkdir(parents=True, exist_ok=True)

    timings: list[tuple[str, float]] = []
    suite_start = time.perf_counter()
    for idx, name in enumerate(SCRIPTS, start=1):
        script = ROOT / 'experiments' / name
        print(f'[{idx:02d}/{len(SCRIPTS):02d}] ==> {name}', flush=True)
        start = time.perf_counter()
        proc = subprocess.run([sys.executable, str(script)], cwd=ROOT, env=env)
        elapsed = time.perf_counter() - start
        timings.append((name, elapsed))
        if proc.returncode:
            print(f'[{idx:02d}/{len(SCRIPTS):02d}] !! {name} FAILED after {elapsed:.1f}s', flush=True)
            return proc.returncode
        print(f'[{idx:02d}/{len(SCRIPTS):02d}] <== {name} OK in {elapsed:.1f}s', flush=True)

    total = time.perf_counter() - suite_start
    print(f'v3.2 suite complete: {len(SCRIPTS)} experiments in {total:.1f}s', flush=True)
    slow = sorted(timings, key=lambda x: x[1], reverse=True)[:3]
    print('slowest: ' + ', '.join(f'{name}={sec:.1f}s' for name, sec in slow), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
