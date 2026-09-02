from pathlib import Path
import numpy as np, matplotlib.pyplot as plt
from commlab.scheduling.network_slicing import simulate_embb_urllc_slicing
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'results'/'data'; FIG=ROOT/'results'/'figures'; OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rates=np.linspace(.1,2.1,9); rows=[]
for i,lam in enumerate(rates):
    for pol in ['reserved','adaptive_reserve','preemptive']:
        o=simulate_embb_urllc_slicing(6000,24,float(lam),3,2,.995,pol,fixed_reserved_prbs=6,seed=1950+i)
        rows.append((lam,pol,o['embb_throughput_bits_per_minislot'],o['urllc_deadline_miss_rate'],o['wasted_reserved_fraction'],o['mean_urllc_delay']))
with open(OUT/'embb_urllc_slicing.csv','w') as f:
    f.write('arrival_rate,policy,embb_throughput,urllc_deadline_miss,wasted_reserved,mean_urllc_delay\n'); [f.write(','.join(map(str,r))+'\n') for r in rows]
fig,ax=plt.subplots(figsize=(7,4.5))
for p in ['reserved','adaptive_reserve','preemptive']:
    rr=[r for r in rows if r[1]==p]; ax.plot([r[0] for r in rr],[r[2] for r in rr],'o-',label=p)
ax.set(xlabel='URLLC arrivals / mini-slot',ylabel='eMBB payload proxy (bit/mini-slot)',title='eMBB–URLLC Coexistence: Throughput Cost'); ax.grid(alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(FIG/'slicing_embb_throughput.png',dpi=180); plt.close(fig)
fig,ax=plt.subplots(figsize=(7,4.5))
for p in ['reserved','adaptive_reserve','preemptive']:
    rr=[r for r in rows if r[1]==p]; ax.semilogy([r[0] for r in rr],np.maximum([r[3] for r in rr],1e-5),'o-',label=p)
ax.set(xlabel='URLLC arrivals / mini-slot',ylabel='URLLC deadline-miss rate',title='eMBB–URLLC Coexistence: Deadline Reliability'); ax.grid(alpha=.3,which='both'); ax.legend(); fig.tight_layout(); fig.savefig(FIG/'slicing_urllc_deadline.png',dpi=180); plt.close(fig)
print(rows[-9:])
