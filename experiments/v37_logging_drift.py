from pathlib import Path
import csv

import matplotlib.pyplot as plt
import numpy as np

from commlab.computation import simulate_propensity_robust_evaluation

ROOT=Path(__file__).resolve().parents[1]; DATA,FIG=ROOT/"results"/"data",ROOT/"results"/"figures"
drifts=[0,.5,1.0,1.5,2.0]; modes=["recorded_nominal","stale_recorded","estimated_full","estimated_crossfit","misspecified"]; rows=[]
for drift in drifts:
    for mode in modes:
        rr=[simulate_propensity_robust_evaluation(n_tasks=6000,propensity_mode=mode,
            hidden_confounding=0,propensity_drift=drift,seed=s) for s in range(6)]
        rows.append({"propensity_drift":drift,"propensity_mode":mode,
            "mean_absolute_error":np.mean([x["absolute_error"] for x in rr]),
            "propensity_mae":np.mean([x["propensity_mae"] for x in rr]),
            "propensity_brier":np.mean([x["propensity_brier"] for x in rr]),
            "max_importance_weight":np.mean([x["max_importance_weight"] for x in rr])})
with (DATA/"v37_logging_drift.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
plt.figure(figsize=(7.6,4.8))
for mode in modes:
    r=[x for x in rows if x["propensity_mode"]==mode]; plt.plot(drifts,100*np.array([x["mean_absolute_error"] for x in r]),marker="o",label=mode)
plt.xlabel("Logging-policy drift strength"); plt.ylabel("Mean absolute OPE error (percentage points)"); plt.title("Stale propensity metadata accumulates observable drift bias"); plt.grid(alpha=.25); plt.legend(fontsize=8); plt.tight_layout(); plt.savefig(FIG/"v37_logging_drift_error.png",dpi=170); plt.close()
plt.figure(figsize=(7.6,4.8))
for mode in modes:
    r=[x for x in rows if x["propensity_mode"]==mode]; plt.plot(drifts,100*np.array([x["propensity_mae"] for x in r]),marker="o",label=mode)
plt.xlabel("Logging-policy drift strength"); plt.ylabel("Propensity MAE (percentage points)"); plt.title("Updating the model helps only with observed drift"); plt.grid(alpha=.25); plt.legend(fontsize=8); plt.tight_layout(); plt.savefig(FIG/"v37_logging_drift_calibration.png",dpi=170); plt.close()
print("wrote v3.7 logging-drift sweep")
