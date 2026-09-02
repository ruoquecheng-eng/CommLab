from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt
from commlab.computation import simulate_semantic_harq
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'results'/'data'; FIG=ROOT/'results'/'figures'; DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rows=[]
for snr in [-4,-2,0,2,4,6]:
    for p in ['no_harq','channel_harq','task_harq']:
        rr=[simulate_semantic_harq(n_samples=10000,policy=p,mean_snr_db=snr,seed=s) for s in range(5)]
        rows.append([snr,p,*[np.mean([x[k] for x in rr]) for k in ['accuracy','hard_sample_accuracy','p90_batch_error','mean_channel_uses','retransmission_rate']]])
with (DATA/'v32_semantic_harq.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['snr_db','policy','accuracy','hard_sample_accuracy','p90_batch_error','mean_channel_uses','retransmission_rate']); w.writerows(rows)
plt.figure(figsize=(7.2,4.7))
for p in ['no_harq','channel_harq','task_harq']:
    r=[x for x in rows if x[1]==p]; plt.plot([x[0] for x in r],[100*x[3] for x in r],marker='o',label=p)
plt.xlabel('Mean SNR (dB)'); plt.ylabel('Hard-sample accuracy (%)'); plt.title('Task-confidence HARQ protects decision-boundary samples'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v32_semantic_harq_hard_accuracy.png',dpi=170); plt.close()
plt.figure(figsize=(7.2,4.7))
for p in ['channel_harq','task_harq']:
    r=[x for x in rows if x[1]==p]; plt.plot([x[0] for x in r],[x[5] for x in r],marker='o',label=p)
plt.xlabel('Mean SNR (dB)'); plt.ylabel('Mean channel uses/sample'); plt.title('Task-driven retransmission cost falls as confidence improves'); plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v32_semantic_harq_cost.png',dpi=170); plt.close()
print('wrote v32 semantic HARQ')
