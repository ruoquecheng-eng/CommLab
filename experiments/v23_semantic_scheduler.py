from pathlib import Path
import csv, numpy as np
import matplotlib.pyplot as plt
from commlab.computation import simulate_semantic_resource_scheduling
OUT=Path('results/data'); FIG=Path('results/figures'); OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rows=[]
for R in [3,4,6,8,10]:
    for st in ['channel','importance','value_per_resource','urgency_aware']:
        vals=[simulate_semantic_resource_scheduling(resources_per_slot=R,strategy=st,slots=500,seed=23300+s) for s in range(18)]
        rows.append({'resources':R,'strategy':st,'task_utility':np.mean([v['task_utility'] for v in vals]),'expired':np.mean([v['expired'] for v in vals]),'delivery_age':np.nanmean([v['mean_delivery_age'] for v in vals]),'utilization':np.mean([v['resource_utilization'] for v in vals])})
with open(OUT/'v23_semantic_scheduler.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
for metric,ylabel,name in [('task_utility','Task utility / slot','v23_semantic_scheduler_utility.png'),('expired','Expired semantic packets','v23_semantic_scheduler_expiry.png')]:
    plt.figure()
    for st in ['channel','importance','value_per_resource','urgency_aware']:
        rr=[r for r in rows if r['strategy']==st];plt.plot([r['resources'] for r in rr],[r[metric] for r in rr],marker='o',label=st)
    plt.xlabel('Resources / slot');plt.ylabel(ylabel);plt.legend();plt.tight_layout();plt.savefig(FIG/name,dpi=180);plt.close()
print(rows)
