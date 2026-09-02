from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt
from commlab.mimo import mu_mrt_precoder, mu_zf_precoder, downlink_sinr, sum_rate_from_sinr, jain_fairness, favorable_propagation_metric
ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'

def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True); rng=np.random.default_rng(1102)
    users=4; snr=10**(10/10); rows=[]
    for nt in (4,8,16,32,64):
        rr=[]; hard=[]; fav=[]; mrt=[]; zf=[]; fair_m=[]; fair_z=[]
        for _ in range(1200):
            H=(rng.normal(size=(users,nt))+1j*rng.normal(size=(users,nt)))/np.sqrt(2)
            s_m=downlink_sinr(H,mu_mrt_precoder(H),snr); s_z=downlink_sinr(H,mu_zf_precoder(H),snr)
            r_m=np.log2(1+s_m); r_z=np.log2(1+s_z)
            mrt.append(np.sum(r_m)); zf.append(np.sum(r_z)); fair_m.append(jain_fairness(r_m)); fair_z.append(jain_fairness(r_z)); fav.append(favorable_propagation_metric(H))
            norms=np.sum(np.abs(H)**2,axis=1)/nt; hard.extend(norms)
        rows.append((nt,np.mean(mrt),np.mean(zf),np.mean(fair_m),np.mean(fair_z),np.mean(fav),np.std(hard)/np.mean(hard)))
        print('Nt',nt,'MRT/ZF',np.mean(mrt),np.mean(zf),'fav',np.mean(fav))
    with open(DATA/'massive_mimo_precoding.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['n_tx','mrt_sum_rate','zf_sum_rate','mrt_jain','zf_jain','mean_interuser_corr','channel_hardening_cv']); w.writerows(rows)
    a=np.asarray(rows,float); plt.figure(figsize=(7.4,4.9)); plt.plot(a[:,0],a[:,1],'o-',label='MRT'); plt.plot(a[:,0],a[:,2],'s-',label='ZF'); plt.xlabel('Base-station antennas'); plt.ylabel('Mean sum spectral efficiency (bit/s/Hz)'); plt.title('4-user MU-MIMO: Array Size vs Downlink Throughput'); plt.grid(alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'massive_mimo_sum_rate.png',dpi=180); plt.close()
    plt.figure(figsize=(7.4,4.9)); plt.plot(a[:,0],a[:,5],'o-',label='Mean inter-user correlation'); plt.plot(a[:,0],a[:,6],'s-',label='Channel-norm coefficient of variation'); plt.xlabel('Base-station antennas'); plt.ylabel('Metric'); plt.title('Massive-MIMO Favorable Propagation and Channel Hardening'); plt.grid(alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'massive_mimo_hardening.png',dpi=180); plt.close()
if __name__=='__main__': main()
