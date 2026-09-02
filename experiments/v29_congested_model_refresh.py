from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt
from commlab.computation import simulate_congested_model_refresh
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'results'/'data'; FIG=ROOT/'results'/'figures'; DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rows=[]
for svc in [.8,1.5,2.8,5.0,8.0]:
    for policy in ['eager','periodic_value','congestion_aware']:
        rr=[simulate_congested_model_refresh(backhaul_service_mb_per_request=svc,policy=policy,seed=s) for s in range(6)]
        rows.append([svc,policy,np.mean([x['mean_task_utility'] for x in rr]),np.mean([x['mean_served_version_age'] for x in rr]),np.mean([x['mean_latency_ms'] for x in rr]),np.mean([x['p95_backhaul_queue_mb'] for x in rr]),np.mean([x['refresh_requested_mb'] for x in rr]),np.mean([x['refresh_delivered_mb'] for x in rr])])
with (DATA/'v29_congested_model_refresh.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['backhaul_service_mb_per_request','policy','task_utility','served_version_age','latency_ms','p95_queue_mb','refresh_requested_mb','refresh_delivered_mb']); w.writerows(rows)
plt.figure(figsize=(7.2,4.7))
for p in ['eager','periodic_value','congestion_aware']:
    r=[x for x in rows if x[1]==p]; plt.plot([x[0] for x in r],[x[2] for x in r],marker='o',label=p)
plt.xlabel('Backhaul service (MB / inference request)'); plt.ylabel('Mean task utility'); plt.title('Model freshness under a congested refresh backhaul'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v29_cache_refresh_utility.png',dpi=170); plt.close()
plt.figure(figsize=(7.2,4.7))
for p in ['eager','periodic_value','congestion_aware']:
    r=[x for x in rows if x[1]==p]; plt.semilogy([x[0] for x in r],[max(x[5],1e-3) for x in r],marker='o',label=p)
plt.xlabel('Backhaul service (MB / inference request)'); plt.ylabel('P95 refresh queue (MB, log scale)'); plt.title('Eager freshness can overload the model-refresh queue'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v29_cache_refresh_queue.png',dpi=170); plt.close()
print('wrote v29 congested refresh')
