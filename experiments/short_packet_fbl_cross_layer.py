from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt
from commlab.scheduling.short_packet import simulate_short_packet_goodput_trace

ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'results/data'; FIG=ROOT/'results/figures'; DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(1503); N=12000
true=rng.normal(5.0,3.0,N); est=true+2.2+rng.normal(0,.9,N)
ths=[-3,1,5,9]; eff=[.5,1,2,3]
rows=[]
for n in [80,120,200,400,800]:
    for scheme,aware,olla in [('Open-loop',False,False),('FBL-aware',True,False),('FBL+OLLA',True,True)]:
        r=simulate_short_packet_goodput_trace(true,est,ths,eff,n,target_bler=1e-2,fbl_aware=aware,use_olla=olla,seed=77)
        rows.append(dict(blocklength=n,scheme=scheme,**r))
with open(DATA/'short_packet_fbl_cross_layer.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
fig,ax=plt.subplots()
for method in ['Open-loop','FBL-aware','FBL+OLLA']:
    rr=[x for x in rows if x['scheme']==method]; ax.plot([x['blocklength'] for x in rr],[x['nack_rate'] for x in rr],marker='o',label=method)
ax.set_xscale('log'); ax.set_xlabel('Blocklength (complex uses)'); ax.set_ylabel('NACK rate'); ax.set_title('Finite-blocklength link adaptation'); ax.grid(True,alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(FIG/'short_packet_fbl_nack.png',dpi=180); plt.close(fig)
fig,ax=plt.subplots()
for method in ['Open-loop','FBL-aware','FBL+OLLA']:
    rr=[x for x in rows if x['scheme']==method]; ax.plot([x['blocklength'] for x in rr],[x['goodput_bits_per_use'] for x in rr],marker='o',label=method)
ax.set_xscale('log'); ax.set_xlabel('Blocklength (complex uses)'); ax.set_ylabel('Goodput (information bit/use)'); ax.set_title('Short-packet reliability vs spectral efficiency'); ax.grid(True,alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(FIG/'short_packet_fbl_goodput.png',dpi=180); plt.close(fig)
fig,ax=plt.subplots()
for method in ['Open-loop','FBL-aware','FBL+OLLA']:
    rr=[x for x in rows if x['scheme']==method]; ax.plot([x['blocklength'] for x in rr],[x['mean_mcs_index'] for x in rr],marker='o',label=method)
ax.set_xscale('log'); ax.set_xlabel('Blocklength'); ax.set_ylabel('Mean MCS index'); ax.set_title('Finite blocklength changes selected MCS'); ax.grid(True,alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(FIG/'short_packet_fbl_mcs.png',dpi=180); plt.close(fig)
print(rows)
