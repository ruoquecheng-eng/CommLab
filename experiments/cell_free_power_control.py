from pathlib import Path
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from commlab.mimo import large_scale_fading,user_centric_mask,sample_cell_free_channel,clustered_mrt_directions,rates_with_power,max_min_sinr_power_allocation,jain_fairness
ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results/figures'; DATA=ROOT/'results/data'; FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(1304); M=24;K=8;snr=10**(-2/10); drops=140; fades=3
vals={'UC-4 equal power':[],'UC-4 max-min':[],'Cell-free equal power':[]}
for _ in range(drops):
    aps=rng.uniform(0,1,(M,2)); users=rng.uniform(0,1,(K,2)); beta=large_scale_fading(aps,users,3.0,.05,3.0,rng)
    masks={'UC-4 equal power':user_centric_mask(beta,4),'UC-4 max-min':user_centric_mask(beta,4),'Cell-free equal power':np.ones((K,M),bool)}
    for _ in range(fades):
        H=sample_cell_free_channel(beta,rng)
        for name,m in masks.items():
            V=clustered_mrt_directions(H,m)
            if name=='UC-4 max-min': p,_=max_min_sinr_power_allocation(H,V,snr)
            else: p=np.full(K,1/K)
            r=rates_with_power(H,V,p,snr); vals[name].append((r.mean(),np.quantile(r,.05),r.min(),jain_fairness(r)))
rows=[]
for n,v in vals.items():
    a=np.asarray(v); rows.append(dict(scheme=n,mean_rate=a[:,0].mean(),mean_5pct=a[:,1].mean(),mean_min_rate=a[:,2].mean(),mean_jain=a[:,3].mean()))
df=pd.DataFrame(rows); df.to_csv(DATA/'cell_free_power_control.csv',index=False)
fig,ax=plt.subplots(figsize=(7.2,4.6)); x=np.arange(len(df)); w=.27
ax.bar(x-w,df.mean_rate,w,label='Mean'); ax.bar(x,df.mean_5pct,w,label='5%-tile'); ax.bar(x+w,df.mean_min_rate,w,label='Minimum user')
ax.set_xticks(x,df.scheme,rotation=12); ax.set_ylabel('Rate (bit/s/Hz)'); ax.grid(True,axis='y',alpha=.25); ax.legend(); fig.tight_layout(); fig.savefig(FIG/'cell_free_power_control_rates.png',dpi=180); plt.close(fig)
print(df.to_string(index=False))
