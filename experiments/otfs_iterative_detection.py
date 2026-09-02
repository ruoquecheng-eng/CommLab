from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

from commlab.otfs import otfs_modulate, otfs_demodulate, apply_delay_doppler_paths, effective_channel_matrix, linear_mmse_detect, sparsify_channel_matrix, cg_lmmse_detect
from commlab.modulation import QAMModem

ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'


def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(704); modem=QAMModem(4); shape=(6,12); cp=3
    paths=[(0,0.0,1.0+0j),(2,1.4,0.48*np.exp(.4j)),(1,-.8,0.24*np.exp(-.7j))]
    mod=lambda X: otfs_modulate(X,cp); dem=lambda y: otfs_demodulate(y,*shape,cp)
    chan=lambda x: apply_delay_doppler_paths(x,paths,shape[1],shape[0])
    A=effective_channel_matrix(mod,dem,shape,chan); n=A.shape[0]
    densities=[2,3,5,8,n]; mats={k:sparsify_channel_matrix(A,k) for k in densities[:-1]}; mats[n]=A
    snr_db=14; nv=10**(-snr_db/10); rows=[]
    for k in densities:
        H=mats[k]; errs=0; bits_total=0; its=[]; residual=[]
        retained=float(np.sum(np.abs(H)**2)/np.sum(np.abs(A)**2))
        for _ in range(140):
            bits=rng.integers(0,2,n*2,dtype=np.uint8); X=modem.modulate(bits).reshape(shape)
            y=dem(chan(mod(X))).reshape(-1); noise=np.sqrt(nv/2)*(rng.normal(size=n)+1j*rng.normal(size=n)); y=y+noise
            xh,it,rel=cg_lmmse_detect(y,H,nv,max_iter=60,tol=1e-7); bh=modem.demodulate(xh)
            errs+=int(np.count_nonzero(bh!=bits)); bits_total+=len(bits); its.append(it); residual.append(rel)
        ber=errs/bits_total; rows.append((k,retained,ber,float(np.mean(its)),float(np.mean(residual))))
        print(f'keep={k:2d}/{n} energy={100*retained:.2f}% BER={ber:.4g} CGiter={np.mean(its):.1f}')
    # direct full LMMSE consistency/performance reference
    errs=0; total=0
    for _ in range(80):
        bits=rng.integers(0,2,n*2,dtype=np.uint8); X=modem.modulate(bits).reshape(shape); y=dem(chan(mod(X))).reshape(-1); y+=np.sqrt(nv/2)*(rng.normal(size=n)+1j*rng.normal(size=n)); bh=modem.demodulate(linear_mmse_detect(y,A,nv)); errs+=int(np.count_nonzero(bh!=bits)); total+=len(bits)
    direct=errs/total; print(f'Direct full LMMSE BER={direct:.4g}')
    with open(DATA/'otfs_iterative_detection.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['coefficients_per_row','retained_channel_energy','ber','mean_cg_iterations','mean_relative_residual']); w.writerows(rows); w.writerow(['direct_full',1.0,direct,'n/a','n/a'])
    a=np.asarray(rows,float); plt.figure(figsize=(7.2,4.8)); plt.semilogy(a[:,0],np.maximum(a[:,2],1e-5),'o-'); plt.axhline(max(direct,1e-5),ls='--',label='Direct full LMMSE'); plt.xlabel('Strongest channel coefficients retained per row'); plt.ylabel('BER'); plt.title(f'Sparse CG-LMMSE OTFS Detector at {snr_db} dB'); plt.grid(True,which='both',alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'otfs_sparse_cg_ber.png',dpi=180); plt.close()
    plt.figure(figsize=(7.2,4.8)); plt.plot(a[:,0],100*a[:,1],'o-',label='Retained channel energy'); ax2=plt.gca().twinx(); ax2.plot(a[:,0],a[:,3],'s--',label='CG iterations'); plt.xlabel('Coefficients retained per row'); plt.ylabel('Channel energy retained (%)'); ax2.set_ylabel('Mean CG iterations'); plt.title('OTFS Sparsity / Iterative-Complexity Trade-off'); plt.grid(True,alpha=.3); plt.tight_layout(); plt.savefig(FIG/'otfs_sparse_cg_complexity.png',dpi=180); plt.close()

if __name__=='__main__': main()
