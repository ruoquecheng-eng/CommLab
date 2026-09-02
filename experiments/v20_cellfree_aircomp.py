from pathlib import Path
import csv,matplotlib.pyplot as plt
from commlab.computation import simulate_cellfree_aircomp
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'results'/'data'; F=ROOT/'results'/'figures'; D.mkdir(parents=True,exist_ok=True); F.mkdir(parents=True,exist_ok=True)
rows=[]
for i,M in enumerate([1,2,4,8,16]):
    o=simulate_cellfree_aircomp(n_aps=M,n_devices=12,vector_dim=24,snr_db=12,n_trials=180,seed=2100+i,n_random=150)
    rows.append((M,o['single_ap_median_mse'],o['cellfree_median_mse'],o['single_ap_mean_weakest_gain'],o['cellfree_mean_weakest_gain']))
with (D/'v20_cellfree_aircomp.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['n_aps','single_ap_median_mse','cellfree_median_mse','single_ap_weakest_gain','cellfree_weakest_gain']); w.writerows(rows)
fig,ax=plt.subplots(figsize=(7.2,4.6)); ax.semilogy([r[0] for r in rows],[r[1] for r in rows],'o-',label='Best single AP'); ax.semilogy([r[0] for r in rows],[r[2] for r in rows],'s-',label='Cooperative combiner'); ax.set(xlabel='Distributed AP count',ylabel='Median aggregation MSE',title='Cell-Free AirComp: Cooperative Receive Combining'); ax.grid(alpha=.3,which='both'); ax.legend(); fig.tight_layout(); fig.savefig(F/'v20_cellfree_aircomp_mse.png',dpi=180); plt.close(fig)
fig,ax=plt.subplots(figsize=(7.2,4.6)); ax.plot([r[0] for r in rows],[r[3] for r in rows],'o-',label='Best single AP'); ax.plot([r[0] for r in rows],[r[4] for r in rows],'s-',label='Cooperative combiner'); ax.set(xlabel='Distributed AP count',ylabel='Mean weakest-device effective gain',title='Cell-Free AirComp Bottleneck Gain'); ax.grid(alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(F/'v20_cellfree_aircomp_gain.png',dpi=180); plt.close(fig)
print(rows)
