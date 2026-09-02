from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt
from commlab.computation import simulate_importance_aware_multicast_repair
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'results/data'; F=ROOT/'results/figures'; D.mkdir(parents=True,exist_ok=True); F.mkdir(parents=True,exist_ok=True)
rows=[]; policies=['no_repair','important_repair','all_repair']
for c in [0,.3,.6,.8,.95]:
    for p in policies:
        vals=[simulate_importance_aware_multicast_repair(policy=p,importance_anticorrelation=c,seed=2770+r) for r in range(60)]
        rows.append((c,p,*[np.mean([v[k] for v in vals]) for k in ['weighted_task_utility','mean_model_coverage','time_ratio_to_full','repaired_fraction']]))
with open(D/'v27_multicast_repair.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['importance_snr_anticorrelation','policy','weighted_task_utility','model_coverage','time_ratio_to_full','repaired_fraction']); w.writerows(rows)
for idx,name,ylabel in [(2,'v27_multicast_repair_utility.png','Importance-weighted model utility'),(4,'v27_multicast_repair_airtime.png','Downlink time / full-common time')]:
    for p in policies:
        rr=[r for r in rows if r[1]==p]; plt.plot([r[0] for r in rr],[r[idx] for r in rr],marker='o',label=p)
    plt.xlabel('Importance / SNR anticorrelation'); plt.ylabel(ylabel); plt.legend(); plt.tight_layout(); plt.savefig(F/name,dpi=180); plt.close()
