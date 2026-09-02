from pathlib import Path
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from commlab.mimo import large_scale_fading, user_centric_mask, sample_cell_free_channel, clustered_mrt_precoder, cell_free_user_rates, jain_fairness, cluster_link_count

ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results/figures'; DATA=ROOT/'results/data'; FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(1301)
M=24; K=8; snr=10**(-2/10); drops=180; fades_per_drop=4
schemes={'Nearest AP':1,'UC-4':4,'UC-8':8,'Cell-free':M}
records={k:[] for k in schemes}
for _ in range(drops):
    aps=rng.uniform(0,1,(M,2)); users=rng.uniform(0,1,(K,2))
    beta=large_scale_fading(aps,users,pathloss_exp=3.0,min_distance=.05,shadow_std_db=3.0,rng=rng)
    masks={name:user_centric_mask(beta,L) for name,L in schemes.items()}
    for _ in range(fades_per_drop):
        H=sample_cell_free_channel(beta,rng)
        for name,m in masks.items():
            W=clustered_mrt_precoder(H,m)
            r=cell_free_user_rates(H,W,snr)
            records[name].append((r.mean(),np.quantile(r,.05),jain_fairness(r),cluster_link_count(m)))
rows=[]
for name,v in records.items():
    a=np.asarray(v)
    rows.append(dict(scheme=name,mean_user_rate=a[:,0].mean(),mean_5pct_user_rate=a[:,1].mean(),mean_jain=a[:,2].mean(),mean_ap_user_links=a[:,3].mean()))
df=pd.DataFrame(rows); df.to_csv(DATA/'cell_free_user_centric.csv',index=False)
fig,ax=plt.subplots(figsize=(7,4.5)); x=np.arange(len(df)); w=.36
ax.bar(x-w/2,df.mean_user_rate,w,label='Mean user rate'); ax.bar(x+w/2,df.mean_5pct_user_rate,w,label='5%-tile user rate')
ax.set_xticks(x,df.scheme); ax.set_ylabel('Spectral efficiency (bit/s/Hz)'); ax.grid(True,axis='y',alpha=.25); ax.legend(); fig.tight_layout(); fig.savefig(FIG/'cell_free_user_centric_rates.png',dpi=180); plt.close(fig)
fig,ax=plt.subplots(figsize=(6.6,4.5)); ax.plot(df.mean_ap_user_links,df.mean_5pct_user_rate,marker='o')
for _,r in df.iterrows(): ax.annotate(r.scheme,(r.mean_ap_user_links,r.mean_5pct_user_rate),xytext=(4,4),textcoords='offset points')
ax.set_xlabel('Average AP-user service links'); ax.set_ylabel('Mean 5%-tile user rate (bit/s/Hz)'); ax.grid(True,alpha=.25); fig.tight_layout(); fig.savefig(FIG/'cell_free_fronthaul_tradeoff.png',dpi=180); plt.close(fig)
print(df.to_string(index=False))
