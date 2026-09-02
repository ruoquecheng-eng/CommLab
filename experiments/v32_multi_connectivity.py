from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt
from commlab.computation import simulate_multi_connectivity_reliability
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'results'/'data'; FIG=ROOT/'results'/'figures'; DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rows=[]
for rho in [0,.2,.4,.6,.8,.95]:
    for p in ['single','full_duplicate','adaptive']:
        rr=[simulate_multi_connectivity_reliability(n_packets=36000,policy=p,correlation=rho,mean_snr_db=-1,seed=s) for s in range(5)]
        keys=['packet_outage_rate','packet_delivery_rate','mean_transmissions_per_packet','duplication_rate','mean_success_latency_ms','p95_success_latency_ms']
        rows.append([rho,p,*[np.mean([x[k] for x in rr]) for k in keys]])
with (DATA/'v32_multi_connectivity.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['link_correlation','policy','packet_outage_rate','packet_delivery_rate','transmissions_per_packet','duplication_rate','mean_success_latency_ms','p95_success_latency_ms']); w.writerows(rows)
plt.figure(figsize=(7.2,4.7))
for p in ['single','full_duplicate','adaptive']:
    r=[x for x in rows if x[1]==p]; plt.semilogy([x[0] for x in r],[x[2] for x in r],marker='o',label=p)
plt.xlabel('Link-failure correlation'); plt.ylabel('Packet outage probability'); plt.title('Correlation erodes dual-link reliability diversity'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v32_multi_connectivity_outage.png',dpi=170); plt.close()
plt.figure(figsize=(7.2,4.7))
for p in ['single','full_duplicate','adaptive']:
    r=[x for x in rows if x[1]==p]; plt.plot([x[0] for x in r],[x[4] for x in r],marker='o',label=p)
plt.xlabel('Link-failure correlation'); plt.ylabel('Transmissions / packet'); plt.title('Adaptive duplication avoids unconditional 2x radio use'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v32_multi_connectivity_overhead.png',dpi=170); plt.close()
print('wrote v32 multi-connectivity')
