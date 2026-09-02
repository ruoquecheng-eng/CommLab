from pathlib import Path
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from commlab.ris.event_triggered import simulate_event_triggered_cellfree_ris

ROOT=Path('results'); OUT=ROOT/'data'; FIG=ROOT/'figures'; OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(1840); K,M,N=3,4,8
D=.25*(rng.normal(size=(K,M))+1j*rng.normal(size=(K,M)))/np.sqrt(2)
G=.25*(rng.normal(size=(N,M))+1j*rng.normal(size=(N,M)))/np.sqrt(2)
R=.25*(rng.normal(size=(K,N))+1j*rng.normal(size=(K,N)))/np.sqrt(2)
seq=[]
for t in range(120):
    rho=.998 if t<40 or t>=80 else .92
    def step(x):
        z=(rng.normal(size=x.shape)+1j*rng.normal(size=x.shape))/np.sqrt(2); p=np.mean(np.abs(x)**2)
        return rho*x+np.sqrt(1-rho*rho)*np.sqrt(p)*z
    D=step(D); G=step(G); R=step(R); seq.append((D.copy(),G.copy(),R.copy()))
settings={
    'fixed4':dict(rate_drop_threshold=.99,min_interval=4,max_interval=4),
    'fixed8':dict(rate_drop_threshold=.99,min_interval=8,max_interval=8),
    'fixed16':dict(rate_drop_threshold=.99,min_interval=16,max_interval=16),
    'event_3pct':dict(rate_drop_threshold=.03,min_interval=2,max_interval=16),
    'event_8pct':dict(rate_drop_threshold=.08,min_interval=2,max_interval=16),
    'event_15pct':dict(rate_drop_threshold=.15,min_interval=2,max_interval=16),
}
rows=[]; traces={}
for name,kw in settings.items():
    o=simulate_event_triggered_cellfree_ris(seq,10,bits=2,seed=1841,**kw); traces[name]=o
    rows.append({'scheme':name,'mean_sum_rate':o['mean_sum_rate'],'edge_rate':o['edge_rate'],
                 'ideal_mean_sum_rate':o['ideal_mean_sum_rate'],'updates':o['n_updates'],
                 'control_bits_per_slot':o['control_bits_per_slot'],'mean_update_interval':o['mean_update_interval']})
df=pd.DataFrame(rows); df.to_csv(OUT/'event_triggered_ris.csv',index=False)
plt.figure(figsize=(6.5,4.3))
plt.scatter(df.control_bits_per_slot,df.mean_sum_rate)
for _,r in df.iterrows(): plt.annotate(r.scheme,(r.control_bits_per_slot,r.mean_sum_rate),xytext=(4,3),textcoords='offset points',fontsize=8)
plt.xlabel('RIS Control Overhead (bit/slot)'); plt.ylabel('Mean Sum Rate (bit/s/Hz)'); plt.grid(alpha=.25); plt.tight_layout()
plt.savefig(FIG/'event_triggered_ris_tradeoff.png',dpi=180); plt.close()
ex=traces['event_8pct']; sums=ex['rates'].sum(axis=1)
plt.figure(figsize=(7,4.2)); plt.plot(sums,label='Held/event-triggered RIS')
plt.plot(ex['ideal_rates'].sum(axis=1),alpha=.65,label='Per-slot ideal refresh')
for x in ex['updates']: plt.axvline(x,alpha=.08)
plt.axvspan(40,80,alpha=.08,label='Fast channel interval')
plt.xlabel('Slot'); plt.ylabel('Sum Rate (bit/s/Hz)'); plt.grid(alpha=.2); plt.legend(fontsize=8); plt.tight_layout()
plt.savefig(FIG/'event_triggered_ris_trace.png',dpi=180); plt.close()
print(df.to_string(index=False))
