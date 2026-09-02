from pathlib import Path
import csv,numpy as np,matplotlib.pyplot as plt
from commlab.computation import simulate_layered_multitask_semantic
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'results'/'data'; F=ROOT/'results'/'figures'; D.mkdir(parents=True,exist_ok=True); F.mkdir(parents=True,exist_ok=True)
rows=[]
for ang in [15,30,45,60,75,90]:
    o=simulate_layered_multitask_semantic(dim=16,n_samples=16000,task_angle_deg=ang,snr_db=10,confidence_threshold=.5,seed=2203)
    rows.append((ang,o['base_accuracy'],o['adaptive_accuracy'],o['full_accuracy'],o['adaptive_mean_uses'],o['enhancement_fraction']))
with (D/'v22_layered_semantic_angle.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['task_angle_deg','base_accuracy','adaptive_accuracy','full_accuracy','adaptive_mean_uses','enhancement_fraction']); w.writerows(rows)
fig,ax=plt.subplots(figsize=(7.3,4.7)); ax.plot([x[0] for x in rows],[x[1] for x in rows],'o-',label='Base layer (1 use)'); ax.plot([x[0] for x in rows],[x[2] for x in rows],'s-',label='Confidence-adaptive'); ax.plot([x[0] for x in rows],[x[3] for x in rows],'^-',label='Two layers (2 uses)'); ax.set(xlabel='Angle between task directions (deg)',ylabel='Mean two-task accuracy',title='Progressive Task-Oriented Representation'); ax.grid(alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(F/'v22_layered_semantic_accuracy.png',dpi=180); plt.close(fig)
fig,ax=plt.subplots(figsize=(7.3,4.7)); ax.plot([x[0] for x in rows],[x[4] for x in rows],'o-'); ax.set(xlabel='Task-direction angle (deg)',ylabel='Mean channel uses per sample',ylim=(.95,2.05),title='Adaptive Enhancement Cost Grows with Task Conflict'); ax.grid(alpha=.3); fig.tight_layout(); fig.savefig(F/'v22_layered_semantic_uses.png',dpi=180); plt.close(fig)
trade=[]
for th in [0,.1,.2,.3,.5,.8,1.2]:
    o=simulate_layered_multitask_semantic(dim=16,n_samples=16000,task_angle_deg=60,snr_db=10,confidence_threshold=th,seed=2204)
    trade.append((th,o['adaptive_accuracy'],o['adaptive_mean_uses'],o['enhancement_fraction']))
with (D/'v22_layered_semantic_threshold.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['confidence_threshold','adaptive_accuracy','mean_uses','enhancement_fraction']); w.writerows(trade)
print(rows); print(trade)
