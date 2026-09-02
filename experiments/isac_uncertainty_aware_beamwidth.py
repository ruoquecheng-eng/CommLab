from pathlib import Path
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from commlab.sensing import expected_ula_rate_under_angle_uncertainty, select_robust_ula_aperture
ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results/figures'; DATA=ROOT/'results/data'; FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
stds=np.array([.2,.5,1,2,3,4,6,8,10],float); candidates=[8,16,32,64]; snr_per_element=10**(-2/10)
rows=[]
for s in stds:
    best,vals=select_robust_ula_aperture(s,candidates,snr_per_element)
    for n in candidates: rows.append(dict(angle_std_deg=s,elements=n,expected_rate=vals[n],selected=(n==best)))
df=pd.DataFrame(rows); df.to_csv(DATA/'isac_uncertainty_aware_beamwidth.csv',index=False)
fig,ax=plt.subplots(figsize=(7,4.5))
for n,g in df.groupby('elements'): ax.plot(g.angle_std_deg,g.expected_rate,marker='o',label=f'{n} elements')
ax.set_xlabel('Angle-estimate standard deviation (deg)'); ax.set_ylabel('Expected rate (bit/s/Hz)'); ax.grid(True,alpha=.25); ax.legend(); fig.tight_layout(); fig.savefig(FIG/'isac_uncertainty_beamwidth_rate.png',dpi=180); plt.close(fig)
best=df[df.selected][['angle_std_deg','elements','expected_rate']]
fig,ax=plt.subplots(figsize=(6.5,4.5)); ax.step(best.angle_std_deg,best.elements,where='mid'); ax.scatter(best.angle_std_deg,best.elements); ax.set_xlabel('Angle uncertainty (deg)'); ax.set_ylabel('Selected active ULA elements'); ax.set_yticks(candidates); ax.grid(True,alpha=.25); fig.tight_layout(); fig.savefig(FIG/'isac_uncertainty_selected_aperture.png',dpi=180); plt.close(fig)
print(best.to_string(index=False))
