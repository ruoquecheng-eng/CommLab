from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt
from commlab.computation import simulate_failure_domain_replication
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'results'/'data'; FIG=ROOT/'results'/'figures'; DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rows=[]
for budget in [2000,2400,2800,3400,4200]:
    for p in ['popularity','independent_risk','domain_aware']:
        rr=[simulate_failure_domain_replication(n_requests=12000,policy=p,storage_budget_mb=budget,seed=s) for s in range(5)]
        rows.append([budget,p,*[np.mean([x[k] for x in rr]) for k in ['task_weighted_outage_rate','model_outage_rate','mean_failure_domains_per_model','mean_replication_factor','mean_latency_ms']]])
with (DATA/'v32_failure_domain_replication.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['storage_budget_mb','policy','task_weighted_outage_rate','raw_outage_rate','failure_domains_per_model','replication_factor','mean_latency_ms']); w.writerows(rows)
plt.figure(figsize=(7.2,4.7))
for p in ['popularity','independent_risk','domain_aware']:
    r=[x for x in rows if x[1]==p]; plt.semilogy([x[0] for x in r],[x[2] for x in r],marker='o',label=p)
plt.xlabel('Storage budget (MB)'); plt.ylabel('Task-weighted model outage'); plt.title('Replicas in the same failure domain are not independent protection'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v32_failure_domain_outage.png',dpi=170); plt.close()
plt.figure(figsize=(7.2,4.7))
for p in ['popularity','independent_risk','domain_aware']:
    r=[x for x in rows if x[1]==p]; plt.plot([x[0] for x in r],[x[4] for x in r],marker='o',label=p)
plt.xlabel('Storage budget (MB)'); plt.ylabel('Mean distinct failure domains / model'); plt.title('Domain-aware placement buys failure diversity, not just more copies'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v32_failure_domain_diversity.png',dpi=170); plt.close()
print('wrote v32 failure-domain replication')
