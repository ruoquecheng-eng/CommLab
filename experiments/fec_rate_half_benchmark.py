from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt
from commlab.coding import ConvolutionalCode, SparseAccumulatorLDPC, PolarCode
ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'

def awgn_llr(coded, ebn0_db, rate, rng):
    eb=10**(ebn0_db/10); sigma2=1/(2*rate*eb); y=(1-2*np.asarray(coded,dtype=float))+np.sqrt(sigma2)*rng.normal(size=len(coded)); return 2*y/sigma2

def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True); rng=np.random.default_rng(815)
    conv=ConvolutionalCode(); ldpc=SparseAccumulatorLDPC(k=96,seed=1701); polar=PolarCode(128,64)
    rows=[]
    for eb in (-1,0,1,2,3,4):
        err={'conv':0,'ldpc':0,'polar':0}; total={'conv':0,'ldpc':0,'polar':0}; iters=[]; fails=0
        for _ in range(90):
            b=rng.integers(0,2,polar.k,dtype=np.uint8); c=polar.encode(b); bh=polar.decode_sc(awgn_llr(c,eb,polar.rate,rng)); err['polar']+=np.count_nonzero(bh!=b); total['polar']+=len(b)
        for _ in range(55):
            b=rng.integers(0,2,ldpc.k,dtype=np.uint8); c=ldpc.encode(b); bh,it,ok=ldpc.decode_min_sum(awgn_llr(c,eb,ldpc.rate,rng),max_iter=40); err['ldpc']+=np.count_nonzero(bh!=b); total['ldpc']+=len(b); iters.append(it); fails+=0 if ok else 1
            b2=rng.integers(0,2,96,dtype=np.uint8); c2=conv.encode(b2,terminate=True); re=len(b2)/len(c2); bh2=conv.decode_soft(awgn_llr(c2,eb,re,rng)); err['conv']+=np.count_nonzero(bh2!=b2); total['conv']+=len(b2)
        vals={k:err[k]/total[k] for k in err}; rows.append((eb,vals['conv'],vals['ldpc'],vals['polar'],float(np.mean(iters)),fails)); print(f'Eb/N0={eb:2d} conv={vals["conv"]:.4g} LDPC={vals["ldpc"]:.4g} polar={vals["polar"]:.4g} ldpc-it={np.mean(iters):.1f}')
    with open(DATA/'fec_rate_half_benchmark.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['ebn0_db','conv_soft_ber','custom_ldpc_min_sum_ber','polar_sc_ber','ldpc_mean_iterations','ldpc_failed_blocks']); w.writerows(rows)
    a=np.asarray(rows,float); plt.figure(figsize=(7.3,4.9)); plt.semilogy(a[:,0],np.maximum(a[:,1],1e-5),'o-',label='Conv. (7,5) soft Viterbi'); plt.semilogy(a[:,0],np.maximum(a[:,2],1e-5),'s-',label='Custom sparse LDPC, Min-Sum'); plt.semilogy(a[:,0],np.maximum(a[:,3],1e-5),'^-',label='Polar N=128 K=64, SC'); plt.xlabel('$E_b/N_0$ (dB)'); plt.ylabel('Information-bit BER'); plt.title('Educational Rate-1/2 FEC Benchmark over BPSK AWGN'); plt.grid(True,which='both',alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'fec_rate_half_benchmark.png',dpi=180); plt.close()
    plt.figure(figsize=(7.1,4.7)); plt.plot(a[:,0],a[:,4],'o-'); plt.xlabel('$E_b/N_0$ (dB)'); plt.ylabel('Mean LDPC Min-Sum iterations'); plt.title('Sparse LDPC Decoder Convergence Cost'); plt.grid(True,alpha=.3); plt.tight_layout(); plt.savefig(FIG/'fec_ldpc_iterations_v08.png',dpi=180); plt.close()
if __name__=='__main__': main()
