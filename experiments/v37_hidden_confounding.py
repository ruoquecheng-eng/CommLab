from pathlib import Path
import csv

import matplotlib.pyplot as plt
import numpy as np

from commlab.computation import simulate_propensity_robust_evaluation

ROOT=Path(__file__).resolve().parents[1]; DATA,FIG=ROOT/"results"/"data",ROOT/"results"/"figures"
levels=[0,.5,1.0,1.5,2.0]; modes=["recorded_true","recorded_nominal","estimated_crossfit","misspecified"]; rows=[]
for level in levels:
    for mode in modes:
        rr=[simulate_propensity_robust_evaluation(n_tasks=6000,propensity_mode=mode,
            hidden_confounding=level,propensity_drift=1.0,sensitivity_gamma=2,seed=s) for s in range(6)]
        rows.append({"hidden_confounding":level,"propensity_mode":mode,
            "mean_absolute_error":np.mean([x["absolute_error"] for x in rr]),
            "propensity_mae":np.mean([x["propensity_mae"] for x in rr]),
            "propensity_induced_gap":np.mean([x["propensity_induced_gap"] for x in rr]),
            "required_sensitivity_gamma":np.median([x["required_sensitivity_gamma"] for x in rr])})
with (DATA/"v37_hidden_confounding.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
plt.figure(figsize=(7.6,4.8))
for mode in modes:
    r=[x for x in rows if x["propensity_mode"]==mode]; plt.plot(levels,100*np.array([x["mean_absolute_error"] for x in r]),marker="o",label=mode)
plt.xlabel("Hidden-confounding strength"); plt.ylabel("Mean absolute OPE error (percentage points)"); plt.title("Cross-fitting cannot reconstruct an unobserved common cause"); plt.grid(alpha=.25); plt.legend(fontsize=8); plt.tight_layout(); plt.savefig(FIG/"v37_hidden_confounding_error.png",dpi=170); plt.close()
plt.figure(figsize=(7.6,4.8))
for mode in modes[1:]:
    r=[x for x in rows if x["propensity_mode"]==mode]; plt.semilogy(levels,[x["required_sensitivity_gamma"] for x in r],marker="o",label=mode)
plt.xlabel("Hidden-confounding strength"); plt.ylabel("Median max row-wise odds gap gamma"); plt.title("Required local odds protection grows rapidly"); plt.grid(alpha=.25); plt.legend(fontsize=8); plt.tight_layout(); plt.savefig(FIG/"v37_hidden_confounding_gamma.png",dpi=170); plt.close()
print("wrote v3.7 hidden-confounding sweep")
