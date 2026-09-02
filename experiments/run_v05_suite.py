"""Run the v0.5 experiment additions sequentially."""
import subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=[
    'soft_coded_ofdm.py',
    'phase_noise_tracking.py',
    'dpd_rapp.py',
    'mimo_channel_estimation.py',
    'alamouti_diversity.py',
]
for name in SCRIPTS:
    print(f'\n=== {name} ===', flush=True)
    subprocess.run([sys.executable, str(ROOT/'experiments'/name)], cwd=ROOT, check=True)
