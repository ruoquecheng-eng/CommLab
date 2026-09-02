import subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=['cell_free_fronthaul_csi.py','cellfree_ris_robust_imperfect_csi.py','short_packet_fbl_cross_layer.py','isac_sensing_resource_scheduling.py','cell_free_csi_aging.py']
for s in SCRIPTS:
    print(f'== {s} ==',flush=True)
    subprocess.run([sys.executable,str(ROOT/'experiments'/s)],check=True,cwd=ROOT)
