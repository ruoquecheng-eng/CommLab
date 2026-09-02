from pathlib import Path
import csv

import matplotlib.pyplot as plt
import numpy as np

from commlab.computation import simulate_adaptive_risk_control

ROOT = Path(__file__).resolve().parents[1]
DATA, FIG = ROOT / "results" / "data", ROOT / "results" / "figures"
DATA.mkdir(parents=True, exist_ok=True); FIG.mkdir(parents=True, exist_ok=True)

drifts = [0.0, 0.4, 0.8, 1.2, 1.6]
policies = ["point_greedy", "static_guard", "adaptive_global", "adaptive_local", "oracle"]
keys = ["post_drift_task_weighted_miss_rate", "post_drift_critical_miss_rate",
        "resilience_credits_per_task", "calibration_gap", "cvar95_latency_ms"]
rows = []
for drift in drifts:
    for policy in policies:
        rr = [simulate_adaptive_risk_control(n_tasks=6000, policy=policy, drift_strength=drift,
              budget_per_task=1.0, seed=s) for s in (1, 2)]
        rows.append([drift, policy, *[np.mean([x[k] for x in rr]) for k in keys]])

with (DATA / "v34_drift_adaptation.csv").open("w", newline="") as f:
    w = csv.writer(f); w.writerow(["drift_strength", "policy", *keys]); w.writerows(rows)

for metric, ylabel, name in [
    (2, "Post-drift weighted miss (%)", "v34_drift_adaptation_reliability.png"),
    (4, "Resilience credits / task", "v34_drift_adaptation_spend.png"),
]:
    plt.figure(figsize=(7.2, 4.7))
    for policy in policies:
        r = [x for x in rows if x[1] == policy]
        y = [100*x[metric] if metric == 2 else x[metric] for x in r]
        plt.plot([x[0] for x in r], y, marker="o", label=policy)
    plt.xlabel("Distribution-drift strength"); plt.ylabel(ylabel)
    plt.title("Adaptive protection has a drift-dependent value")
    plt.grid(alpha=.25); plt.legend(fontsize=8); plt.tight_layout(); plt.savefig(FIG/name, dpi=170); plt.close()
print("wrote v3.4 drift-adaptation sweep")
