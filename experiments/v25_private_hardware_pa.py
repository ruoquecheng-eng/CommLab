from pathlib import Path
import csv, matplotlib.pyplot as plt
from commlab.computation import simulate_private_hardware_aircomp
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'results/data'; F=ROOT/'results/figures'; D.mkdir(parents=True,exist_ok=True); F.mkdir(parents=True,exist_ok=True)
rows=[]
for sat in [.45,.6,.8,1.0,1.5,2.5,4.0]:
 o=simulate_private_hardware_aircomp(privacy_noise_multiplier=.25,adc_bits=6,pa_saturation=sat,trials=200,seed=2521)
 rows.append((sat,o['median_mse'],o['p90_mse'],o['mean_pa_clip_fraction']))
with open(D/'v25_private_hardware_pa.csv','w',newline='') as f:
 w=csv.writer(f); w.writerow(['pa_saturation','median_mse','p90_mse','pa_clip_fraction']); w.writerows(rows)
fig,ax=plt.subplots(); ax.plot([r[0] for r in rows],[r[1] for r in rows],marker='o'); ax.set_yscale('log'); ax.set_xlabel('PA saturation'); ax.set_ylabel('Median aggregation MSE'); fig.tight_layout(); fig.savefig(F/'v25_private_hardware_pa.png',dpi=180); plt.close(fig)
