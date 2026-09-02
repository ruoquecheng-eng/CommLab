from pathlib import Path
import csv, numpy as np, matplotlib.pyplot as plt
from commlab.otfs import otfs_modulate, otfs_demodulate, apply_fractional_delay_doppler_paths, refine_fractional_delay_doppler_paths
ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'

def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True); rng=np.random.default_rng(1105)
    N=M=8; P=np.zeros((N,M),complex); P[0,0]=1; x=otfs_modulate(P,0); true_d=2.35; true_k=1.42; rows=[]
    for snr_db in (10,15,20,25,30):
        de=[]; ke=[]; res=[]
        for _ in range(18):
            y=apply_fractional_delay_doppler_paths(x,[(true_d,true_k,1+.2j)],M,N); nv=np.mean(abs(y)**2)/10**(snr_db/10); y=y+np.sqrt(nv/2)*(rng.normal(size=len(y))+1j*rng.normal(size=len(y))); Y=otfs_demodulate(y,N,M,0)
            ref,rr=refine_fractional_delay_doppler_paths(Y,P,[(2,1,1+0j)],.65,.7,points=11,coordinate_passes=2); d,k,_=ref[0]; de.append(abs(d-true_d)); ke.append(abs(k-true_k)); res.append(rr)
        rows.append((snr_db,.35,.42,np.mean(de),np.mean(ke),np.mean(res))); print(snr_db,rows[-1])
    with open(DATA/'otfs_fractional_delay_refinement.csv','w',newline='') as f: csv.writer(f).writerows([['pilot_snr_db','coarse_delay_error','coarse_doppler_error','refined_delay_mae','refined_doppler_mae','relative_residual'],*rows])
    a=np.asarray(rows,float); plt.figure(figsize=(7.4,4.9)); plt.axhline(.35,ls='--',label='Coarse delay error'); plt.axhline(.42,ls=':',label='Coarse Doppler error'); plt.plot(a[:,0],a[:,3],'o-',label='Refined delay MAE'); plt.plot(a[:,0],a[:,4],'s-',label='Refined Doppler MAE'); plt.yscale('log'); plt.xlabel('Pilot SNR (dB)'); plt.ylabel('Absolute grid-bin error'); plt.title('OTFS: Joint Fractional Delay/Doppler Grid Refinement'); plt.grid(True,which='both',alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'otfs_fractional_delay_refinement.png',dpi=180); plt.close()
if __name__=='__main__': main()
