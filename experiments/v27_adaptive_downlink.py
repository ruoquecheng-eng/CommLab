from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt
from commlab.computation import simulate_adaptive_differential_broadcast
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'results/data'; F=ROOT/'results/figures'; D.mkdir(parents=True,exist_ok=True); F.mkdir(parents=True,exist_ok=True)
rows=[]
for block in [0,3,5,7,9,11]:
    for pol in ['fixed','budgeted_age']:
        vals=[simulate_adaptive_differential_broadcast(policy=pol,fixed_keyframe_interval=5,age_threshold=24,target_downlink_size=.36,blockage_db=block,seed=2710+r) for r in range(24)]
        rows.append((block,pol,*[np.mean([v[k] for v in vals]) for k in ['mean_version_age','mean_model_mse','normalized_downlink_size_per_round','keyframes','packet_success_fraction']]))
with open(D/'v27_adaptive_downlink.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['blockage_db','policy','mean_version_age','mean_model_mse','normalized_size_per_round','mean_keyframes','packet_success_fraction']); w.writerows(rows)
for idx,name,ylabel in [(2,'v27_adaptive_downlink_age.png','Mean client model age (rounds)'),(3,'v27_adaptive_downlink_mse.png','Mean client model MSE')]:
    for p in ['fixed','budgeted_age']:
        rr=[r for r in rows if r[1]==p]; plt.plot([r[0] for r in rr],[r[idx] for r in rr],marker='o',label=p)
    plt.xlabel('Common blockage penalty (dB)'); plt.ylabel(ylabel); plt.legend(); plt.tight_layout(); plt.savefig(F/name,dpi=180); plt.close()
