from pathlib import Path
import csv, numpy as np
import matplotlib.pyplot as plt
from commlab.computation import simulate_split_inference
OUT=Path('results/data'); FIG=Path('results/figures'); OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rows=[]
for snr in [0,5,10,15,20]:
    for th in [.55,.65,.75,.85,.92]:
        vals=[simulate_split_inference(snr_db=snr,confidence_threshold=th,mode='adaptive',n_samples=10000,seed=23400+s) for s in range(8)]
        rows.append({'snr_db':snr,'threshold':th,'accuracy':np.mean([v['accuracy'] for v in vals]),'channel_uses':np.mean([v['mean_channel_uses'] for v in vals]),'offload_fraction':np.mean([v['offload_fraction'] for v in vals]),'mean_latency_ms':np.mean([v['mean_latency_ms'] for v in vals])})
for snr in [0,5,10,15,20]:
    for mode in ['local','edge']:
        vals=[simulate_split_inference(snr_db=snr,mode=mode,n_samples=10000,seed=23400+s) for s in range(8)]
        rows.append({'snr_db':snr,'threshold':-1 if mode=='local' else 2,'accuracy':np.mean([v['accuracy'] for v in vals]),'channel_uses':np.mean([v['mean_channel_uses'] for v in vals]),'offload_fraction':np.mean([v['offload_fraction'] for v in vals]),'mean_latency_ms':np.mean([v['mean_latency_ms'] for v in vals])})
with open(OUT/'v23_split_inference.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
plt.figure()
for snr in [0,10,20]:
    rr=[r for r in rows if r['snr_db']==snr and 0<r['threshold']<1];plt.plot([r['channel_uses'] for r in rr],[r['accuracy'] for r in rr],marker='o',label=f'{snr} dB adaptive')
plt.xlabel('Mean residual-feature channel uses');plt.ylabel('Classification accuracy');plt.legend();plt.tight_layout();plt.savefig(FIG/'v23_split_accuracy_resource.png',dpi=180);plt.close()
plt.figure()
for snr in [0,10,20]:
    rr=[r for r in rows if r['snr_db']==snr and 0<r['threshold']<1];plt.plot([r['mean_latency_ms'] for r in rr],[r['accuracy'] for r in rr],marker='o',label=f'{snr} dB')
plt.xlabel('Mean end-to-end latency (ms)');plt.ylabel('Classification accuracy');plt.legend();plt.tight_layout();plt.savefig(FIG/'v23_split_accuracy_latency.png',dpi=180);plt.close()
plt.figure()
for th in [.55,.75,.92]:
    rr=[r for r in rows if r['threshold']==th];plt.plot([r['snr_db'] for r in rr],[r['accuracy'] for r in rr],marker='o',label=f'th={th}')
plt.xlabel('Offload SNR (dB)');plt.ylabel('Adaptive accuracy');plt.legend();plt.tight_layout();plt.savefig(FIG/'v23_split_snr.png',dpi=180);plt.close()
print(rows)
