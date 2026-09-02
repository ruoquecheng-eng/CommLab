from pathlib import Path
import os,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
scripts=[
 'v22_budgeted_gradient_compression.py','v22_aircomp_hardware.py','v22_layered_semantic.py',
 'v22_importance_random_access_fl.py','v22_two_timescale_ris_fl.py']
env=os.environ.copy(); env['PYTHONPATH']=str(ROOT/'src')+(os.pathsep+env['PYTHONPATH'] if env.get('PYTHONPATH') else '')
for s in scripts:
    print(f'==> {s}',flush=True); subprocess.run([sys.executable,str(ROOT/'experiments'/s)],check=True,env=env,cwd=ROOT)
