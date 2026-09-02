from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt
from commlab.computation import simulate_networked_control_scheduling
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'results'/'data'; FIG=ROOT/'results'/'figures'; DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rows=[]
for snr in [-4,-1,2,5,8]:
    for policy in ['round_robin','max_age','max_error','control_value']:
        rr=[simulate_networked_control_scheduling(mean_snr_db=snr,policy=policy,seed=s) for s in range(9)]
        rows.append([snr,policy,np.mean([x['mean_control_cost'] for x in rr]),np.mean([x['p95_control_cost'] for x in rr]),np.mean([x['mean_estimation_rmse'] for x in rr]),np.mean([x['mean_information_age'] for x in rr]),np.mean([x['max_state_excursion'] for x in rr]),np.mean([x['successful_update_fraction'] for x in rr]),np.mean([x['selection_jain'] for x in rr])])
with (DATA/'v29_networked_control.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['mean_snr_db','policy','mean_control_cost','p95_control_cost','estimation_rmse','mean_information_age','max_state_excursion','update_success_fraction','selection_jain']); w.writerows(rows)
plt.figure(figsize=(7.2,4.7))
for p in ['round_robin','max_age','max_error','control_value']:
    r=[x for x in rows if x[1]==p]; plt.semilogy([x[0] for x in r],[x[2] for x in r],marker='o',label=p)
plt.xlabel('Mean sensor-link SNR (dB)'); plt.ylabel('Mean closed-loop cost (log scale)'); plt.title('Wireless scheduling changes physical control performance'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v29_control_cost.png',dpi=170); plt.close()
plt.figure(figsize=(7.2,4.7))
for p in ['max_age','max_error','control_value']:
    r=[x for x in rows if x[1]==p]; plt.plot([x[5] for x in r],[x[2] for x in r],marker='o',label=p)
plt.xlabel('Mean information age (slots)'); plt.ylabel('Mean closed-loop cost'); plt.title('Freshness alone is not the same as control value'); plt.yscale('log'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v29_control_age_value.png',dpi=170); plt.close()
print('wrote v29 networked control')
