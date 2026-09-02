"""Run the experiments introduced in CommLab-OFDM v0.6."""
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=[
    'iq_imbalance_compensation.py',
    'sampling_clock_offset.py',
    'narrowband_interference.py',
    'ldpc_min_sum_ofdm.py',
    'learned_polynomial_dpd.py',
    'otfs_high_doppler.py',
]

if __name__=='__main__':
    for name in SCRIPTS:
        print(f'\n=== {name} ===', flush=True)
        subprocess.run([sys.executable,str(ROOT/'experiments'/name)],cwd=ROOT,check=True)
