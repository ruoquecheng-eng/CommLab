from pathlib import Path
import csv,numpy as np,matplotlib.pyplot as plt
from commlab.computation import simulate_two_timescale_ris_aircomp_fl
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'results'/'data'; F=ROOT/'results'/'figures'; D.mkdir(parents=True,exist_ok=True); F.mkdir(parents=True,exist_ok=True)
rows=[]
for rho in [.995,.98,.95]:
    for interval in [1,4,8,16,70]:
        vals=[]
        for rep in range(10):
            o=simulate_two_timescale_ris_aircomp_fl(n_clients=8,n_ris=10,rounds=70,update_interval=interval,rho=rho,bits=2,snr_db=12,learning_rate=.08,seed=2400+rep)
            vals.append([o['final_loss'],o['mean_weakest_gain'],o['p10_weakest_gain'],o['control_bits_per_round']])
        a=np.asarray(vals); rows.append((rho,interval,np.median(a[:,0]),a[:,0].mean(),a[:,1].mean(),a[:,2].mean(),a[:,3].mean()))
with (D/'v22_two_timescale_ris_fl.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['rho','update_interval','median_final_loss','mean_final_loss','mean_weakest_gain','mean_p10_weakest_gain','control_bits_per_round']); w.writerows(rows)
fig,ax=plt.subplots(figsize=(7.3,4.7))
for rho in [.995,.98,.95]:
    r=[x for x in rows if x[0]==rho]; ax.plot([x[1] for x in r],[x[2] for x in r],'o-',label=f'rho={rho}')
ax.set(xlabel='RIS update interval (FL rounds)',ylabel='Median final learning loss',title='Two-Timescale RIS-AirComp-FL: Mobility Shrinks the Slow-Control Window'); ax.grid(alpha=.3); ax.legend(); ax.set_xscale('log',base=2); fig.tight_layout(); fig.savefig(F/'v22_two_timescale_ris_fl_loss.png',dpi=180); plt.close(fig)
fig,ax=plt.subplots(figsize=(7.3,4.7))
for rho in [.995,.98,.95]:
    r=[x for x in rows if x[0]==rho]; ax.plot([x[6] for x in r],[x[4] for x in r],'o-',label=f'rho={rho}')
ax.set(xlabel='RIS control bits per FL round',ylabel='Mean weakest-device effective gain',title='RIS Control Overhead vs AirComp Bottleneck Gain'); ax.grid(alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(F/'v22_two_timescale_ris_fl_control.png',dpi=180); plt.close(fig)
print(rows)
