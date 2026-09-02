from pathlib import Path
import csv

import matplotlib.pyplot as plt
import numpy as np

from commlab.computation import simulate_observable_resilience

ROOT=Path(__file__).resolve().parents[1]; DATA,FIG=ROOT/"results"/"data",ROOT/"results"/"figures"
DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
modes=["none","radio","edge","mixed"]
policies=["outcome_only","component_telemetry","hybrid_feedback"]
metrics=["post_drift_weighted_miss_rate","duplicate_action_rate","replica_action_rate",
         "mean_radio_debt","mean_edge_debt","resilience_credits_per_task"]
rows=[]
for mode in modes:
    for policy in policies:
        rr=[simulate_observable_resilience(n_tasks=7000,policy=policy,drift_mode=mode,
            budget_per_task=.9,telemetry_probability=.8,audit_rate=.05,seed=s) for s in (1,2,3)]
        rows.append({"drift_mode":mode,"policy":policy,**{k:float(np.mean([x[k] for x in rr])) for k in metrics}})
with (DATA/"v35_regime_attribution.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
x=np.arange(len(modes)); width=.25
plt.figure(figsize=(7.6,4.8))
for i,p in enumerate(policies):
    r=[next(x for x in rows if x["drift_mode"]==m and x["policy"]==p) for m in modes]
    plt.bar(x+(i-1)*width,[100*z["post_drift_weighted_miss_rate"] for z in r],width,label=p)
plt.xticks(x,modes); plt.ylabel("Post-drift weighted miss (%)"); plt.title("Correct attribution is not sufficient for lower task loss")
plt.grid(axis="y",alpha=.25); plt.legend(fontsize=8); plt.tight_layout(); plt.savefig(FIG/"v35_regime_attribution_reliability.png",dpi=170); plt.close()
plt.figure(figsize=(7.6,4.8))
for p,ls in [("outcome_only","--"),("component_telemetry","-"),("hybrid_feedback",":")]:
    r=[next(x for x in rows if x["drift_mode"]==m and x["policy"]==p) for m in modes]
    plt.plot(modes,[100*z["duplicate_action_rate"] for z in r],marker="o",ls=ls,label=f"{p}: duplication")
    plt.plot(modes,[100*z["replica_action_rate"] for z in r],marker="s",ls=ls,label=f"{p}: replica")
plt.ylabel("Action rate (%)"); plt.title("Component feedback reallocates protection by failure source")
plt.grid(alpha=.25); plt.legend(fontsize=7,ncol=2); plt.tight_layout(); plt.savefig(FIG/"v35_regime_attribution_actions.png",dpi=170); plt.close()
print("wrote v3.5 regime-attribution sweep")
