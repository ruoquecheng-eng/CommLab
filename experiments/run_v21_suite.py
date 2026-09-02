import os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=['v21_non_iid_client_selection.py','v21_random_access_federated.py','v21_robust_aircomp_uncertainty.py','v21_multitask_semantic.py']
env=os.environ.copy(); env['PYTHONPATH']=str(ROOT/'src')+(os.pathsep+env['PYTHONPATH'] if env.get('PYTHONPATH') else '')
for s in SCRIPTS:
    print(f'== {s} ==',flush=True); subprocess.run([sys.executable,str(ROOT/'experiments'/s)],check=True,cwd=ROOT,env=env)
