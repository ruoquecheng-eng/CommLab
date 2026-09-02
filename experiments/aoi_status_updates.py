from pathlib import Path
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from commlab.scheduling.aoi import simulate_status_update_aoi

ROOT=Path('results'); OUT=ROOT/'data'; FIG=ROOT/'figures'; OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(1830); S,U=2500,5; base=np.array([-2.,0.,2.,4.,6.])
true=np.empty((S,U)); true[0]=base+rng.normal(0,2,U)
for t in range(1,S): true[t]=.95*true[t-1]+.05*base+rng.normal(0,.8,U)
est=true+rng.normal(0,1.0,(S,U))
rows=[]; example=None
for rate in [.7,1.0,1.3]:
    for retrans in ['fresh','chase']:
        for policy in ['max_age','max_snr','age_reliability']:
            o=simulate_status_update_aoi(true,est,blocklength=90,rate=rate,policy=policy,
                                         retransmission=retrans,max_rounds=3,seed=1831)
            rows.append({'rate_bit_per_use':rate,'retransmission':retrans,'policy':policy,
                         'mean_aoi':o['mean_aoi'],'p95_aoi':o['p95_aoi'],'mean_peak_aoi':o['mean_peak_aoi'],
                         'delivery_rate_per_slot':o['delivery_rate_per_slot'],
                         'min_user_deliveries':int(o['successes'].min()),'max_user_deliveries':int(o['successes'].max())})
            if rate==1.0 and retrans=='chase' and policy=='age_reliability': example=o

df=pd.DataFrame(rows); df.to_csv(OUT/'aoi_status_updates.csv',index=False)
plt.figure(figsize=(7,4.4))
for (r,p),g in df.groupby(['retransmission','policy']):
    plt.plot(g.rate_bit_per_use,g.mean_aoi,marker='o',label=f'{r}/{p}')
plt.xlabel('Status-Update Rate (bit/use)'); plt.ylabel('Mean Age of Information (slots)'); plt.yscale('log'); plt.grid(alpha=.25); plt.legend(fontsize=7); plt.tight_layout()
plt.savefig(FIG/'aoi_policy_comparison.png',dpi=180); plt.close()
plt.figure(figsize=(7,4.3))
for u in range(example['age_history'].shape[1]):
    plt.plot(example['age_history'][:300,u],linewidth=1,label=f'User {u+1}')
plt.xlabel('Slot'); plt.ylabel('AoI (slots)'); plt.grid(alpha=.2); plt.legend(ncol=5,fontsize=7); plt.tight_layout()
plt.savefig(FIG/'aoi_example_trace.png',dpi=180); plt.close()
print(df.to_string(index=False))
