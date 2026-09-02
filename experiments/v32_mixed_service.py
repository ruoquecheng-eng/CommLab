from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt
from commlab.computation import simulate_mixed_control_inference
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'results'/'data'; FIG=ROOT/'results'/'figures'; DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rows=[]
for load in [.2,.35,.5,.65,.8]:
    for p in ['control_first','inference_first','age_first','task_value']:
        rr=[simulate_mixed_control_inference(slots=3000,policy=p,inference_arrival=load,mean_snr_db=0,seed=s) for s in range(4)]
        rows.append([load,p,*[np.mean([x[k] for x in rr]) for k in ['mean_control_cost','p95_control_cost','safety_violation_rate','inference_completion_rate','inference_deadline_miss_rate','inference_utility_per_slot','control_slot_fraction']]])
with (DATA/'v32_mixed_control_inference.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['arrival_prob','policy','mean_control_cost','p95_control_cost','safety_violation_rate','inference_completion_rate','inference_deadline_miss_rate','inference_utility_per_slot','control_slot_fraction']); w.writerows(rows)
plt.figure(figsize=(7.2,4.7))
for p in ['control_first','inference_first','age_first','task_value']:
    r=[x for x in rows if x[1]==p]; plt.semilogy([x[0] for x in r],[x[2] for x in r],marker='o',label=p)
plt.xlabel('Inference arrival probability / slot'); plt.ylabel('Mean control cost'); plt.title('Inference traffic competes directly with physical control feedback'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v32_mixed_service_control_cost.png',dpi=170); plt.close()
plt.figure(figsize=(7.2,4.7))
for p in ['control_first','inference_first','age_first','task_value']:
    r=[x for x in rows if x[1]==p]; plt.plot([x[0] for x in r],[x[7] for x in r],marker='o',label=p)
plt.xlabel('Inference arrival probability / slot'); plt.ylabel('Delivered inference utility / slot'); plt.title('Task-value scheduling balances control and inference service value'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v32_mixed_service_inference_utility.png',dpi=170); plt.close()
print('wrote v32 mixed service')
