from pathlib import Path
import csv, numpy as np
import matplotlib.pyplot as plt
from commlab.computation import simulate_byzantine_federated
OUT=Path('results/data'); FIG=Path('results/figures'); OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rows=[]
for frac in [0,.067,.133,.2,.267,.333]:
    for method in ['mean','median','trimmed_mean']:
        vals=[simulate_byzantine_federated(method=method,byzantine_fraction=frac,attack_scale=6,rounds=90,heterogeneity=.9,seed=23100+s) for s in range(12)]
        rows.append({'byzantine_fraction':frac,'method':method,'final_loss':np.median([v['final_loss'] for v in vals]),'parameter_error':np.median([v['parameter_error'] for v in vals])})
with open(OUT/'v23_byzantine_fl.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
plt.figure()
for m in ['mean','median','trimmed_mean']:
    rr=[r for r in rows if r['method']==m];plt.plot([r['byzantine_fraction'] for r in rr],[r['final_loss'] for r in rr],marker='o',label=m)
plt.yscale('log');plt.xlabel('Byzantine client fraction');plt.ylabel('Median final loss');plt.legend();plt.tight_layout();plt.savefig(FIG/'v23_byzantine_robustness.png',dpi=180);plt.close()
print(rows)
