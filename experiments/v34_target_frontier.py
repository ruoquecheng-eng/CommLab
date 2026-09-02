from pathlib import Path
import csv

import matplotlib.pyplot as plt
import numpy as np

from commlab.computation import simulate_adaptive_risk_control

ROOT=Path(__file__).resolve().parents[1]
DATA,FIG=ROOT/"results"/"data",ROOT/"results"/"figures"
DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)

targets=[.05,.075,.10,.13,.16]
policies=["static_guard","adaptive_local"]
keys=["post_drift_task_weighted_miss_rate","post_drift_critical_miss_rate","critical_target_excess",
      "resilience_credits_per_task","mean_transmissions_per_task","replica_execution_rate","cvar95_latency_ms"]
rows=[]
for target in targets:
    for policy in policies:
        rr=[simulate_adaptive_risk_control(n_tasks=6500,policy=policy,target_miss_rate=target,
            drift_strength=1.2,budget_per_task=1.0,seed=s) for s in (8,9)]
        rows.append([target,policy,*[np.mean([x[k] for x in rr]) for k in keys]])
with (DATA/"v34_target_frontier.csv").open("w",newline="") as f:
    w=csv.writer(f); w.writerow(["target_miss_rate","policy",*keys]); w.writerows(rows)

plt.figure(figsize=(7.2,4.7))
for policy in policies:
    r=[x for x in rows if x[1]==policy]
    plt.plot([x[5] for x in r],[100*x[2] for x in r],marker="o",label=policy)
plt.xlabel("Credits spent / task"); plt.ylabel("Post-drift weighted miss (%)")
plt.title("Requested risk and achievable risk are not the same")
plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/"v34_target_resource_frontier.png",dpi=170); plt.close()

plt.figure(figsize=(7.2,4.7))
for policy in policies:
    r=[x for x in rows if x[1]==policy]
    plt.plot([x[0] for x in r],[100*x[4] for x in r],marker="o",label=policy)
plt.axhline(0,color="black",lw=1); plt.xlabel("Requested global miss target"); plt.ylabel("Critical target excess (percentage points)")
plt.title("A hard resource cap creates infeasible reliability targets")
plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/"v34_target_infeasibility.png",dpi=170); plt.close()
print("wrote v3.4 target frontier")
