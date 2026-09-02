import subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=['irsa_coded_random_access.py','aircomp_aggregation.py','embb_urllc_slicing.py','energy_harvesting_aoi.py']
for s in SCRIPTS:
    print(f'== {s} ==',flush=True)
    subprocess.run([sys.executable,str(ROOT/'experiments'/s)],check=True,cwd=ROOT)
