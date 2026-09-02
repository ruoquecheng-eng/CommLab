from pathlib import Path
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from commlab.mimo.cell_free import large_scale_fading, sample_cell_free_channel
from commlab.mimo.ap_activation import strongest_ap_activation, coverage_aware_ap_activation, rates_with_active_aps, network_energy_efficiency
ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results/figures'; DATA=ROOT/'results/data'; FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(1405); M=32; K=8; snr=10**(-3/10); drops=90; counts=[4,8,12,16,24,32]; rows=[]
for n in counts:
    for scheme in ['Strongest aggregate','Coverage-aware']:
        vals=[]
        for _ in range(drops):
            aps=rng.uniform(0,1,(M,2)); users=rng.uniform(0,1,(K,2)); beta=large_scale_fading(aps,users,pathloss_exp=3.0,min_distance=.05,shadow_std_db=2.5,rng=rng); H=sample_cell_free_channel(beta,rng)
            active=strongest_ap_activation(beta,n) if scheme.startswith('Strongest') else coverage_aware_ap_activation(beta,n)
            r=rates_with_active_aps(H,active,snr); sr=r.sum(); vals.append((r.mean(),np.quantile(r,.05),network_energy_efficiency(sr,n,tx_power_w=1,circuit_power_per_ap_w=.12,fixed_power_w=.6)))
        a=np.asarray(vals); rows.append(dict(active_aps=n,scheme=scheme,mean_user_rate=a[:,0].mean(),mean_5pct_rate=a[:,1].mean(),energy_efficiency=a[:,2].mean()))
df=pd.DataFrame(rows); df.to_csv(DATA/'cell_free_ap_activation_energy.csv',index=False)
for col,ylabel,fname in [('mean_5pct_rate','Mean 5%-tile user rate (bit/s/Hz)','cell_free_ap_activation_edge_rate.png'),('energy_efficiency','Rate / modeled power (bit/s/Hz/W)','cell_free_ap_activation_energy_efficiency.png')]:
    fig,ax=plt.subplots(figsize=(6.8,4.5))
    for name,g in df.groupby('scheme'): ax.plot(g.active_aps,g[col],marker='o',label=name)
    ax.set_xlabel('Active APs'); ax.set_ylabel(ylabel); ax.grid(True,alpha=.25); ax.legend(); fig.tight_layout(); fig.savefig(FIG/fname,dpi=180); plt.close(fig)
print(df.to_string(index=False))
