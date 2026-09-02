from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

from commlab.coding import ConvolutionalCode
from commlab.modulation import QAMModem
from commlab.mimo import k_best_detect, k_best_soft_llr, maxlog_ml_llr
from commlab.metrics import ber_with_wilson

ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'


def labels_and_constellation(modem):
    labels=((np.arange(modem.order)[:,None] >> np.arange(modem.bits_per_symbol-1,-1,-1)) & 1).astype(np.uint8)
    return labels,modem.modulate(labels.reshape(-1))


def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(9011); modem=QAMModem(4); labels,const=labels_and_constellation(modem); code=ConvolutionalCode()
    snrs=[0,2,4,6,8,10]; frames=28; info_len=220
    methods=['Hard K=4 + hard Viterbi','Soft K=4 + soft Viterbi','Exact max-log + soft Viterbi']
    rows=[]
    for snr_db in snrs:
        nv=10**(-snr_db/10); counts={m:[0,0,0] for m in methods}
        for _ in range(frames):
            info=[rng.integers(0,2,info_len,dtype=np.uint8) for _ in range(2)]
            coded=[code.encode(b,terminate=True) for b in info]
            T=len(coded[0])//2
            x=np.column_stack([modem.modulate(c) for c in coded])
            H=(rng.normal(size=(T,2,2))+1j*rng.normal(size=(T,2,2)))/2.0  # E total Rx signal power ~1
            noise=np.sqrt(nv/2)*(rng.normal(size=(T,2))+1j*rng.normal(size=(T,2)))
            y=np.einsum('bij,bj->bi',H,x)+noise

            # Hard list detector -> hard Viterbi
            xh=k_best_detect(y,H,const,k_best=4)
            bh=[]
            for tx in range(2): bh.append(code.decode_hard(modem.demodulate(xh[:,tx]),terminated=True,trim_tail=True))
            # Soft K-best list -> soft Viterbi
            Lk=k_best_soft_llr(y,H,const,labels,nv,k_best=4,llr_clip=30)
            bk=[code.decode_soft(Lk[:,tx,:].reshape(-1),terminated=True,trim_tail=True) for tx in range(2)]
            # Exact max-log reference -> soft Viterbi
            Lm=maxlog_ml_llr(y,H,const,labels,nv)
            bm=[code.decode_soft(Lm[:,tx,:].reshape(-1),terminated=True,trim_tail=True) for tx in range(2)]
            for method,est in zip(methods,[bh,bk,bm]):
                frame_error=False
                for tx in range(2):
                    e=int(np.count_nonzero(est[tx]!=info[tx])); counts[method][0]+=e; counts[method][1]+=info_len; frame_error |= e>0
                counts[method][2]+=int(frame_error)
        for m in methods:
            ber,lo,hi=ber_with_wilson(counts[m][0],counts[m][1]); fer=counts[m][2]/frames
            rows.append((snr_db,m,ber,lo,hi,fer,counts[m][0],counts[m][1]))
        print(f'{snr_db:>2} dB  '+ ' | '.join(f'{m.split(" +")[0]} BER={counts[m][0]/counts[m][1]:.4g} FER={counts[m][2]/frames:.3f}' for m in methods))

    with open(DATA/'coded_mimo_soft_output.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['snr_db','receiver','ber','ci95_low','ci95_high','frame_error_rate','bit_errors','bits']); w.writerows(rows)
    plt.figure(figsize=(7.8,5.1))
    for m in methods:
        q=np.array([[r[0],r[2]] for r in rows if r[1]==m],float); plt.semilogy(q[:,0],np.maximum(q[:,1],1e-5),'o-',label=m)
    plt.xlabel('SNR (dB)'); plt.ylabel('Information-bit BER'); plt.title('2x2 QPSK Coded MIMO: Hard vs Soft-Output Detection'); plt.grid(True,which='both',alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'coded_mimo_soft_output_ber.png',dpi=180); plt.close()
    plt.figure(figsize=(7.8,5.1))
    for m in methods:
        q=np.array([[r[0],r[5]] for r in rows if r[1]==m],float); plt.semilogy(q[:,0],np.maximum(q[:,1],1/frames/3),'o-',label=m)
    plt.xlabel('SNR (dB)'); plt.ylabel('Frame error rate'); plt.title('Coded MIMO Frame Reliability'); plt.grid(True,which='both',alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'coded_mimo_soft_output_fer.png',dpi=180); plt.close()

if __name__=='__main__': main()
