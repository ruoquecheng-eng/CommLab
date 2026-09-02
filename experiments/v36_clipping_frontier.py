from pathlib import Path
import csv

import matplotlib.pyplot as plt
import numpy as np

from commlab.computation import simulate_offline_resilience_evaluation

ROOT=Path(__file__).resolve().parents[1]; DATA,FIG=ROOT/"results"/"data",ROOT/"results"/"figures"
DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
caps=[2,4,8,12,20,50,120]; rows=[]
for cap in caps:
    rr=[simulate_offline_resilience_evaluation(n_tasks=10000,estimator="clipped_dr",target_policy="balanced",
        exploration_rate=.01,nonlinearity=1.5,clip_weight=cap,seed=s) for s in range(24)]
    err=np.array([x["signed_error"] for x in rr])
    rows.append({"clip_weight":cap,"mean_absolute_error":np.mean(np.abs(err)),"rmse":np.sqrt(np.mean(err**2)),
        "signed_bias":np.mean(err),"empirical_error_std":np.std(err,ddof=1),
        "mean_reported_standard_error":np.mean([x["standard_error"] for x in rr]),
        "ci95_coverage":np.mean([x["ci95_low"]<=x["oracle_weighted_miss"]<=x["ci95_high"] for x in rr])})
with (DATA/"v36_clipping_frontier.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
plt.figure(figsize=(7.2,4.7)); plt.plot(caps,[100*x["mean_absolute_error"] for x in rows],marker="o",label="MAE")
plt.plot(caps,[100*x["rmse"] for x in rows],marker="s",label="RMSE"); plt.xscale("log")
plt.xlabel("DR importance-weight clip"); plt.ylabel("Error (percentage points)"); plt.title("Clipping trades rare-weight variance for bias")
plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/"v36_clipping_frontier_error.png",dpi=170); plt.close()
plt.figure(figsize=(7.2,4.7)); plt.plot(caps,[100*abs(x["signed_bias"]) for x in rows],marker="o",label="absolute bias")
plt.plot(caps,[100*x["empirical_error_std"] for x in rows],marker="s",label="empirical error std"); plt.xscale("log")
plt.xlabel("DR importance-weight clip"); plt.ylabel("Percentage points"); plt.title("No clipping threshold is universally best")
plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/"v36_clipping_frontier_bias_variance.png",dpi=170); plt.close()
print("wrote v3.6 clipping frontier")
