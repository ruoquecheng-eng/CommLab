from pathlib import Path
import csv

import matplotlib.pyplot as plt
import numpy as np

from commlab.computation import simulate_offline_resilience_evaluation

ROOT=Path(__file__).resolve().parents[1]; DATA,FIG=ROOT/"results"/"data",ROOT/"results"/"figures"
DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rates=[.005,.01,.02,.05,.10,.20]; estimators=["dm","ips","snips","dr","clipped_dr"]
rows=[]
for rate in rates:
    for estimator in estimators:
        rr=[simulate_offline_resilience_evaluation(n_tasks=10000,estimator=estimator,target_policy="balanced",
            exploration_rate=rate,nonlinearity=1.5,clip_weight=8,seed=s) for s in range(8)]
        errors=np.array([x["signed_error"] for x in rr])
        rows.append({"exploration_rate":rate,"estimator":estimator,"mean_absolute_error":np.mean(np.abs(errors)),
            "rmse":np.sqrt(np.mean(errors**2)),"signed_bias":np.mean(errors),
            "effective_sample_fraction":np.mean([x["effective_sample_fraction"] for x in rr]),
            "max_importance_weight":np.mean([x["max_importance_weight"] for x in rr]),
            "ci95_coverage":np.mean([x["ci95_low"]<=x["oracle_weighted_miss"]<=x["ci95_high"] for x in rr])})
with (DATA/"v36_exploration_overlap.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
plt.figure(figsize=(7.4,4.8))
for e in estimators:
    r=[x for x in rows if x["estimator"]==e]
    plt.plot(rates,[100*x["mean_absolute_error"] for x in r],marker="o",label=e)
plt.xscale("log"); plt.xlabel("Routine/important exploration floor"); plt.ylabel("Mean absolute OPE error (percentage points)")
plt.title("Weak overlap makes unbiased corrections noisy"); plt.grid(alpha=.25); plt.legend(fontsize=8); plt.tight_layout(); plt.savefig(FIG/"v36_exploration_overlap_error.png",dpi=170); plt.close()
r=[x for x in rows if x["estimator"]=="dr"]
fig,ax=plt.subplots(figsize=(7.4,4.8)); ax.plot(rates,[100*x["effective_sample_fraction"] for x in r],marker="o",label="effective sample (%)")
ax.set_xscale("log"); ax.set_xlabel("Exploration floor"); ax.set_ylabel("Effective sample (%)"); ax.grid(alpha=.25)
ax2=ax.twinx(); ax2.plot(rates,[x["max_importance_weight"] for x in r],marker="s",color="tab:red",label="max weight"); ax2.set_ylabel("Maximum importance weight")
ax.set_title("Nominal log size is not effective support"); fig.tight_layout(); fig.savefig(FIG/"v36_exploration_overlap_support.png",dpi=170); plt.close(fig)
print("wrote v3.6 exploration-overlap sweep")
