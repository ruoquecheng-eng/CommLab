from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt
from commlab.computation import simulate_channel_adaptive_depth
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'results'/'data'; FIG=ROOT/'results'/'figures'; DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rows=[]
for snr in [-4,-2,0,2,4,6,10]:
    for p in ['fixed_light','fixed_deep','adaptive']:
        rr=[simulate_channel_adaptive_depth(n_tasks=2400,policy=p,mean_snr_db=snr,latency_budget_ms=3.0,seed=s) for s in range(4)]
        rows.append([snr,p,np.mean([x['on_time_accuracy'] for x in rr]),np.mean([x['deadline_miss_rate'] for x in rr]),np.mean([x['mean_feature_bits'] for x in rr]),np.mean([x['mean_model_depth'] for x in rr]),np.mean([x['mean_latency_ms'] for x in rr])])
with (DATA/'v31_adaptive_depth.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['mean_snr_db','policy','on_time_accuracy','deadline_miss_rate','mean_feature_bits','mean_model_depth','mean_latency_ms']); w.writerows(rows)
plt.figure(figsize=(7.2,4.7))
for p in ['fixed_light','fixed_deep','adaptive']:
    r=[x for x in rows if x[1]==p]; plt.plot([x[0] for x in r],[100*x[2] for x in r],marker='o',label=p)
plt.xlabel('Mean feature-link SNR (dB)'); plt.ylabel('On-time task accuracy (%)'); plt.title('Channel-adaptive feature precision and model depth'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v31_adaptive_depth_accuracy.png',dpi=170); plt.close()
plt.figure(figsize=(7.2,4.7))
r=[x for x in rows if x[1]=='adaptive']; plt.plot([x[0] for x in r],[x[4] for x in r],marker='o',label='feature bits'); plt.plot([x[0] for x in r],[x[5] for x in r],marker='s',label='model depth')
plt.xlabel('Mean feature-link SNR (dB)'); plt.ylabel('Adaptive operating point'); plt.title('The runtime policy shifts radio precision and compute depth together'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v31_adaptive_depth_actions.png',dpi=170); plt.close()
print('wrote v31 adaptive depth')
