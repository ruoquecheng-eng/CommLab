import subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=[
    'cell_free_user_centric.py','cell_free_power_control.py','ris_multiuser_coordinate.py',
    'isac_predictive_beam_tracking.py','isac_uncertainty_aware_beamwidth.py',
]
for s in SCRIPTS:
    print(f'== {s} ==',flush=True); subprocess.run([sys.executable,str(ROOT/'experiments'/s)],check=True,cwd=ROOT)
