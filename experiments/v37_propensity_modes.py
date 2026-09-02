from pathlib import Path
import csv

import matplotlib.pyplot as plt
import numpy as np

from commlab.computation import simulate_propensity_robust_evaluation

ROOT=Path(__file__).resolve().parents[1]; DATA,FIG=ROOT/"results"/"data",ROOT/"results"/"figures"
DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
modes=["recorded_true","recorded_nominal","stale_recorded","estimated_full","estimated_crossfit","misspecified"]
rows=[]
for mode in modes:
    rr=[simulate_propensity_robust_evaluation(n_tasks=6000,propensity_mode=mode,
        hidden_confounding=.8,propensity_drift=1.0,sensitivity_gamma=2,seed=s) for s in range(6)]
    rows.append({"propensity_mode":mode,
        "mean_absolute_error":np.mean([x["absolute_error"] for x in rr]),
        "signed_bias":np.mean([x["signed_error"] for x in rr]),
        "propensity_mae":np.mean([x["propensity_mae"] for x in rr]),
        "propensity_ece":np.mean([x["propensity_ece"] for x in rr]),
        "effective_sample_fraction":np.mean([x["effective_sample_fraction"] for x in rr]),
        "required_sensitivity_gamma":np.median([x["required_sensitivity_gamma"] for x in rr])})
with (DATA/"v37_propensity_modes.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
labels=[x["propensity_mode"].replace("recorded_","").replace("estimated_","") for x in rows]; pos=np.arange(len(rows))
plt.figure(figsize=(8.4,4.8)); plt.bar(pos,100*np.array([x["mean_absolute_error"] for x in rows]))
plt.xticks(pos,labels,rotation=18,ha="right"); plt.ylabel("Mean absolute OPE error (percentage points)")
plt.title("Estimated propensities do not recover an omitted severity cue"); plt.grid(axis="y",alpha=.25); plt.tight_layout(); plt.savefig(FIG/"v37_propensity_modes_error.png",dpi=170); plt.close()
fig,ax=plt.subplots(figsize=(8.4,4.8)); ax.bar(pos,100*np.array([x["propensity_mae"] for x in rows]),label="propensity MAE")
ax.set_xticks(pos,labels,rotation=18,ha="right"); ax.set_ylabel("Propensity MAE (percentage points)"); ax.grid(axis="y",alpha=.25)
ax2=ax.twinx(); ax2.plot(pos,[x["required_sensitivity_gamma"] for x in rows],color="tab:red",marker="o",label="required gamma"); ax2.set_ylabel("Max row-wise odds gap gamma")
ax.set_title("Calibration averages can hide a large row-wise odds gap"); fig.tight_layout(); fig.savefig(FIG/"v37_propensity_modes_calibration.png",dpi=170); plt.close(fig)
print("wrote v3.7 propensity-mode comparison")
