from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt
from commlab.computation import simulate_safety_bit_allocation
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'results'/'data'; FIG=ROOT/'results'/'figures'; DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rows=[]
for snr in [-5,-3,-1,1,3,5,8]:
    for p in ['uniform_low','single_high','risk_bitalloc']:
        rr=[simulate_safety_bit_allocation(slots=3000,policy=p,mean_snr_db=snr,bit_budget=10,seed=s) for s in range(4)]
        rows.append([snr,p,*[np.mean([x[k] for x in rr]) for k in ['mean_control_cost','p95_control_cost','safety_violation_rate','mean_payload_bits_per_slot','component_delivery_rate_per_slot']]])
with (DATA/'v32_safety_bit_allocation.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['mean_snr_db','policy','mean_control_cost','p95_control_cost','safety_violation_rate','payload_bits_per_slot','component_deliveries_per_slot']); w.writerows(rows)
plt.figure(figsize=(7.2,4.7))
for p in ['uniform_low','single_high','risk_bitalloc']:
    r=[x for x in rows if x[1]==p]; plt.semilogy([x[0] for x in r],[x[2] for x in r],marker='o',label=p)
plt.xlabel('Mean state-update SNR (dB)'); plt.ylabel('Mean control cost'); plt.title('Precision allocation has a channel-dependent operating region'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v32_safety_bitalloc_cost.png',dpi=170); plt.close()
plt.figure(figsize=(7.2,4.7))
for p in ['uniform_low','single_high','risk_bitalloc']:
    r=[x for x in rows if x[1]==p]; plt.plot([x[0] for x in r],[100*x[4] for x in r],marker='o',label=p)
plt.xlabel('Mean state-update SNR (dB)'); plt.ylabel('Safety violation rate (%)'); plt.title('More precision does not compensate for poor update deliverability'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v32_safety_bitalloc_safety.png',dpi=170); plt.close()
print('wrote v32 safety bit allocation')
