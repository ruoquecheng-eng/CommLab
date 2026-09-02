from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt
from commlab.computation import simulate_multiconnectivity_safety_control
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'results'/'data'; FIG=ROOT/'results'/'figures'; DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rows=[]
for rho in [0,.2,.4,.6,.8,.95]:
    for p in ['single','full_duplicate','adaptive_duplicate']:
        rr=[simulate_multiconnectivity_safety_control(slots=2400,policy=p,correlation=rho,mean_snr_db=-2,seed=s) for s in range(4)]
        keys=['mean_control_cost','p95_control_cost','safety_violation_rate','update_success_rate','mean_transmissions_per_slot','duplication_rate']
        rows.append([rho,p,*[np.mean([x[k] for x in rr]) for k in keys]])
with (DATA/'v32_multiconnectivity_safety_control.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['link_correlation','policy','mean_control_cost','p95_control_cost','safety_violation_rate','update_success_rate','transmissions_per_slot','duplication_rate']); w.writerows(rows)
plt.figure(figsize=(7.2,4.7))
for p in ['single','full_duplicate','adaptive_duplicate']:
    r=[x for x in rows if x[1]==p]; plt.semilogy([x[0] for x in r],np.maximum([x[4] for x in r],1e-5),marker='o',label=p)
plt.xlabel('Link-failure correlation'); plt.ylabel('Safety-violation probability'); plt.title('Packet diversity matters only through downstream control safety'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v32_multiconnectivity_control_safety.png',dpi=170); plt.close()
plt.figure(figsize=(7.2,4.7))
for p in ['single','full_duplicate','adaptive_duplicate']:
    r=[x for x in rows if x[1]==p]; plt.plot([x[0] for x in r],[x[6] for x in r],marker='o',label=p)
plt.xlabel('Link-failure correlation'); plt.ylabel('Radio transmissions / control slot'); plt.title('Safety-aware adaptive duplication reduces radio use'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v32_multiconnectivity_control_overhead.png',dpi=170); plt.close()
print('wrote v32 multi-connectivity x safety control')
