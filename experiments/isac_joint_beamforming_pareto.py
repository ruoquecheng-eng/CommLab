from pathlib import Path
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from commlab.sensing.joint_beamforming import joint_isac_beamformer, communication_rate, sensing_gain, ula_steering
ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results/figures'; DATA=ROOT/'results/data'; FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
N=32; snr=10**(0/10); comm_angle=-20.0; weights=np.linspace(0,1,41); rows=[]
for sensing_angle in [-10.0,5.0,25.0,55.0]:
    h=np.sqrt(N)*ula_steering(N,comm_angle).conj()  # row channel convention
    for a in weights:
        w=joint_isac_beamformer(h,sensing_angle,a)
        rows.append(dict(sensing_angle_deg=sensing_angle,weight_comm=a,rate=communication_rate(h,w,snr),sensing_gain=sensing_gain(w,sensing_angle)))
df=pd.DataFrame(rows); df.to_csv(DATA/'isac_joint_beamforming_pareto.csv',index=False)
fig,ax=plt.subplots(figsize=(7,4.7))
for ang,g in df.groupby('sensing_angle_deg'):
    ax.plot(g.sensing_gain,g.rate,marker='.',label=f'{ang:g}° sensing')
ax.set_xlabel('Normalized sensing beam gain'); ax.set_ylabel('Communication rate (bit/s/Hz)'); ax.grid(True,alpha=.25); ax.legend(); fig.tight_layout(); fig.savefig(FIG/'isac_comm_sensing_pareto.png',dpi=180); plt.close(fig)
fig,ax=plt.subplots(figsize=(7,4.5))
sel=df[df.sensing_angle_deg==25.0]; ax.plot(sel.weight_comm,sel.rate,label='Comm rate'); ax.plot(sel.weight_comm,sel.sensing_gain,label='Sensing gain')
ax.set_xlabel('Communication weight'); ax.set_ylabel('Normalized metric'); ax.grid(True,alpha=.25); ax.legend(); fig.tight_layout(); fig.savefig(FIG/'isac_joint_weight_sweep.png',dpi=180); plt.close(fig)
print(df.groupby('sensing_angle_deg')[['rate','sensing_gain']].agg(['min','max']).to_string())
