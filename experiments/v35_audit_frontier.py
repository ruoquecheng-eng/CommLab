from pathlib import Path
import csv

import matplotlib.pyplot as plt
import numpy as np

from commlab.computation import simulate_observable_resilience

ROOT=Path(__file__).resolve().parents[1]; DATA,FIG=ROOT/"results"/"data",ROOT/"results"/"figures"
DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rates=[0,.02,.05,.1,.2,.35]
metrics=["post_drift_weighted_miss_rate","routine_miss_rate","critical_miss_rate","audit_fraction",
         "critical_audit_fraction","resilience_credits_per_task","masked_fraction_of_base_failures"]
rows=[]
for rate in rates:
    rr=[simulate_observable_resilience(n_tasks=7000,policy="audit_feedback",drift_mode="mixed",
        budget_per_task=.9,telemetry_probability=0,audit_rate=rate,seed=s) for s in (1,2,3)]
    rows.append({"requested_audit_rate":rate,**{k:float(np.mean([x[k] for x in rr])) for k in metrics}})
with (DATA/"v35_audit_frontier.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
plt.figure(figsize=(7.2,4.7))
plt.plot([100*x["routine_miss_rate"] for x in rows],[100*x["critical_miss_rate"] for x in rows],marker="o")
for x in rows: plt.annotate(f'{x["requested_audit_rate"]:.0%}',(100*x["routine_miss_rate"],100*x["critical_miss_rate"]),xytext=(4,4),textcoords="offset points",fontsize=8)
plt.xlabel("Routine-task miss (%)"); plt.ylabel("Critical-task miss (%)"); plt.title("Safe audits expose routine tasks to learn and preserve critical budget")
plt.grid(alpha=.25); plt.tight_layout(); plt.savefig(FIG/"v35_audit_frontier_class_tradeoff.png",dpi=170); plt.close()
plt.figure(figsize=(7.2,4.7))
plt.plot([100*x["audit_fraction"] for x in rows],[x["resilience_credits_per_task"] for x in rows],marker="o")
plt.xlabel("Realized audit fraction (%)"); plt.ylabel("Resilience credits / task"); plt.title("Auditing is an intervention with a resource consequence")
plt.grid(alpha=.25); plt.tight_layout(); plt.savefig(FIG/"v35_audit_frontier_resource.png",dpi=170); plt.close()
print("wrote v3.5 safe-audit frontier")
