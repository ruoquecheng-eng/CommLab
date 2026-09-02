from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt
from commlab.computation import simulate_joint_cache_offload
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'results'/'data'; FIG=ROOT/'results'/'figures'; DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rows=[]
for cap in [260,360,520,700]:
    for policy in ['nearest','cache_first','joint']:
        rr=[simulate_joint_cache_offload(n_requests=6000,cache_capacity_mb=cap,policy=policy,seed=s) for s in range(6)]
        rows.append([cap,policy,np.mean([x['mean_latency_ms'] for x in rr]),np.mean([x['p95_latency_ms'] for x in rr]),np.mean([x['cache_hit_rate'] for x in rr]),np.mean([x['backhaul_mb_per_request'] for x in rr]),np.mean([x['offload_jain'] for x in rr])])
with (DATA/'v30_joint_cache_offload.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['cache_capacity_mb','policy','mean_latency_ms','p95_latency_ms','cache_hit_rate','backhaul_mb_per_request','offload_jain']); w.writerows(rows)
plt.figure(figsize=(7.2,4.7))
for p in ['nearest','cache_first','joint']:
    r=[x for x in rows if x[1]==p]; plt.plot([x[0] for x in r],[x[2] for x in r],marker='o',label=p)
plt.xlabel('Edge model-cache capacity (MB)'); plt.ylabel('Mean inference latency (ms)'); plt.title('Caching and offloading must be optimized together'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v30_cache_offload_latency.png',dpi=170); plt.close()
plt.figure(figsize=(7.2,4.7))
for p in ['nearest','cache_first','joint']:
    r=[x for x in rows if x[1]==p]; plt.plot([100*x[4] for x in r],[x[2] for x in r],marker='o',label=p)
plt.xlabel('Cache hit rate (%)'); plt.ylabel('Mean inference latency (ms)'); plt.title('High hit rate can still create edge-queue imbalance'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v30_cache_hit_latency.png',dpi=170); plt.close()
print('wrote v30 joint cache/offload')
