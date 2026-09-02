from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt
from commlab.computation import simulate_battery_carbon_fair_fl
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'results'/'data'; FIG=ROOT/'results'/'figures'; DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rows=[]
for h in [.12,.22,.35,.50,.75,1.0]:
    for policy in ['random_feasible','carbon_only','debt_carbon','debt_battery_carbon']:
        rr=[simulate_battery_carbon_fair_fl(harvest_scale=h,policy=policy,seed=s) for s in range(7)]
        rows.append([h,policy,np.mean([x['excess_loss'] for x in rr]),np.mean([x['total_carbon_proxy'] for x in rr]),np.mean([x['participation_jain'] for x in rr]),np.mean([x['minimum_participation_rate'] for x in rr]),np.mean([x['underfilled_round_fraction'] for x in rr]),np.mean([x['mean_fraction_clients_energy_infeasible'] for x in rr])])
with (DATA/'v29_battery_carbon_fair_fl.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['harvest_scale','policy','excess_loss','carbon_proxy','jain_fairness','min_participation','underfilled_round_fraction','energy_infeasible_fraction']); w.writerows(rows)
plt.figure(figsize=(7.2,4.7))
for p in ['random_feasible','carbon_only','debt_carbon','debt_battery_carbon']:
    r=[x for x in rows if x[1]==p]; plt.plot([x[0] for x in r],[x[2] for x in r],marker='o',label=p)
plt.xlabel('Energy-harvest scale'); plt.ylabel('Final excess FL loss'); plt.title('Battery causality changes when carbon/fairness control matters'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v29_battery_carbon_loss.png',dpi=170); plt.close()
plt.figure(figsize=(7.2,4.7))
for p in ['carbon_only','debt_carbon','debt_battery_carbon']:
    r=[x for x in rows if x[1]==p]; plt.plot([x[3] for x in r],[x[4] for x in r],marker='o',label=p)
plt.xlabel('Modeled carbon proxy'); plt.ylabel('Jain participation fairness'); plt.title('Long-horizon FL: sustainability versus persistent participation'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v29_battery_carbon_pareto.png',dpi=170); plt.close()
print('wrote v29 battery-carbon FL')
