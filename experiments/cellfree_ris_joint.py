from pathlib import Path
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from commlab.ris.cellfree import cellfree_ris_rates, coordinate_optimize_cellfree_ris
ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results/figures'; DATA=ROOT/'results/data'; FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(1402); K=4; M=10; N=24; snr=10**(7/10); trials=45
schemes=['Direct only','Random RIS','Sum-rate RIS','Min-rate RIS']; vals={s:[] for s in schemes}; histories=[]
for t in range(trials):
    D=.34*(rng.normal(size=(K,M))+1j*rng.normal(size=(K,M)))/np.sqrt(2)
    G=.22*(rng.normal(size=(N,M))+1j*rng.normal(size=(N,M)))/np.sqrt(2)
    R=.22*(rng.normal(size=(K,N))+1j*rng.normal(size=(K,N)))/np.sqrt(2)
    zero=np.zeros(N); rand=rng.uniform(-np.pi,np.pi,N)
    # Direct-only is represented by zero-amplitude-equivalent channels using zero G.
    rd=cellfree_ris_rates(D,np.zeros_like(G),R,zero,snr)
    rr=cellfree_ris_rates(D,G,R,rand,snr)
    ts,hs=coordinate_optimize_cellfree_ris(D,G,R,snr,bits=2,iterations=2,objective='sum_rate',initial_phases=rand)
    tm,hm=coordinate_optimize_cellfree_ris(D,G,R,snr,bits=2,iterations=2,objective='min_rate',initial_phases=rand)
    rs=cellfree_ris_rates(D,G,R,ts,snr); rm=cellfree_ris_rates(D,G,R,tm,snr)
    for name,r in [('Direct only',rd),('Random RIS',rr),('Sum-rate RIS',rs),('Min-rate RIS',rm)]: vals[name].append((r.sum(),r.min(),r.mean()))
    if t<12: histories.append((hs,hm))
rows=[]
for name,v in vals.items():
    a=np.asarray(v); rows.append(dict(scheme=name,mean_sum_rate=a[:,0].mean(),mean_min_user_rate=a[:,1].mean(),mean_user_rate=a[:,2].mean()))
df=pd.DataFrame(rows); df.to_csv(DATA/'cellfree_ris_joint.csv',index=False)
fig,ax=plt.subplots(figsize=(7.2,4.6)); x=np.arange(len(df)); w=.36
ax.bar(x-w/2,df.mean_sum_rate,w,label='Sum rate'); ax.bar(x+w/2,df.mean_min_user_rate,w,label='Minimum-user rate')
ax.set_xticks(x,df.scheme,rotation=15); ax.set_ylabel('Spectral efficiency (bit/s/Hz)'); ax.grid(True,axis='y',alpha=.25); ax.legend(); fig.tight_layout(); fig.savefig(FIG/'cellfree_ris_sum_min_tradeoff.png',dpi=180); plt.close(fig)
fig,ax=plt.subplots(figsize=(6.5,4.4))
for hs,hm in histories:
    ax.plot(range(len(hs)),hs,alpha=.25)
ax.set_xlabel('Coordinate sweeps'); ax.set_ylabel('Sum-rate objective'); ax.grid(True,alpha=.25); fig.tight_layout(); fig.savefig(FIG/'cellfree_ris_convergence.png',dpi=180); plt.close(fig)
print(df.to_string(index=False))
