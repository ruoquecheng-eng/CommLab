from pathlib import Path
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from commlab.mimo.cell_free import large_scale_fading, user_centric_mask, sample_cell_free_channel, clustered_mrt_precoder, per_user_rates
from commlab.mimo.pilot_assignment import (random_pilot_assignment, greedy_contamination_aware_assignment,
    pilot_contamination_cost, lmmse_pilot_channel_estimate, normalized_channel_mse)
ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results/figures'; DATA=ROOT/'results/data'; FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(1401); M=24; K=12; snr=10**(0/10); pilot_snr=10**(10/10); drops=70
rows=[]
for tau in [3,4,6,12]:
    acc={s:[] for s in ['Random','Contamination-aware']}
    for _ in range(drops):
        aps=rng.uniform(0,1,(M,2)); users=rng.uniform(0,1,(K,2))
        beta=large_scale_fading(aps,users,pathloss_exp=3.1,min_distance=.05,shadow_std_db=3.0,rng=rng)
        H=sample_cell_free_channel(beta,rng); mask=user_centric_mask(beta,6)
        assigns={
            'Random':random_pilot_assignment(K,tau,rng),
            'Contamination-aware':greedy_contamination_aware_assignment(beta,tau),
        }
        for name,p in assigns.items():
            Hh=lmmse_pilot_channel_estimate(H,beta,p,pilot_snr,rng)
            W=clustered_mrt_precoder(Hh,mask)
            r=per_user_rates(H,W,snr)
            acc[name].append((pilot_contamination_cost(beta,p),normalized_channel_mse(H,Hh),r.mean(),np.quantile(r,.05)))
    for name,v in acc.items():
        a=np.asarray(v)
        rows.append(dict(pilots=tau,scheme=name,contamination_cost=a[:,0].mean(),channel_nmse=a[:,1].mean(),mean_user_rate=a[:,2].mean(),mean_5pct_rate=a[:,3].mean()))
df=pd.DataFrame(rows); df.to_csv(DATA/'cell_free_pilot_contamination.csv',index=False)
for col,ylabel,fname in [
    ('channel_nmse','Channel-estimation NMSE','cell_free_pilot_nmse.png'),
    ('mean_5pct_rate','Mean 5%-tile user rate (bit/s/Hz)','cell_free_pilot_edge_rate.png'),
    ('contamination_cost','Large-scale co-pilot overlap cost','cell_free_pilot_overlap.png')]:
    fig,ax=plt.subplots(figsize=(6.8,4.5))
    for name,g in df.groupby('scheme'):
        ax.plot(g.pilots,g[col],marker='o',label=name)
    ax.set_xlabel('Available orthogonal pilots'); ax.set_ylabel(ylabel); ax.grid(True,alpha=.25); ax.legend(); fig.tight_layout(); fig.savefig(FIG/fname,dpi=180); plt.close(fig)
print(df.to_string(index=False))
