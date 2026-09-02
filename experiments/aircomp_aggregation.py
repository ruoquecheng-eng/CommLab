from pathlib import Path
import numpy as np, matplotlib.pyplot as plt
from commlab.computation.aircomp import simulate_aircomp_mean_aggregation
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'results'/'data'; FIG=ROOT/'results'/'figures'; OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rows=[]
for i,snr in enumerate([0,5,10,15,20,25]):
    o=simulate_aircomp_mean_aggregation(20,24,snr,350,.35,seed=1910+i)
    rows.append((snr,o['orthogonal_mse'],o['full_inversion_mse'],o['truncated_inversion_mse'],o['orthogonal_median_mse'],o['full_inversion_median_mse'],o['truncated_inversion_median_mse'],o['full_inversion_p90_mse'],o['mean_active_fraction']))
with open(OUT/'aircomp_aggregation.csv','w') as f:
    f.write('snr_db,orthogonal_mean_mse,full_mean_mse,truncated_mean_mse,orthogonal_median_mse,full_median_mse,truncated_median_mse,full_p90_mse,active_fraction\n'); [f.write(','.join(map(str,r))+'\n') for r in rows]
fig,ax=plt.subplots(figsize=(7,4.5));
ax.semilogy([r[0] for r in rows],[r[4] for r in rows],'o-',label='Orthogonal median (20 uses)'); ax.semilogy([r[0] for r in rows],[r[5] for r in rows],'o-',label='Full inversion median (1 use)'); ax.semilogy([r[0] for r in rows],[r[6] for r in rows],'o-',label='Truncated median (1 use)');
ax.set(xlabel='SNR (dB)',ylabel='Mean-aggregation MSE',title='Over-the-Air Computation: MSE vs Channel Uses'); ax.grid(alpha=.3,which='both'); ax.legend(); fig.tight_layout(); fig.savefig(FIG/'aircomp_mse_snr.png',dpi=180); plt.close(fig)
ths=np.linspace(.12,.85,9); tr=[]
for i,th in enumerate(ths):
    o=simulate_aircomp_mean_aggregation(20,24,12,400,float(th),seed=1930+i); tr.append((th,o['truncated_inversion_mse'],o['mean_active_fraction']))
with open(OUT/'aircomp_threshold_tradeoff.csv','w') as f:
    f.write('threshold,truncated_mse,active_fraction\n'); [f.write(','.join(map(str,r))+'\n') for r in tr]
fig,ax1=plt.subplots(figsize=(7,4.5)); ax1.semilogy([r[0] for r in tr],[r[1] for r in tr],'o-'); ax1.set_xlabel('Channel-inversion threshold |h|'); ax1.set_ylabel('Aggregation MSE'); ax1.grid(alpha=.3); ax2=ax1.twinx(); ax2.plot([r[0] for r in tr],[r[2] for r in tr],'s--'); ax2.set_ylabel('Active-device fraction'); ax1.set_title('AirComp: Deep-Fade Suppression vs Participant Dropout'); fig.tight_layout(); fig.savefig(FIG/'aircomp_threshold_tradeoff.png',dpi=180); plt.close(fig)
print(rows); print(tr)
