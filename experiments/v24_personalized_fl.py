from pathlib import Path
import csv, numpy as np
import matplotlib.pyplot as plt
from commlab.computation import simulate_personalized_federated
OUT=Path('results/data'); FIG=Path('results/figures'); OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rows=[]
for h in [0,.3,.6,1.0,1.4]:
    for a in [0,.2,.4,.6,.8,1.0]:
        vals=[simulate_personalized_federated(heterogeneity=h,personalization=a,seed=2400+s) for s in range(20)]
        rows.append({'heterogeneity':h,'personalization':a,'test_mse':np.mean([v['mean_personalized_test_mse'] for v in vals]),'p90_client_mse':np.mean([v['p90_personalized_test_mse'] for v in vals]),'drift':np.mean([v['personalization_drift'] for v in vals])})
with open(OUT/'v24_personalized_fl.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
plt.figure()
for h in [0,.3,.6,1.0,1.4]:
    rr=[r for r in rows if r['heterogeneity']==h]; plt.plot([r['personalization'] for r in rr],[r['test_mse'] for r in rr],marker='o',label=f'h={h}')
plt.xlabel('Personalization blend α'); plt.ylabel('Mean client test MSE'); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v24_personalization_tradeoff.png',dpi=180); plt.close()
best=[]
for h in [0,.3,.6,1.0,1.4]:
    rr=[r for r in rows if r['heterogeneity']==h]; q=min(rr,key=lambda x:x['test_mse']); best.append((h,q['personalization'],q['test_mse']))
plt.figure(); plt.plot([x[0] for x in best],[x[1] for x in best],marker='o'); plt.xlabel('Client heterogeneity'); plt.ylabel('Best personalization α'); plt.tight_layout(); plt.savefig(FIG/'v24_personalization_optimum.png',dpi=180); plt.close()
print(best)
