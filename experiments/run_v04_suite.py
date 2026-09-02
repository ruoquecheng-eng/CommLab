import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = [
    "coded_ofdm.py",
    "mimo_ofdm_multipath.py",
    "pa_nonlinearity.py",
    "doppler_ici.py",
    "papr_slm.py",
    "channel_estimation_methods.py",
    "waterfilling_ofdm.py",
]

for name in SCRIPTS:
    print(f"\n=== {name} ===", flush=True)
    subprocess.run([sys.executable, str(ROOT / "experiments" / name)], check=True, cwd=ROOT)
