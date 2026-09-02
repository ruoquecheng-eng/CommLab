from pathlib import Path
import csv

import matplotlib.pyplot as plt
import numpy as np

from commlab.computation import simulate_offline_resilience_evaluation

ROOT=Path(__file__).resolve().parents[1]; DATA,FIG=ROOT/"results"/"data",ROOT/"results"/"figures"
DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
loggers=["deterministic","conservative","safe_explore"]; targets=["balanced","unsafe_critical_probe"]
estimators=["dm","ips","dr"]; rows=[]
for logger in loggers:
    for target in targets:
        for estimator in estimators:
            rr=[simulate_offline_resilience_evaluation(n_tasks=10000,logging_policy=logger,target_policy=target,
                estimator=estimator,exploration_rate=.08,nonlinearity=1.2,seed=s) for s in range(10)]
            err=np.array([x["signed_error"] for x in rr])
            rows.append({"logging_policy":logger,"target_policy":target,"estimator":estimator,
                "support_violation_mass":np.mean([x["support_violation_mass"] for x in rr]),
                "identifiable_fraction":np.mean([x["identifiable"] for x in rr]),
                "mean_absolute_error":np.mean(np.abs(err)),"signed_bias":np.mean(err),
                "critical_target_unprotected_probability":np.mean([x["critical_target_unprotected_probability"] for x in rr])})
with (DATA/"v36_support_boundary.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
labels=[f"{l}\n{t.replace('_critical_probe',' crit-probe')}" for l in loggers for t in targets]
x=np.arange(len(labels)); width=.25
plt.figure(figsize=(9.0,4.9))
for i,e in enumerate(estimators):
    r=[next(z for z in rows if z["logging_policy"]==l and z["target_policy"]==t and z["estimator"]==e) for l in loggers for t in targets]
    plt.bar(x+(i-1)*width,[100*z["mean_absolute_error"] for z in r],width,label=e)
plt.xticks(x,labels,fontsize=8); plt.ylabel("Mean absolute error (percentage points)"); plt.title("A numerical estimate is not proof of identification")
plt.grid(axis="y",alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/"v36_support_boundary_error.png",dpi=170); plt.close()
r=[x for x in rows if x["estimator"]=="dr"]
plt.figure(figsize=(8.5,4.8)); plt.bar(labels,[100*x["support_violation_mass"] for x in r])
plt.ylabel("Unsupported target mass (%)"); plt.title("Critical-task safety creates an explicit counterfactual boundary")
plt.grid(axis="y",alpha=.25); plt.tight_layout(); plt.savefig(FIG/"v36_support_boundary_mass.png",dpi=170); plt.close()
print("wrote v3.6 support-boundary sweep")
