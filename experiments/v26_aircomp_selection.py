from pathlib import Path
import csv,numpy as np,matplotlib.pyplot as plt
from commlab.computation import simulate_aircomp_selection_federated
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'results/data'; F=ROOT/'results/figures'; D.mkdir(parents=True,exist_ok=True); F.mkdir(parents=True,exist_ok=True)
rows=[]; strategies=['all','random','channel','diversity']
for d in [0,4,8,12]:
    for s in strategies:
        vals=[simulate_aircomp_selection_federated(strategy=s,channel_disparity_db=d,rounds=90,seed=2610+r) for r in range(20)]
        rows.append((d,s,*[np.mean([v[k] for v in vals]) for k in ['final_global_loss','mean_analog_mse_to_selected_mean','mean_selection_bias_mse','plus_selection_fraction','participation_jain','mean_selected_weakest_gain']]))
with open(D/'v26_aircomp_selection.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['channel_disparity_db','strategy','final_global_loss','analog_mse_selected','selection_bias_mse','plus_selection_fraction','participation_jain','weakest_gain']); w.writerows(rows)
for metric,idx,name,ylabel,yscale in [('loss',2,'v26_aircomp_selection_loss.png','Final global loss',None),('bias',4,'v26_aircomp_selection_bias.png','Selection-bias MSE','log')]:
    for s in strategies:
        rr=[r for r in rows if r[1]==s]; plt.plot([r[0] for r in rr],[r[idx] for r in rr],marker='o',label=s)
    if yscale: plt.yscale(yscale)
    plt.xlabel('Long-term channel disparity (dB)'); plt.ylabel(ylabel); plt.legend(); plt.tight_layout(); plt.savefig(F/name,dpi=180); plt.close()
