from pathlib import Path
import csv, numpy as np
import matplotlib.pyplot as plt
from commlab.computation import simulate_straggler_resilience
OUT=Path('results/data'); FIG=Path('results/figures'); OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rows=[]
for p in [0,.05,.1,.15,.2,.3]:
    for name,r in [('uncoded',0),('mds2',2),('mds4',4),('mds8',8),('replication',4)]:
        strat='replication' if name=='replication' else ('uncoded' if name=='uncoded' else 'mds')
        o=simulate_straggler_resilience(strategy=strat,redundancy=r,rounds=18000,straggler_probability=p,seed=2410)
        rows.append({'straggler_probability':p,'scheme':name,'mean_latency_ms':o['mean_latency_ms'],'p95_latency_ms':o['p95_latency_ms'],'p99_latency_ms':o['p99_latency_ms'],'compute_load_ratio':o['compute_load_ratio']})
with open(OUT/'v24_straggler_coding.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
plt.figure()
for s in ['uncoded','mds2','mds4','mds8','replication']:
    rr=[r for r in rows if r['scheme']==s]; plt.plot([r['straggler_probability'] for r in rr],[r['p95_latency_ms'] for r in rr],marker='o',label=s)
plt.xlabel('Straggler probability'); plt.ylabel('P95 round latency (ms)'); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v24_straggler_tail_latency.png',dpi=180); plt.close()
rr=[r for r in rows if r['straggler_probability']==.15]
plt.figure(); plt.scatter([r['compute_load_ratio'] for r in rr],[r['p95_latency_ms'] for r in rr]);
for r in rr: plt.annotate(r['scheme'],(r['compute_load_ratio'],r['p95_latency_ms']))
plt.xlabel('Compute load ratio'); plt.ylabel('P95 latency (ms)'); plt.tight_layout(); plt.savefig(FIG/'v24_straggler_load_tradeoff.png',dpi=180); plt.close()
print([r for r in rows if r['straggler_probability']==.15])
