from pathlib import Path
import concurrent.futures, os, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=['v31_safety_control.py','v31_adaptive_depth.py','v31_failure_recovery.py','v31_model_replication.py','v31_component_control.py']
def run_one(item):
    idx,s=item; env=os.environ.copy(); env['PYTHONPATH']=str(ROOT/'src')+(os.pathsep+env['PYTHONPATH'] if env.get('PYTHONPATH') else '')
    mpl=ROOT/'.mplcache'/f'v31_{idx}'; mpl.mkdir(parents=True,exist_ok=True); env['MPLCONFIGDIR']=str(mpl)
    print(f'==> {s}',flush=True); subprocess.run([sys.executable,str(ROOT/'experiments'/s)],check=True,env=env,cwd=ROOT); return s
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
    futs=[ex.submit(run_one,x) for x in enumerate(SCRIPTS)]
    for fut in concurrent.futures.as_completed(futs): print(f'<== {fut.result()} OK',flush=True)
