import subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=['joint_csi_fronthaul_control.py','deadline_harq_scheduling.py','aoi_status_updates.py','event_triggered_ris.py','budget_constrained_isac.py','grant_free_noma_random_access.py']
for s in SCRIPTS:
    print(f'== {s} ==',flush=True)
    subprocess.run([sys.executable,str(ROOT/'experiments'/s)],check=True,cwd=ROOT)
