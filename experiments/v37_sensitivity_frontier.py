from pathlib import Path
import csv

import matplotlib.pyplot as plt
import numpy as np

from commlab.computation import simulate_propensity_robust_evaluation

ROOT=Path(__file__).resolve().parents[1]; DATA,FIG=ROOT/"results"/"data",ROOT/"results"/"figures"
gammas=[1,1.25,1.5,2,3,5,10]; rows=[]
for gamma in gammas:
    rr=[simulate_propensity_robust_evaluation(n_tasks=6000,propensity_mode="recorded_nominal",
        hidden_confounding=1.5,propensity_drift=1.0,sensitivity_gamma=gamma,seed=s) for s in range(16)]
    rows.append({"sensitivity_gamma":gamma,
        "mean_interval_width":np.mean([x["sensitivity_width"] for x in rr]),
        "oracle_coverage":np.mean([x["sensitivity_contains_oracle"] for x in rr]),
        "true_propensity_estimate_coverage":np.mean([x["sensitivity_contains_true_propensity_estimate"] for x in rr]),
        "mean_point_error":np.mean([x["absolute_error"] for x in rr]),
        "median_required_rowwise_gamma":np.median([x["required_sensitivity_gamma"] for x in rr])})
with (DATA/"v37_sensitivity_frontier.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
fig,ax=plt.subplots(figsize=(7.6,4.8)); ax.plot(gammas,100*np.array([x["mean_interval_width"] for x in rows]),marker="o",label="interval width")
ax.set_xscale("log"); ax.set_xlabel("Sensitivity gamma"); ax.set_ylabel("Mean interval width (percentage points)"); ax.grid(alpha=.25)
ax2=ax.twinx(); ax2.plot(gammas,[x["oracle_coverage"] for x in rows],marker="s",color="tab:red",label="oracle coverage"); ax2.set_ylabel("Empirical oracle coverage"); ax2.set_ylim(-.03,1.03)
ax.set_title("Coverage is bought with rapidly widening ambiguity"); fig.tight_layout(); fig.savefig(FIG/"v37_sensitivity_frontier_width.png",dpi=170); plt.close(fig)
plt.figure(figsize=(7.6,4.8)); plt.plot(gammas,[x["oracle_coverage"] for x in rows],marker="o",label="paired oracle")
plt.plot(gammas,[x["true_propensity_estimate_coverage"] for x in rows],marker="s",label="true-propensity estimate")
plt.xscale("log"); plt.ylim(-.03,1.03); plt.xlabel("Sensitivity gamma"); plt.ylabel("Empirical coverage"); plt.title("Aggregate coverage is not a sharp causal guarantee"); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/"v37_sensitivity_frontier_coverage.png",dpi=170); plt.close()
print("wrote v3.7 sensitivity frontier")
