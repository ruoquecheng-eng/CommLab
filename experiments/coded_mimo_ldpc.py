from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

from commlab.coding import SparseAccumulatorLDPC
from commlab.modulation import QAMModem
from commlab.mimo import k_best_soft_llr, maxlog_ml_llr
from commlab.metrics import ber_with_wilson

ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'


def labels_and_constellation(modem):
    labels=((np.arange(modem.order)[:,None] >> np.arange(modem.bits_per_symbol-1,-1,-1)) & 1).astype(np.uint8)
    return labels,modem.modulate(labels.reshape(-1))


def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(10002); modem=QAMModem(4); labels,const=labels_and_constellation(modem); code=SparseAccumulatorLDPC(k=96,seed=1701)
    snrs=[0,4,8,12]; frames=70; methods=['K-best K=4 + LDPC','Exact max-log + LDPC']; rows=[]
    for snr in snrs:
        nv=10**(-snr/10); counts={m:[0,0,0,0] for m in methods}
        for _ in range(frames):
            u=rng.integers(0,2,code.k,dtype=np.uint8); cw=code.encode(u)
            syms=modem.modulate(cw); x=syms.reshape(-1,2); T=len(x)
            H=(rng.normal(size=(T,2,2))+1j*rng.normal(size=(T,2,2)))/2
            n=np.sqrt(nv/2)*(rng.normal(size=(T,2))+1j*rng.normal(size=(T,2))); y=np.einsum('bij,bj->bi',H,x)+n
            Lk,exp=k_best_soft_llr(y,H,const,labels,nv,k_best=4,llr_clip=35,return_expansions=True)
            Le=maxlog_ml_llr(y,H,const,labels,nv)
            for name,L in zip(methods,[Lk,Le]):
                dec,it,ok=code.decode_min_sum(L.reshape(-1),max_iter=40)
                err=int(np.count_nonzero(dec!=u)); counts[name][0]+=err; counts[name][1]+=len(u); counts[name][2]+=int(err>0); counts[name][3]+=it
        for m in methods:
            ber,lo,hi=ber_with_wilson(counts[m][0],counts[m][1]); rows.append((snr,m,ber,lo,hi,counts[m][2]/frames,counts[m][3]/frames))
        print(f'{snr:>2} dB  '+' | '.join(f'{m.split(" +")[0]} BER={counts[m][0]/counts[m][1]:.4g}, FER={counts[m][2]/frames:.3f}' for m in methods))
    with open(DATA/'coded_mimo_ldpc.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['snr_db','receiver','ber','ci95_low','ci95_high','fer','avg_ldpc_iterations']); w.writerows(rows)
    plt.figure(figsize=(7.6,5.1))
    for m in methods:
        a=np.array([[r[0],r[2]] for r in rows if r[1]==m],float); plt.semilogy(a[:,0],np.maximum(a[:,1],1e-5),'o-',label=m)
    plt.xlabel('SNR (dB)'); plt.ylabel('Information-bit BER'); plt.title('2x2 QPSK + Sparse LDPC: Soft MIMO Detection'); plt.grid(True,which='both',alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'coded_mimo_ldpc_ber.png',dpi=180); plt.close()
    plt.figure(figsize=(7.6,5.1))
    for m in methods:
        a=np.array([[r[0],r[6]] for r in rows if r[1]==m],float); plt.plot(a[:,0],a[:,1],'o-',label=m)
    plt.xlabel('SNR (dB)'); plt.ylabel('Average Min-Sum iterations'); plt.title('Detector Reliability Changes LDPC Convergence Cost'); plt.grid(alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'coded_mimo_ldpc_iterations.png',dpi=180); plt.close()

if __name__=='__main__': main()
