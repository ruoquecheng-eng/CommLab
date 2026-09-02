from pathlib import Path
import csv, numpy as np
import matplotlib.pyplot as plt
from commlab.computation import simulate_asynchronous_federated
OUT=Path('results/data'); FIG=Path('results/figures'); OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rows=[]
for dm in [0,1,2,4,6,8]:
    for strategy in ['naive','decay','quadratic_corrected']:
        vals=[]
        for s in range(12):
            o=simulate_asynchronous_federated(strategy=strategy,rounds=140,max_delay=12,delay_mean=dm,heterogeneity=1.2,learning_rate=.09,seed=23000+s)
            vals.append(o)
        rows.append({'delay_mean':dm,'strategy':strategy,'final_loss':np.mean([v['final_loss'] for v in vals]),
                     'parameter_error':np.mean([v['parameter_error'] for v in vals]),
                     'cosine':np.mean([v['mean_stale_current_cosine'] for v in vals])})
with open(OUT/'v23_async_fl.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
for metric,ylabel,name in [('final_loss','Final global loss','v23_async_fl_loss.png'),('cosine','Stale/current gradient cosine','v23_async_fl_conflict.png')]:
    plt.figure()
    for st in ['naive','decay','quadratic_corrected']:
        rr=[r for r in rows if r['strategy']==st]; plt.plot([r['delay_mean'] for r in rr],[r[metric] for r in rr],marker='o',label=st)
    plt.xlabel('Mean staleness (server updates)');plt.ylabel(ylabel);plt.legend();plt.tight_layout();plt.savefig(FIG/name,dpi=180);plt.close()
print(rows)
