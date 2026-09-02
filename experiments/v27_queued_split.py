from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt
from commlab.computation import simulate_queued_progressive_split
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'results/data'; F=ROOT/'results/figures'; D.mkdir(parents=True,exist_ok=True); F.mkdir(parents=True,exist_ok=True)
rows=[]; policies=['fifo','edf','value','urgency_value','completion_aware']
for load in [.35,.5,.65,.8,.95,1.1]:
    for p in policies:
        vals=[simulate_queued_progressive_split(policy=p,arrival_rate=load,slots=1400,seed=2740+r) for r in range(8)]
        rows.append((load,p,*[np.mean([v[k] for v in vals]) for k in ['on_time_accuracy','on_time_task_utility','deadline_miss_rate','mean_radio_uses_per_request','mean_backlog']]))
with open(D/'v27_queued_split.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['arrival_rate','policy','on_time_accuracy','on_time_task_utility','deadline_miss_rate','radio_uses_per_request','mean_backlog']); w.writerows(rows)
for idx,name,ylabel in [(3,'v27_queued_split_utility.png','On-time task-weighted utility'),(4,'v27_queued_split_deadline.png','Deadline miss rate')]:
    for p in policies:
        rr=[r for r in rows if r[1]==p]; plt.plot([r[0] for r in rr],[r[idx] for r in rr],marker='o',label=p)
    plt.xlabel('Mean inference arrivals / slot'); plt.ylabel(ylabel); plt.legend(fontsize=7); plt.tight_layout(); plt.savefig(F/name,dpi=180); plt.close()
