from pathlib import Path
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from commlab.scheduling.deadline_harq import simulate_deadline_fbl_harq

ROOT=Path('results'); OUT=ROOT/'data'; FIG=ROOT/'figures'; OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(1820); S,U=1200,4; base=np.array([-1.,1.,3.,5.])
true=np.empty((S,U)); true[0]=base+rng.normal(0,1,U)
for t in range(1,S): true[t]=.92*true[t-1]+.08*base+rng.normal(0,.6,U)
est=true+1.5+rng.normal(0,1.0,(S,U))
rows=[]
for load in [.08,.12,.16,.20]:
    arr_rng=np.random.default_rng(1822+int(load*100)); arrivals=(arr_rng.random((S,U))<load).astype(int)
    for policy in ['pf','edf','risk']:
        o=simulate_deadline_fbl_harq(true,est,arrivals,[-5,-1,3,7],[.5,1,1.8,2.6],deadline_slots=6,
                                     round_blocklength=80,mode='ir',policy=policy,use_olla=True,seed=1821)
        rows.append({'arrival_probability':load,'policy':policy,'arrivals':int(arrivals.sum()),
                     'goodput':o['goodput_bits_per_channel_use'],'deadline_miss_rate':o['deadline_miss_rate'],
                     'nack_rate':o['nack_rate'],'mean_delay':o['mean_delay_slots'],'p95_delay':o['p95_delay_slots'],
                     'deadline_drops':o['deadline_drops'],'maxround_drops':o['maxround_drops']})
df=pd.DataFrame(rows); df.to_csv(OUT/'deadline_harq_scheduling.csv',index=False)
plt.figure(figsize=(6.5,4.2))
for p,g in df.groupby('policy'):
    plt.plot(g.arrival_probability,100*g.deadline_miss_rate,marker='o',label=p)
plt.xlabel('Packet Arrival Probability / User / Slot'); plt.ylabel('Deadline Miss Rate (%)'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout()
plt.savefig(FIG/'deadline_harq_miss_rate.png',dpi=180); plt.close()
plt.figure(figsize=(6.5,4.2))
for p,g in df.groupby('policy'):
    plt.plot(g.arrival_probability,g.goodput,marker='o',label=p)
plt.xlabel('Packet Arrival Probability / User / Slot'); plt.ylabel('Goodput (payload bit/channel-use)'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout()
plt.savefig(FIG/'deadline_harq_goodput.png',dpi=180); plt.close()
print(df.to_string(index=False))
