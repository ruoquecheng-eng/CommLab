from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt
from commlab.computation import simulate_risk_aware_model_replication
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'results'/'data'; FIG=ROOT/'results'/'figures'; DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rows=[]
for budget in [1600,1800,2200,2600,3200,4000]:
    for p in ['popularity','risk_aware']:
        rr=[simulate_risk_aware_model_replication(n_requests=9000,policy=p,storage_budget_mb=budget,seed=s) for s in range(5)]
        rows.append([budget,p,np.mean([x['model_outage_rate'] for x in rr]),np.mean([x['task_weighted_outage_rate'] for x in rr]),np.mean([x['task_weighted_utility'] for x in rr]),np.mean([x['storage_used_mb'] for x in rr]),np.mean([x['mean_replication_factor'] for x in rr])])
with (DATA/'v31_model_replication.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['storage_budget_mb','policy','model_outage_rate','task_weighted_outage_rate','task_weighted_utility','storage_used_mb','mean_replication_factor']); w.writerows(rows)
plt.figure(figsize=(7.2,4.7))
for p in ['popularity','risk_aware']:
    r=[x for x in rows if x[1]==p]; plt.semilogy([x[0] for x in r],np.maximum([x[3] for x in r],1e-5),marker='o',label=p)
plt.xlabel('Model-replica storage budget (MB)'); plt.ylabel('Task-weighted outage rate'); plt.title('Risk-aware replicas protect critical models, not only popular ones'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v31_model_replication_weighted_outage.png',dpi=170); plt.close()
plt.figure(figsize=(7.2,4.7))
for p in ['popularity','risk_aware']:
    r=[x for x in rows if x[1]==p]; plt.plot([x[0] for x in r],[x[2] for x in r],marker='o',label=p)
plt.xlabel('Model-replica storage budget (MB)'); plt.ylabel('Unweighted model outage rate'); plt.title('Protecting task value can differ from minimizing raw outage count'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v31_model_replication_raw_outage.png',dpi=170); plt.close()
print('wrote v31 model replication')
