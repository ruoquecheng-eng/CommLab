from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt
from commlab.computation import simulate_fair_carbon_orchestration
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'results'/'data'; FIG=ROOT/'results'/'figures'; DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
policies=['random','carbon','age_balanced','virtual_debt']; rows=[]
for p in policies:
    rr=[simulate_fair_carbon_orchestration(policy=p,rounds=260,carbon_weight=1.0,debt_weight=8.0,seed=s) for s in range(14)]
    rows.append([p,np.mean([x['excess_loss'] for x in rr]),np.mean([x['total_carbon_proxy'] for x in rr]),np.mean([x['participation_jain'] for x in rr]),np.mean([x['minimum_participation_rate'] for x in rr]),np.mean([x['participation_shortfall_fraction'] for x in rr]),np.mean([x['final_max_virtual_debt'] for x in rr])])
with (DATA/'v28_fair_carbon_policies.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['policy','excess_loss','total_carbon_proxy','participation_jain','minimum_participation_rate','participation_shortfall_fraction','final_max_virtual_debt']); w.writerows(rows)
prows=[]
for dw in [.5,1,2,4,8,12]:
    rr=[simulate_fair_carbon_orchestration(policy='virtual_debt',rounds=260,carbon_weight=1.0,debt_weight=dw,seed=s) for s in range(12)]
    prows.append([dw,np.mean([x['excess_loss'] for x in rr]),np.mean([x['total_carbon_proxy'] for x in rr]),np.mean([x['participation_jain'] for x in rr]),np.mean([x['minimum_participation_rate'] for x in rr])])
with (DATA/'v28_fair_carbon_pareto.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['debt_weight','excess_loss','total_carbon_proxy','participation_jain','minimum_participation_rate']); w.writerows(prows)
plt.figure(figsize=(7.2,4.7)); plt.plot([x[2] for x in prows],[x[3] for x in prows],marker='o');
for x in prows: plt.annotate(str(x[0]),(x[2],x[3]),xytext=(4,4),textcoords='offset points')
plt.xlabel('Total modeled carbon proxy'); plt.ylabel('Participation Jain fairness'); plt.title('Persistent fairness debt has a carbon price'); plt.grid(alpha=.25); plt.tight_layout(); plt.savefig(FIG/'v28_fair_carbon_pareto.png',dpi=170); plt.close()
plt.figure(figsize=(7.2,4.7));
for r in rows: plt.scatter(r[2],r[1],s=60,label=r[0])
plt.xlabel('Total modeled carbon proxy'); plt.ylabel('Final excess loss'); plt.title('Carbon, convergence, and long-run participation'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v28_fair_carbon_policies.png',dpi=170); plt.close()
print('wrote v28 fair carbon orchestration')
