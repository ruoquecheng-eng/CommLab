from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt
from commlab.computation import simulate_carbon_aware_federated
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'results/data'; F=ROOT/'results/figures'; D.mkdir(parents=True,exist_ok=True); F.mkdir(parents=True,exist_ok=True)
polrows=[]
for p in ['random','utility','carbon','balanced']:
    vals=[simulate_carbon_aware_federated(policy=p,carbon_weight=.8,fairness_weight=1.0,seed=2720+r) for r in range(36)]
    polrows.append((p,*[np.mean([v[k] for v in vals]) for k in ['excess_loss','total_carbon_proxy','participation_jain','p95_round_latency_ms']]))
with open(D/'v27_carbon_policies.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['policy','excess_loss','total_carbon_proxy','participation_jain','p95_round_latency_ms']); w.writerows(polrows)
rows=[]
for cw in [0,.25,.5,.75,1,1.5,2.0]:
    vals=[simulate_carbon_aware_federated(policy='balanced',carbon_weight=cw,fairness_weight=1.0,seed=2750+r) for r in range(30)]
    rows.append((cw,*[np.mean([v[k] for v in vals]) for k in ['excess_loss','total_carbon_proxy','participation_jain']]))
with open(D/'v27_carbon_pareto.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['carbon_weight','excess_loss','total_carbon_proxy','participation_jain']); w.writerows(rows)
plt.plot([r[2] for r in rows],[r[1] for r in rows],marker='o')
for r in rows: plt.annotate(f'w={r[0]:g}',(r[2],r[1]),fontsize=7)
plt.xlabel('Total carbon proxy'); plt.ylabel('Final excess FL loss'); plt.tight_layout(); plt.savefig(F/'v27_carbon_loss_pareto.png',dpi=180); plt.close()
plt.plot([r[0] for r in rows],[r[3] for r in rows],marker='o'); plt.xlabel('Carbon weight'); plt.ylabel('Participation Jain fairness'); plt.tight_layout(); plt.savefig(F/'v27_carbon_fairness.png',dpi=180); plt.close()
