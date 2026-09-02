from pathlib import Path
import csv

import matplotlib.pyplot as plt
import numpy as np

from commlab.computation import simulate_adaptive_risk_control

ROOT = Path(__file__).resolve().parents[1]
DATA, FIG = ROOT / "results" / "data", ROOT / "results" / "figures"
DATA.mkdir(parents=True, exist_ok=True); FIG.mkdir(parents=True, exist_ok=True)

budgets = [.35, .55, .75, 1.0, 1.3]
policies = ["point_greedy", "adaptive_global", "adaptive_local"]
keys = ["post_drift_task_weighted_miss_rate", "post_drift_routine_miss_rate",
        "post_drift_important_miss_rate", "post_drift_critical_miss_rate",
        "resilience_credits_per_task", "mean_active_risk_debt"]
rows = []
for budget in budgets:
    for policy in policies:
        rr = [simulate_adaptive_risk_control(n_tasks=7000, policy=policy, drift_strength=1.4,
              budget_per_task=budget, seed=s) for s in (3, 4, 5)]
        rows.append([budget, policy, *[np.mean([x[k] for x in rr]) for k in keys]])
with (DATA / "v34_localized_risk.csv").open("w", newline="") as f:
    w=csv.writer(f); w.writerow(["budget_per_task", "policy", *keys]); w.writerows(rows)

plt.figure(figsize=(7.2, 4.7))
for policy in policies:
    r=[x for x in rows if x[1] == policy]
    plt.plot([x[0] for x in r], [100*x[5] for x in r], marker="o", label=policy)
plt.xlabel("Available credits / task"); plt.ylabel("Post-drift critical miss (%)")
plt.title("A global risk debt can hide the critical class")
plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/"v34_localized_critical_risk.png",dpi=170); plt.close()

plt.figure(figsize=(7.2, 4.7))
for policy in policies:
    r=[x for x in rows if x[1] == policy]
    plt.plot([x[0] for x in r], [100*x[2] for x in r], marker="o", label=policy)
plt.xlabel("Available credits / task"); plt.ylabel("Post-drift weighted miss (%)")
plt.title("Localized control helps only after budget becomes usable")
plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/"v34_localized_budget_crossover.png",dpi=170); plt.close()
print("wrote v3.4 localized-risk sweep")
