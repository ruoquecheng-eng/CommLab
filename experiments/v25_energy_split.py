from pathlib import Path
import numpy as np,csv,matplotlib.pyplot as plt
from commlab.computation import simulate_energy_aware_split
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'results/data'; F=ROOT/'results/figures'; D.mkdir(parents=True,exist_ok=True); F.mkdir(parents=True,exist_ok=True)
rows=[]
for snr in [0,3,6,9,12]:
  for p in ['static','deadline_aware','energy_aware']:
    o=simulate_energy_aware_split(mean_snr_db=snr,policy=p,deadline_ms=2.2,seed=2530)
    rows.append((snr,p,o['accuracy'],o['on_time_accuracy'],o['mean_energy_mj'],o['mean_latency_ms'],o['offload_fraction']))
with open(D/'v25_energy_split.csv','w',newline='') as f:
 w=csv.writer(f); w.writerow(['mean_snr_db','policy','accuracy','on_time_accuracy','mean_energy_mj','mean_latency_ms','offload_fraction']); w.writerows(rows)
for p in ['static','deadline_aware','energy_aware']:
 q=[r for r in rows if r[1]==p]; plt.plot([r[4] for r in q],[r[3] for r in q],marker='o',label=p)
plt.xlabel('Mean device energy (mJ)'); plt.ylabel('On-time task accuracy'); plt.legend(); plt.tight_layout(); plt.savefig(F/'v25_energy_split_pareto.png',dpi=180); plt.close()
