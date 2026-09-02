from pathlib import Path
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from commlab.ris import optimal_ris_phases, quantize_phases, ris_effective_channel, ris_spectral_efficiency

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'results'; FIG=OUT/'figures'; DATA=OUT/'data'; FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(1201); snr=10.0; trials=700; amp=.025
rows=[]
for n in [4,8,16,32,64,128]:
    vals={k:[] for k in ['random','1-bit','2-bit','3-bit','continuous']}
    gains={k:[] for k in vals}
    for _ in range(trials):
        a=(rng.normal(size=n)+1j*rng.normal(size=n))/np.sqrt(2)
        b=(rng.normal(size=n)+1j*rng.normal(size=n))/np.sqrt(2)
        hd=.25*(rng.normal()+1j*rng.normal())/np.sqrt(2)
        th=optimal_ris_phases(a,b,hd)
        configs={
            'random':rng.uniform(-np.pi,np.pi,n),
            '1-bit':quantize_phases(th,1),'2-bit':quantize_phases(th,2),'3-bit':quantize_phases(th,3),'continuous':th,
        }
        for k,p in configs.items():
            h=ris_effective_channel(a,b,p,hd,amplitude=amp); vals[k].append(ris_spectral_efficiency(h,snr)); gains[k].append(abs(h)**2)
    for k in vals:
        rows.append(dict(elements=n,scheme=k,mean_rate=np.mean(vals[k]),mean_power_gain=np.mean(gains[k])))
df=pd.DataFrame(rows); df.to_csv(DATA/'ris_phase_quantization.csv',index=False)
fig,ax=plt.subplots(figsize=(7,4.5))
for k,g in df.groupby('scheme'): ax.plot(g.elements,g.mean_rate,marker='o',label=k)
ax.set_xscale('log',base=2); ax.set_xlabel('RIS elements'); ax.set_ylabel('Mean spectral efficiency (bit/s/Hz)'); ax.grid(True,alpha=.25); ax.legend(); fig.tight_layout(); fig.savefig(FIG/'ris_phase_quantization_rate.png',dpi=180); plt.close(fig)
fig,ax=plt.subplots(figsize=(7,4.5))
for k,g in df[df.scheme!='random'].groupby('scheme'): ax.plot(g.elements,10*np.log10(g.mean_power_gain),marker='o',label=k)
ax.set_xscale('log',base=2); ax.set_xlabel('RIS elements'); ax.set_ylabel('Mean effective-channel power (dB)'); ax.grid(True,alpha=.25); ax.legend(); fig.tight_layout(); fig.savefig(FIG/'ris_phase_quantization_gain.png',dpi=180); plt.close(fig)
print(df[df.elements.isin([16,64,128])].to_string(index=False))
