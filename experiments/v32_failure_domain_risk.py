from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt
from commlab.computation import simulate_failure_domain_replication
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'results'/'data'; FIG=ROOT/'results'/'figures'; DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rows=[]
for z in [.01,.03,.06,.10,.15,.20]:
    for p in ['popularity','criticality','diversity_risk']:
        rr=[simulate_failure_domain_replication(n_requests=14000,policy=p,storage_budget_mb=2800,zone_failure_prob=z,seed=s) for s in range(5)]
        rows.append([z,p,*[np.mean([x[k] for x in rr]) for k in ['task_weighted_outage_rate','model_outage_rate','mean_failure_domains_per_model','mean_replication_factor','mean_latency_ms','p95_latency_ms']]])
with (DATA/'v32_failure_domain_zone_risk.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['zone_failure_probability','policy','task_weighted_outage_rate','raw_outage_rate','failure_domains_per_model','replication_factor','mean_latency_ms','p95_latency_ms']); w.writerows(rows)
plt.figure(figsize=(7.2,4.7))
for p in ['popularity','criticality','diversity_risk']:
    r=[x for x in rows if x[1]==p]; plt.semilogy([x[0] for x in r],[x[2] for x in r],marker='o',label=p)
plt.xlabel('Shared zone-failure probability'); plt.ylabel('Task-weighted model outage'); plt.title('Replica count cannot replace failure-domain diversity'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v32_failure_domain_zone_outage.png',dpi=170); plt.close()
plt.figure(figsize=(7.2,4.7))
for p in ['popularity','criticality','diversity_risk']:
    r=[x for x in rows if x[1]==p]; plt.plot([x[0] for x in r],[x[4] for x in r],marker='o',label=p)
plt.xlabel('Shared zone-failure probability'); plt.ylabel('Distinct failure domains / model'); plt.title('Diversity-risk placement buys independent failure exposure'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v32_failure_domain_zone_diversity.png',dpi=170); plt.close()
print('wrote v32 failure-domain zone risk')
