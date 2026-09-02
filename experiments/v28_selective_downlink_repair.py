from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt
from commlab.computation import simulate_selective_downlink_repair

ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'results'/'data'; FIG=ROOT/'results'/'figures'; DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
policies=['periodic_keyframe','selective_age','selective_importance']; snrs=[-2,0,2,4,6,8,10,12]
rows=[]
for snr in snrs:
    for p in policies:
        rr=[simulate_selective_downlink_repair(policy=p,mean_snr_db=snr,importance_snr_anticorrelation=.9,seed=s) for s in range(16)]
        rows.append([snr,p,np.mean([x['weighted_version_age'] for x in rr]),np.mean([x['weighted_model_mse'] for x in rr]),np.mean([x['weighted_fresh_coverage'] for x in rr]),np.mean([x['normalized_downlink_size_per_round'] for x in rr]),np.mean([x['repair_transmissions'] for x in rr]),np.mean([x['keyframes'] for x in rr])])
with (DATA/'v28_selective_downlink_repair.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['mean_snr_db','policy','weighted_version_age','weighted_model_mse','weighted_fresh_coverage','normalized_downlink_size_per_round','repair_transmissions','keyframes']); w.writerows(rows)
for metric,idx,title,ylabel,name in [('age',2,'Selective repair has an operating region','Weighted model-version age','v28_selective_repair_age.png'),('mse',3,'Weighted synchronization error','Weighted model MSE','v28_selective_repair_mse.png')]:
    plt.figure(figsize=(7.2,4.6))
    for p in policies:
        r=[x for x in rows if x[1]==p]; plt.plot([x[0] for x in r],[x[idx] for x in r],marker='o',label=p)
    plt.xlabel('Mean client SNR (dB)'); plt.ylabel(ylabel); plt.title(title); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/name,dpi=170); plt.close()
print('wrote v28 selective downlink repair')
