from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=[
    "v34_drift_adaptation.py","v34_localized_risk.py","v34_feedback_delay.py",
    "v34_adaptation_gain.py","v34_target_frontier.py","v34_correlation_reallocation.py",
]

def main():
    base=os.environ.copy(); timings=[]; start=time.perf_counter()
    for i,name in enumerate(SCRIPTS,1):
        print(f"[{i:02d}/{len(SCRIPTS):02d}] ==> {name}",flush=True)
        env=base.copy(); env["MPLCONFIGDIR"]=str(ROOT/".mplcache"/"v34_suite"/Path(name).stem)
        Path(env["MPLCONFIGDIR"]).mkdir(parents=True,exist_ok=True)
        t0=time.perf_counter(); p=subprocess.run([sys.executable,str(ROOT/"experiments"/name)],cwd=ROOT,env=env)
        dt=time.perf_counter()-t0; timings.append((name,dt))
        if p.returncode: return p.returncode
        print(f"[{i:02d}/{len(SCRIPTS):02d}] <== {name} OK in {dt:.1f}s",flush=True)
    print(f"v3.4 suite complete: {len(SCRIPTS)} experiments in {time.perf_counter()-start:.1f}s",flush=True)
    print("slowest: "+", ".join(f"{n}={t:.1f}s" for n,t in sorted(timings,key=lambda x:x[1],reverse=True)[:3]),flush=True)
    return 0

if __name__=="__main__": raise SystemExit(main())
