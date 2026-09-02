from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt
from commlab.computation import simulate_progressive_split_admission
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'results'/'data'; FIG=ROOT/'results'/'figures'; DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
policies=['admit_all','backlog_gate','backpressure']; loads=[.4,.6,.8,1.0,1.2,1.5]; rows=[]
for load in loads:
    for p in policies:
        rr=[simulate_progressive_split_admission(policy=p,slots=1500,arrival_rate=load,seed=s) for s in range(10)]
        rows.append([load,p,np.mean([x['on_time_task_utility'] for x in rr]),np.mean([x['on_time_accuracy'] for x in rr]),np.mean([x['deadline_miss_rate'] for x in rr]),np.mean([x['radio_uses_per_request'] for x in rr]),np.mean([x['admission_fraction'] for x in rr]),np.mean([x['mean_backlog'] for x in rr])])
with (DATA/'v28_split_admission.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['arrival_rate','policy','on_time_task_utility','on_time_accuracy','deadline_miss_rate','radio_uses_per_request','admission_fraction','mean_backlog']); w.writerows(rows)
plt.figure(figsize=(7.2,4.7))
for p in policies:
    r=[x for x in rows if x[1]==p]; plt.plot([x[0] for x in r],[x[2] for x in r],marker='o',label=p)
plt.xlabel('Arrival rate (requests/slot)'); plt.ylabel('On-time task utility'); plt.title('Admission control prevents overload collapse'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v28_split_admission_utility.png',dpi=170); plt.close()
plt.figure(figsize=(7.2,4.7))
for p in policies:
    r=[x for x in rows if x[1]==p]; plt.plot([x[0] for x in r],[x[4] for x in r],marker='o',label=p)
plt.xlabel('Arrival rate (requests/slot)'); plt.ylabel('Deadline miss rate'); plt.title('Rejecting some refinements can improve real-time service'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v28_split_admission_deadline.png',dpi=170); plt.close()
print('wrote v28 split admission')
