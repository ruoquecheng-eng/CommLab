from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt
from commlab.computation import simulate_unified_risk_orchestration

ROOT = Path(__file__).resolve().parents[1]; DATA=ROOT/'results'/'data'; FIG=ROOT/'results'/'figures'
DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
regimes = [
    ('radio_limited', -4.0, .45),
    ('mixed', 5.0, 1.0),
    ('edge_limited', 14.0, 2.2),
]
policies = ['radio_first', 'edge_first', 'risk_budget', 'uncertainty_gated']
keys = ['task_weighted_deadline_miss_rate','mean_latency_ms','duplicate_action_rate','replicate_action_rate','migrate_action_rate','resilience_credits_per_task']
rows=[]
for name,snr,ers in regimes:
    for policy in policies:
        rr=[simulate_unified_risk_orchestration(
            n_tasks=2400,policy=policy,budget_per_task=.72,forecast_noise=.35,
            mean_snr_db=snr,radio_correlation=.25,edge_risk_scale=ers,seed=s,
        ) for s in range(2)]
        rows.append([name,snr,ers,policy,*[np.mean([x[k] for x in rr]) for k in keys]])
with (DATA/'v33_risk_regimes.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['regime','mean_snr_db','edge_risk_scale','policy',*keys]); w.writerows(rows)

rb=[r for r in rows if r[3]=='risk_budget']
x=np.arange(len(regimes)); width=.24
plt.figure(figsize=(7.4,4.8))
plt.bar(x-width,[r[6] for r in rb],width,label='duplicate')
plt.bar(x,[r[7] for r in rb],width,label='replicate')
plt.bar(x+width,[r[8] for r in rb],width,label='migrate')
plt.xticks(x,[r[0].replace('_',' ') for r in regimes]); plt.ylabel('Action rate')
plt.title('Risk budget shifts between radio and edge resilience')
plt.grid(axis='y',alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v33_risk_regimes_action_mix.png',dpi=170); plt.close()

plt.figure(figsize=(7.2,4.7))
for policy in policies:
    r=[x for x in rows if x[3]==policy]
    plt.plot(range(len(r)),[100*x[4] for x in r],marker='o',label=policy)
plt.xticks(range(len(regimes)),[r[0].replace('_',' ') for r in regimes]); plt.ylabel('Task-weighted deadline miss (%)')
plt.title('No fixed resilience priority is best in every failure regime')
plt.grid(alpha=.25); plt.legend(fontsize=8); plt.tight_layout(); plt.savefig(FIG/'v33_risk_regimes_reliability.png',dpi=170); plt.close()
print('wrote v33 risk-regime sweep')
