from pathlib import Path
import numpy as np,csv,matplotlib.pyplot as plt
from commlab.computation import simulate_layered_model_multicast
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'results/data'; F=ROOT/'results/figures'; D.mkdir(parents=True,exist_ok=True); F.mkdir(parents=True,exist_ok=True)
rows=[]
for std in [1,3,5,7,9,11]:
 vals=[simulate_layered_model_multicast(snr_std_db=std,seed=2540+r) for r in range(30)]
 rows.append((std,*[np.mean([v[k] for v in vals]) for k in ['common_time','layered_time','unicast_time','layered_mean_utility']]))
with open(D/'v25_model_multicast.csv','w',newline='') as f:
 w=csv.writer(f); w.writerow(['snr_std_db','common_time','layered_time','unicast_time','layered_mean_utility']); w.writerows(rows)
plt.plot([r[0] for r in rows],[r[1] for r in rows],marker='o',label='common multicast'); plt.plot([r[0] for r in rows],[r[2] for r in rows],marker='o',label='layered multicast'); plt.plot([r[0] for r in rows],[r[3] for r in rows],marker='o',label='serial unicast')
plt.yscale('log'); plt.xlabel('Client SNR standard deviation (dB)'); plt.ylabel('Normalized delivery time'); plt.legend(); plt.tight_layout(); plt.savefig(F/'v25_model_multicast_time.png',dpi=180); plt.close()
