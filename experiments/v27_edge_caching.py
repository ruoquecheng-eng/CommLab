from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt
from commlab.computation import simulate_edge_model_caching
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'results/data'; F=ROOT/'results/figures'; D.mkdir(parents=True,exist_ok=True); F.mkdir(parents=True,exist_ok=True)
polrows=[]
for p in ['static','lru','periodic_popularity','periodic_value']:
    vals=[simulate_edge_model_caching(policy=p,recache_interval=160,seed=2730+r) for r in range(24)]
    polrows.append((p,*[np.mean([v[k] for v in vals]) for k in ['mean_latency_ms','p95_latency_ms','cache_hit_rate','backhaul_mb','cache_updates']]))
with open(D/'v27_edge_caching_policies.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['policy','mean_latency_ms','p95_latency_ms','cache_hit_rate','backhaul_mb','cache_updates']); w.writerows(polrows)
rows=[]
for k in [40,80,160,320,640,1280]:
    vals=[simulate_edge_model_caching(policy='periodic_value',recache_interval=k,seed=2760+r) for r in range(24)]
    rows.append((k,*[np.mean([v[q] for v in vals]) for q in ['mean_latency_ms','cache_hit_rate','backhaul_mb','cache_updates']]))
with open(D/'v27_edge_caching_interval.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['recache_interval','mean_latency_ms','cache_hit_rate','backhaul_mb','cache_updates']); w.writerows(rows)
plt.plot([r[0] for r in rows],[r[1] for r in rows],marker='o'); plt.xscale('log',base=2); plt.xlabel('Recache interval (requests)'); plt.ylabel('Mean inference latency (ms)'); plt.tight_layout(); plt.savefig(F/'v27_edge_caching_latency.png',dpi=180); plt.close()
plt.plot([r[0] for r in rows],[r[3] for r in rows],marker='o'); plt.xscale('log',base=2); plt.xlabel('Recache interval (requests)'); plt.ylabel('Backhaul traffic (MB)'); plt.tight_layout(); plt.savefig(F/'v27_edge_caching_backhaul.png',dpi=180); plt.close()
