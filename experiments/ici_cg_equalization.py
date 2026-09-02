from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt
from commlab.equalization import time_varying_ofdm_channel_matrix, linear_lmmse_ici_detect, cg_lmmse_ici_detect, band_limit_channel_matrix, ici_energy_fraction
from commlab.modulation import QAMModem
ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'

def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True); rng=np.random.default_rng(814); modem=QAMModem(4)
    n=48; H=time_varying_ofdm_channel_matrix(np.array([1,.6*np.exp(.5j)]),np.array([0,3]),np.array([0.,1.5]),n_fft=n,cp_len=8); ici=ici_energy_fraction(H); rows=[]
    for snr_db in (6,10,14,18,22):
        nv=10**(-snr_db/10); nframes=260; err={b:0 for b in (0,1,2,4)}; bits_total=0; iters={b:[] for b in (1,2,4)}; rels={b:[] for b in (1,2,4)}
        for _ in range(nframes):
            bits=rng.integers(0,2,n*2,dtype=np.uint8); x=modem.modulate(bits); y=H@x+np.sqrt(nv/2)*(rng.normal(size=n)+1j*rng.normal(size=n));
            # one-tap baseline from diagonal
            z0=y/np.where(abs(np.diag(H))>1e-12,np.diag(H),1); err[0]+=np.count_nonzero(modem.demodulate(z0)!=bits)
            for bw in (1,2,4):
                z,it,rel=cg_lmmse_ici_detect(y,H,nv,bandwidth=bw,max_iter=80,tol=1e-7); err[bw]+=np.count_nonzero(modem.demodulate(z)!=bits); iters[bw].append(it); rels[bw].append(rel)
            bits_total+=len(bits)
        row=[snr_db,ici,err[0]/bits_total]
        for bw in (1,2,4): row += [err[bw]/bits_total,float(np.mean(iters[bw])),float(np.mean(rels[bw])),int(np.count_nonzero(band_limit_channel_matrix(H,bw)))]
        rows.append(row); print('SNR',snr_db,'ICI',ici,'one',row[2],'bands',[(b,err[b]/bits_total,np.mean(iters[b])) for b in (1,2,4)])
    hdr=['snr_db','ici_energy_fraction','one_tap_ber']
    for bw in (1,2,4): hdr += [f'cg_bw{bw}_ber',f'cg_bw{bw}_iterations',f'cg_bw{bw}_relres',f'cg_bw{bw}_nnz']
    with open(DATA/'ici_cg_equalization.csv','w',newline='') as f: w=csv.writer(f); w.writerow(hdr); w.writerows(rows)
    a=np.asarray(rows,float); plt.figure(figsize=(7.4,4.9)); plt.semilogy(a[:,0],a[:,2],'o-',label='One-tap');
    for j,b,m in [(3,1,'s-'),(7,2,'^-'),(11,4,'d-')]: plt.semilogy(a[:,0],np.maximum(a[:,j],1e-5),m,label=f'CG-LMMSE band ±{b}')
    plt.xlabel('SNR (dB)'); plt.ylabel('BER'); plt.title(f'Iterative ICI Equalization (off-diagonal energy {100*ici:.1f}%)'); plt.grid(True,which='both',alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'ici_cg_equalization_ber.png',dpi=180); plt.close()
    plt.figure(figsize=(7.2,4.7));
    for j,b,m in [(4,1,'s-'),(8,2,'^-'),(12,4,'d-')]: plt.plot(a[:,0],a[:,j],m,label=f'band ±{b}')
    plt.xlabel('SNR (dB)'); plt.ylabel('Mean CG iterations'); plt.title('ICI-LMMSE Iterative Solver Convergence'); plt.grid(True,alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'ici_cg_iterations.png',dpi=180); plt.close()
if __name__=='__main__': main()
