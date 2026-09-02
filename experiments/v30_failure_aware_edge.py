from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt
from commlab.computation import simulate_failure_aware_edge_orchestration
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'results'/'data'; FIG=ROOT/'results'/'figures'; DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rows=[]
for load in [.6,.9,1.2,1.5,1.8]:
    for policy in ['latency_only','trust_aware','risk_aware']:
        rr=[simulate_failure_aware_edge_orchestration(n_tasks=5000,policy=policy,load=load,seed=s) for s in range(6)]
        rows.append([load,policy,np.mean([x['mean_latency_ms'] for x in rr]),np.mean([x['p95_latency_ms'] for x in rr]),np.mean([x['failure_rate'] for x in rr]),np.mean([x['deadline_miss_rate'] for x in rr]),np.mean([x['energy_proxy_per_task'] for x in rr])])
with (DATA/'v30_failure_aware_edge.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['load','policy','mean_latency_ms','p95_latency_ms','failure_rate','deadline_miss_rate','energy_proxy_per_task']); w.writerows(rows)
plt.figure(figsize=(7.2,4.7))
for p in ['latency_only','trust_aware','risk_aware']:
    r=[x for x in rows if x[1]==p]; plt.plot([x[0] for x in r],[100*x[4] for x in r],marker='o',label=p)
plt.xlabel('Offered task load'); plt.ylabel('Execution failure rate (%)'); plt.title('Lowest-latency edge is not necessarily the safest edge'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v30_edge_failure.png',dpi=170); plt.close()
plt.figure(figsize=(7.2,4.7))
for p in ['latency_only','trust_aware','risk_aware']:
    r=[x for x in rows if x[1]==p]; plt.plot([100*x[4] for x in r],[x[2] for x in r],marker='o',label=p)
plt.xlabel('Execution failure rate (%)'); plt.ylabel('Mean task latency (ms)'); plt.title('Reliability-aware orchestration pays a latency premium'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v30_edge_latency_reliability.png',dpi=170); plt.close()
print('wrote v30 failure-aware edge')
