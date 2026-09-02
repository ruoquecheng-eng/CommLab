from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt
from commlab.computation import simulate_chance_constrained_inference
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'results'/'data'; FIG=ROOT/'results'/'figures'; DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rows=[]
for jitter in [0,.25,.5,.75,1.0]:
    for p in ['mean_latency','chance']:
        rr=[simulate_chance_constrained_inference(n_tasks=14000,policy=p,jitter_scale=jitter,deadline_ms=50,reliability_target=.99,seed=s) for s in range(5)]
        keys=['admission_rate','rejection_rate','deadline_miss_rate','overall_late_fraction','raw_utility_per_task','on_time_utility_per_task','mean_admitted_latency_ms','p95_admitted_latency_ms']
        rows.append([jitter,p,*[np.mean([x[k] for x in rr]) for k in keys]])
with (DATA/'v32_chance_constrained_inference.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['jitter_scale','policy','admission_rate','rejection_rate','admitted_deadline_miss_rate','overall_late_fraction','raw_utility_per_task','on_time_utility_per_task','mean_admitted_latency_ms','p95_admitted_latency_ms']); w.writerows(rows)
plt.figure(figsize=(7.2,4.7))
for p in ['mean_latency','chance']:
    r=[x for x in rows if x[1]==p]; plt.semilogy([x[0] for x in r],np.maximum([x[4] for x in r],1e-5),marker='o',label=p)
plt.xlabel('Latency-jitter scale'); plt.ylabel('Admitted deadline-miss probability'); plt.title('Chance constraints trade admission for deadline reliability'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v32_chance_inference_deadline.png',dpi=170); plt.close()
plt.figure(figsize=(7.2,4.7))
for p in ['mean_latency','chance']:
    r=[x for x in rows if x[1]==p]; plt.plot([x[0] for x in r],[x[7] for x in r],marker='o',label=f'{p}: on-time utility'); plt.plot([x[0] for x in r],[x[6] for x in r],ls='--',alpha=.6,label=f'{p}: raw utility')
plt.xlabel('Latency-jitter scale'); plt.ylabel('Utility / task'); plt.title('Raw utility can hide deadline-tail collapse'); plt.grid(alpha=.25); plt.legend(fontsize=8); plt.tight_layout(); plt.savefig(FIG/'v32_chance_inference_utility.png',dpi=170); plt.close()
print('wrote v32 chance-constrained inference')
