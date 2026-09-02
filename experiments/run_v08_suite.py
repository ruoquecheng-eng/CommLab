import os, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=[
    'mimo_kbest_detection.py',
    'mimo_spatial_correlation.py',
    'limited_feedback_beamforming.py',
    'ici_cg_equalization.py',
    'adaptive_memory_dpd.py',
    'generalized_memory_dpd.py',
    'fec_rate_half_benchmark.py',
    'proportional_fair_ofdma.py',
]
env=os.environ.copy(); env['PYTHONPATH']=str(ROOT/'src')+os.pathsep+env.get('PYTHONPATH','')
for s in SCRIPTS:
    print(f'\n=== {s} ===',flush=True)
    subprocess.run([sys.executable,str(ROOT/'experiments'/s)],check=True,cwd=ROOT,env=env)
