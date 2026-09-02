from __future__ import annotations

from pathlib import Path
import os
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = [
    'v33_resilience_budget.py',
    'v33_risk_regimes.py',
    'v33_forecast_uncertainty.py',
    'v33_correlation_reallocation.py',
    'v33_budget_saturation.py',
    'v33_task_weighting.py',
]


def main() -> int:
    base_env = os.environ.copy()
    timings=[]; start_all=time.perf_counter()
    for idx,name in enumerate(SCRIPTS,1):
        print(f'[{idx:02d}/{len(SCRIPTS):02d}] ==> {name}',flush=True)
        t0=time.perf_counter()
        env = base_env.copy()
        env['MPLCONFIGDIR'] = str(ROOT / '.mplcache' / 'v33_suite' / Path(name).stem)
        Path(env['MPLCONFIGDIR']).mkdir(parents=True, exist_ok=True)
        proc=subprocess.run([sys.executable,str(ROOT/'experiments'/name)],cwd=ROOT,env=env)
        dt=time.perf_counter()-t0; timings.append((name,dt))
        if proc.returncode:
            print(f'[{idx:02d}/{len(SCRIPTS):02d}] !! {name} FAILED after {dt:.1f}s',flush=True)
            return proc.returncode
        print(f'[{idx:02d}/{len(SCRIPTS):02d}] <== {name} OK in {dt:.1f}s',flush=True)
    total=time.perf_counter()-start_all
    print(f'v3.3 suite complete: {len(SCRIPTS)} experiments in {total:.1f}s',flush=True)
    print('slowest: '+', '.join(f'{n}={t:.1f}s' for n,t in sorted(timings,key=lambda x:x[1],reverse=True)[:3]),flush=True)
    return 0

if __name__=='__main__':
    raise SystemExit(main())
