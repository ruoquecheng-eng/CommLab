from pathlib import Path
import csv

import matplotlib.pyplot as plt
import numpy as np

from commlab.computation import simulate_offline_resilience_evaluation

ROOT=Path(__file__).resolve().parents[1]; DATA,FIG=ROOT/"results"/"data",ROOT/"results"/"figures"
DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
levels=[0,.5,1,1.5,2.5]; estimators=["dm","ips","snips","dr","clipped_dr"]; rows=[]
for level in levels:
    for estimator in estimators:
        rr=[simulate_offline_resilience_evaluation(n_tasks=10000,estimator=estimator,target_policy="balanced",
            exploration_rate=.08,nonlinearity=level,clip_weight=8,seed=s) for s in range(10)]
        err=np.array([x["signed_error"] for x in rr])
        rows.append({"nonlinearity":level,"estimator":estimator,"mean_absolute_error":np.mean(np.abs(err)),
            "rmse":np.sqrt(np.mean(err**2)),"signed_bias":np.mean(err),
            "mean_standard_error":np.mean([x["standard_error"] for x in rr])})
with (DATA/"v36_model_misspecification.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
for key,ylabel,name,title in [
    ("mean_absolute_error","Mean absolute error (percentage points)","v36_model_misspecification_error.png","Doubly robust correction helps only with usable overlap"),
    ("signed_bias","Signed error (percentage points)","v36_model_misspecification_bias.png","A direct model can be precise but systematically wrong")]:
    plt.figure(figsize=(7.3,4.7))
    for e in estimators:
        r=[x for x in rows if x["estimator"]==e]
        plt.plot(levels,[100*x[key] for x in r],marker="o",label=e)
    plt.xlabel("Unmodeled environment nonlinearity"); plt.ylabel(ylabel); plt.title(title)
    plt.grid(alpha=.25); plt.legend(fontsize=8); plt.tight_layout(); plt.savefig(FIG/name,dpi=170); plt.close()
print("wrote v3.6 model-misspecification sweep")
