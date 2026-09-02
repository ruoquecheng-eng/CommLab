from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt
from commlab.mimo.cell_free import large_scale_fading,user_centric_mask,sample_cell_free_channel,clustered_mrt_precoder,per_user_rates
from commlab.mimo.fronthaul import quantize_complex_csi,csi_quantization_nmse,fronthaul_csi_bits

ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'results/data'; FIG=ROOT/'results/figures'; DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(1501); M,K=24,8
ap=rng.uniform(0,1,(M,2)); ue=rng.uniform(.08,.92,(K,2)); beta=large_scale_fading(ap,ue,shadow_std_db=2.0,rng=rng)
clusters=[4,8,24]; bits_list=[2,3,4,6,8]; trials=260; snr=10.0
Hs=[sample_cell_free_channel(beta,rng) for _ in range(trials)]
rows=[]
for L in clusters:
    mask=user_centric_mask(beta,L)
    for bits in bits_list:
        mean=[]; edge=[]; nm=[]
        for H in Hs:
            Hq=quantize_complex_csi(H,bits)
            W=clustered_mrt_precoder(Hq,mask=mask)
            r=per_user_rates(H,W,snr)
            mean.append(r.mean()); edge.append(np.percentile(r,5)); nm.append(csi_quantization_nmse(H,Hq))
        rows.append(dict(aps_per_user=L,bits_per_component=bits,mean_rate=np.mean(mean),edge_rate=np.mean(edge),
                         csi_nmse=np.mean(nm),fronthaul_bits_per_update=fronthaul_csi_bits(mask,bits)))
with open(DATA/'cell_free_fronthaul_csi.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
fig,ax=plt.subplots()
for L in clusters:
    rr=[x for x in rows if x['aps_per_user']==L]; ax.plot([x['fronthaul_bits_per_update'] for x in rr],[x['edge_rate'] for x in rr],marker='o',label=f'UC-{L}')
ax.set_xlabel('CSI fronthaul bits / update'); ax.set_ylabel('Mean 5%-tile user rate (bit/s/Hz)'); ax.set_title('Cell-Free CSI fidelity vs fronthaul'); ax.grid(True,alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(FIG/'cell_free_fronthaul_edge_rate.png',dpi=180); plt.close(fig)
fig,ax=plt.subplots()
for L in clusters:
    rr=[x for x in rows if x['aps_per_user']==L]; ax.semilogy([x['bits_per_component'] for x in rr],[x['csi_nmse'] for x in rr],marker='o',label=f'UC-{L}')
ax.set_xlabel('Quantization bits / real component'); ax.set_ylabel('CSI quantization NMSE'); ax.set_title('Quantized distributed CSI'); ax.grid(True,which='both',alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(FIG/'cell_free_fronthaul_nmse.png',dpi=180); plt.close(fig)
print(rows)
