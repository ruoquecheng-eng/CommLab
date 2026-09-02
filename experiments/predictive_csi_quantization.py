from pathlib import Path
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from commlab.mimo.predictive_csi import predictive_csi_quantization_trace

ROOT=Path('results'); OUT=ROOT/'data'; FIG=ROOT/'figures'; OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(1740); beta=np.exp(rng.normal(0,1,(8,20)))
rows=[]
for rho in [.8,.95,.98,.995]:
    for bits in [2,3,4,6]:
        o=predictive_csi_quantization_trace(beta,rho,bits,n_slots=450,seed=1741)
        rows.append({'correlation':rho,'bits':bits,'absolute_nmse':o['mean_absolute_nmse'],
                     'predictive_nmse':o['mean_predictive_nmse'],
                     'nmse_gain_db':10*np.log10(o['mean_absolute_nmse']/max(o['mean_predictive_nmse'],1e-15)),
                     'innovation_power':o['mean_innovation_power']})
df=pd.DataFrame(rows); df.to_csv(OUT/'predictive_csi_quantization.csv',index=False)
plt.figure(figsize=(6.5,4.2))
for b,g in df.groupby('bits'):
    plt.plot(g.correlation,g.nmse_gain_db,marker='o',label=f'{b}-bit')
plt.xlabel('One-step Channel Correlation'); plt.ylabel('Predictive CSI NMSE Gain (dB)'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout()
plt.savefig(FIG/'predictive_csi_nmse_gain.png',dpi=180); plt.close()
plt.figure(figsize=(6.5,4.2))
g=df[df.bits==3]
plt.semilogy(g.correlation,g.absolute_nmse,marker='o',label='Absolute CSI')
plt.semilogy(g.correlation,g.predictive_nmse,marker='o',label='Predictive innovation')
plt.xlabel('One-step Channel Correlation'); plt.ylabel('Mean CSI NMSE'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout()
plt.savefig(FIG/'predictive_csi_3bit_nmse.png',dpi=180); plt.close()
print(df.to_string(index=False))
