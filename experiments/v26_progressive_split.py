from pathlib import Path
import csv,numpy as np,matplotlib.pyplot as plt
from commlab.computation import simulate_progressive_split_inference
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'results/data'; F=ROOT/'results/figures'; D.mkdir(parents=True,exist_ok=True); F.mkdir(parents=True,exist_ok=True)
rows=[]; policies=['local','full','confidence','adaptive']
for snr in [-2,2,6,10,14]:
    for p in policies:
        vals=[simulate_progressive_split_inference(mean_snr_db=snr,policy=p,seed=2620+r) for r in range(12)]
        rows.append((snr,p,*[np.mean([v[k] for v in vals]) for k in ['accuracy','on_time_accuracy','mean_channel_uses','mean_latency_ms','deadline_miss_rate','mean_energy_mj']]))
with open(D/'v26_progressive_split.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['mean_snr_db','policy','accuracy','on_time_accuracy','mean_channel_uses','mean_latency_ms','deadline_miss_rate','mean_energy_mj']); w.writerows(rows)
for idx,name,ylabel in [(3,'v26_progressive_split_ontime.png','On-time task accuracy'),(4,'v26_progressive_split_uses.png','Mean residual feature channel uses')]:
    for p in policies:
        rr=[r for r in rows if r[1]==p]; plt.plot([r[0] for r in rr],[r[idx] for r in rr],marker='o',label=p)
    plt.xlabel('Mean residual-link SNR (dB)'); plt.ylabel(ylabel); plt.legend(); plt.tight_layout(); plt.savefig(F/name,dpi=180); plt.close()
