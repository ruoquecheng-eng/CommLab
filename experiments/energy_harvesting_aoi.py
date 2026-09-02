from pathlib import Path
import numpy as np, matplotlib.pyplot as plt
from commlab.scheduling.energy_aoi import simulate_energy_harvesting_aoi
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'results'/'data'; FIG=ROOT/'results'/'figures'; OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(1970); S,U=3500,5; means=np.array([-1.,1.,3.,5.,7.]); T=rng.normal(means,2.5,(S,U)); base=np.array([.65,.8,1.,1.15,1.3]); scales=np.linspace(.08,.65,8); rows=[]
for i,s in enumerate(scales):
    hp=np.clip(s*base,0,.95)
    for pol in ['max_age','max_snr','age_reliability','energy_aware']:
        o=simulate_energy_harvesting_aoi(T,hp,3,90,1.0,pol,seed=1980+i)
        rows.append((s,pol,o['mean_aoi'],o['p95_aoi'],o['delivery_rate_per_slot'],o['energy_outage_fraction']))
with open(OUT/'energy_harvesting_aoi.csv','w') as f:
    f.write('harvest_scale,policy,mean_aoi,p95_aoi,delivery_rate,energy_outage\n'); [f.write(','.join(map(str,r))+'\n') for r in rows]
fig,ax=plt.subplots(figsize=(7,4.5))
for p in ['max_age','max_snr','age_reliability','energy_aware']:
    rr=[r for r in rows if r[1]==p]; ax.semilogy([r[0] for r in rr],[r[2] for r in rr],'o-',label=p)
ax.set(xlabel='Energy-harvest probability scale',ylabel='Mean AoI (slots)',title='Energy-Harvesting Status Updates'); ax.grid(alpha=.3,which='both'); ax.legend(); fig.tight_layout(); fig.savefig(FIG/'energy_aoi_mean.png',dpi=180); plt.close(fig)
fig,ax=plt.subplots(figsize=(7,4.5))
for p in ['max_age','max_snr','age_reliability','energy_aware']:
    rr=[r for r in rows if r[1]==p]; ax.plot([r[0] for r in rr],[r[4] for r in rr],'o-',label=p)
ax.set(xlabel='Energy-harvest probability scale',ylabel='Successful fresh updates / slot',title='Freshness vs Energy Availability'); ax.grid(alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(FIG/'energy_aoi_delivery.png',dpi=180); plt.close(fig)
print(rows[-8:])
