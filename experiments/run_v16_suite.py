import subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=['cellfree_ris_aged_quantized_csi.py','fbl_harq_queue_coupled.py','isac_predictive_sensing_on_demand.py','cellfree_fronthaul_energy_joint.py']
for s in SCRIPTS:
    print(f'== {s} ==',flush=True)
    subprocess.run([sys.executable,str(ROOT/'experiments'/s)],check=True,cwd=ROOT)
