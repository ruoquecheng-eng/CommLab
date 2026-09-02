import subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=['memory_polynomial_dpd.py','ici_aware_equalization.py','mimo_lmmse_estimation.py','otfs_iterative_detection.py','mimo_ml_detection.py','ber_confidence_intervals.py','mimo_pilot_efficiency.py','frequency_selective_iq.py']
for s in SCRIPTS:
    print('\n===',s,'===',flush=True)
    subprocess.run([sys.executable,str(ROOT/'experiments'/s)],check=True,cwd=ROOT)
