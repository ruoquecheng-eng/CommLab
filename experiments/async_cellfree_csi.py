from pathlib import Path
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from commlab.mimo.cell_free import large_scale_fading, user_centric_mask
from commlab.mimo.async_csi import simulate_async_cellfree_csi

ROOT=Path('results'); OUT=ROOT/'data'; FIG=ROOT/'figures'; OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(1701)
M,K=20,8
aps=rng.uniform(0,1,(M,2)); users=rng.uniform(0,1,(K,2))
beta=large_scale_fading(aps,users,shadow_std_db=2.0,rng=rng); mask=user_centric_mask(beta,6)
# Heterogeneous temporal correlation: some AP links age faster than others.
rho=np.linspace(.94,.997,M)
rows=[]
for budget in [1,2,4,8]:
    for policy in ['round_robin','uncertainty','bounded_uncertainty']:
        o=simulate_async_cellfree_csi(beta,mask,rho,8.0,bits_per_component=6,
                                      updates_per_slot=budget,n_slots=450,policy=policy,seed=1702)
        rows.append({'updates_per_slot':budget,'policy':policy,'mean_sum_rate':o['mean_sum_rate'],
                     'edge_rate':o['edge_rate'],'mean_csi_nmse':o['mean_csi_nmse'],
                     'mean_ap_age':o['mean_ap_age'],'p95_ap_age':o['p95_ap_age']})
df=pd.DataFrame(rows); df.to_csv(OUT/'async_cellfree_csi.csv',index=False)
for metric,ylabel,name in [('edge_rate','5% User Rate (bit/s/Hz)','async_csi_edge_rate.png'),
                            ('mean_csi_nmse','Mean CSI NMSE','async_csi_nmse.png')]:
    plt.figure(figsize=(6.4,4.2))
    for p,g in df.groupby('policy'):
        plt.plot(g.updates_per_slot,g[metric],marker='o',label=p.replace('_',' ').title())
    plt.xlabel('AP CSI Refreshes per Slot'); plt.ylabel(ylabel); plt.grid(alpha=.25); plt.legend(); plt.tight_layout()
    plt.savefig(FIG/name,dpi=180); plt.close()
print(df.to_string(index=False))
