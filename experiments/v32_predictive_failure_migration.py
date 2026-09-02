from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt
from commlab.computation import simulate_predictive_failure_migration
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'results'/'data'; FIG=ROOT/'results'/'figures'; DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rows=[]
for noise in [0.0,.2,.5,.8,1.0,1.2]:
    for p in ['sticky','reactive','predictive_risk']:
        rr=[simulate_predictive_failure_migration(steps=4600,policy=p,forecast_noise=noise,seed=s) for s in range(4)]
        keys=['mean_latency_ms','p95_latency_ms','deadline_miss_rate','failure_event_rate','migration_rate','proactive_migration_rate','migration_traffic_mb_per_step']
        rows.append([noise,p,*[np.mean([x[k] for x in rr]) for k in keys]])
with (DATA/'v32_predictive_failure_migration.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['forecast_noise','policy','mean_latency_ms','p95_latency_ms','deadline_miss_rate','failure_event_rate','migration_rate','proactive_migration_rate','migration_traffic_mb_per_step']); w.writerows(rows)
plt.figure(figsize=(7.2,4.7))
for p in ['sticky','reactive','predictive_risk']:
    r=[x for x in rows if x[1]==p]; plt.plot([x[0] for x in r],[x[2] for x in r],marker='o',label=p)
plt.xlabel('Forecast-noise scale'); plt.ylabel('Mean task latency (ms)'); plt.title('Prediction benefit crosses into migration churn'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v32_predictive_migration_latency.png',dpi=170); plt.close()
plt.figure(figsize=(7.2,4.7))
for p in ['reactive','predictive_risk']:
    r=[x for x in rows if x[1]==p]; plt.plot([x[0] for x in r],[100*x[6] for x in r],marker='o',label=p)
plt.xlabel('Forecast-noise scale'); plt.ylabel('Migrations (% of steps)'); plt.title('Noisy forecasts create proactive migration churn'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v32_predictive_migration_churn.png',dpi=170); plt.close()
print('wrote v32 predictive failure migration')
