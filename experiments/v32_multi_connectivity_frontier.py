from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt
from commlab.computation import simulate_multi_connectivity_reliability
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'results'/'data'; FIG=ROOT/'results'/'figures'; DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rows=[]
for rho in [0.1,0.5,0.9]:
    for thr in [.04,.08,.12,.172,.24,.34,.50]:
        rr=[simulate_multi_connectivity_reliability(n_packets=28000,policy='adaptive',correlation=rho,mean_snr_db=-1,seed=s,duplication_threshold=thr) for s in range(4)]
        outage=float(np.mean([x['packet_outage_rate'] for x in rr])); tx=float(np.mean([x['mean_transmissions_per_packet'] for x in rr])); dup=float(np.mean([x['duplication_rate'] for x in rr])); lat=float(np.mean([x['p95_success_latency_ms'] for x in rr]))
        rows.append([rho,thr,outage,tx,dup,lat])
with (DATA/'v32_multi_connectivity_frontier.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['link_correlation','duplication_threshold','packet_outage_rate','transmissions_per_packet','duplication_rate','p95_success_latency_ms']); w.writerows(rows)
plt.figure(figsize=(7.2,4.7))
for rho in [0.1,0.5,0.9]:
    r=[x for x in rows if x[0]==rho]; plt.plot([x[3] for x in r],[x[2] for x in r],marker='o',label=f'rho={rho:.1f}')
plt.xlabel('Transmissions / packet'); plt.ylabel('Packet outage probability'); plt.yscale('log'); plt.title('Adaptive duplication reliability-resource frontier'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v32_multi_connectivity_frontier.png',dpi=170); plt.close()
plt.figure(figsize=(7.2,4.7))
for rho in [0.1,0.5,0.9]:
    r=[x for x in rows if x[0]==rho]; plt.plot([x[1] for x in r],[x[3] for x in r],marker='o',label=f'rho={rho:.1f}')
plt.xlabel('Adaptive duplication threshold'); plt.ylabel('Transmissions / packet'); plt.title('Risk threshold directly controls duplication overhead'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v32_multi_connectivity_threshold_overhead.png',dpi=170); plt.close()
print('wrote v32 multi-connectivity frontier')
