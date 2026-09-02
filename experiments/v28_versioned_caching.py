from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt
from commlab.computation import simulate_version_aware_edge_caching
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'results'/'data'; FIG=ROOT/'results'/'figures'; DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
policies=['popularity','latency_value','version_value','lru']; rows=[]
for p in policies:
    rr=[simulate_version_aware_edge_caching(policy=p,n_requests=3200,refresh_interval=100,refresh_budget_mb=180,seed=s) for s in range(10)]
    rows.append([p,np.mean([x['cache_hit_rate'] for x in rr]),np.mean([x['mean_latency_ms'] for x in rr]),np.mean([x['mean_task_utility'] for x in rr]),np.mean([x['mean_served_version_age'] for x in rr]),np.mean([x['backhaul_mb'] for x in rr]),np.mean([x['model_refresh_mb'] for x in rr])])
with (DATA/'v28_versioned_caching_policies.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['policy','cache_hit_rate','mean_latency_ms','mean_task_utility','mean_served_version_age','backhaul_mb','model_refresh_mb']); w.writerows(rows)
brows=[]
for b in [80,120,180,260,400,700]:
    rr=[simulate_version_aware_edge_caching(policy='version_value',n_requests=3200,refresh_interval=100,refresh_budget_mb=b,seed=s) for s in range(10)]
    brows.append([b,np.mean([x['cache_hit_rate'] for x in rr]),np.mean([x['mean_latency_ms'] for x in rr]),np.mean([x['mean_task_utility'] for x in rr]),np.mean([x['mean_served_version_age'] for x in rr]),np.mean([x['backhaul_mb'] for x in rr])])
with (DATA/'v28_versioned_caching_budget.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['refresh_budget_mb_per_epoch','cache_hit_rate','mean_latency_ms','mean_task_utility','mean_served_version_age','backhaul_mb']); w.writerows(brows)
plt.figure(figsize=(7.2,4.7)); plt.plot([x[5] for x in brows],[x[3] for x in brows],marker='o');
for x in brows: plt.annotate(str(x[0]),(x[5],x[3]),xytext=(4,4),textcoords='offset points')
plt.xlabel('Total modeled backhaul (MB)'); plt.ylabel('Mean task utility'); plt.title('Version freshness requires a refresh budget'); plt.grid(alpha=.25); plt.tight_layout(); plt.savefig(FIG/'v28_versioned_cache_utility_backhaul.png',dpi=170); plt.close()
plt.figure(figsize=(7.2,4.7));
for i,r in enumerate(rows): plt.scatter(r[5],r[3],s=55,label=r[0])
plt.xlabel('Total modeled backhaul (MB)'); plt.ylabel('Mean task utility'); plt.title('Cache hit rate is not enough when models evolve'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v28_versioned_cache_policies.png',dpi=170); plt.close()
print('wrote v28 versioned caching')
