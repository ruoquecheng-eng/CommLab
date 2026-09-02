from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt
from commlab.computation import simulate_twin_guided_model_prefetch
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'results'/'data'; FIG=ROOT/'results'/'figures'; DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rows=[]
for noise in [.10,.30,.50,.80,1.20,1.80]:
    for policy in ['reactive','predictive','uncertainty_gated']:
        rr=[simulate_twin_guided_model_prefetch(twin_noise_std=noise,policy=policy,seed=s) for s in range(8)]
        rows.append([noise,policy,np.mean([x['mean_inference_latency_ms'] for x in rr]),np.mean([x['cache_hit_rate'] for x in rr]),np.mean([x['total_backhaul_mb'] for x in rr]),np.mean([x['wrong_prefetch_fraction'] for x in rr]),np.mean([x['prefetch_attempts'] for x in rr])])
with (DATA/'v29_twin_guided_prefetch.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['twin_noise_std','policy','latency_ms','cache_hit_rate','backhaul_mb','wrong_prefetch_fraction','prefetch_attempts']); w.writerows(rows)
plt.figure(figsize=(7.2,4.7))
for p in ['reactive','predictive','uncertainty_gated']:
    r=[x for x in rows if x[1]==p]; plt.plot([x[0] for x in r],[x[2] for x in r],marker='o',label=p)
plt.xlabel('Digital-twin uncertainty (std)'); plt.ylabel('Mean inference latency (ms)'); plt.title('Twin prediction helps until model prediction becomes unreliable'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v29_twin_prefetch_latency.png',dpi=170); plt.close()
plt.figure(figsize=(7.2,4.7))
for p in ['predictive','uncertainty_gated']:
    r=[x for x in rows if x[1]==p]; plt.plot([x[0] for x in r],[x[4] for x in r],marker='o',label=p)
plt.xlabel('Digital-twin uncertainty (std)'); plt.ylabel('Total model backhaul (MB)'); plt.title('Uncertainty gating suppresses wrong speculative model loads'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v29_twin_prefetch_backhaul.png',dpi=170); plt.close()
print('wrote v29 twin prefetch')
