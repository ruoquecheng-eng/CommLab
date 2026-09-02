from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt
from commlab.computation import simulate_unified_risk_orchestration

ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'results'/'data'; FIG=ROOT/'results'/'figures'
DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
budgets=[.2,.3,.4,.5,.6,.8]; policies=['risk_budget_unweighted','risk_budget']
keys=['deadline_miss_rate','task_weighted_deadline_miss_rate','mean_transmissions_per_task','replica_execution_rate','proactive_migration_rate','resilience_credits_per_task']
rows=[]
for b in budgets:
    for policy in policies:
        rr=[simulate_unified_risk_orchestration(
            n_tasks=2400,policy=policy,budget_per_task=b,forecast_noise=.35,
            mean_snr_db=6.0,radio_correlation=.25,edge_risk_scale=1.0,seed=s,
        ) for s in range(3)]
        rows.append([b,policy,*[np.mean([x[k] for x in rr]) for k in keys]])
with (DATA/'v33_task_weighting.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['budget_per_task','policy',*keys]); w.writerows(rows)
plt.figure(figsize=(7.2,4.7))
for policy in policies:
    r=[x for x in rows if x[1]==policy]
    plt.plot([x[0] for x in r],[100*x[3] for x in r],marker='o',label=policy)
plt.xlabel('Normalized resilience credits / task'); plt.ylabel('Task-weighted deadline miss (%)')
plt.title('Task weighting is regime dependent under a myopic risk proxy')
plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v33_task_weighting_tradeoff.png',dpi=170); plt.close()
print('wrote v33 task-weighting sweep')
