from pathlib import Path
import numpy as np,csv,matplotlib.pyplot as plt
from commlab.computation import simulate_clustered_personalization
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'results/data'; F=ROOT/'results/figures'; D.mkdir(parents=True,exist_ok=True); F.mkdir(parents=True,exist_ok=True)
rows=[]
for sep in [0,.3,.6,.9,1.2]:
  for err in [0,.1,.25]:
    vals=[simulate_clustered_personalization(cluster_separation=sep,cluster_assignment_error=err,seed=2510+r) for r in range(20)]
    rows.append((sep,err,*[np.mean([v[k] for v in vals]) for k in ['global_mse','cluster_mse','local_mse']]))
with open(D/'v25_cluster_personalization.csv','w',newline='') as f:
  w=csv.writer(f); w.writerow(['cluster_separation','assignment_error','global_mse','cluster_mse','local_mse']); w.writerows(rows)
for err in [0,.1,.25]:
 q=[r for r in rows if r[1]==err]; plt.plot([r[0] for r in q],[r[3] for r in q],marker='o',label=f'cluster err={err}')
q=[r for r in rows if r[1]==0]; plt.plot([r[0] for r in q],[r[2] for r in q],marker='x',label='global'); plt.plot([r[0] for r in q],[r[4] for r in q],marker='s',label='local')
plt.xlabel('Cluster separation'); plt.ylabel('Test MSE'); plt.legend(); plt.tight_layout(); plt.savefig(F/'v25_cluster_personalization_mse.png',dpi=180); plt.close()
