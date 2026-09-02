from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt
from commlab.computation import simulate_cooperative_networked_control
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'results'/'data'; FIG=ROOT/'results'/'figures'; DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rows=[]
for snr in [-4,-2,0,2,4]:
    for policy in ['max_age','local_error','system_value']:
        rr=[simulate_cooperative_networked_control(slots=3000,policy=policy,mean_snr_db=snr,seed=s) for s in range(6)]
        rows.append([snr,policy,np.mean([x['mean_system_cost'] for x in rr]),np.mean([x['p95_system_cost'] for x in rr]),np.mean([x['mean_formation_error'] for x in rr]),np.mean([x['mean_information_age'] for x in rr])])
with (DATA/'v30_cooperative_control.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['mean_snr_db','policy','mean_system_cost','p95_system_cost','mean_formation_error','mean_information_age']); w.writerows(rows)
plt.figure(figsize=(7.2,4.7))
for p in ['max_age','local_error','system_value']:
    r=[x for x in rows if x[1]==p]; plt.semilogy([x[0] for x in r],[x[2] for x in r],marker='o',label=p)
plt.xlabel('Mean shared-link SNR (dB)'); plt.ylabel('Mean multi-agent system cost'); plt.title('System-level scheduling helps most in the communication-limited regime'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v30_cooperative_cost.png',dpi=170); plt.close()
plt.figure(figsize=(7.2,4.7))
for p in ['max_age','local_error','system_value']:
    r=[x for x in rows if x[1]==p]; plt.plot([x[0] for x in r],[x[4] for x in r],marker='o',label=p)
plt.xlabel('Mean shared-link SNR (dB)'); plt.ylabel('Mean formation error'); plt.title('Local estimation error is not always the full system value'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v30_cooperative_formation.png',dpi=170); plt.close()
print('wrote v30 cooperative control')
