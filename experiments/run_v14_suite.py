import subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=['cell_free_pilot_contamination.py','cellfree_ris_joint.py','cross_layer_olla_harq_queue.py','isac_joint_beamforming_pareto.py','cell_free_ap_activation_energy.py']
for s in SCRIPTS:
    print(f'== {s} ==',flush=True)
    subprocess.run([sys.executable,str(ROOT/'experiments'/s)],check=True,cwd=ROOT)
