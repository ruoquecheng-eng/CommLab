from pathlib import Path
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from commlab.scheduling.ir_harq_fbl import simulate_fbl_ir_harq_queue

ROOT=Path('results'); OUT=ROOT/'data'; FIG=ROOT/'figures'; OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rows=[]
for snr in [-2,0,2,4,6]:
    rng=np.random.default_rng(1710+snr)
    S=1800; true=rng.normal(float(snr),1.0,(S,1)); est=true+rng.normal(0,.35,(S,1))
    arrivals=(rng.random((S,1))<.22).astype(int)
    for mode in ['chase','ir']:
        o=simulate_fbl_ir_harq_queue(true,est,arrivals,[-100],[1.5],round_blocklength=80,
                                     mode=mode,max_rounds=4,use_olla=False,policy='max_rate',seed=1717)
        rows.append({'snr_db':snr,'mode':mode,'goodput':o['goodput_bits_per_channel_use'],
                     'nack_rate':o['nack_rate'],'drops':o['drops'],'mean_delay':o['mean_delay_slots'],
                     'p95_delay':o['p95_delay_slots'],'mean_rounds':o['mean_rounds_per_completed']})
df=pd.DataFrame(rows); df.to_csv(OUT/'fbl_ir_harq.csv',index=False)
for metric,ylabel,name in [('goodput','Payload Goodput (bit/channel-use)','fbl_ir_harq_goodput.png'),
                            ('mean_rounds','Mean Transmission Rounds','fbl_ir_harq_rounds.png')]:
    plt.figure(figsize=(6.4,4.2))
    for p,g in df.groupby('mode'):
        plt.plot(g.snr_db,g[metric],marker='o',label=p.upper())
    plt.xlabel('Mean SNR (dB)'); plt.ylabel(ylabel); plt.grid(alpha=.25); plt.legend(); plt.tight_layout()
    plt.savefig(FIG/name,dpi=180); plt.close()
print(df.to_string(index=False))
