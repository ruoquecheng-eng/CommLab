from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt
from commlab.computation import simulate_control_uep
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'results'/'data'; FIG=ROOT/'results'/'figures'; DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rows=[]
for snr in [-6,-4,-2,0,2,5,8,12]:
    for p in ['equal','critical_uep']:
        rr=[simulate_control_uep(slots=3400,policy=p,mean_snr_db=snr,seed=s) for s in range(4)]
        rows.append([snr,p,np.mean([x['mean_control_cost'] for x in rr]),np.mean([x['p95_control_cost'] for x in rr]),np.mean([x['safety_violation_rate'] for x in rr]),np.mean([x['critical_component_miss_rate'] for x in rr]),np.mean([x['mean_repetitions_per_slot'] for x in rr])])
with (DATA/'v32_control_uep.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['mean_snr_db','policy','mean_control_cost','p95_control_cost','safety_violation_rate','critical_component_miss_rate','repetitions_per_slot']); w.writerows(rows)
plt.figure(figsize=(7.2,4.7))
for p in ['equal','critical_uep']:
    r=[x for x in rows if x[1]==p]; plt.semilogy([x[0] for x in r],[x[2] for x in r],marker='o',label=p)
plt.xlabel('Mean state-link SNR (dB)'); plt.ylabel('Mean control cost'); plt.title('UEP helps primarily in the communication-limited region'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v32_control_uep_cost.png',dpi=170); plt.close()
plt.figure(figsize=(7.2,4.7))
for p in ['equal','critical_uep']:
    r=[x for x in rows if x[1]==p]; plt.semilogy([x[0] for x in r],np.maximum([x[5] for x in r],1e-5),marker='o',label=p)
plt.xlabel('Mean state-link SNR (dB)'); plt.ylabel('Critical-component miss probability'); plt.title('Unequal repetition spends reliability on the critical state'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v32_control_uep_delivery.png',dpi=170); plt.close()
print('wrote v32 control UEP')
