from pathlib import Path
import csv

import matplotlib.pyplot as plt
import numpy as np

from commlab.computation import simulate_adaptive_risk_control

ROOT=Path(__file__).resolve().parents[1]
DATA,FIG=ROOT/"results"/"data",ROOT/"results"/"figures"
DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)

delays=[1,8,32,96,256,512]
keys=["early_post_drift_weighted_miss_rate","post_drift_task_weighted_miss_rate",
      "post_drift_critical_miss_rate","resilience_credits_per_task","action_switch_rate"]
rows=[]
for delay in delays:
    rr=[simulate_adaptive_risk_control(n_tasks=7000,policy="adaptive_local",drift_strength=1.4,
        budget_per_task=1.0,feedback_delay=delay,seed=s) for s in range(4)]
    rows.append([delay,*[np.mean([x[k] for x in rr]) for k in keys]])
with (DATA/"v34_feedback_delay.csv").open("w",newline="") as f:
    w=csv.writer(f); w.writerow(["feedback_delay",*keys]); w.writerows(rows)

plt.figure(figsize=(7.2,4.7))
plt.semilogx([x[0] for x in rows],[100*x[1] for x in rows],marker="o",label="early post-drift")
plt.semilogx([x[0] for x in rows],[100*x[2] for x in rows],marker="s",label="full post-drift")
plt.xlabel("Outcome-feedback delay (tasks, log scale)"); plt.ylabel("Weighted miss (%)")
plt.title("Fast feedback can chase noise; long delay slows recovery")
plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/"v34_feedback_delay_reliability.png",dpi=170); plt.close()

plt.figure(figsize=(7.2,4.7))
plt.semilogx([x[0] for x in rows],[x[5] for x in rows],marker="o",label="action switch rate")
plt.semilogx([x[0] for x in rows],[x[4] for x in rows],marker="s",label="credits/task")
plt.xlabel("Outcome-feedback delay (tasks, log scale)"); plt.ylabel("Rate / normalized spend")
plt.title("Feedback delay changes control activity")
plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/"v34_feedback_delay_activity.png",dpi=170); plt.close()
print("wrote v3.4 feedback-delay sweep")
