from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt
from commlab.computation import simulate_task_aware_model_repair
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'results'/'data'; FIG=ROOT/'results'/'figures'; DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rows=[]
for burst in [.6,1.2,1.8,2.4,3.0,3.6]:
    for policy in ['age_only','static_importance','task_aware']:
        rr=[simulate_task_aware_model_repair(burst_strength=burst,policy=policy,seed=s) for s in range(8)]
        rows.append([burst,policy,np.mean([x['task_utility_ratio'] for x in rr]),np.mean([x['mean_active_task_model_age'] for x in rr]),np.mean([x['mean_static_weighted_model_age'] for x in rr]),np.mean([x['normalized_downlink_size_per_round'] for x in rr])])
with (DATA/'v29_task_aware_repair.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['burst_strength','policy','task_utility_ratio','active_task_model_age','static_weighted_age','downlink_size_per_round']); w.writerows(rows)
plt.figure(figsize=(7.2,4.7))
for p in ['age_only','static_importance','task_aware']:
    r=[x for x in rows if x[1]==p]; plt.plot([x[0] for x in r],[x[2] for x in r],marker='o',label=p)
plt.xlabel('Task-demand burst strength'); plt.ylabel('Realized / ideal task utility'); plt.title('Repair value depends on current task demand'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v29_task_repair_utility.png',dpi=170); plt.close()
plt.figure(figsize=(7.2,4.7))
for p in ['age_only','static_importance','task_aware']:
    r=[x for x in rows if x[1]==p]; plt.plot([x[0] for x in r],[x[3] for x in r],marker='o',label=p)
plt.xlabel('Task-demand burst strength'); plt.ylabel('Task-weighted model age (rounds)'); plt.title('Dynamic repair targets clients that are stale *and* busy'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v29_task_repair_age.png',dpi=170); plt.close()
print('wrote v29 task-aware repair')
