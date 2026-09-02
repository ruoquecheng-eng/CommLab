import os, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=[
    'coded_mimo_soft_output.py',
    'harq_chase_combining.py',
    'queue_aware_ofdma.py',
    'ici_matrix_estimation.py',
    'otfs_sparse_path_estimation.py',
    'finite_blocklength_awgn.py',
]
env=os.environ.copy(); env['PYTHONPATH']=str(ROOT/'src')+os.pathsep+env.get('PYTHONPATH','')
for s in SCRIPTS:
    print(f'\n=== {s} ===',flush=True)
    subprocess.run([sys.executable,str(ROOT/'experiments'/s)],check=True,cwd=ROOT,env=env)
