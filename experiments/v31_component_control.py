from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt
from commlab.computation import simulate_component_selective_control
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'results'/'data'; FIG=ROOT/'results'/'figures'; DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rows=[]
for snr in [-5,-3,-1,1,3,5,8]:
    for p in ['round_robin','all_low','value_component']:
        rr=[simulate_component_selective_control(slots=3000,policy=p,mean_snr_db=snr,seed=s) for s in range(6)]
        rows.append([snr,p,np.mean([x['mean_control_cost'] for x in rr]),np.mean([x['p95_control_cost'] for x in rr]),np.mean([x['mean_payload_bits_per_slot'] for x in rr]),np.mean([x['update_success_rate'] for x in rr])])
with (DATA/'v31_component_control.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['mean_snr_db','policy','mean_control_cost','p95_control_cost','mean_payload_bits_per_slot','update_success_rate']); w.writerows(rows)
plt.figure(figsize=(7.2,4.7))
for p in ['round_robin','all_low','value_component']:
    r=[x for x in rows if x[1]==p]; plt.semilogy([x[0] for x in r],[x[2] for x in r],marker='o',label=p)
plt.xlabel('Mean feedback SNR (dB)'); plt.ylabel('Mean control cost'); plt.title('Control-semantic compression should preserve valuable state components'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v31_component_control_cost.png',dpi=170); plt.close()
plt.figure(figsize=(7.2,4.7))
for p in ['round_robin','all_low','value_component']:
    r=[x for x in rows if x[1]==p]; plt.plot([x[0] for x in r],[100*x[5] for x in r],marker='o',label=p)
plt.xlabel('Mean feedback SNR (dB)'); plt.ylabel('Update delivery rate (%)'); plt.title('All-low precision improves delivery but can distort important states'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v31_component_control_delivery.png',dpi=170); plt.close()
print('wrote v31 component control')
