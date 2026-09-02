"""Run only experiments introduced in the v1.0 milestone."""
import subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=[
    'harq_incremental_redundancy.py',
    'coded_mimo_ldpc.py',
    'otfs_offgrid_refinement.py',
    'olla_link_adaptation.py',
    'ofdm_isac_range_doppler.py',
    'ofdm_isac_cfar.py',
    'full_receiver_impairment_stress.py',
]

if __name__=='__main__':
    for s in SCRIPTS:
        print(f'\n=== {s} ===',flush=True)
        subprocess.run([sys.executable,str(ROOT/'experiments'/s)],cwd=ROOT,check=True)
