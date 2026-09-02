from pathlib import Path
import pandas as pd, matplotlib.pyplot as plt
from commlab.random_access.grant_free import simulate_grant_free_random_access

ROOT=Path('results'); OUT=ROOT/'data'; FIG=ROOT/'figures'; OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rows=[]
for spread in [0,4,8,12]:
    for p in [.02,.05,.08,.12,.18]:
        for mode in ['oma_collision','noma_sic']:
            o=simulate_grant_free_random_access(120,24,1200,p,mean_snr_db=10,power_spread_db=spread,
                                                sinr_threshold_db=2,mode=mode,seed=1850)
            rows.append({'power_spread_db':spread,'activity_probability':p,'mode':mode,**o})
df=pd.DataFrame(rows); df.to_csv(OUT/'grant_free_noma_random_access.csv',index=False)
sub=df[df.power_spread_db==8]
plt.figure(figsize=(6.5,4.2))
for m,g in sub.groupby('mode'):
    plt.plot(g.offered_load_per_resource,g.throughput_packets_per_slot,marker='o',label=m)
plt.xlabel('Offered Load (attempts/resource/slot)'); plt.ylabel('Decoded Packets / Slot'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout()
plt.savefig(FIG/'grant_free_noma_throughput.png',dpi=180); plt.close()
sub=df[df.activity_probability==.18]
piv=sub.pivot(index='power_spread_db',columns='mode',values='throughput_packets_per_slot')
plt.figure(figsize=(6.5,4.2))
for c in piv.columns: plt.plot(piv.index,piv[c],marker='o',label=c)
plt.xlabel('Received-Power Spread Std (dB)'); plt.ylabel('Decoded Packets / Slot'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout()
plt.savefig(FIG/'grant_free_noma_power_spread.png',dpi=180); plt.close()
print(df.to_string(index=False))
