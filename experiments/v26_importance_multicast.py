from pathlib import Path
import csv,numpy as np,matplotlib.pyplot as plt
from commlab.computation import simulate_importance_aware_model_multicast
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'results/data'; F=ROOT/'results/figures'; D.mkdir(parents=True,exist_ok=True); F.mkdir(parents=True,exist_ok=True)
rows=[]
for c in [0,.3,.6,.9]:
    vals=[simulate_importance_aware_model_multicast(importance_anticorrelation=c,seed=2650+r) for r in range(80)]
    rows.append((c,*[np.mean([v[k] for v in vals]) for k in ['importance_snr_correlation','snr_half_weighted_utility','importance_weighted_utility','snr_half_time','importance_time','importance_enhanced_fraction']]))
with open(D/'v26_importance_multicast.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['importance_anticorrelation','empirical_importance_snr_corr','snr_half_weighted_utility','importance_weighted_utility','snr_half_time','importance_time','importance_enhanced_fraction']); w.writerows(rows)
plt.plot([r[0] for r in rows],[r[2] for r in rows],marker='o',label='SNR-half layered'); plt.plot([r[0] for r in rows],[r[3] for r in rows],marker='o',label='importance-aware')
plt.xlabel('Configured importance / SNR anticorrelation'); plt.ylabel('Importance-weighted task utility'); plt.legend(); plt.tight_layout(); plt.savefig(F/'v26_importance_multicast_utility.png',dpi=180); plt.close()
plt.plot([r[0] for r in rows],[r[4] for r in rows],marker='o',label='SNR-half layered'); plt.plot([r[0] for r in rows],[r[5] for r in rows],marker='o',label='importance-aware')
plt.xlabel('Configured importance / SNR anticorrelation'); plt.ylabel('Normalized downlink time'); plt.legend(); plt.tight_layout(); plt.savefig(F/'v26_importance_multicast_time.png',dpi=180); plt.close()
