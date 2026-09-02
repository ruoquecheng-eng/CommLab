from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from commlab.ris.cellfree_imperfect import predicted_channel_samples, quantize_ris_cellfree_csi
from commlab.ris.cellfree import coordinate_optimize_cellfree_ris, cellfree_ris_rates
from commlab.ris.robust import sample_average_optimize_cellfree_ris

ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'; FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(1601); K,M,N=3,6,10; snr=10.0; rho=.98; delays=[0,2,5,10,20]
rows=[]
for delay in delays:
    vals={'random':[],'naive':[],'robust':[],'ideal':[]}
    for outer in range(4):
        D=.20*(rng.normal(size=(K,M))+1j*rng.normal(size=(K,M)))/np.sqrt(2)
        G=.18*(rng.normal(size=(N,M))+1j*rng.normal(size=(N,M)))/np.sqrt(2)
        R=.18*(rng.normal(size=(K,N))+1j*rng.normal(size=(K,N)))/np.sqrt(2)
        Q=quantize_ris_cellfree_csi(D,G,R,4)
        naive,_=coordinate_optimize_cellfree_ris(*Q,snr,bits=2,iterations=2)
        samples=predicted_channel_samples(Q,rho,delay,10,rng)
        robust,_=sample_average_optimize_cellfree_ris(samples,snr,bits=2,iterations=2)
        random_phase=rng.uniform(-np.pi,np.pi,N)
        tests=predicted_channel_samples(Q,rho,delay,12,rng)
        for j,cur in enumerate(tests):
            vals['random'].append(cellfree_ris_rates(*cur,random_phase,snr).sum())
            vals['naive'].append(cellfree_ris_rates(*cur,naive,snr).sum())
            vals['robust'].append(cellfree_ris_rates(*cur,robust,snr).sum())
            if j<3:
                ideal,_=coordinate_optimize_cellfree_ris(*cur,snr,bits=2,iterations=1)
                vals['ideal'].append(cellfree_ris_rates(*cur,ideal,snr).sum())
    for method,v in vals.items():
        rows.append({'delay_steps':delay,'effective_correlation':rho**delay,'method':method,
                     'mean_sum_rate':float(np.mean(v)),'p10_sum_rate':float(np.quantile(v,.1)),
                     'samples':len(v)})
df=pd.DataFrame(rows); df.to_csv(DATA/'cellfree_ris_aged_quantized_csi.csv',index=False)
fig,ax=plt.subplots()
for method in ['random','naive','robust','ideal']:
    s=df[df.method==method]; ax.plot(s.delay_steps,s.mean_sum_rate,marker='o',label=method)
ax.set_xlabel('CSI age (Gauss-Markov steps)'); ax.set_ylabel('Mean sum-rate (bit/s/Hz)'); ax.set_title('Cell-Free RIS under aged + 4-bit quantized CSI'); ax.grid(True,alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(FIG/'cellfree_ris_aged_quantized_mean_rate.png',dpi=180); plt.close(fig)
fig,ax=plt.subplots()
for method in ['random','naive','robust']:
    s=df[df.method==method]; ax.plot(s.delay_steps,s.p10_sum_rate,marker='o',label=method)
ax.set_xlabel('CSI age (steps)'); ax.set_ylabel('10th-percentile sum-rate'); ax.set_title('Tail robustness under CSI aging'); ax.grid(True,alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(FIG/'cellfree_ris_aged_quantized_p10.png',dpi=180); plt.close(fig)

# Separate CSI-quantization sweep at moderate age, using identical channel
# realizations for every bit depth so the comparison isolates quantization.
bit_rows=[]; delay=5
base_sets=[]
for outer in range(6):
    D=.20*(rng.normal(size=(K,M))+1j*rng.normal(size=(K,M)))/np.sqrt(2)
    G=.18*(rng.normal(size=(N,M))+1j*rng.normal(size=(N,M)))/np.sqrt(2)
    R=.18*(rng.normal(size=(K,N))+1j*rng.normal(size=(K,N)))/np.sqrt(2)
    # Current-channel noise seeds are frozen per base realization.
    test_seed=int(rng.integers(0,2**31-1))
    robust_seed=int(rng.integers(0,2**31-1))
    base_sets.append((D,G,R,test_seed,robust_seed))
for qbits in [2,3,4,6,8]:
    naive_v=[]; robust_v=[]
    for D,G,R,test_seed,robust_seed in base_sets:
        Q=quantize_ris_cellfree_csi(D,G,R,qbits)
        naive,_=coordinate_optimize_cellfree_ris(*Q,snr,bits=2,iterations=2)
        robust_rng=np.random.default_rng(robust_seed)
        samples=predicted_channel_samples(Q,rho,delay,12,robust_rng)
        robust,_=sample_average_optimize_cellfree_ris(samples,snr,bits=2,iterations=2)
        test_rng=np.random.default_rng(test_seed)
        # True current channels evolve from the unquantized stale CSI.
        tests=predicted_channel_samples((D,G,R),rho,delay,20,test_rng)
        for cur in tests:
            naive_v.append(cellfree_ris_rates(*cur,naive,snr).sum())
            robust_v.append(cellfree_ris_rates(*cur,robust,snr).sum())
    bit_rows += [
        {'csi_bits':qbits,'method':'naive','mean_sum_rate':float(np.mean(naive_v)),'p10_sum_rate':float(np.quantile(naive_v,.1))},
        {'csi_bits':qbits,'method':'robust','mean_sum_rate':float(np.mean(robust_v)),'p10_sum_rate':float(np.quantile(robust_v,.1))},
    ]
bdf=pd.DataFrame(bit_rows); bdf.to_csv(DATA/'cellfree_ris_csi_quantization_sweep.csv',index=False)
fig,ax=plt.subplots()
for method in ['naive','robust']:
    z=bdf[bdf.method==method]; ax.plot(z.csi_bits,z.mean_sum_rate,marker='o',label=method)
ax.set_xlabel('CSI quantization bits / real component'); ax.set_ylabel('Mean sum-rate'); ax.set_title('RIS control under quantized CSI (common channel draws)'); ax.grid(True,alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(FIG/'cellfree_ris_csi_quantization_sweep.png',dpi=180); plt.close(fig)

print(df.to_string(index=False))
print("\nCSI-bit sweep\n",bdf.to_string(index=False))
