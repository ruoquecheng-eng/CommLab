import os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=['v20_federated_aircomp_learning.py','v20_ris_aircomp_learning.py','v20_cellfree_aircomp.py','v20_task_oriented_semcom.py','v20_capture_irsa.py']
env=os.environ.copy(); env['PYTHONPATH']=str(ROOT/'src')+(os.pathsep+env['PYTHONPATH'] if env.get('PYTHONPATH') else '')
for s in SCRIPTS:
    print(f'== {s} ==',flush=True)
    subprocess.run([sys.executable,str(ROOT/'experiments'/s)],check=True,cwd=ROOT,env=env)
