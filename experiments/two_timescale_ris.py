from pathlib import Path
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from commlab.ris.cellfree_imperfect import age_complex_channel
from commlab.ris.two_timescale import simulate_two_timescale_cellfree_ris

ROOT=Path('results'); OUT=ROOT/'data'; FIG=ROOT/'figures'; OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(1720); K,M,N=3,5,6; T=60; rho=.985
D=.28*(rng.normal(size=(K,M))+1j*rng.normal(size=(K,M)))/np.sqrt(2)
G=.22*(rng.normal(size=(N,M))+1j*rng.normal(size=(N,M)))/np.sqrt(2)
R=.28*(rng.normal(size=(K,N))+1j*rng.normal(size=(K,N)))/np.sqrt(2)
seq=[]
for t in range(T):
    if t:
        D=age_complex_channel(D,rho,1,rng); G=age_complex_channel(G,rho,1,rng); R=age_complex_channel(R,rho,1,rng)
    seq.append((D.copy(),G.copy(),R.copy()))
rows=[]
for interval in [1,4,8,16]:
    o=simulate_two_timescale_cellfree_ris(seq,10.0,bits=2,ris_update_interval=interval,
                                          history_window=8,phase_noise_std_deg=3.0,seed=1721)
    for scheme in ['fast','two_timescale','stale','random']:
        rows.append({'update_interval':interval,'scheme':scheme,
                     'mean_sum_rate':o[scheme]['mean_sum_rate'],'edge_rate':o[scheme]['edge_rate'],
                     'control_bits_per_slot':o['ris_control_bits_per_slot_fast'] if scheme=='fast' else
                         (o['ris_control_bits_per_slot_two_timescale'] if scheme=='two_timescale' else 0.0)})
df=pd.DataFrame(rows); df.to_csv(OUT/'two_timescale_ris.csv',index=False)
plt.figure(figsize=(6.6,4.3))
for p,g in df.groupby('scheme'):
    plt.plot(g.update_interval,g.mean_sum_rate,marker='o',label=p.replace('_',' ').title())
plt.xlabel('RIS Update Interval (slots)'); plt.ylabel('Mean Sum Rate (bit/s/Hz)'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout()
plt.savefig(FIG/'two_timescale_ris_rate.png',dpi=180); plt.close()
# Only two-timescale control curve: rate against passive-control overhead.
g=df[df.scheme=='two_timescale'].sort_values('control_bits_per_slot')
plt.figure(figsize=(6.2,4.2)); plt.plot(g.control_bits_per_slot,g.mean_sum_rate,marker='o')
plt.xlabel('RIS Control Bits per Slot'); plt.ylabel('Mean Sum Rate (bit/s/Hz)'); plt.grid(alpha=.25); plt.tight_layout()
plt.savefig(FIG/'two_timescale_ris_overhead.png',dpi=180); plt.close()
print(df.to_string(index=False))
