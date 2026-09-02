from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt
from commlab.computation import simulate_unified_risk_orchestration

ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'results'/'data'; FIG=ROOT/'results'/'figures'
DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
noises=[0,.25,.5,.8,1.1,1.5,2.0]; policies=['risk_budget','uncertainty_gated']
keys=['task_weighted_deadline_miss_rate','mean_latency_ms','proactive_migration_rate','migration_traffic_mb_per_task','duplicate_action_rate','replicate_action_rate','resilience_credits_per_task']
rows=[]
for noise in noises:
    for policy in policies:
        rr=[simulate_unified_risk_orchestration(
            n_tasks=2400,policy=policy,budget_per_task=.85,forecast_noise=noise,
            mean_snr_db=8.0,radio_correlation=.25,edge_risk_scale=1.4,seed=s,
        ) for s in range(3)]
        rows.append([noise,policy,*[np.mean([x[k] for x in rr]) for k in keys]])
with (DATA/'v33_forecast_uncertainty.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['forecast_noise','policy',*keys]); w.writerows(rows)

plt.figure(figsize=(7.2,4.7))
for policy in policies:
    r=[x for x in rows if x[1]==policy]
    plt.plot([x[0] for x in r],[100*x[4] for x in r],marker='o',label=policy)
plt.xlabel('Forecast-noise scale'); plt.ylabel('Proactive migrations (% tasks)')
plt.title('Uncertainty gating suppresses speculative migration')
plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v33_uncertainty_migration_churn.png',dpi=170); plt.close()

plt.figure(figsize=(7.2,4.7))
for policy in policies:
    r=[x for x in rows if x[1]==policy]
    plt.plot([x[0] for x in r],[100*x[2] for x in r],marker='o',label=policy)
plt.xlabel('Forecast-noise scale'); plt.ylabel('Task-weighted deadline miss (%)')
plt.title('Calibration reduces churn but is not universally better')
plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v33_uncertainty_reliability.png',dpi=170); plt.close()
print('wrote v33 forecast-uncertainty sweep')
