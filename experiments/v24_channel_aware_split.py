from pathlib import Path
import csv, numpy as np
import matplotlib.pyplot as plt
from commlab.computation import simulate_channel_aware_split
OUT=Path('results/data'); FIG=Path('results/figures'); OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rows=[]
for deadline in [1.5,1.8,2.2,3.0]:
    for snr in [0,5,10,15]:
        for pol in ['static','channel_aware']:
            vals=[simulate_channel_aware_split(policy=pol,mean_snr_db=snr,deadline_ms=deadline,seed=2430+s) for s in range(16)]
            rows.append({'deadline_ms':deadline,'mean_snr_db':snr,'policy':pol,'accuracy':np.mean([v['accuracy'] for v in vals]),'on_time_accuracy':np.mean([v['on_time_accuracy'] for v in vals]),'channel_uses':np.mean([v['mean_channel_uses'] for v in vals]),'latency_ms':np.mean([v['mean_latency_ms'] for v in vals]),'deadline_miss':np.mean([v['deadline_miss_rate'] for v in vals])})
with open(OUT/'v24_channel_aware_split.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
plt.figure()
for pol in ['static','channel_aware']:
    rr=[r for r in rows if r['deadline_ms']==1.8 and r['policy']==pol]; plt.plot([r['mean_snr_db'] for r in rr],[r['on_time_accuracy'] for r in rr],marker='o',label=pol)
plt.xlabel('Mean offload SNR (dB)'); plt.ylabel('On-time task accuracy'); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v24_split_accuracy_snr.png',dpi=180); plt.close()
plt.figure()
for pol in ['static','channel_aware']:
    rr=[r for r in rows if r['mean_snr_db']==5 and r['policy']==pol]; plt.plot([r['deadline_ms'] for r in rr],[100*r['deadline_miss'] for r in rr],marker='o',label=pol)
plt.xlabel('Deadline (ms)'); plt.ylabel('Deadline miss (%)'); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v24_split_deadline.png',dpi=180); plt.close()
print([r for r in rows if r['deadline_ms']==1.8 and r['mean_snr_db']==5])
