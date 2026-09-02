import subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=['async_cellfree_csi.py','predictive_csi_quantization.py','fbl_ir_harq.py','two_timescale_ris.py','queue_aware_isac.py']
for s in SCRIPTS:
    print(f'== {s} ==',flush=True)
    subprocess.run([sys.executable,str(ROOT/'experiments'/s)],check=True,cwd=ROOT)
