from pathlib import Path
import csv

import matplotlib.pyplot as plt
import numpy as np

from commlab.computation import simulate_observable_resilience

ROOT=Path(__file__).resolve().parents[1]; DATA,FIG=ROOT/"results"/"data",ROOT/"results"/"figures"
DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
correlations=[0,.25,.5,.75,.95]; policies=["outcome_only","component_telemetry"]
metrics=["post_drift_weighted_miss_rate","masked_fraction_of_base_failures","duplicate_action_rate",
         "replica_action_rate","resilience_credits_per_task","mean_radio_debt"]
rows=[]
for rho in correlations:
    for policy in policies:
        rr=[simulate_observable_resilience(n_tasks=7000,policy=policy,drift_mode="mixed",budget_per_task=.9,
            telemetry_probability=.8,audit_rate=0,radio_correlation=rho,seed=s) for s in (1,2,3)]
        rows.append({"radio_correlation":rho,"policy":policy,**{k:float(np.mean([x[k] for x in rr])) for k in metrics}})
with (DATA/"v35_correlation_observability.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
for key,ylabel,name,title in [
    ("post_drift_weighted_miss_rate","Post-drift weighted miss (%)","v35_correlation_observability_reliability.png","Observability cannot create missing path diversity"),
    ("masked_fraction_of_base_failures","Masked base failures (%)","v35_correlation_observability_masking.png","Correlation reduces what duplication can hide or rescue")]:
    plt.figure(figsize=(7.2,4.7))
    for p in policies:
        r=[x for x in rows if x["policy"]==p]
        plt.plot(correlations,[100*x[key] for x in r],marker="o",label=p)
    plt.xlabel("Radio-path failure correlation"); plt.ylabel(ylabel); plt.title(title)
    plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/name,dpi=170); plt.close()
print("wrote v3.5 correlation-observability sweep")
