from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt
from commlab.computation import simulate_edge_failure_recovery
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'results'/'data'; FIG=ROOT/'results'/'figures'; DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rows=[]
for pf in [.01,.04,.08,.12,.18,.25]:
    for p in ['restart','checkpoint','replicate']:
        rr=[simulate_edge_failure_recovery(n_tasks=5000,policy=p,failure_probability=pf,seed=s) for s in range(5)]
        rows.append([pf,p,np.mean([x['mean_latency_ms'] for x in rr]),np.mean([x['p95_latency_ms'] for x in rr]),np.mean([x['deadline_miss_rate'] for x in rr]),np.mean([x['recovery_traffic_mb_per_task'] for x in rr]),np.mean([x['compute_load_ratio'] for x in rr])])
with (DATA/'v31_failure_recovery.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['failure_probability','policy','mean_latency_ms','p95_latency_ms','deadline_miss_rate','recovery_traffic_mb_per_task','compute_load_ratio']); w.writerows(rows)
plt.figure(figsize=(7.2,4.7))
for p in ['restart','checkpoint','replicate']:
    r=[x for x in rows if x[1]==p]; plt.plot([100*x[0] for x in r],[x[3] for x in r],marker='o',label=p)
plt.xlabel('Per-task edge failure probability (%)'); plt.ylabel('P95 completion latency (ms)'); plt.title('Checkpointing and replication trade resources for tail recovery'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v31_failure_recovery_p95.png',dpi=170); plt.close()
plt.figure(figsize=(7.2,4.7))
for p in ['restart','checkpoint','replicate']:
    r=[x for x in rows if x[1]==p]; plt.plot([x[6] for x in r],[x[3] for x in r],marker='o',label=p)
plt.xlabel('Compute-load ratio'); plt.ylabel('P95 completion latency (ms)'); plt.title('Recovery speed has a compute-cost frontier'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v31_failure_recovery_compute.png',dpi=170); plt.close()
print('wrote v31 failure recovery')
