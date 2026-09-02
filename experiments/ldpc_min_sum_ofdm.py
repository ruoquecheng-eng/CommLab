from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

from commlab.coding import SparseAccumulatorLDPC, ConvolutionalCode
from commlab.config import OFDMConfig
from commlab.modulation import QAMModem
from commlab.ofdm import OFDMTransceiver
from commlab.channels import add_awgn, noise_power_for_snr
from commlab.metrics import bit_error_rate

ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'


def txrx_soft(coded_bits, snr_db, rng, cfg, modem, ofdm):
    block=cfg.n_data*modem.bits_per_symbol; pad=(-len(coded_bits))%block; padded=np.pad(coded_bits,(0,pad))
    tx=ofdm.modulate(modem.modulate(padded)); nv=noise_power_for_snr(tx,snr_db); rx=add_awgn(tx,snr_db,rng)
    syms,_=ofdm.demodulate(rx); return modem.llr_maxlog(syms,nv)[:len(coded_bits)]


def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
    cfg=OFDMConfig(); modem=QAMModem(4); ofdm=OFDMTransceiver(cfg); ldpc=SparseAccumulatorLDPC(k=96,seed=1701); conv=ConvolutionalCode(); rng=np.random.default_rng(781)
    n_blocks=100; infos=rng.integers(0,2,(n_blocks,ldpc.k),dtype=np.uint8); info=infos.reshape(-1)
    ldpc_bits=np.concatenate([ldpc.encode(u) for u in infos])
    conv_bits=conv.encode(info)
    rows=[]
    for snr in (-2,0,2,4,6,8):
        ldpc_llr=txrx_soft(ldpc_bits,snr,np.random.default_rng(7900+snr),cfg,modem,ofdm)
        decoded=[]; iters=[]; ok=[]
        for b in range(n_blocks):
            u,it,success=ldpc.decode_min_sum(ldpc_llr[b*ldpc.n:(b+1)*ldpc.n],max_iter=40,normalized_factor=.8)
            decoded.append(u); iters.append(it); ok.append(success)
        ldpc_hat=np.concatenate(decoded)
        conv_llr=txrx_soft(conv_bits,snr,np.random.default_rng(8000+snr),cfg,modem,ofdm); conv_hat=conv.decode_soft(conv_llr)
        row=(snr,bit_error_rate(info,ldpc_hat),bit_error_rate(info,conv_hat),float(np.mean(iters)),float(np.mean(ok)))
        rows.append(row); print('SNR=%3d LDPC=%.5g Conv=%.5g avgIter=%.2f success=%.2f'%row)
    with open(DATA/'ldpc_min_sum_ofdm.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['snr_db','sparse_ldpc_min_sum_ber','conv_soft_viterbi_ber','ldpc_avg_iterations','ldpc_converged_fraction']); w.writerows(rows)
    a=np.asarray(rows,float); floor=1/len(info)
    plt.figure(figsize=(7.3,4.9)); plt.semilogy(a[:,0],np.maximum(a[:,1],floor),'o-',label='Sparse LDPC + normalized Min-Sum'); plt.semilogy(a[:,0],np.maximum(a[:,2],floor),'s-',label='(7,5) convolutional + soft Viterbi'); plt.xlabel('Sample-domain SNR (dB)'); plt.ylabel('Information-bit BER'); plt.title('Two Rate-1/2 FEC Families on QPSK-OFDM'); plt.grid(True,which='both',alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'ldpc_vs_convolutional.png',dpi=180); plt.close()
    plt.figure(figsize=(7.3,4.9)); plt.plot(a[:,0],a[:,3],'o-',label='Average Min-Sum iterations'); plt.plot(a[:,0],40*(1-a[:,4]),'s-',label='40 × nonconverged fraction'); plt.xlabel('SNR (dB)'); plt.ylabel('Iteration / scaled failure metric'); plt.title('Iterative Decoder Complexity Falls with SNR'); plt.grid(True,alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'ldpc_decoder_iterations.png',dpi=180); plt.close()

if __name__=='__main__': main()
