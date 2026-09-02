from pathlib import Path
import concurrent.futures, os, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=['v30_risk_sensitive_control.py','v30_variable_rate_control.py','v30_failure_aware_edge.py','v30_joint_cache_offload.py','v30_cooperative_control.py']
def run_one(item):
    idx,s=item; env=os.environ.copy(); env['PYTHONPATH']=str(ROOT/'src')+(os.pathsep+env['PYTHONPATH'] if env.get('PYTHONPATH') else '')
    mpl=ROOT/'.mplcache'/f'v30_{idx}'; mpl.mkdir(parents=True,exist_ok=True); env['MPLCONFIGDIR']=str(mpl)
    print(f'==> {s}',flush=True); subprocess.run([sys.executable,str(ROOT/'experiments'/s)],check=True,env=env,cwd=ROOT); return s
with concurrent.futures.ThreadPoolExecutor(max_workers=min(5,len(SCRIPTS))) as ex:
    futs=[ex.submit(run_one,x) for x in enumerate(SCRIPTS)]
    for fut in concurrent.futures.as_completed(futs): print(f'<== {fut.result()} OK',flush=True)
