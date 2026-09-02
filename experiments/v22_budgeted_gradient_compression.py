from pathlib import Path
import csv,numpy as np,matplotlib.pyplot as plt
from commlab.computation import simulate_budgeted_compressed_fl
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'results'/'data'; F=ROOT/'results'/'figures'; D.mkdir(parents=True,exist_ok=True); F.mkdir(parents=True,exist_ok=True)
rows=[]; budget=32
strategies=[('topk_noef',False,'equal'),('equal_ef',True,'equal'),('residual_ef',True,'residual')]
for name,ef,alloc in strategies:
    for ns in [1,2,3,4,6,8,12]:
        vals=[]
        for rep in range(8):
            o=simulate_budgeted_compressed_fl(n_clients=12,n_select=ns,coordinate_budget=budget,dim=32,rounds=100,heterogeneity=1.2,learning_rate=.08,error_feedback=ef,clustered=True,allocation=alloc,seed=2200+rep)
            vals.append([o['final_loss'],o['parameter_error'],o['topk_per_client'],o['coordinates_per_round']])
        a=np.asarray(vals); rows.append((name,ns,*a.mean(axis=0),a[:,0].std(),a[:,1].std()))
with (D/'v22_budgeted_gradient_compression.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['strategy','selected_clients','final_loss','parameter_error','nominal_equal_topk','coordinates_per_round','sd_final_loss','sd_parameter_error']); w.writerows(rows)
fig,ax=plt.subplots(figsize=(7.3,4.7))
for name,label in [('topk_noef','Top-k only'),('equal_ef','Top-k + error feedback'),('residual_ef','Residual-aware allocation + EF')]:
    r=[x for x in rows if x[0]==name]; ax.plot([x[1] for x in r],[x[3] for x in r],'o-',label=label)
ax.set(xlabel='Selected clients per round',ylabel='Parameter error to global optimum',title='Fixed 32-Coordinate Uplink Budget: Participation vs Compression'); ax.grid(alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(F/'v22_budgeted_fl_parameter_error.png',dpi=180); plt.close(fig)
fig,ax=plt.subplots(figsize=(7.3,4.7)); r=[x for x in rows if x[0]=='equal_ef']; ax.plot([x[1] for x in r],[x[4] for x in r],'o-'); ax.set(xlabel='Selected clients per round',ylabel='Nominal equal top-k coordinates/client',title='Same Uplink Budget Forces Stronger Per-Client Compression'); ax.grid(alpha=.3); fig.tight_layout(); fig.savefig(F/'v22_budgeted_fl_topk.png',dpi=180); plt.close(fig)
print(rows)
