from pathlib import Path
import csv,numpy as np,matplotlib.pyplot as plt
from commlab.computation import simulate_energy_harvesting_aircomp_fl
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'results/data'; F=ROOT/'results/figures'; D.mkdir(parents=True,exist_ok=True); F.mkdir(parents=True,exist_ok=True)
rows=[]; policies=['channel','energy_channel','age_energy']
for h in [.12,.20,.30,.40,.55,.70]:
    for p in policies:
        vals=[simulate_energy_harvesting_aircomp_fl(policy=p,harvest_scale=h,rounds=120,seed=2640+r) for r in range(24)]
        rows.append((h,p,*[np.mean([v[k] for v in vals]) for k in ['final_global_loss','participation_jain','energy_outage_slot_fraction','plus_selection_fraction','mean_selected_weakest_gain']]))
with open(D/'v26_eh_aircomp_fl.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['harvest_scale','policy','final_global_loss','participation_jain','outage_slot_fraction','plus_selection_fraction','weakest_gain']); w.writerows(rows)
for idx,name,ylabel in [(2,'v26_eh_aircomp_loss.png','Final global loss'),(3,'v26_eh_aircomp_fairness.png','Participation Jain fairness')]:
    for p in policies:
        rr=[r for r in rows if r[1]==p]; plt.plot([r[0] for r in rr],[r[idx] for r in rr],marker='o',label=p)
    plt.xlabel('Energy-harvest scale'); plt.ylabel(ylabel); plt.legend(); plt.tight_layout(); plt.savefig(F/name,dpi=180); plt.close()
