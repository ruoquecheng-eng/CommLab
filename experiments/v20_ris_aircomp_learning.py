from pathlib import Path
import csv,numpy as np,matplotlib.pyplot as plt
from commlab.computation import effective_ris_aircomp_channel,optimize_ris_aircomp,aircomp_noise_mse_from_channel,simulate_federated_aircomp
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'results'/'data'; F=ROOT/'results'/'figures'; D.mkdir(parents=True,exist_ok=True); F.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(2050); K,N=12,24
hd=.12*(rng.normal(size=K)+1j*rng.normal(size=K))/np.sqrt(2); dev=(rng.normal(size=(K,N))+1j*rng.normal(size=(K,N)))/np.sqrt(2*N); rb=(rng.normal(size=N)+1j*rng.normal(size=N))/np.sqrt(2*N)
phases={'random':np.exp(1j*2*np.pi*rng.random(N))}
for obj in ['sumgain','maxmin']: phases[obj]=optimize_ris_aircomp(hd,dev,rb,bits=2,sweeps=3,objective=obj)[0]
rows=[]; curves={}
for j,(name,p) in enumerate(phases.items()):
    h=effective_ris_aircomp_channel(hd,dev,rb,p); mse=aircomp_noise_mse_from_channel(h,8,vector_dim=24,n_trials=400,seed=2060+j)
    fl=simulate_federated_aircomp(n_clients=K,rounds=80,mode='full_inversion',snr_db=8,fixed_channel=h,seed=2070)
    curves[name]=fl['loss_history']; rows.append((name,np.min(np.abs(h)),np.sum(np.abs(h)**2),mse['median_mse'],fl['final_loss'],fl['parameter_error']))
with (D/'v20_ris_aircomp_learning.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['ris_objective','weakest_gain','sum_channel_power','aircomp_median_mse','fl_final_loss','fl_parameter_error']); w.writerows(rows)
fig,ax=plt.subplots(figsize=(7.2,4.6)); x=np.arange(len(rows)); ax.bar(x,[r[1] for r in rows]); ax.set_xticks(x,[r[0] for r in rows]); ax.set_ylabel('Weakest effective |h_k|'); ax.set_title('RIS Objective Matters for AirComp'); ax.grid(alpha=.25,axis='y'); fig.tight_layout(); fig.savefig(F/'v20_ris_aircomp_weakest_gain.png',dpi=180); plt.close(fig)
fig,ax=plt.subplots(figsize=(7.2,4.6));
for name,c in curves.items(): ax.semilogy(range(len(c)),c,label=name)
ax.set(xlabel='Federated round',ylabel='Global loss',title='RIS-Assisted AirComp-FL (8 dB, Fixed Fading)'); ax.grid(alpha=.3,which='both'); ax.legend(); fig.tight_layout(); fig.savefig(F/'v20_ris_aircomp_fl_convergence.png',dpi=180); plt.close(fig)
print(rows)
