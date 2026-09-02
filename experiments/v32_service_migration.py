from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt
from commlab.computation import simulate_checkpoint_aware_migration
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'results'/'data'; FIG=ROOT/'results'/'figures'; DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rows=[]
for mobility in [.02,.05,.10,.18,.28]:
    for p in ['cold_reactive','periodic_checkpoint','predictive_checkpoint']:
        rr=[simulate_checkpoint_aware_migration(steps=5000,policy=p,mobility=mobility,checkpoint_interval=8,seed=s) for s in range(4)]
        rows.append([mobility,p,*[np.mean([x[k] for x in rr]) for k in ['mean_latency_ms','p95_latency_ms','deadline_miss_rate','migration_traffic_mb_per_step','cold_migration_rate','speculative_mispredict_rate']]])
with (DATA/'v32_service_migration.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['mobility','policy','mean_latency_ms','p95_latency_ms','deadline_miss_rate','traffic_mb_per_step','cold_migration_rate','speculative_mispredict_rate']); w.writerows(rows)
plt.figure(figsize=(7.2,4.7))
for p in ['cold_reactive','periodic_checkpoint','predictive_checkpoint']:
    r=[x for x in rows if x[1]==p]; plt.plot([x[0] for x in r],[x[2] for x in r],marker='o',label=p)
plt.xlabel('Mobility probability / step'); plt.ylabel('Mean service latency (ms)'); plt.title('Checkpointing reduces cold migration but prediction errors still cost'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v32_service_migration_latency.png',dpi=170); plt.close()
plt.figure(figsize=(7.2,4.7))
for p in ['cold_reactive','periodic_checkpoint','predictive_checkpoint']:
    r=[x for x in rows if x[1]==p]; plt.plot([x[0] for x in r],[x[5] for x in r],marker='o',label=p)
plt.xlabel('Mobility probability / step'); plt.ylabel('Migration/checkpoint traffic (MB/step)'); plt.title('Predictive checkpoints save traffic only when mobility is predictable'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v32_service_migration_traffic.png',dpi=170); plt.close()
print('wrote v32 service migration')
