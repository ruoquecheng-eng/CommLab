from pathlib import Path
import csv

import matplotlib.pyplot as plt
import numpy as np

from commlab.computation import simulate_observable_resilience

ROOT=Path(__file__).resolve().parents[1]
DATA,FIG=ROOT/"results"/"data",ROOT/"results"/"figures"
DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
budgets=[.2,.4,.6,.9,1.2,1.6]; policies=["outcome_only","component_telemetry"]
metrics=["protected_miss_rate","masked_fraction_of_base_failures","resilience_credits_per_task",
         "mean_outcome_debt","mean_radio_debt","mean_edge_debt"]
rows=[]
for budget in budgets:
    for policy in policies:
        rr=[simulate_observable_resilience(n_tasks=7000,policy=policy,drift_mode="mixed",
            budget_per_task=budget,telemetry_probability=.8,audit_rate=0,seed=s) for s in (1,2,3)]
        rows.append({"budget_per_task":budget,"policy":policy,
                     **{k:float(np.mean([x[k] for x in rr])) for k in metrics}})
with (DATA/"v35_masking_budget.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
for ykey,ylabel,name,title in [
    ("masked_fraction_of_base_failures","Masked base failures (%)","v35_masking_budget_fraction.png","Protection hides an increasing share of primary failures"),
    ("mean_outcome_debt","Mean learned risk debt","v35_masking_budget_debt.png","Outcome-only feedback becomes self-reassuring")]:
    plt.figure(figsize=(7.2,4.7))
    for policy in policies:
        r=[x for x in rows if x["policy"]==policy]
        y=[100*x[ykey] if "fraction" in ykey else x[ykey] for x in r]
        plt.plot(budgets,y,marker="o",label=policy)
    plt.xlabel("Available resilience credits / task"); plt.ylabel(ylabel); plt.title(title)
    plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/name,dpi=170); plt.close()
print("wrote v3.5 masking-budget sweep")
