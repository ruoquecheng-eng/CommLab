from pathlib import Path
import concurrent.futures, os, subprocess, sys, tempfile

ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=['v27_adaptive_downlink.py','v27_carbon_federated.py','v27_edge_caching.py','v27_queued_split.py','v27_multicast_repair.py']

def run_one(item):
    idx,s=item
    env=os.environ.copy()
    env['PYTHONPATH']=str(ROOT/'src')+(os.pathsep+env['PYTHONPATH'] if env.get('PYTHONPATH') else '')
    # Avoid matplotlib cache contention while independent experiments run in parallel.
    mpl=ROOT/'.mplcache'/f'v27_{idx}'
    mpl.mkdir(parents=True,exist_ok=True)
    env['MPLCONFIGDIR']=str(mpl)
    print(f'==> {s}',flush=True)
    subprocess.run([sys.executable,str(ROOT/'experiments'/s)],check=True,env=env,cwd=ROOT)
    return s

with concurrent.futures.ThreadPoolExecutor(max_workers=min(5,len(SCRIPTS))) as ex:
    futs=[ex.submit(run_one,x) for x in enumerate(SCRIPTS)]
    for fut in concurrent.futures.as_completed(futs):
        print(f'<== {fut.result()} OK',flush=True)
