from pathlib import Path
import numpy as np, matplotlib.pyplot as plt
from commlab.random_access.irsa import simulate_irsa

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'results'/'data'; FIG=ROOT/'results'/'figures'; OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
loads=np.linspace(.1,1.15,12); rows=[]
schemes=[('Slotted ALOHA',{1:1.0},False),('Rep-3 / no SIC',{3:1.0},False),('IRSA SIC',{2:.50,3:.28,8:.22},True)]
for i,g in enumerate(loads):
    for name,dist,sic in schemes:
        o=simulate_irsa(100,float(g),300,dist,sic,seed=1900+i)
        rows.append((g,name,o['throughput_packets_per_slot'],o['packet_loss_rate'],o['replicas_per_decoded_packet'],o['mean_sic_iterations']))
arr=np.array(rows,dtype=object)
with open(OUT/'irsa_coded_random_access.csv','w') as f:
    f.write('offered_load,scheme,throughput,packet_loss_rate,replicas_per_decoded,mean_iterations\n')
    for r in rows: f.write(','.join(map(str,r))+'\n')
fig,ax=plt.subplots(figsize=(7,4.5))
for name,_,_ in schemes:
    rr=[r for r in rows if r[1]==name]; ax.plot([r[0] for r in rr],[r[2] for r in rr],'o-',label=name)
ax.plot(loads,loads,'--',alpha=.4,label='offered load'); ax.set(xlabel='Offered load G (packet/slot)',ylabel='Decoded throughput (packet/slot)',title='Coded Random Access: Iterative SIC Gain'); ax.grid(alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(FIG/'irsa_throughput.png',dpi=180); plt.close(fig)
fig,ax=plt.subplots(figsize=(7,4.5))
for name,_,_ in schemes:
    rr=[r for r in rows if r[1]==name]; ax.semilogy([r[0] for r in rr],np.maximum([r[3] for r in rr],1e-4),'o-',label=name)
ax.set(xlabel='Offered load G',ylabel='Packet loss rate',title='IRSA Reliability vs Offered Load'); ax.grid(alpha=.3,which='both'); ax.legend(); fig.tight_layout(); fig.savefig(FIG/'irsa_packet_loss.png',dpi=180); plt.close(fig)
print(rows[-3:])
