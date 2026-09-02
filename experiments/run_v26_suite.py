from pathlib import Path
import os,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
scripts=['v26_aircomp_selection.py','v26_progressive_split.py','v26_downlink_differential.py','v26_eh_aircomp_fl.py','v26_importance_multicast.py']
env=os.environ.copy(); env['PYTHONPATH']=str(ROOT/'src')+(os.pathsep+env['PYTHONPATH'] if env.get('PYTHONPATH') else '')
for s in scripts:
    print(f'==> {s}',flush=True); subprocess.run([sys.executable,str(ROOT/'experiments'/s)],check=True,env=env,cwd=ROOT)
