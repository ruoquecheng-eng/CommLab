"""Run the main v0.3 experiment suite sequentially."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = [
    "ber_awgn.py",
    "channel_estimation.py",
    "rayleigh_equalizers.py",
    "mmse_symbol_mse.py",
    "synchronization_cfo.py",
    "full_system_sync.py",
    "pilot_density_tradeoff.py",
    "cp_length_tradeoff.py",
    "papr_clipping.py",
    "adaptive_modulation.py",
    "mimo_2x2.py",
]

if __name__ == "__main__":
    for script in SCRIPTS:
        print(f"\n=== {script} ===", flush=True)
        subprocess.run([sys.executable, str(ROOT / "experiments" / script)], check=True, cwd=ROOT)
    print("\nAll v0.3 experiments completed successfully.")
