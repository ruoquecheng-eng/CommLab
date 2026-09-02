from pathlib import Path
import csv

import matplotlib.pyplot as plt
import numpy as np

from commlab.computation import simulate_observable_resilience

ROOT=Path(__file__).resolve().parents[1]; DATA,FIG=ROOT/"results"/"data",ROOT/"results"/"figures"
DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
delays=[1,8,32,96,256,512]; policies=["outcome_only","component_telemetry","hybrid_feedback"]
metrics=["post_drift_weighted_miss_rate","detection_delay_tasks","resilience_credits_per_task",
         "duplicate_action_rate","replica_action_rate"]
rows=[]
for delay in delays:
    for policy in policies:
        rr=[simulate_observable_resilience(n_tasks=7000,policy=policy,drift_mode="mixed",budget_per_task=.9,
            telemetry_probability=.6,audit_rate=.08,feedback_delay=delay,seed=s) for s in (1,2,3)]
        rows.append({"feedback_delay":delay,"policy":policy,**{k:float(np.mean([x[k] for x in rr])) for k in metrics}})
with (DATA/"v35_feedback_delay.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
for key,ylabel,name,title,pct in [
    ("detection_delay_tasks","Detected-drift delay (tasks)","v35_feedback_delay_detection.png","Component telemetry detects drift earlier",False),
    ("post_drift_weighted_miss_rate","Post-drift weighted miss (%)","v35_feedback_delay_reliability.png","Faster detection does not guarantee lower task loss",True)]:
    plt.figure(figsize=(7.2,4.7))
    for p in policies:
        r=[x for x in rows if x["policy"]==p]
        plt.plot(delays,[100*x[key] if pct else x[key] for x in r],marker="o",label=p)
    plt.xscale("log",base=2); plt.xlabel("Feedback delay (tasks)"); plt.ylabel(ylabel); plt.title(title)
    plt.grid(alpha=.25); plt.legend(fontsize=8); plt.tight_layout(); plt.savefig(FIG/name,dpi=170); plt.close()
print("wrote v3.5 feedback-delay sweep")
