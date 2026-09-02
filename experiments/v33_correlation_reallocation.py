from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt
from commlab.computation import simulate_unified_risk_orchestration

ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'results'/'data'; FIG=ROOT/'results'/'figures'
DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rhos=[0,.2,.4,.6,.8,.95]
keys=['task_weighted_deadline_miss_rate','mean_latency_ms','duplicate_action_rate','replicate_action_rate','migrate_action_rate','mean_transmissions_per_task','resilience_credits_per_task']
rows=[]
for rho in rhos:
    rr=[simulate_unified_risk_orchestration(
        n_tasks=2400,policy='risk_budget',budget_per_task=.72,forecast_noise=.35,
        mean_snr_db=5.0,radio_correlation=rho,edge_risk_scale=1.1,seed=s,
    ) for s in range(3)]
    rows.append([rho,*[np.mean([x[k] for x in rr]) for k in keys]])
with (DATA/'v33_correlation_reallocation.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['radio_correlation',*keys]); w.writerows(rows)

plt.figure(figsize=(7.2,4.7))
plt.plot([r[0] for r in rows],[r[3] for r in rows],marker='o',label='duplicate')
plt.plot([r[0] for r in rows],[r[4] for r in rows],marker='o',label='replicate')
plt.plot([r[0] for r in rows],[r[5] for r in rows],marker='o',label='migrate')
plt.xlabel('Radio-path correlation'); plt.ylabel('Action rate')
plt.title('Correlated radio paths redirect resilience budget toward edge replicas')
plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v33_correlation_budget_shift.png',dpi=170); plt.close()

plt.figure(figsize=(7.2,4.7))
plt.plot([r[0] for r in rows],[100*r[1] for r in rows],marker='o')
plt.xlabel('Radio-path correlation'); plt.ylabel('Task-weighted deadline miss (%)')
plt.title('Reallocation cannot fully recover lost radio diversity')
plt.grid(alpha=.25); plt.tight_layout(); plt.savefig(FIG/'v33_correlation_reliability.png',dpi=170); plt.close()
print('wrote v33 correlation reallocation sweep')
