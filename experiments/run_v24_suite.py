from pathlib import Path
import os,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
scripts=['v24_personalized_fl.py','v24_straggler_coding.py','v24_federated_distillation.py','v24_channel_aware_split.py','v24_sign_aircomp.py']
env=os.environ.copy(); env['PYTHONPATH']=str(ROOT/'src')+(os.pathsep+env['PYTHONPATH'] if env.get('PYTHONPATH') else '')
for s in scripts:
    print(f'==> {s}',flush=True); subprocess.run([sys.executable,str(ROOT/'experiments'/s)],check=True,env=env,cwd=ROOT)
