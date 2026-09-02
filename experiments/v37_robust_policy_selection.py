from pathlib import Path
import csv

import matplotlib.pyplot as plt
import numpy as np

from commlab.computation import select_propensity_robust_policy

ROOT=Path(__file__).resolve().parents[1]; DATA,FIG=ROOT/"results"/"data",ROOT/"results"/"figures"
levels=[0,.5,1.0,1.5,2.0]; selectors=["point","sensitivity_guard"]; rows=[]
for level in levels:
    for selector in selectors:
        rr=[select_propensity_robust_policy(n_tasks=4000,propensity_mode="recorded_nominal",selector=selector,
            hidden_confounding=level,propensity_drift=1.0,sensitivity_gamma=2,seed=s) for s in range(12)]
        rows.append({"hidden_confounding":level,"selector":selector,
            "mean_selection_regret":np.mean([x["selection_regret"] for x in rr]),
            "p90_selection_regret":np.quantile([x["selection_regret"] for x in rr],.9),
            "baseline_fallback_rate":np.mean([x["baseline_fallback"] for x in rr]),
            "oracle_selection_rate":np.mean([x["selected_policy"]==x["oracle_best_policy"] for x in rr])})
with (DATA/"v37_robust_policy_selection.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
plt.figure(figsize=(7.4,4.8))
for selector in selectors:
    r=[x for x in rows if x["selector"]==selector]; plt.plot(levels,100*np.array([x["mean_selection_regret"] for x in r]),marker="o",label=selector)
plt.xlabel("Hidden-confounding strength"); plt.ylabel("Mean selection regret (objective points x100)"); plt.title("Sensitivity protection trades adaptation for fallback"); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/"v37_robust_policy_selection_regret.png",dpi=170); plt.close()
plt.figure(figsize=(7.4,4.8))
for selector in selectors:
    r=[x for x in rows if x["selector"]==selector]; plt.plot(levels,100*np.array([x["baseline_fallback_rate"] for x in r]),marker="o",label=selector)
plt.xlabel("Hidden-confounding strength"); plt.ylabel("Baseline fallback rate (%)"); plt.ylim(-3,103); plt.title("A conservative guard can freeze policy improvement"); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/"v37_robust_policy_selection_fallback.png",dpi=170); plt.close()
print("wrote v3.7 robust policy-selection sweep")
