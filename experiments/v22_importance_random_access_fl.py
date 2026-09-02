from pathlib import Path
import csv,numpy as np,matplotlib.pyplot as plt
from commlab.computation import simulate_importance_aware_random_access_fl
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'results'/'data'; F=ROOT/'results'/'figures'; D.mkdir(parents=True,exist_ok=True); F.mkdir(parents=True,exist_ok=True)
rows=[]
for slots in [10,12,14,16,18,20,24]:
    for mode in ['uniform','importance']:
        vals=[]
        for rep in range(16):
            o=simulate_importance_aware_random_access_fl(n_clients=16,frame_slots=slots,rounds=30,participation_prob=.9,heterogeneity=1.2,learning_rate=.1,mode=mode,seed=2300+rep)
            vals.append([o['final_loss'],o['mean_decoded_fraction'],o['mean_decoded_gradient_mass'],o['mean_repetition_degree'],o['empty_round_fraction']])
        a=np.asarray(vals); rows.append((slots,mode,*a.mean(axis=0)))
with (D/'v22_importance_random_access_fl.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['frame_slots','mode','final_loss','decoded_fraction','decoded_gradient_mass','mean_repetition_degree','empty_round_fraction']); w.writerows(rows)
fig,ax=plt.subplots(figsize=(7.3,4.7))
for mode in ['uniform','importance']:
    r=[x for x in rows if x[1]==mode]; ax.plot([x[0] for x in r],[x[4] for x in r],'o-',label=mode)
ax.set(xlabel='Shared random-access slots per FL round',ylabel='Decoded gradient-norm mass fraction',title='Importance-Aware Repetition Protects High-Utility Updates'); ax.grid(alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(F/'v22_importance_ra_gradient_mass.png',dpi=180); plt.close(fig)
fig,ax=plt.subplots(figsize=(7.3,4.7))
for mode in ['uniform','importance']:
    r=[x for x in rows if x[1]==mode]; ax.semilogy([x[0] for x in r],[x[2] for x in r],'o-',label=mode)
ax.set(xlabel='Shared slots per FL round',ylabel='Final global loss after 30 rounds',title='MAC-Level Importance Protection Can Help Only Outside Severe Overload'); ax.grid(alpha=.3,which='both'); ax.legend(); fig.tight_layout(); fig.savefig(F/'v22_importance_ra_learning.png',dpi=180); plt.close(fig)
print(rows)
