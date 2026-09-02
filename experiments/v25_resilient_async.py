from pathlib import Path
import numpy as np, csv, matplotlib.pyplot as plt
from commlab.computation import simulate_resilient_async_federated
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'results/data'; F=ROOT/'results/figures'; D.mkdir(parents=True,exist_ok=True); F.mkdir(parents=True,exist_ok=True)
rows=[]
for frac in [0,.07,.13,.2,.27]:
  for s in ['naive_mean','median','stale_robust']:
    vals=[simulate_resilient_async_federated(strategy=s,byzantine_fraction=frac,delay_mean=4,rounds=90,seed=2500+r) for r in range(10)]
    rows.append((frac,s,np.median([v['final_loss'] for v in vals]),np.mean([v['mean_accept_fraction'] for v in vals])))
with open(D/'v25_resilient_async.csv','w',newline='') as f:
  w=csv.writer(f); w.writerow(['byzantine_fraction','strategy','median_final_loss','mean_accept_fraction']); w.writerows(rows)
for s in ['naive_mean','median','stale_robust']:
  q=[r for r in rows if r[1]==s]; plt.plot([100*r[0] for r in q],[r[2] for r in q],marker='o',label=s)
plt.yscale('log'); plt.xlabel('Byzantine clients (%)'); plt.ylabel('Median final loss'); plt.legend(); plt.tight_layout(); plt.savefig(F/'v25_resilient_async_loss.png',dpi=180); plt.close()
