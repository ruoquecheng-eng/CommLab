from pathlib import Path
import csv, numpy as np
import matplotlib.pyplot as plt
from commlab.computation import simulate_federated_distillation
OUT=Path('results/data'); FIG=Path('results/figures'); OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rows=[]
for snr in [0,5,10,20]:
    for m in [4,6,8,12,16,24]:
        vals=[simulate_federated_distillation(public_probes=m,snr_db=snr,seed=2420+s) for s in range(18)]
        rows.append({'snr_db':snr,'public_probes':m,'model_accuracy':np.mean([v['model_average_accuracy'] for v in vals]),'distilled_accuracy':np.mean([v['distilled_accuracy'] for v in vals]),'upload_scalars':10*m,'compression_ratio':24/m})
with open(OUT/'v24_federated_distillation.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
plt.figure()
for snr in [0,5,10,20]:
    rr=[r for r in rows if r['snr_db']==snr]; plt.plot([r['upload_scalars'] for r in rr],[r['distilled_accuracy'] for r in rr],marker='o',label=f'{snr} dB')
plt.axvline(240,linestyle='--',label='full-model upload scalars'); plt.xlabel('Uploaded teacher scalars / round'); plt.ylabel('Distilled task accuracy'); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v24_distillation_accuracy_budget.png',dpi=180); plt.close()
plt.figure()
for m in [6,8,12]:
    rr=[r for r in rows if r['public_probes']==m]; plt.plot([r['snr_db'] for r in rr],[r['distilled_accuracy'] for r in rr],marker='o',label=f'{m} probes')
plt.xlabel('Logit-upload SNR (dB)'); plt.ylabel('Distilled accuracy'); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'v24_distillation_snr.png',dpi=180); plt.close()
print([r for r in rows if r['snr_db']==10])
