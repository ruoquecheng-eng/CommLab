from pathlib import Path
import csv,numpy as np,matplotlib.pyplot as plt
from commlab.computation import simulate_differential_model_broadcast
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'results/data'; F=ROOT/'results/figures'; D.mkdir(parents=True,exist_ok=True); F.mkdir(parents=True,exist_ok=True)
rows=[]; schemes=['full','chained_delta','anchored_delta']
for k in [2,4,8,12,20,30]:
    for s in schemes:
        vals=[simulate_differential_model_broadcast(scheme=s,keyframe_interval=k,seed=2630+r) for r in range(30)]
        rows.append((k,s,*[np.mean([v[q] for v in vals]) for q in ['mean_model_mse','mean_version_age','normalized_downlink_size_per_round','packet_success_fraction']]))
with open(D/'v26_downlink_differential.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['keyframe_interval','scheme','mean_model_mse','mean_version_age','normalized_size_per_round','packet_success_fraction']); w.writerows(rows)
for idx,name,ylabel in [(2,'v26_downlink_differential_mse.png','Mean client model MSE'),(4,'v26_downlink_differential_overhead.png','Normalized downlink size / round')]:
    for s in schemes:
        rr=[r for r in rows if r[1]==s]; plt.plot([r[0] for r in rr],[r[idx] for r in rr],marker='o',label=s)
    plt.xlabel('Full-keyframe interval (rounds)'); plt.ylabel(ylabel); plt.legend(); plt.tight_layout(); plt.savefig(F/name,dpi=180); plt.close()
