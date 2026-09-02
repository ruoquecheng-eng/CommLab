from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from commlab.mimo.cell_free import large_scale_fading
from commlab.mimo.ap_activation import strongest_ap_activation
from commlab.mimo.fronthaul_energy import simulate_cellfree_fronthaul_energy

ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'; FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(1604); M,K=24,8; aps=rng.uniform(0,1,(M,2)); users=rng.uniform(.05,.95,(K,2)); beta=large_scale_fading(aps,users,3.1,.04,2.0,rng)
rows=[]
for rho in [.995,.98,.95]:
    active=strongest_ap_activation(beta,16)
    for interval in [1,2,4,8,16,32]:
        r=simulate_cellfree_fronthaul_energy(beta,active,6,interval,rho,10,n_slots=500,seed=1605,energy_per_fronthaul_bit_j=5e-7)
        rows.append({'sweep':'mobility','rho':rho,'active_aps':16,'bits':6,'update_interval':interval,
                     **{k:r[k] for k in ['mean_user_rate','edge_rate','mean_sum_rate','fronthaul_power_w','total_power_w','energy_efficiency']}})
for n in [8,12,16,24]:
    active=strongest_ap_activation(beta,n)
    for bits in [3,4,6]:
        for interval in [1,4,8,16]:
            r=simulate_cellfree_fronthaul_energy(beta,active,bits,interval,.98,10,n_slots=250,seed=1606,energy_per_fronthaul_bit_j=5e-7)
            rows.append({'sweep':'joint','rho':.98,'active_aps':n,'bits':bits,'update_interval':interval,
                         **{k:r[k] for k in ['mean_user_rate','edge_rate','mean_sum_rate','fronthaul_power_w','total_power_w','energy_efficiency']}})
df=pd.DataFrame(rows); df.to_csv(DATA/'cellfree_fronthaul_energy_joint.csv',index=False)
fig,ax=plt.subplots(); mob=df[df.sweep=='mobility']
for rho in [.995,.98,.95]:
    s=mob[mob.rho==rho]; ax.plot(s.update_interval,s.energy_efficiency,marker='o',label=f'rho={rho}')
ax.set_xscale('log',base=2); ax.set_xlabel('CSI update interval (slots)'); ax.set_ylabel('Energy efficiency (sum-rate / W)'); ax.set_title('Mobility shifts the fronthaul-energy optimum'); ax.grid(True,alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(FIG/'cellfree_fronthaul_energy_vs_interval.png',dpi=180); plt.close(fig)
fig,ax=plt.subplots()
for rho in [.995,.98,.95]:
    s=mob[mob.rho==rho]; ax.plot(s.update_interval,s.edge_rate,marker='o',label=f'rho={rho}')
ax.set_xscale('log',base=2); ax.set_xlabel('CSI update interval (slots)'); ax.set_ylabel('5%-tile user rate'); ax.set_title('Stale CSI hurts mobile cell-edge users'); ax.grid(True,alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(FIG/'cellfree_fronthaul_edge_vs_interval.png',dpi=180); plt.close(fig)
j=df[df.sweep=='joint']; fig,ax=plt.subplots(); sc=ax.scatter(j.fronthaul_power_w,j.mean_sum_rate,s=25+8*j.active_aps,c=j.energy_efficiency); ax.set_xlabel('Fronthaul CSI power (W, abstract)'); ax.set_ylabel('Mean sum-rate'); ax.set_title('Joint AP / CSI / refresh design space'); fig.colorbar(sc,ax=ax,label='Energy efficiency'); ax.grid(True,alpha=.3); fig.tight_layout(); fig.savefig(FIG/'cellfree_fronthaul_joint_pareto.png',dpi=180); plt.close(fig)
print('Mobility sweep\n',mob.to_string(index=False)); print('\nTop joint EE configs\n',j.sort_values('energy_efficiency',ascending=False).head(10).to_string(index=False))
