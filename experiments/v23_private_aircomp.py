from pathlib import Path
import csv, numpy as np
import matplotlib.pyplot as plt
from commlab.computation import simulate_private_aircomp_fl
OUT=Path('results/data'); FIG=Path('results/figures'); OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rows=[]
for snr in [5,10,15,20]:
    for sig in [0,.1,.25,.5,.75,1.0]:
        vals=[simulate_private_aircomp_fl(snr_db=snr,privacy_noise_multiplier=sig,rounds=75,clip_norm=.8,learning_rate=.09,seed=23200+s) for s in range(10)]
        rows.append({'snr_db':snr,'noise_multiplier':sig,'final_loss':np.median([v['final_loss'] for v in vals]),'aggregation_mse':np.median([v['mean_aggregation_mse'] for v in vals])})
with open(OUT/'v23_private_aircomp.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
for metric,ylabel,name in [('final_loss','Median final loss','v23_private_aircomp_loss.png'),('aggregation_mse','Median aggregation MSE','v23_private_aircomp_mse.png')]:
    plt.figure()
    for snr in [5,10,15,20]:
        rr=[r for r in rows if r['snr_db']==snr];plt.plot([r['noise_multiplier'] for r in rr],[r[metric] for r in rr],marker='o',label=f'{snr} dB')
    if metric=='aggregation_mse': plt.yscale('log')
    plt.xlabel('Client Gaussian noise multiplier');plt.ylabel(ylabel);plt.legend();plt.tight_layout();plt.savefig(FIG/name,dpi=180);plt.close()
print(rows)
