from pathlib import Path
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from commlab.scheduling.cross_layer import simulate_cross_layer_link
ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results/figures'; DATA=ROOT/'results/data'; FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(1403); S=5000; U=4
means=np.array([-1.0,2.0,5.0,8.0]); true=np.zeros((S,U)); true[0]=means+rng.normal(0,1,U)
for t in range(1,S): true[t]=means+.94*(true[t-1]-means)+rng.normal(0,.75,U)
est=true+2.0+rng.normal(0,1.1,(S,U))
arr=(rng.random((S,U))<np.array([.05,.07,.09,.11])[None,:]).astype(int)
base=dict(true_snr_db=true,estimated_snr_db=est,arrivals=arr,thresholds_db=[-4,0,4,8,12],efficiencies=[.5,1,2,3,4],payload_bits=12000,seed=1404)
configs=[
 ('Open-loop / no HARQ',dict(policy='pf',use_olla=False,use_harq=False,max_attempts=1)),
 ('HARQ only',dict(policy='pf',use_olla=False,use_harq=True,max_attempts=4)),
 ('OLLA + HARQ',dict(policy='pf',use_olla=True,use_harq=True,max_attempts=4)),
 ('Delay-PF + OLLA + HARQ',dict(policy='delay_pf',use_olla=True,use_harq=True,max_attempts=4)),
]
rows=[]; traces={}
for name,opt in configs:
    r=simulate_cross_layer_link(**base,**opt)
    arrivals_total=int(arr.sum())
    rows.append(dict(scheme=name,goodput_kbit_per_slot=r['goodput_bits_per_slot']/1000,nack_rate=r['nack_rate'],p95_delay_slots=r['p95_delay_slots'],mean_delay_slots=r['mean_delay_slots'],dropped_packets=r['dropped_packets'],pending_packets=r['pending_packets'],delivery_fraction=r['completed_packets']/max(arrivals_total,1)))
    traces[name]=r['backlog_packets'].sum(axis=1)
df=pd.DataFrame(rows); df.to_csv(DATA/'cross_layer_olla_harq_queue.csv',index=False)
fig,ax=plt.subplots(figsize=(7.4,4.6)); x=np.arange(len(df)); ax.bar(x,df.goodput_kbit_per_slot); ax.set_xticks(x,df.scheme,rotation=18); ax.set_ylabel('Goodput (kbit/slot)'); ax.grid(True,axis='y',alpha=.25); fig.tight_layout(); fig.savefig(FIG/'cross_layer_goodput.png',dpi=180); plt.close(fig)
fig,ax=plt.subplots(figsize=(7.4,4.6));
for name,b in traces.items(): ax.plot(np.arange(S),b,label=name,alpha=.8)
ax.set_xlabel('Slot'); ax.set_ylabel('Queued packets'); ax.grid(True,alpha=.25); ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(FIG/'cross_layer_backlog.png',dpi=180); plt.close(fig)
fig,ax=plt.subplots(figsize=(7.2,4.5)); ax.scatter(df.p95_delay_slots,df.goodput_kbit_per_slot)
for _,r in df.iterrows(): ax.annotate(r.scheme,(r.p95_delay_slots,r.goodput_kbit_per_slot),xytext=(4,4),textcoords='offset points',fontsize=8)
ax.set_xlabel('P95 packet delay (slots)'); ax.set_ylabel('Goodput (kbit/slot)'); ax.grid(True,alpha=.25); fig.tight_layout(); fig.savefig(FIG/'cross_layer_delay_goodput_tradeoff.png',dpi=180); plt.close(fig)
print(df.to_string(index=False))
