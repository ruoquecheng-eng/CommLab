from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt
from commlab.computation import simulate_safety_aware_control
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'results'/'data'; FIG=ROOT/'results'/'figures'; DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rows=[]
for snr in [-5,-3,-1,1,3]:
    for p in ['max_age','max_error','safety_value']:
        rr=[simulate_safety_aware_control(slots=3000,policy=p,mean_snr_db=snr,seed=s) for s in range(6)]
        rows.append([snr,p,np.mean([x['mean_control_cost'] for x in rr]),np.mean([x['p95_control_cost'] for x in rr]),np.mean([x['safety_violation_rate'] for x in rr]),np.mean([x['mean_information_age'] for x in rr])])
with (DATA/'v31_safety_control.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['mean_snr_db','policy','mean_control_cost','p95_control_cost','safety_violation_rate','mean_information_age']); w.writerows(rows)
plt.figure(figsize=(7.2,4.7))
for p in ['max_age','max_error','safety_value']:
    r=[x for x in rows if x[1]==p]; plt.semilogy([x[0] for x in r],np.maximum([x[4] for x in r],1e-5),marker='o',label=p)
plt.xlabel('Mean feedback SNR (dB)'); plt.ylabel('Safety-violation probability'); plt.title('Safety value matters most near the communication-limited boundary'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v31_safety_violation.png',dpi=170); plt.close()
plt.figure(figsize=(7.2,4.7))
for p in ['max_age','max_error','safety_value']:
    r=[x for x in rows if x[1]==p]; plt.semilogy([x[0] for x in r],[x[2] for x in r],marker='o',label=p)
plt.xlabel('Mean feedback SNR (dB)'); plt.ylabel('Mean control cost'); plt.title('Safety protection is not free in every operating region'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v31_safety_cost.png',dpi=170); plt.close()
print('wrote v31 safety control')
