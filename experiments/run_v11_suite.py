import subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=['mimo_mmse_sic.py','massive_mimo_precoding.py','massive_mimo_pilot_contamination.py','hybrid_beamforming.py','ofdm_isac_angle.py','isac_music_angle.py','isac_range_tracking.py','otfs_fractional_delay_refinement.py','harq_circular_redundancy_versions.py']
for s in SCRIPTS:
    print(f'== {s} ==',flush=True); subprocess.run([sys.executable,str(ROOT/'experiments'/s)],check=True,cwd=ROOT)
