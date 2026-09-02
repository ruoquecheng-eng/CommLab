from pathlib import Path
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from commlab.mimo.cell_free import user_centric_mask
from commlab.mimo.joint_csi_control import simulate_joint_predictive_csi_control

ROOT=Path('results'); OUT=ROOT/'data'; FIG=ROOT/'figures'; OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(1800); beta=np.exp(rng.normal(0,1,(6,16))); mask=user_centric_mask(beta,6)
rows=[]
for rho in [.95,.98,.995]:
    for budget in [64,96,128,192]:
        for policy in ['round_robin','uncertainty_fixed','joint']:
            o=simulate_joint_predictive_csi_control(beta,mask,rho,10,budget,n_slots=280,policy=policy,
                                                    fixed_bits=5,min_bits=2,max_bits=8,seed=1801)
            rows.append({'correlation':rho,'budget_bits_per_slot':budget,'policy':policy,
                         'mean_csi_nmse':o['mean_csi_nmse'],'edge_rate':o['edge_rate'],
                         'mean_sum_rate':o['mean_sum_rate'],'used_bits_per_slot':o['mean_fronthaul_bits_per_slot'],
                         'p95_ap_age':o['p95_ap_age']})
df=pd.DataFrame(rows); df.to_csv(OUT/'joint_csi_fronthaul_control.csv',index=False)
sub=df[df.correlation==.98]
plt.figure(figsize=(6.5,4.2))
for p,g in sub.groupby('policy'):
    plt.semilogy(g.budget_bits_per_slot,g.mean_csi_nmse,marker='o',label=p)
plt.xlabel('CSI Fronthaul Budget (bit/slot)'); plt.ylabel('Mean CSI NMSE'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout()
plt.savefig(FIG/'joint_csi_budget_nmse.png',dpi=180); plt.close()
plt.figure(figsize=(6.5,4.2))
for p,g in sub.groupby('policy'):
    plt.plot(g.budget_bits_per_slot,g.edge_rate,marker='o',label=p)
plt.xlabel('CSI Fronthaul Budget (bit/slot)'); plt.ylabel('5%-Quantile User Rate (bit/s/Hz)'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout()
plt.savefig(FIG/'joint_csi_budget_edge_rate.png',dpi=180); plt.close()
print(df.to_string(index=False))
