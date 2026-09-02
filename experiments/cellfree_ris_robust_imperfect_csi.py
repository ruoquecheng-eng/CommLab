from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt
from commlab.ris.cellfree import coordinate_optimize_cellfree_ris,cellfree_ris_rates
from commlab.ris.robust import perturb_complex_channel,sample_average_optimize_cellfree_ris

ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'results/data'; FIG=ROOT/'results/figures'; DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(1502); K,M,N=3,6,16; snr=10.0
D0=.22*(rng.normal(size=(K,M))+1j*rng.normal(size=(K,M)))/np.sqrt(2)
G0=.19*(rng.normal(size=(N,M))+1j*rng.normal(size=(N,M)))/np.sqrt(2)
R0=.19*(rng.normal(size=(K,N))+1j*rng.normal(size=(K,N)))/np.sqrt(2)
nmse_grid=[0,.02,.05,.1,.2]
rows=[]
for nmse in nmse_grid:
    # One noisy CSI snapshot for naive optimization; multiple posterior samples for robust design.
    Dn=perturb_complex_channel(D0,nmse,rng); Gn=perturb_complex_channel(G0,nmse,rng); Rn=perturb_complex_channel(R0,nmse,rng)
    th_naive,_=coordinate_optimize_cellfree_ris(Dn,Gn,Rn,snr,bits=2,iterations=2,objective='sum_rate')
    train=[(perturb_complex_channel(Dn,nmse,rng),perturb_complex_channel(Gn,nmse,rng),perturb_complex_channel(Rn,nmse,rng)) for _ in range(8)]
    th_rob,_=sample_average_optimize_cellfree_ris(train,snr,bits=2,iterations=2,objective='sum_rate')
    vals={'naive':[],'robust':[],'random':[]}
    for _ in range(120):
        Dt=perturb_complex_channel(D0,nmse,rng); Gt=perturb_complex_channel(G0,nmse,rng); Rt=perturb_complex_channel(R0,nmse,rng)
        rand=rng.uniform(-np.pi,np.pi,N)
        vals['naive'].append(cellfree_ris_rates(Dt,Gt,Rt,th_naive,snr).sum())
        vals['robust'].append(cellfree_ris_rates(Dt,Gt,Rt,th_rob,snr).sum())
        vals['random'].append(cellfree_ris_rates(Dt,Gt,Rt,rand,snr).sum())
    for method in vals:
        rows.append(dict(channel_nmse=nmse,method=method,mean_sum_rate=np.mean(vals[method]),p10_sum_rate=np.percentile(vals[method],10)))
with open(DATA/'cellfree_ris_robust_imperfect_csi.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
fig,ax=plt.subplots()
for method in ['random','naive','robust']:
    rr=[x for x in rows if x['method']==method]; ax.plot([x['channel_nmse'] for x in rr],[x['mean_sum_rate'] for x in rr],marker='o',label=method)
ax.set_xlabel('CSI uncertainty NMSE'); ax.set_ylabel('Held-out mean sum-rate (bit/s/Hz)'); ax.set_title('Robust RIS under imperfect CSI'); ax.grid(True,alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(FIG/'cellfree_ris_robust_mean_rate.png',dpi=180); plt.close(fig)
fig,ax=plt.subplots()
for method in ['random','naive','robust']:
    rr=[x for x in rows if x['method']==method]; ax.plot([x['channel_nmse'] for x in rr],[x['p10_sum_rate'] for x in rr],marker='o',label=method)
ax.set_xlabel('CSI uncertainty NMSE'); ax.set_ylabel('10%-tile held-out sum-rate'); ax.set_title('RIS robustness tail performance'); ax.grid(True,alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(FIG/'cellfree_ris_robust_tail.png',dpi=180); plt.close(fig)
print(rows)
