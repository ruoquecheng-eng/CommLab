from pathlib import Path
import os,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
scripts=['v23_async_federated.py','v23_byzantine_robust_fl.py','v23_private_aircomp.py','v23_semantic_scheduler.py','v23_split_inference.py']
env=os.environ.copy(); env['PYTHONPATH']=str(ROOT/'src')+(os.pathsep+env['PYTHONPATH'] if env.get('PYTHONPATH') else '')
for s in scripts:
    print(f'==> {s}',flush=True)
    subprocess.run([sys.executable,str(ROOT/'experiments'/s)],check=True,env=env,cwd=ROOT)
