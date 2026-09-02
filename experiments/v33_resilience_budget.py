from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt
from commlab.computation import simulate_unified_risk_orchestration

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'results' / 'data'
FIG = ROOT / 'results' / 'figures'
DATA.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

budgets = [0.0, .2, .4, .6, .8, 1.0, 1.2]
policies = ['reactive', 'radio_first', 'edge_first', 'risk_budget', 'uncertainty_gated']
keys = [
    'deadline_miss_rate', 'task_weighted_deadline_miss_rate', 'mean_latency_ms', 'p95_latency_ms',
    'mean_transmissions_per_task', 'replica_execution_rate', 'proactive_migration_rate',
    'migration_traffic_mb_per_task', 'resilience_credits_per_task',
]
rows = []
for budget in budgets:
    for policy in policies:
        rr = [simulate_unified_risk_orchestration(
            n_tasks=2200, policy=policy, budget_per_task=budget, forecast_noise=.4,
            mean_snr_db=6.0, radio_correlation=.25, edge_risk_scale=1.0, seed=s,
        ) for s in range(2)]
        rows.append([budget, policy, *[np.mean([x[k] for x in rr]) for k in keys]])

with (DATA / 'v33_resilience_budget.csv').open('w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['budget_per_task', 'policy', *keys])
    w.writerows(rows)

plt.figure(figsize=(7.2, 4.7))
for policy in policies:
    r = [x for x in rows if x[1] == policy]
    plt.plot([x[0] for x in r], [100*x[3] for x in r], marker='o', label=policy)
plt.xlabel('Normalized resilience credits / task')
plt.ylabel('Task-weighted deadline miss (%)')
plt.title('Reliability budget has diminishing returns')
plt.grid(alpha=.25); plt.legend(fontsize=8); plt.tight_layout()
plt.savefig(FIG / 'v33_resilience_budget_reliability.png', dpi=170); plt.close()

plt.figure(figsize=(7.2, 4.7))
for policy in ['radio_first', 'edge_first', 'risk_budget', 'uncertainty_gated']:
    r = [x for x in rows if x[1] == policy]
    plt.plot([x[0] for x in r], [x[6] + x[7] + x[8] for x in r], marker='o', label=policy)
plt.xlabel('Normalized resilience credits / task')
plt.ylabel('Action-rate sum (duplication + replica + proactive migration)')
plt.title('Extra budget increasingly buys redundant actions')
plt.grid(alpha=.25); plt.legend(fontsize=8); plt.tight_layout()
plt.savefig(FIG / 'v33_resilience_budget_actions.png', dpi=170); plt.close()
print('wrote v33 resilience-budget sweep')
