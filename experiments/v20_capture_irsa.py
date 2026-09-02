from pathlib import Path
import csv,numpy as np,matplotlib.pyplot as plt
from commlab.random_access import simulate_capture_irsa
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'results'/'data'; F=ROOT/'results'/'figures'; D.mkdir(parents=True,exist_ok=True); F.mkdir(parents=True,exist_ok=True)
rows=[]; loads=np.linspace(.2,1.2,11)
for ps in [0,6,9]:
    for i,G in enumerate(loads):
        o=simulate_capture_irsa(float(G),frame_slots=120,n_frames=160,power_spread_db=ps,sinr_threshold_db=3,seed=2200+ps*20+i)
        rows.append((ps,G,o['throughput'],o['packet_loss_rate'],o['mean_sic_iterations']))
with (D/'v20_capture_irsa.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['power_spread_db','offered_load','throughput','packet_loss_rate','sic_iterations']); w.writerows(rows)
fig,ax=plt.subplots(figsize=(7.2,4.6));
for ps in [0,6,9]:
    rr=[r for r in rows if r[0]==ps]; ax.plot([r[1] for r in rr],[r[2] for r in rr],'o-',label=f'{ps} dB power spread')
ax.set(xlabel='Offered load G (packets/slot)',ylabel='Decoded throughput (packets/slot)',title='Capture-Aware IRSA: Power-Domain Structure Helps SIC'); ax.grid(alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(F/'v20_capture_irsa_throughput.png',dpi=180); plt.close(fig)
fig,ax=plt.subplots(figsize=(7.2,4.6));
for ps in [0,6,9]:
    rr=[r for r in rows if r[0]==ps]; ax.semilogy([r[1] for r in rr],[max(r[3],1e-4) for r in rr],'o-',label=f'{ps} dB power spread')
ax.set(xlabel='Offered load G',ylabel='Packet loss rate',title='Capture-Aware IRSA Packet Loss'); ax.grid(alpha=.3,which='both'); ax.legend(); fig.tight_layout(); fig.savefig(F/'v20_capture_irsa_plr.png',dpi=180); plt.close(fig)
print(rows)
