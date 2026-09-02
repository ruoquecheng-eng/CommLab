from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

from commlab.otfs import otfs_modulate,otfs_demodulate,apply_delay_doppler_paths,effective_channel_matrix,linear_mmse_detect,omp_estimate_delay_doppler_paths
from commlab.modulation import QAMModem
from commlab.metrics import ber_with_wilson

ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'


def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(9051); N,M=6,12; shape=(N,M); modem=QAMModem(4)
    raw=[(0,0,1+0j),(2,1,.48*np.exp(.4j)),(4,-2,.30*np.exp(-.7j))]
    norm=np.sqrt(sum(abs(c)**2 for _,_,c in raw)); paths=[(d,k,c/norm) for d,k,c in raw]
    pilot=np.zeros(shape,complex); pilot[0,0]=1.0
    delay_candidates=list(range(0,6)); doppler_candidates=list(range(-2,3)); n_paths=len(paths)
    true_support={(d,float(k)) for d,k,_ in paths}
    mod=lambda G: otfs_modulate(G,0); dem=lambda w: otfs_demodulate(w,N,M,0)
    true_channel=lambda w: apply_delay_doppler_paths(w,paths,M,N)
    # Precompute one effective matrix per candidate path. OMP estimates can then
    # be converted to a full detector matrix by a cheap linear combination.
    basis={}
    for d in delay_candidates:
        for k in doppler_candidates:
            ch=lambda w,d=d,k=k: apply_delay_doppler_paths(w,[(d,k,1+0j)],M,N)
            basis[(d,float(k))]=effective_channel_matrix(mod,dem,shape,ch)
    Atrue=sum(c*basis[(d,float(k))] for d,k,c in paths)
    pilot_snrs=[0,5,10,15,20,25]; data_snr_db=16; data_nv=10**(-data_snr_db/10); rows=[]
    for psnr in pilot_snrs:
        pnv=10**(-psnr/10); support_ok=0; residuals=[]; gain_nmse=[]; err_est=err_true=total=0
        pilot_trials=40; data_per_estimate=10
        for trial in range(pilot_trials):
            yp=true_channel(mod(pilot))+np.sqrt(pnv/2)*(rng.normal(size=N*M)+1j*rng.normal(size=N*M)); Yp=dem(yp)
            est,rel=omp_estimate_delay_doppler_paths(Yp,pilot,delay_candidates,doppler_candidates,n_paths)
            got={(d,float(k)) for d,k,_ in est}; support_ok += int(got==true_support); residuals.append(rel)
            if got==true_support:
                td={(d,float(k)):c for d,k,c in paths}; ed={(d,float(k)):c for d,k,c in est}
                gain_nmse.append(sum(abs(ed[q]-td[q])**2 for q in td)/sum(abs(td[q])**2 for q in td))
            Aest=sum(c*basis[(d,float(k))] for d,k,c in est)
            for _ in range(data_per_estimate):
                bits=rng.integers(0,2,N*M*2,dtype=np.uint8); X=modem.modulate(bits).reshape(shape)
                y=true_channel(mod(X))+np.sqrt(data_nv/2)*(rng.normal(size=N*M)+1j*rng.normal(size=N*M)); Y=dem(y).reshape(-1)
                be=modem.demodulate(linear_mmse_detect(Y,Aest,data_nv)); bt=modem.demodulate(linear_mmse_detect(Y,Atrue,data_nv))
                err_est+=int(np.count_nonzero(be!=bits)); err_true+=int(np.count_nonzero(bt!=bits)); total+=len(bits)
        support_rate=support_ok/pilot_trials; mean_gain=float(np.mean(gain_nmse)) if gain_nmse else np.nan
        ber_est,lo,hi=ber_with_wilson(err_est,total); ber_true,_,_=ber_with_wilson(err_true,total)
        rows.append((psnr,support_rate,float(np.mean(residuals)),mean_gain,ber_est,lo,hi,ber_true))
        print(f'pilot={psnr:2d} dB support={support_rate:.3f} gainNMSE={mean_gain:.4g} estBER={ber_est:.4g} genieBER={ber_true:.4g}')
    with open(DATA/'otfs_sparse_path_estimation.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['pilot_snr_db','exact_support_probability','pilot_relative_residual','gain_nmse_when_support_correct','estimated_path_lmmse_ber','ci95_low','ci95_high','genie_lmmse_ber']); w.writerows(rows)
    q=np.array(rows,float)
    fig,ax1=plt.subplots(figsize=(7.6,4.9)); ax1.plot(q[:,0],q[:,1],'o-'); ax1.set_xlabel('OTFS pilot SNR (dB)'); ax1.set_ylabel('Exact sparse-path support probability'); ax1.set_ylim(-.03,1.03); ax1.grid(True,alpha=.3); ax1.set_title('OMP Delay-Doppler Path Acquisition'); fig.tight_layout(); fig.savefig(FIG/'otfs_path_support_recovery.png',dpi=180); plt.close(fig)
    plt.figure(figsize=(7.6,4.9)); plt.semilogy(q[:,0],np.maximum(q[:,4],1e-5),'o-',label='OMP-estimated paths'); plt.semilogy(q[:,0],np.maximum(q[:,7],1e-5),'o-',label='Genie physical paths'); plt.xlabel('OTFS pilot SNR (dB)'); plt.ylabel(f'Data BER at {data_snr_db} dB'); plt.title('OTFS Detection after Sparse Physical-Path Estimation'); plt.grid(True,which='both',alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'otfs_path_estimation_ber.png',dpi=180); plt.close()

if __name__=='__main__': main()
