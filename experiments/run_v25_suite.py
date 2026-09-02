from pathlib import Path
import os,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
scripts=['v25_resilient_async.py','v25_cluster_personalization.py','v25_private_hardware_aircomp.py','v25_private_hardware_pa.py','v25_energy_split.py','v25_model_multicast.py']
env=os.environ.copy(); env['PYTHONPATH']=str(ROOT/'src')+(os.pathsep+env['PYTHONPATH'] if env.get('PYTHONPATH') else '')
for s in scripts:
    print(f'==> {s}',flush=True); subprocess.run([sys.executable,str(ROOT/'experiments'/s)],check=True,env=env,cwd=ROOT)
