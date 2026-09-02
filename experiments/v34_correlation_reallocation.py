from pathlib import Path
import csv

import matplotlib.pyplot as plt
import numpy as np

from commlab.computation import simulate_adaptive_risk_control

ROOT=Path(__file__).resolve().parents[1]
DATA,FIG=ROOT/"results"/"data",ROOT/"results"/"figures"
DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)

correlations=[0,.25,.50,.75,.95]
policies=["adaptive_global","adaptive_local"]
keys=["post_drift_task_weighted_miss_rate","duplicate_action_rate","replicate_action_rate",
      "resilience_credits_per_task","cvar95_latency_ms"]
rows=[]
for rho in correlations:
    for policy in policies:
        rr=[simulate_adaptive_risk_control(n_tasks=6500,policy=policy,drift_strength=1.2,
            budget_per_task=1.0,radio_correlation=rho,seed=s) for s in (10,11)]
        rows.append([rho,policy,*[np.mean([x[k] for x in rr]) for k in keys]])
with (DATA/"v34_correlation_reallocation.csv").open("w",newline="") as f:
    w=csv.writer(f); w.writerow(["radio_correlation","policy",*keys]); w.writerows(rows)

plt.figure(figsize=(7.2,4.7))
for policy in policies:
    r=[x for x in rows if x[1]==policy]
    plt.plot([x[0] for x in r],[100*x[3] for x in r],marker="o",label=policy+" duplication")
    plt.plot([x[0] for x in r],[100*x[4] for x in r],marker="s",ls="--",label=policy+" replica")
plt.xlabel("Radio-path correlation"); plt.ylabel("Action rate (%)")
plt.title("Online risk control still reallocates away from correlated radio")
plt.grid(alpha=.25); plt.legend(fontsize=8); plt.tight_layout(); plt.savefig(FIG/"v34_correlation_action_mix.png",dpi=170); plt.close()

plt.figure(figsize=(7.2,4.7))
for policy in policies:
    r=[x for x in rows if x[1]==policy]
    plt.plot([x[0] for x in r],[100*x[2] for x in r],marker="o",label=policy)
plt.xlabel("Radio-path correlation"); plt.ylabel("Post-drift weighted miss (%)")
plt.title("Feedback cannot create missing path diversity")
plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/"v34_correlation_reliability.png",dpi=170); plt.close()
print("wrote v3.4 correlation-reallocation sweep")
