from pathlib import Path
import csv

import matplotlib.pyplot as plt
import numpy as np

from commlab.computation import simulate_offline_resilience_evaluation

ROOT=Path(__file__).resolve().parents[1]; DATA,FIG=ROOT/"results"/"data",ROOT/"results"/"figures"
DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
drifts=[0,.5,1,1.5,2]; fractions=[.1,.2,.4,.7,1.0]; rows=[]
for drift in drifts:
    for fraction in fractions:
        rr=[simulate_offline_resilience_evaluation(n_tasks=12000,estimator="dr",target_policy="balanced",
            exploration_rate=.08,drift_strength=drift,nonlinearity=0,recency_fraction=fraction,seed=s) for s in range(10)]
        rows.append({"drift_strength":drift,"recency_fraction":fraction,
            "current_mean_absolute_error":np.mean([x["current_absolute_error"] for x in rr]),
            "window_mean_absolute_error":np.mean([x["absolute_error"] for x in rr]),
            "estimated_weighted_miss":np.mean([x["estimated_weighted_miss"] for x in rr]),
            "current_oracle_weighted_miss":np.mean([x["current_oracle_weighted_miss"] for x in rr]),
            "mean_standard_error":np.mean([x["standard_error"] for x in rr])})
with (DATA/"v36_temporal_reuse.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
plt.figure(figsize=(7.4,4.8))
for drift in drifts:
    r=[x for x in rows if x["drift_strength"]==drift]
    plt.plot(fractions,[100*x["current_mean_absolute_error"] for x in r],marker="o",label=f"drift={drift:g}")
plt.xlabel("Fraction of most-recent log reused"); plt.ylabel("Error for current policy value (percentage points)")
plt.title("Old data becomes bias under drift; too little data restores variance"); plt.grid(alpha=.25); plt.legend(fontsize=8); plt.tight_layout(); plt.savefig(FIG/"v36_temporal_reuse_current_error.png",dpi=170); plt.close()
r=[x for x in rows if x["drift_strength"]==2]
plt.figure(figsize=(7.2,4.7)); plt.plot(fractions,[100*x["estimated_weighted_miss"] for x in r],marker="o",label="offline estimate")
plt.plot(fractions,[100*x["current_oracle_weighted_miss"] for x in r],marker="s",label="current oracle")
plt.xlabel("Fraction of most-recent log reused"); plt.ylabel("Weighted miss (%)"); plt.title("Full-history OPE answers the wrong time-average question")
plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/"v36_temporal_reuse_value.png",dpi=170); plt.close()
print("wrote v3.6 temporal-reuse sweep")
