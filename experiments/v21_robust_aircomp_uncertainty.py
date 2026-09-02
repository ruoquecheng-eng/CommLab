from pathlib import Path
import csv,numpy as np,matplotlib.pyplot as plt
from commlab.computation import optimize_ris_aircomp,optimize_robust_ris_aircomp,effective_ris_aircomp_channel,simulate_lcb_cellfree_aircomp
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'results'/'data'; F=ROOT/'results'/'figures'; D.mkdir(parents=True,exist_ok=True); F.mkdir(parents=True,exist_ok=True)
errs=[0,.05,.1,.2,.3,.5]; risrows=[]
for err in errs:
    vals=[]
    for t in range(40):
        rng=np.random.default_rng(7000+t); K,N=8,12
        hd=(rng.normal(size=K)+1j*rng.normal(size=K))/np.sqrt(2)*.2
        Fr=(rng.normal(size=(K,N))+1j*rng.normal(size=(K,N)))/np.sqrt(2*N)
        g=(rng.normal(size=N)+1j*rng.normal(size=N))/np.sqrt(2*N)
        hdh=hd+(rng.normal(size=K)+1j*rng.normal(size=K))/np.sqrt(2)*(err*.2)
        Fh=Fr+(rng.normal(size=(K,N))+1j*rng.normal(size=(K,N)))/np.sqrt(2)*(err/np.sqrt(N))
        gh=g+(rng.normal(size=N)+1j*rng.normal(size=N))/np.sqrt(2)*(err/np.sqrt(N))
        pn=optimize_ris_aircomp(hdh,Fh,gh,bits=2,sweeps=3,objective='maxmin')[0]
        pr=optimize_robust_ris_aircomp(hdh,Fh,gh,error_std=err,bits=2,sweeps=3,n_uncertainty=64,quantile=.25,seed=8000+t)[0]
        wn=np.min(np.abs(effective_ris_aircomp_channel(hd,Fr,g,pn))); wr=np.min(np.abs(effective_ris_aircomp_channel(hd,Fr,g,pr)))
        vals.append((wn,wr))
    a=np.asarray(vals); risrows.append((err,a[:,0].mean(),a[:,1].mean(),np.quantile(a[:,0],.1),np.quantile(a[:,1],.1),np.mean(a[:,1]>a[:,0])))
with (D/'v21_robust_ris_aircomp.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['relative_csi_error','naive_mean_weakest_gain','robust_mean_weakest_gain','naive_p10_weakest_gain','robust_p10_weakest_gain','robust_win_fraction']); w.writerows(risrows)
fig,ax=plt.subplots(figsize=(7.3,4.7)); ax.plot([r[0] for r in risrows],[r[1] for r in risrows],'o-',label='Naive estimated-CSI max-min'); ax.plot([r[0] for r in risrows],[r[2] for r in risrows],'s-',label='Uncertainty-sampled robust'); ax.set(xlabel='Relative CSI uncertainty',ylabel='Mean true weakest device gain',title='RIS-AirComp Under CSI Uncertainty'); ax.grid(alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(F/'v21_robust_ris_aircomp_mean.png',dpi=180); plt.close(fig)
fig,ax=plt.subplots(figsize=(7.3,4.7)); ax.plot([r[0] for r in risrows],[r[3] for r in risrows],'o-',label='Naive 10%-tile'); ax.plot([r[0] for r in risrows],[r[4] for r in risrows],'s-',label='Robust 10%-tile'); ax.set(xlabel='Relative CSI uncertainty',ylabel='10%-tile true weakest gain',title='RIS-AirComp Lower-Tail Robustness'); ax.grid(alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(F/'v21_robust_ris_aircomp_tail.png',dpi=180); plt.close(fig)
cfrows=[]
for e in [.1,.2,.3,.4,.5,.7]:
    o=simulate_lcb_cellfree_aircomp(max_csi_error=e,n_trials=140,z=.5,seed=2290)
    cfrows.append((e,o['naive_median_mse'],o['lcb_median_mse'],o['naive_p90_mse'],o['lcb_p90_mse'],o['lcb_win_fraction']))
with (D/'v21_cellfree_aircomp_imperfect_csi.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['max_ap_csi_error','naive_median_mse','lcb_median_mse','naive_p90_mse','lcb_p90_mse','lcb_win_fraction']); w.writerows(cfrows)
fig,ax=plt.subplots(figsize=(7.3,4.7)); ax.semilogy([r[0] for r in cfrows],[r[3] for r in cfrows],'o-',label='Naive p90 MSE'); ax.semilogy([r[0] for r in cfrows],[r[4] for r in cfrows],'s-',label='Uncertainty-aware LCB p90 MSE'); ax.set(xlabel='Worst AP CSI error std',ylabel='90%-tile aggregation MSE',title='Cell-Free AirComp: Tail Risk under Heterogeneous CSI Quality'); ax.grid(alpha=.3,which='both'); ax.legend(); fig.tight_layout(); fig.savefig(F/'v21_cellfree_aircomp_imperfect_csi.png',dpi=180); plt.close(fig)
print('RIS',risrows); print('Cell-free',cfrows)
