from pathlib import Path
import csv

import matplotlib.pyplot as plt
import numpy as np

from commlab.computation import simulate_observable_resilience

ROOT=Path(__file__).resolve().parents[1]; DATA,FIG=ROOT/"results"/"data",ROOT/"results"/"figures"
DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
telemetry=[0,.2,.5,.8,1.0]; policies=["component_telemetry","hybrid_feedback"]
metrics=["post_drift_weighted_miss_rate","component_observation_rate","audit_fraction",
         "duplicate_action_rate","replica_action_rate","resilience_credits_per_task"]
rows=[]
for availability in telemetry:
    for policy in policies:
        rr=[simulate_observable_resilience(n_tasks=7000,policy=policy,drift_mode="mixed",
            budget_per_task=.9,telemetry_probability=availability,audit_rate=.08,seed=s) for s in (1,2,3)]
        rows.append({"telemetry_probability":availability,"policy":policy,
                     **{k:float(np.mean([x[k] for x in rr])) for k in metrics}})
with (DATA/"v35_telemetry_dropout.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
for key,ylabel,name,title,pct in [
    ("post_drift_weighted_miss_rate","Post-drift weighted miss (%)","v35_telemetry_dropout_reliability.png","Audits help primarily when telemetry is missing",True),
    ("audit_fraction","Audit fraction (%)","v35_telemetry_dropout_audits.png","Hybrid audits switch off as telemetry recovers",True)]:
    plt.figure(figsize=(7.2,4.7))
    for policy in policies:
        r=[x for x in rows if x["policy"]==policy]
        plt.plot(telemetry,[100*x[key] if pct else x[key] for x in r],marker="o",label=policy)
    plt.xlabel("Component-telemetry availability"); plt.ylabel(ylabel); plt.title(title)
    plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/name,dpi=170); plt.close()
print("wrote v3.5 telemetry-dropout sweep")
