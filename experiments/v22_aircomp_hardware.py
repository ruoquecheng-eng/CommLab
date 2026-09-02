from pathlib import Path
import csv,numpy as np,matplotlib.pyplot as plt
from commlab.computation import simulate_aircomp_hardware
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'results'/'data'; F=ROOT/'results'/'figures'; D.mkdir(parents=True,exist_ok=True); F.mkdir(parents=True,exist_ok=True)
rows=[]
for bits in [2,3,4,6,8]:
    for agc in [False,True]:
        o=simulate_aircomp_hardware(n_devices=16,vector_dim=64,snr_db=24,pa_saturation=3.0,adc_bits=bits,agc=agc,n_trials=500,seed=2201)
        rows.append((bits,agc,o['median_mse'],o['p90_mse'],o['mean_adc_overload_fraction']))
with (D/'v22_aircomp_adc_agc.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['adc_bits','agc','median_mse','p90_mse','adc_overload_fraction']); w.writerows(rows)
fig,ax=plt.subplots(figsize=(7.3,4.7))
for agc,label in [(False,'Fixed ADC range'),(True,'Per-vector AGC')]:
    r=[x for x in rows if x[1]==agc]; ax.semilogy([x[0] for x in r],[x[2] for x in r],'o-',label=label)
ax.set(xlabel='ADC bits per I/Q component',ylabel='Median aggregation MSE',title='AirComp ADC Resolution and AGC'); ax.grid(alpha=.3,which='both'); ax.legend(); fig.tight_layout(); fig.savefig(F/'v22_aircomp_adc_agc.png',dpi=180); plt.close(fig)
pa=[]
for sat in [.7,1.0,1.4,2.0,3.0,None]:
    o=simulate_aircomp_hardware(n_devices=16,vector_dim=64,snr_db=30,pa_saturation=sat,adc_bits=8,agc=True,n_trials=500,seed=2202)
    pa.append((99.0 if sat is None else sat,o['median_mse'],o['p90_mse'],o['mean_pa_clip_fraction']))
with (D/'v22_aircomp_pa_clipping.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['pa_saturation','median_mse','p90_mse','clip_fraction']); w.writerows(pa)
fig,ax=plt.subplots(figsize=(7.3,4.7)); r=pa[:-1]; ax.semilogy([x[0] for x in r],[x[1] for x in r],'o-'); ax.axhline(pa[-1][1],ls='--',label='No PA clipping'); ax.set(xlabel='PA magnitude saturation (normalized)',ylabel='Median aggregation MSE',title='Analog Aggregation Is Sensitive to Transmit Clipping'); ax.grid(alpha=.3,which='both'); ax.legend(); fig.tight_layout(); fig.savefig(F/'v22_aircomp_pa_clipping.png',dpi=180); plt.close(fig)
print(rows); print(pa)
