from pathlib import Path
import concurrent.futures, os, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=['v28_selective_downlink_repair.py','v28_versioned_caching.py','v28_fair_carbon_orchestration.py','v28_split_admission.py','v28_digital_twin_sync.py']
def run_one(item):
    idx,s=item; env=os.environ.copy(); env['PYTHONPATH']=str(ROOT/'src')+(os.pathsep+env['PYTHONPATH'] if env.get('PYTHONPATH') else '')
    mpl=ROOT/'.mplcache'/f'v28_{idx}'; mpl.mkdir(parents=True,exist_ok=True); env['MPLCONFIGDIR']=str(mpl)
    print(f'==> {s}',flush=True); subprocess.run([sys.executable,str(ROOT/'experiments'/s)],check=True,env=env,cwd=ROOT); return s
with concurrent.futures.ThreadPoolExecutor(max_workers=min(5,len(SCRIPTS))) as ex:
    futs=[ex.submit(run_one,x) for x in enumerate(SCRIPTS)]
    for fut in concurrent.futures.as_completed(futs): print(f'<== {fut.result()} OK',flush=True)
