from pathlib import Path
import csv, matplotlib.pyplot as plt
from commlab.computation import simulate_random_access_federated
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'results'/'data'; F=ROOT/'results'/'figures'; D.mkdir(parents=True,exist_ok=True); F.mkdir(parents=True,exist_ok=True)
slots=[6,8,10,12,14,16,18,20,24]; rows=[]
for nslot in slots:
    for mode in ['aloha','irsa']:
        o=simulate_random_access_federated(mode,n_clients=20,frame_slots=nslot,rounds=35,participation_prob=.8,heterogeneity=1.5,seed=2170)
        rows.append((nslot,mode,o['mean_decoded_fraction'],o['empty_round_fraction'],o['final_loss'],o['channel_uses'],o['loss_reduction_per_1000_uses']))
ref=simulate_random_access_federated('orthogonal',n_clients=20,rounds=35,participation_prob=.8,heterogeneity=1.5,seed=2170)
with (D/'v21_random_access_federated.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['frame_slots','access','decoded_fraction','empty_round_fraction','final_loss','channel_uses','loss_reduction_per_1000_uses']); w.writerows(rows); w.writerow(['orthogonal','orthogonal',1.0,0.0,ref['final_loss'],ref['channel_uses'],ref['loss_reduction_per_1000_uses']])
fig,ax=plt.subplots(figsize=(7.3,4.7))
for m in ['aloha','irsa']:
    rr=[r for r in rows if r[1]==m]; ax.plot([r[0] for r in rr],[r[2] for r in rr],'o-',label=m.upper())
ax.set(xlabel='Random-access frame slots',ylabel='Mean decoded fraction of active clients',ylim=(-.03,1.03),title='Random Access Determines Federated Participation'); ax.grid(alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(F/'v21_random_access_fl_decode.png',dpi=180); plt.close(fig)
fig,ax=plt.subplots(figsize=(7.3,4.7))
for m in ['aloha','irsa']:
    rr=[r for r in rows if r[1]==m]; ax.semilogy([r[0] for r in rr],[r[4] for r in rr],'o-',label=m.upper())
ax.axhline(ref['final_loss'],ls='--',label='Orthogonal FL'); ax.set(xlabel='Random-access frame slots',ylabel='Final global loss',title='Learning Degrades Only After Access Collapse'); ax.grid(alpha=.3,which='both'); ax.legend(); fig.tight_layout(); fig.savefig(F/'v21_random_access_fl_loss.png',dpi=180); plt.close(fig)
print(rows); print('orthogonal',ref)
