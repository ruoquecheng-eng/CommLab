from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt
from commlab.computation import simulate_unified_risk_orchestration

ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'results'/'data'; FIG=ROOT/'results'/'figures'
DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
budgets=[.8,1.0,1.2,1.4,1.6,1.8,2.2]; policies=['risk_budget','uncertainty_gated']
keys=['task_weighted_deadline_miss_rate','mean_latency_ms','duplicate_action_rate','replicate_action_rate','proactive_migration_rate','migration_traffic_mb_per_task','resilience_credits_per_task']
rows=[]
for b in budgets:
    for p in policies:
        rr=[simulate_unified_risk_orchestration(
            n_tasks=2200,policy=p,budget_per_task=b,forecast_noise=.4,mean_snr_db=6,
            radio_correlation=.25,edge_risk_scale=1.0,seed=s,
        ) for s in range(2)]
        rows.append([b,p,*[np.mean([x[k] for x in rr]) for k in keys]])
with (DATA/'v33_budget_saturation.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['budget_per_task','policy',*keys]); w.writerows(rows)

plt.figure(figsize=(7.2,4.7))
for p in policies:
    r=[x for x in rows if x[1]==p]
    plt.plot([x[0] for x in r],[100*x[2] for x in r],marker='o',label=p)
plt.xlabel('Available resilience credits / task'); plt.ylabel('Task-weighted deadline miss (%)')
plt.title('Reliability gain saturates before available budget does')
plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v33_budget_saturation_reliability.png',dpi=170); plt.close()

plt.figure(figsize=(7.2,4.7))
for p in policies:
    r=[x for x in rows if x[1]==p]
    plt.plot([x[0] for x in r],[x[8] for x in r],marker='o',label=f'{p}: spent')
plt.plot(budgets,budgets,linestyle='--',label='available budget')
plt.xlabel('Available resilience credits / task'); plt.ylabel('Credits actually spent / task')
plt.title('Uncertainty gating refuses low-confidence excess spending')
plt.grid(alpha=.25); plt.legend(fontsize=8); plt.tight_layout(); plt.savefig(FIG/'v33_budget_saturation_spend.png',dpi=170); plt.close()
print('wrote v33 budget-saturation sweep')
