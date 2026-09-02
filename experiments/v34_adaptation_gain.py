from pathlib import Path
import csv

import matplotlib.pyplot as plt
import numpy as np

from commlab.computation import simulate_adaptive_risk_control

ROOT=Path(__file__).resolve().parents[1]
DATA,FIG=ROOT/"results"/"data",ROOT/"results"/"figures"
DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)

rates=[0.0,.005,.015,.035,.08,.16]
keys=["post_drift_task_weighted_miss_rate","post_drift_critical_miss_rate",
      "max_rolling_weighted_miss_rate","resilience_credits_per_task","action_switch_rate","mean_active_risk_debt"]
rows=[]
for rate in rates:
    rr=[simulate_adaptive_risk_control(n_tasks=7000,policy="adaptive_local",drift_strength=1.4,
        budget_per_task=1.0,adaptation_rate=rate,seed=s) for s in range(4)]
    rows.append([rate,*[np.mean([x[k] for x in rr]) for k in keys]])
with (DATA/"v34_adaptation_gain.csv").open("w",newline="") as f:
    w=csv.writer(f); w.writerow(["adaptation_rate",*keys]); w.writerows(rows)

plt.figure(figsize=(7.2,4.7))
plt.plot([x[0] for x in rows],[100*x[1] for x in rows],marker="o",label="post-drift weighted miss")
plt.plot([x[0] for x in rows],[100*x[3] for x in rows],marker="s",label="worst rolling weighted miss")
plt.xlabel("Risk-debt adaptation rate"); plt.ylabel("Miss (%)")
plt.title("Too little adaptation is stale; too much chases noise")
plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/"v34_adaptation_gain_risk.png",dpi=170); plt.close()

plt.figure(figsize=(7.2,4.7))
plt.plot([x[0] for x in rows],[x[4] for x in rows],marker="o",label="credits/task")
plt.plot([x[0] for x in rows],[x[5] for x in rows],marker="s",label="action switch rate")
plt.xlabel("Risk-debt adaptation rate"); plt.ylabel("Activity")
plt.title("Aggressive feedback raises spend and switching")
plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/"v34_adaptation_gain_activity.png",dpi=170); plt.close()
print("wrote v3.4 adaptation-gain sweep")
