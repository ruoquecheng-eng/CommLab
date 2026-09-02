from pathlib import Path
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from commlab.sensing.queue_control import simulate_queue_aware_isac_control, simulate_predictive_queue_aware_isac_control

ROOT=Path('results'); OUT=ROOT/'data'; FIG=ROOT/'figures'; OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(1730); S,U=120,2
proc=np.r_[np.full(30,.08),np.linspace(.08,1.1,25),np.full(25,1.1),np.linspace(1.1,.1,20),np.full(20,.1)]
base=np.clip(rng.normal(180,28,(S,U)),80,260)
rows=[]; traces={}
for load in [55,95]:
    arrivals=np.maximum(0,rng.poisson(load,(S,U))).astype(float)
    configs=[
        ('tracking-only', lambda: simulate_queue_aware_isac_control(proc,arrivals,base,.5,[8,16,32],[0,.03,.08,.15],.16,sensing_value_weight=1500,queue_aware=False)),
        ('queue-aware', lambda: simulate_queue_aware_isac_control(proc,arrivals,base,.5,[8,16,32],[0,.03,.08,.15],.16,sensing_value_weight=1500,queue_aware=True)),
        ('predictive-queue', lambda: simulate_predictive_queue_aware_isac_control(proc,arrivals,base,.5,[8,16,32],[0,.03,.08,.15],.16,sensing_value_weight=1500,lookahead_weight=.75)),
    ]
    for name,fn in configs:
        o=fn(); key=f"{name}_{load}"; traces[key]=o
        rows.append({'arrival_mean_bits':load,'controller':name,
                     'delivered_bits':o['total_delivered_bits'],'mean_sensing':o['mean_sensing_fraction'],
                     'mean_posterior_std_deg':o['mean_posterior_std_deg'],'mean_backlog_bits':o['mean_backlog_bits'],
                     'final_backlog_bits':o['final_backlog_bits']})
df=pd.DataFrame(rows); df.to_csv(OUT/'queue_aware_isac.csv',index=False)
plt.figure(figsize=(6.5,4.2))
for p,g in df.groupby('controller'):
    plt.plot(g.arrival_mean_bits,g.mean_backlog_bits,marker='o',label=p.title())
plt.xlabel('Mean Arrival per User (bit/slot)'); plt.ylabel('Mean Total Backlog (bits)'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout()
plt.savefig(FIG/'queue_aware_isac_backlog.png',dpi=180); plt.close()
# High-load sensing trace
plt.figure(figsize=(7.0,4.0))
for key,label in [('tracking-only_95','Tracking-only'),('queue-aware_95','Queue-aware'),('predictive-queue_95','Predictive queue')]:
    f=[r['sensing_fraction'] for r in traces[key]['rows']]; plt.plot(f,label=label)
plt.xlabel('Slot'); plt.ylabel('Sensing Fraction'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout()
plt.savefig(FIG/'queue_aware_isac_sensing_trace.png',dpi=180); plt.close()
print(df.to_string(index=False))
