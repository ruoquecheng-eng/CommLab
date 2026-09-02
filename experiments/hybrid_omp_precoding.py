from pathlib import Path
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from commlab.mimo import sparse_geometric_mimo_channel, dft_codebook, hybrid_omp_precoder, precoded_mimo_rate, full_digital_svd_rate
ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results/figures'; DATA=ROOT/'results/data'; FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(1205); nr=8; nt=32; ns=2; snr=10.; trials=450
rows=[]
for q in [2,3,4,6,8]:
    ro=[]; rd=[]; rf=[]
    for _ in range(trials):
        H,_,_=sparse_geometric_mimo_channel(nr,nt,5,rng)
        full=full_digital_svd_rate(H,snr,ns)
        # Non-iterative DFT selection baseline: rank beams once by raw received energy,
        # then least-squares fit the dominant SVD subspace.
        D=dft_codebook(nt); score=np.sum(np.abs(H@D)**2,axis=0); idx=np.argsort(score)[-q:]; Frf=D[:,idx]
        _,_,Vh=np.linalg.svd(H,full_matrices=False); Fopt=Vh.conj().T[:,:ns]; Fbb=np.linalg.pinv(Frf)@Fopt; Fd=Frf@Fbb; Fd*=np.sqrt(ns/np.sum(np.abs(Fd)**2))
        Fo=hybrid_omp_precoder(H,ns,q)
        rf.append(full); rd.append(precoded_mimo_rate(H,Fd,snr,ns)); ro.append(precoded_mimo_rate(H,Fo,snr,ns))
    rows.append(dict(rf_chains=q,full_digital=np.mean(rf),dft_one_shot=np.mean(rd),omp_hybrid=np.mean(ro),omp_fraction_of_full=np.mean(ro)/np.mean(rf)))
df=pd.DataFrame(rows); df.to_csv(DATA/'hybrid_omp_precoding.csv',index=False)
fig,ax=plt.subplots(figsize=(7,4.5)); ax.plot(df.rf_chains,df.full_digital,marker='o',label='Full digital SVD'); ax.plot(df.rf_chains,df.dft_one_shot,marker='o',label='One-shot DFT selection'); ax.plot(df.rf_chains,df.omp_hybrid,marker='o',label='OMP hybrid'); ax.set_xlabel('Tx RF chains'); ax.set_ylabel('Mean rate (bit/s/Hz)'); ax.grid(True,alpha=.25); ax.legend(); fig.tight_layout(); fig.savefig(FIG/'hybrid_omp_precoding_rate.png',dpi=180); plt.close(fig)
print(df.to_string(index=False))
