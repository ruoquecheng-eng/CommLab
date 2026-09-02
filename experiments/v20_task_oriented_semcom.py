from pathlib import Path
import csv,matplotlib.pyplot as plt
from commlab.computation import simulate_task_oriented_classification
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'results'/'data'; F=ROOT/'results'/'figures'; D.mkdir(parents=True,exist_ok=True); F.mkdir(parents=True,exist_ok=True)
rows=[]
for i,snr in enumerate([-5,0,5,10,15,20]):
    o=simulate_task_oriented_classification(dim=16,n_samples=15000,separation=2.0,snr_db=snr,seed=2150+i)
    rows.append((snr,o['raw_accuracy'],o['task_accuracy'],o['raw_reconstruction_mse'],o['task_reconstruction_mse'],o['raw_channel_uses'],o['task_channel_uses']))
with (D/'v20_task_oriented_semcom.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['snr_db','raw_accuracy','task_accuracy','raw_reconstruction_mse','task_reconstruction_mse','raw_channel_uses','task_channel_uses']); w.writerows(rows)
fig,ax=plt.subplots(figsize=(7.2,4.6)); ax.plot([r[0] for r in rows],[r[1] for r in rows],'o-',label='Raw 16-D features (16 uses)'); ax.plot([r[0] for r in rows],[r[2] for r in rows],'s-',label='Task statistic (1 use)'); ax.set(xlabel='SNR (dB)',ylabel='Classification accuracy',ylim=(0.45,1.01),title='Task-Oriented Communication: Utility per Channel Use'); ax.grid(alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(F/'v20_task_semcom_accuracy.png',dpi=180); plt.close(fig)
fig,ax=plt.subplots(figsize=(7.2,4.6)); ax.semilogy([r[0] for r in rows],[r[3] for r in rows],'o-',label='Raw feature reconstruction'); ax.semilogy([r[0] for r in rows],[r[4] for r in rows],'s-',label='Task-statistic rank-1 reconstruction'); ax.set(xlabel='SNR (dB)',ylabel='Source reconstruction MSE',title='Task Utility Does Not Imply Source Fidelity'); ax.grid(alpha=.3,which='both'); ax.legend(); fig.tight_layout(); fig.savefig(F/'v20_task_semcom_reconstruction.png',dpi=180); plt.close(fig)
print(rows)
