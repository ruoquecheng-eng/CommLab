from pathlib import Path
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from commlab.sensing import ula_steering_vector, estimate_source_count_mdl, music_angle_spectrum, bartlett_covariance_spectrum
ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results/figures'; DATA=ROOT/'results/data'; FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(1203); m=10; true_angles=[-22,2,27]; A=np.column_stack([ula_steering_vector(a,m) for a in true_angles])
rows=[]
for nsnap in [30,60,120,300]:
  for snr_db in [-10,-5,0,5,10]:
    ok=0; est=[]
    sig=10**(snr_db/10)
    for _ in range(120):
      S=np.sqrt(sig)*(rng.normal(size=(3,nsnap))+1j*rng.normal(size=(3,nsnap)))/np.sqrt(2)
      N=(rng.normal(size=(m,nsnap))+1j*rng.normal(size=(m,nsnap)))/np.sqrt(2)
      X=A@S+N; k,_=estimate_source_count_mdl(X,max_sources=6); est.append(k); ok+=k==3
    rows.append(dict(snapshots=nsnap,snr_db=snr_db,accuracy=ok/120,mean_estimated_sources=np.mean(est)))
df=pd.DataFrame(rows); df.to_csv(DATA/'music_mdl_model_order.csv',index=False)
fig,ax=plt.subplots(figsize=(7,4.5))
for ns,g in df.groupby('snapshots'): ax.plot(g.snr_db,g.accuracy,marker='o',label=f'{ns} snapshots')
ax.set_xlabel('Per-source SNR (dB)'); ax.set_ylabel('P(MDL estimates 3 sources)'); ax.set_ylim(-.03,1.03); ax.grid(True,alpha=.25); ax.legend(); fig.tight_layout(); fig.savefig(FIG/'music_mdl_source_count_accuracy.png',dpi=180); plt.close(fig)
# Close-angle example with estimated source count.
ns=180; sig=10**(3/10); close=[-8,0,9]; Ac=np.column_stack([ula_steering_vector(a,m) for a in close]); S=np.sqrt(sig)*(rng.normal(size=(3,ns))+1j*rng.normal(size=(3,ns)))/np.sqrt(2); X=Ac@S+(rng.normal(size=(m,ns))+1j*rng.normal(size=(m,ns)))/np.sqrt(2)
k,_=estimate_source_count_mdl(X,max_sources=6); grid=np.linspace(-30,30,1201); pm=music_angle_spectrum(X,max(k,1),grid); pb=bartlett_covariance_spectrum(X,grid); pm/=pm.max(); pb/=pb.max()
pd.DataFrame({'angle_deg':grid,'bartlett':pb,'music':pm}).to_csv(DATA/'music_mdl_close_angle_spectrum.csv',index=False)
fig,ax=plt.subplots(figsize=(7,4.5)); ax.plot(grid,pb,label='Bartlett'); ax.plot(grid,pm,label=f'MUSIC (MDL k={k})'); [ax.axvline(a,linestyle='--',alpha=.4) for a in close]; ax.set_xlabel('Angle (deg)'); ax.set_ylabel('Normalized spectrum'); ax.grid(True,alpha=.25); ax.legend(); fig.tight_layout(); fig.savefig(FIG/'music_mdl_close_angle_spectrum.png',dpi=180); plt.close(fig)
print(df[df.snr_db.isin([-5,0,5])].to_string(index=False)); print('close-angle MDL source count:',k)
