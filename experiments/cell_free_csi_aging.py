from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt
from commlab.mimo.cell_free import large_scale_fading,user_centric_mask,sample_cell_free_channel,clustered_mrt_precoder,per_user_rates
from commlab.mimo.fronthaul import quantize_complex_csi,fronthaul_csi_bits,gauss_markov_channel_step

ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'results/data'; FIG=ROOT/'results/figures'; DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rng0=np.random.default_rng(1505); M,K=24,8
ap=rng0.uniform(0,1,(M,2)); ue=rng0.uniform(.05,.95,(K,2)); beta=large_scale_fading(ap,ue,shadow_std_db=1.5,rng=rng0); mask=user_centric_mask(beta,8)
intervals=[1,2,4,8,16,32]; correlations=[.995,.97]; labels={.995:'slow',.97:'fast'}; bits=6; slots=900; snr=10.0
rows=[]
for corr in correlations:
    rng=np.random.default_rng(2000+int(corr*1000)); H=sample_cell_free_channel(beta,rng); traj=[]
    for t in range(slots):
        traj.append(H.copy()); H=gauss_markov_channel_step(H,beta,corr,rng)
    for interval in intervals:
        W=None; means=[]; edges=[]
        for t,H in enumerate(traj):
            if t%interval==0 or W is None:
                Hq=quantize_complex_csi(H,bits); W=clustered_mrt_precoder(Hq,mask=mask)
            r=per_user_rates(H,W,snr); means.append(r.mean()); edges.append(np.percentile(r,5))
        rows.append(dict(mobility=labels[corr],correlation=corr,update_interval=interval,
                         fronthaul_bits_per_slot=fronthaul_csi_bits(mask,bits)/interval,
                         mean_rate=np.mean(means),edge_rate=np.mean(edges)))
with open(DATA/'cell_free_csi_aging.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
fig,ax=plt.subplots()
for label in ['slow','fast']:
    rr=[x for x in rows if x['mobility']==label]; ax.plot([x['fronthaul_bits_per_slot'] for x in rr],[x['edge_rate'] for x in rr],marker='o',label=label)
ax.set_xscale('log'); ax.set_xlabel('CSI fronthaul bits / slot'); ax.set_ylabel('Mean 5%-tile rate'); ax.set_title('CSI freshness vs fronthaul under channel aging'); ax.grid(True,alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(FIG/'cell_free_csi_aging_edge_rate.png',dpi=180); plt.close(fig)
fig,ax=plt.subplots()
for label in ['slow','fast']:
    rr=[x for x in rows if x['mobility']==label]; ax.plot([x['update_interval'] for x in rr],[x['mean_rate'] for x in rr],marker='o',label=label)
ax.set_xscale('log',base=2); ax.set_xlabel('CSI update interval (slots)'); ax.set_ylabel('Mean user rate'); ax.set_title('Stale CSI degradation'); ax.grid(True,alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(FIG/'cell_free_csi_aging_mean_rate.png',dpi=180); plt.close(fig)
print(rows)
