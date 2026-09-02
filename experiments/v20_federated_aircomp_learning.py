from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt
from commlab.computation import simulate_federated_aircomp
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'results'/'data'; F=ROOT/'results'/'figures'; D.mkdir(parents=True,exist_ok=True); F.mkdir(parents=True,exist_ok=True)
modes=['ideal','orthogonal','full_inversion','truncated']; runs={}
for m in modes:
    runs[m]=simulate_federated_aircomp(rounds=80,mode=m,snr_db=10,inversion_threshold=.35,heterogeneity=.8,seed=2001)
with (D/'v20_federated_aircomp_convergence.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['round']+[f'{m}_loss' for m in modes])
    for r in range(81): w.writerow([r]+[runs[m]['loss_history'][r] for m in modes])
fig,ax=plt.subplots(figsize=(7.2,4.6))
for m in modes: ax.semilogy(range(81),runs[m]['loss_history'],label=m.replace('_',' '))
ax.set(xlabel='Federated round',ylabel='Global MSE objective',title='Federated Learning with Noisy Over-the-Air Gradient Aggregation (10 dB)'); ax.grid(alpha=.3,which='both'); ax.legend(); fig.tight_layout(); fig.savefig(F/'v20_federated_aircomp_convergence.png',dpi=180); plt.close(fig)
# Communication-normalized convergence excludes ideal (zero modeled channel uses).
fig,ax=plt.subplots(figsize=(7.2,4.6))
for m in ['orthogonal','full_inversion','truncated']:
    per=12 if m=='orthogonal' else 1
    ax.semilogy(np.arange(81)*per,runs[m]['loss_history'],label=m.replace('_',' '))
ax.set(xlabel='Cumulative channel uses',ylabel='Global MSE objective',title='Learning Progress per Communication Resource'); ax.grid(alpha=.3,which='both'); ax.legend(); fig.tight_layout(); fig.savefig(F/'v20_federated_aircomp_channel_uses.png',dpi=180); plt.close(fig)
ths=np.linspace(.1,1.0,10); rows=[]
for i,th in enumerate(ths):
    o=simulate_federated_aircomp(rounds=80,mode='truncated',snr_db=5,inversion_threshold=float(th),heterogeneity=1.0,seed=2020)
    rows.append((th,o['final_loss'],o['parameter_error'],o['mean_active_fraction'],o['mean_aggregation_mse']))
with (D/'v20_federated_aircomp_threshold.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['threshold','final_loss','parameter_error','active_fraction','aggregation_mse']); w.writerows(rows)
fig,ax1=plt.subplots(figsize=(7.2,4.6)); ax1.plot([r[0] for r in rows],[r[1] for r in rows],'o-'); ax1.set_xlabel('Truncated-inversion threshold |h|'); ax1.set_ylabel('Final global loss'); ax1.grid(alpha=.3); ax2=ax1.twinx(); ax2.plot([r[0] for r in rows],[r[3] for r in rows],'s--'); ax2.set_ylabel('Mean active-client fraction'); ax1.set_title('AirComp-FL: Deep-Fade Suppression vs Client Participation (5 dB)'); fig.tight_layout(); fig.savefig(F/'v20_federated_aircomp_threshold.png',dpi=180); plt.close(fig)
print({m:(runs[m]['final_loss'],runs[m]['channel_uses']) for m in modes}); print(rows)
