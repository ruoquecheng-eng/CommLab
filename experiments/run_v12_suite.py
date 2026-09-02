import subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=['ris_phase_quantization.py','mu_mimo_user_selection.py','music_mdl_model_order.py','isac_multitarget_kalman.py','hybrid_omp_precoding.py']
for s in SCRIPTS:
    print(f'== {s} ==',flush=True); subprocess.run([sys.executable,str(ROOT/'experiments'/s)],check=True,cwd=ROOT)
