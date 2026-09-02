from pathlib import Path
import csv

import matplotlib.pyplot as plt
import numpy as np

from commlab.computation import select_offline_resilience_policy

ROOT=Path(__file__).resolve().parents[1]; DATA,FIG=ROOT/"results"/"data",ROOT/"results"/"figures"
DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
sizes=[1200,2500,5000,10000,20000]; selectors=["greedy","conservative"]; rows=[]
for size in sizes:
    for selector in selectors:
        rr=[select_offline_resilience_policy(n_tasks=size,estimator="dr",selector=selector,
            exploration_rate=.05,drift_strength=1,nonlinearity=1.5,protection_cost=.10,seed=s) for s in range(24)]
        rows.append({"n_tasks":size,"selector":selector,"mean_selection_regret":np.mean([x["selection_regret"] for x in rr]),
            "p90_selection_regret":np.quantile([x["selection_regret"] for x in rr],.9),
            "baseline_fallback_rate":np.mean([x["baseline_fallback"] for x in rr]),
            "oracle_selection_rate":np.mean([x["selected_policy"]==x["oracle_best_policy"] for x in rr]),
            "aggressive_selection_rate":np.mean([x["selected_policy"]=="aggressive" for x in rr])})
with (DATA/"v36_policy_selection.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
plt.figure(figsize=(7.2,4.7))
for selector in selectors:
    r=[x for x in rows if x["selector"]==selector]
    plt.plot(sizes,[100*x["mean_selection_regret"] for x in r],marker="o",label=selector)
plt.xscale("log"); plt.xlabel("Logged tasks"); plt.ylabel("Mean oracle regret (percentage points)")
plt.title("Greedy errors shrink with data; conservative selection can freeze"); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/"v36_policy_selection_regret.png",dpi=170); plt.close()
plt.figure(figsize=(7.2,4.7))
for selector in selectors:
    r=[x for x in rows if x["selector"]==selector]
    plt.plot(sizes,[100*x["baseline_fallback_rate"] for x in r],marker="o",label=selector)
plt.xscale("log"); plt.xlabel("Logged tasks"); plt.ylabel("Baseline fallback (%)"); plt.title("Conservatism pays an opportunity cost")
plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/"v36_policy_selection_fallback.png",dpi=170); plt.close()
print("wrote v3.6 policy-selection sweep")
