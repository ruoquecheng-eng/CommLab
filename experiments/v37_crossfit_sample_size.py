from pathlib import Path
import csv

import matplotlib.pyplot as plt
import numpy as np

from commlab.computation import simulate_propensity_robust_evaluation

ROOT=Path(__file__).resolve().parents[1]; DATA,FIG=ROOT/"results"/"data",ROOT/"results"/"figures"
sizes=[800,1200,2000,4000,8000]; modes=["estimated_full","estimated_crossfit"]; rows=[]
for n in sizes:
    for mode in modes:
        rr=[simulate_propensity_robust_evaluation(n_tasks=n,propensity_mode=mode,
            hidden_confounding=0,propensity_drift=1.0,seed=s) for s in range(12)]
        rows.append({"n_tasks":n,"propensity_mode":mode,
            "mean_absolute_error":np.mean([x["absolute_error"] for x in rr]),
            "propensity_mae":np.mean([x["propensity_mae"] for x in rr]),
            "max_importance_weight":np.mean([x["max_importance_weight"] for x in rr]),
            "effective_sample_fraction":np.mean([x["effective_sample_fraction"] for x in rr])})
with (DATA/"v37_crossfit_sample_size.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
plt.figure(figsize=(7.4,4.8))
for mode in modes:
    r=[x for x in rows if x["propensity_mode"]==mode]; plt.plot(sizes,100*np.array([x["mean_absolute_error"] for x in r]),marker="o",label=mode)
plt.xscale("log"); plt.xlabel("Logged tasks"); plt.ylabel("Mean absolute OPE error (percentage points)"); plt.title("Cross-fitting is not automatically a finite-sample win"); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/"v37_crossfit_sample_size_error.png",dpi=170); plt.close()
plt.figure(figsize=(7.4,4.8))
for mode in modes:
    r=[x for x in rows if x["propensity_mode"]==mode]; plt.plot(sizes,[x["max_importance_weight"] for x in r],marker="o",label=mode)
plt.xscale("log"); plt.xlabel("Logged tasks"); plt.ylabel("Mean maximum importance weight"); plt.title("Fold-wise nuisance fits can amplify small-sample weights"); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/"v37_crossfit_sample_size_weights.png",dpi=170); plt.close()
print("wrote v3.7 cross-fitting sample-size sweep")
