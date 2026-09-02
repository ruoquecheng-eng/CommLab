from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt
from commlab.computation import simulate_variable_rate_control
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'results'/'data'; FIG=ROOT/'results'/'figures'; DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rows=[]
for snr in [-2,0,2,4,6]:
    for policy in ['fixed_low','fixed_high','adaptive']:
        rr=[simulate_variable_rate_control(slots=2600,policy=policy,mean_snr_db=snr,seed=s) for s in range(6)]
        rows.append([snr,policy,np.mean([x['mean_control_cost'] for x in rr]),np.mean([x['p95_control_cost'] for x in rr]),np.mean([x['mean_payload_bits_per_slot'] for x in rr]),np.mean([x['update_success_rate'] for x in rr])])
with (DATA/'v30_variable_rate_control.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['mean_snr_db','policy','mean_control_cost','p95_control_cost','payload_bits_per_slot','update_success_rate']); w.writerows(rows)
plt.figure(figsize=(7.2,4.7))
for p in ['fixed_low','fixed_high','adaptive']:
    r=[x for x in rows if x[1]==p]; plt.semilogy([x[0] for x in r],[x[2] for x in r],marker='o',label=p)
plt.xlabel('Mean sensor-link SNR (dB)'); plt.ylabel('Mean control cost (log scale)'); plt.title('State precision competes with packet deliverability'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v30_semantic_control_cost.png',dpi=170); plt.close()
plt.figure(figsize=(7.2,4.7))
for p in ['fixed_low','fixed_high','adaptive']:
    r=[x for x in rows if x[1]==p]; plt.plot([x[4] for x in r],[x[2] for x in r],marker='o',label=p)
plt.xlabel('Mean payload bits / slot'); plt.ylabel('Mean control cost'); plt.yscale('log'); plt.title('Variable-rate control exposes precision–radio-cost trade-offs'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v30_semantic_control_tradeoff.png',dpi=170); plt.close()
print('wrote v30 variable-rate control')
