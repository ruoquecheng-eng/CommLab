from pathlib import Path
import numpy as np,csv,matplotlib.pyplot as plt
from commlab.computation import simulate_private_hardware_aircomp
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'results/data'; F=ROOT/'results/figures'; D.mkdir(parents=True,exist_ok=True); F.mkdir(parents=True,exist_ok=True)
rows=[]
for priv in [0,.1,.25,.5,.75]:
  for bits in [3,4,6,8]:
    o=simulate_private_hardware_aircomp(privacy_noise_multiplier=priv,adc_bits=bits,pa_saturation=1.5,trials=180,seed=2520)
    rows.append((priv,bits,o['median_mse'],o['p90_mse'],o['mean_pa_clip_fraction']))
with open(D/'v25_private_hardware_aircomp.csv','w',newline='') as f:
  w=csv.writer(f); w.writerow(['privacy_noise','adc_bits','median_mse','p90_mse','pa_clip_fraction']); w.writerows(rows)
for bits in [3,4,6,8]:
 q=[r for r in rows if r[1]==bits]; plt.plot([r[0] for r in q],[r[2] for r in q],marker='o',label=f'{bits}-bit')
plt.yscale('log'); plt.xlabel('Privacy noise multiplier'); plt.ylabel('Median aggregation MSE'); plt.legend(); plt.tight_layout(); plt.savefig(F/'v25_private_hardware_aircomp_mse.png',dpi=180); plt.close()
