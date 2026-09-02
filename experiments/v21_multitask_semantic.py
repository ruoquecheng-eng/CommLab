from pathlib import Path
import csv,matplotlib.pyplot as plt
from commlab.computation import simulate_multitask_task_oriented
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'results'/'data'; F=ROOT/'results'/'figures'; D.mkdir(parents=True,exist_ok=True); F.mkdir(parents=True,exist_ok=True)
angles=[0,15,30,45,60,75,90]; rows=[]
for a in angles:
    o=simulate_multitask_task_oriented(dim=16,n_samples=18000,task_angle_deg=a,snr_db=10,seed=2320+a)
    rows.append((a,o['raw_mean_accuracy'],o['task_specific_mean_accuracy'],o['shared_rank1_mean_accuracy'],o['shared_rank2_mean_accuracy'],o['raw_uses'],o['task_specific_uses'],o['shared_rank1_uses'],o['shared_rank2_uses']))
with (D/'v21_multitask_semantic.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['task_angle_deg','raw_mean_accuracy','task_specific_mean_accuracy','shared_rank1_mean_accuracy','shared_rank2_mean_accuracy','raw_uses','task_specific_uses','shared_rank1_uses','shared_rank2_uses']); w.writerows(rows)
fig,ax=plt.subplots(figsize=(7.3,4.7)); ax.plot([r[0] for r in rows],[r[1] for r in rows],'o-',label='Raw 16-D (16 uses)'); ax.plot([r[0] for r in rows],[r[2] for r in rows],'s-',label='Task-specific stats (2 uses)'); ax.plot([r[0] for r in rows],[r[3] for r in rows],'^-',label='Shared rank-1 (1 use)'); ax.plot([r[0] for r in rows],[r[4] for r in rows],'d-',label='Shared rank-2 (2 uses)'); ax.set(xlabel='Angle between task-relevant directions (deg)',ylabel='Mean task accuracy',ylim=(.62,.94),title='Multi-Task Semantic Compression: Sharing vs Task Conflict'); ax.grid(alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(F/'v21_multitask_semantic_accuracy.png',dpi=180); plt.close(fig)
fig,ax=plt.subplots(figsize=(7.3,4.7)); names=['Raw','Task-specific','Shared rank-1','Shared rank-2']; uses=[16,2,1,2]; acc=[rows[-1][1],rows[-1][2],rows[-1][3],rows[-1][4]]; ax.scatter(uses,acc,s=80); [ax.annotate(n,(u,a),xytext=(5,5),textcoords='offset points') for n,u,a in zip(names,uses,acc)]; ax.set(xscale='log',xlabel='Channel uses for both tasks',ylabel='Mean accuracy at 90° task separation',title='Task Utility vs Communication Cost'); ax.grid(alpha=.3); fig.tight_layout(); fig.savefig(F/'v21_multitask_semantic_tradeoff.png',dpi=180); plt.close(fig)
print(rows)
