from pathlib import Path
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from commlab.ris import ris_mu_sum_rate, coordinate_optimize_ris

ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results/figures'; DATA=ROOT/'results/data'; FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(1302); K=3; Nt=4; N=16; snr=10**(10/10); trials=70
records=[]; conv=[]
for t in range(trials):
    D=.22*(rng.normal(size=(K,Nt))+1j*rng.normal(size=(K,Nt)))/np.sqrt(2)
    G=(rng.normal(size=(N,Nt))+1j*rng.normal(size=(N,Nt)))/np.sqrt(2*N)
    R=(rng.normal(size=(K,N))+1j*rng.normal(size=(K,N)))/np.sqrt(2*N)
    init=rng.uniform(-np.pi,np.pi,N)
    records.append(('Random',ris_mu_sum_rate(D,G,R,init,snr)))
    for bits in [1,2,3]:
        _,hist=coordinate_optimize_ris(D,G,R,snr,bits=bits,iterations=2,initial_phases=init)
        records.append((f'{bits}-bit coord.',hist[-1]))
        for i,v in enumerate(hist): conv.append((t,bits,i,v))
df=pd.DataFrame(records,columns=['scheme','sum_rate']); summary=df.groupby('scheme',as_index=False).agg(mean_sum_rate=('sum_rate','mean'),p10_sum_rate=('sum_rate',lambda x:np.quantile(x,.1)))
summary.to_csv(DATA/'ris_multiuser_coordinate.csv',index=False)
pd.DataFrame(conv,columns=['trial','bits','iteration','sum_rate']).to_csv(DATA/'ris_coordinate_convergence.csv',index=False)
fig,ax=plt.subplots(figsize=(7,4.5)); order=['Random','1-bit coord.','2-bit coord.','3-bit coord.']; g=summary.set_index('scheme').loc[order]
ax.bar(order,g.mean_sum_rate); ax.set_ylabel('Mean 3-user ZF sum rate (bit/s/Hz)'); ax.grid(True,axis='y',alpha=.25); fig.tight_layout(); fig.savefig(FIG/'ris_multiuser_coordinate_rate.png',dpi=180); plt.close(fig)
cdf=pd.DataFrame(conv,columns=['trial','bits','iteration','sum_rate']).groupby(['bits','iteration'],as_index=False).sum_rate.mean()
fig,ax=plt.subplots(figsize=(6.5,4.5))
for b,gg in cdf.groupby('bits'): ax.plot(gg.iteration,gg.sum_rate,marker='o',label=f'{b}-bit')
ax.set_xlabel('Coordinate-ascent sweep'); ax.set_ylabel('Mean sum rate (bit/s/Hz)'); ax.set_xticks([0,1,2]); ax.grid(True,alpha=.25); ax.legend(); fig.tight_layout(); fig.savefig(FIG/'ris_coordinate_convergence.png',dpi=180); plt.close(fig)
print(summary.to_string(index=False))
