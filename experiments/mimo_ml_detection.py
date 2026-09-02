from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

from commlab.mimo import zf_detect, mmse_detect, ml_detect_small
from commlab.modulation import QAMModem

ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'


def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(705); modem=QAMModem(4)
    labels=np.arange(4,dtype=np.uint8)[:,None]; bitslab=((labels >> np.array([1,0])) & 1).astype(np.uint8); const=modem.modulate(bitslab.reshape(-1))
    rows=[]
    for snr_db in (0,3,6,9,12,15,18):
        nv=10**(-snr_db/10); n=12000
        H=(rng.normal(size=(n,2,2))+1j*rng.normal(size=(n,2,2)))/np.sqrt(2)
        idx=rng.integers(0,4,size=(n,2)); x=const[idx]
        noise=np.sqrt(nv/2)*(rng.normal(size=(n,2))+1j*rng.normal(size=(n,2))); y=np.einsum('bij,bj->bi',H,x)+noise
        methods={'ZF':zf_detect(y,H),'MMSE':mmse_detect(y,H,nv),'ML':ml_detect_small(y,H,const)}
        vals={}
        true_bits=bitslab[idx].reshape(-1)
        for name,xh in methods.items():
            # nearest constellation point per stream
            nearest=np.argmin(abs(xh[...,None]-const[None,None,:]),axis=-1)
            bh=bitslab[nearest].reshape(-1); vals[name]=np.mean(bh!=true_bits)
        rows.append((snr_db,vals['ZF'],vals['MMSE'],vals['ML']))
        print(f'SNR={snr_db:2d} ZF={vals["ZF"]:.4g} MMSE={vals["MMSE"]:.4g} ML={vals["ML"]:.4g}')
    with open(DATA/'mimo_ml_detection.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['snr_db','zf_ber','mmse_ber','ml_ber']); w.writerows(rows)
    a=np.asarray(rows,float); plt.figure(figsize=(7.2,4.8));
    plt.semilogy(a[:,0],a[:,1],'o-',label='ZF'); plt.semilogy(a[:,0],a[:,2],'s-',label='MMSE'); plt.semilogy(a[:,0],np.maximum(a[:,3],1e-5),'^-',label='Exhaustive ML (16 candidates/use)')
    plt.xlabel('SNR (dB)'); plt.ylabel('BER'); plt.title('2x2 QPSK MIMO: Linear vs Maximum-Likelihood Detection'); plt.grid(True,which='both',alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'mimo_ml_detection_ber.png',dpi=180); plt.close()

if __name__=='__main__': main()
