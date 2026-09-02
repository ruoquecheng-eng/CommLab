from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

from commlab.coding import ConvolutionalCode
from commlab.config import OFDMConfig
from commlab.modulation import QAMModem
from commlab.ofdm import OFDMTransceiver
from commlab.channels import add_awgn, noise_power_for_snr
from commlab.metrics import bit_error_rate

ROOT = Path(__file__).resolve().parents[1]
FIG, DATA = ROOT/'results'/'figures', ROOT/'results'/'data'


def receive(bits, snr_db, rng, cfg, modem, ofdm, soft=False):
    bits=np.asarray(bits,dtype=np.uint8); block=cfg.n_data*modem.bits_per_symbol
    pad=(-len(bits))%block; padded=np.pad(bits,(0,pad))
    tx=ofdm.modulate(modem.modulate(padded))
    nv=noise_power_for_snr(tx,snr_db)
    rx=add_awgn(tx,snr_db,rng)
    syms,_=ofdm.demodulate(rx)
    if soft:
        return modem.llr_maxlog(syms, nv)[:len(bits)]
    return modem.demodulate(syms)[:len(bits)]


def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
    cfg=OFDMConfig(); modem=QAMModem(4); ofdm=OFDMTransceiver(cfg); code=ConvolutionalCode()
    rng=np.random.default_rng(501); info=rng.integers(0,2,50000,dtype=np.uint8); coded=code.encode(info)
    rows=[]
    for snr in np.arange(-2,9,2):
        unc=receive(info,snr,np.random.default_rng(5100+snr),cfg,modem,ofdm,False)
        hard=receive(coded,snr,np.random.default_rng(5200+snr),cfg,modem,ofdm,False)
        llr=receive(coded,snr,np.random.default_rng(5200+snr),cfg,modem,ofdm,True)
        bh=code.decode_hard(hard); bs=code.decode_soft(llr)
        row=(snr,bit_error_rate(info,unc),bit_error_rate(info,bh),bit_error_rate(info,bs))
        rows.append(row); print('SNR=%3d unc=%.5g hard=%.5g soft=%.5g'%row)
    with open(DATA/'soft_coded_ofdm.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['snr_db','uncoded_ber','hard_viterbi_ber','soft_viterbi_ber']); w.writerows(rows)
    a=np.asarray(rows,float); floor=1/len(info)
    plt.figure(figsize=(7.3,4.9))
    plt.semilogy(a[:,0],np.maximum(a[:,1],floor),'o-',label='Uncoded')
    plt.semilogy(a[:,0],np.maximum(a[:,2],floor),'s-',label='Hard Viterbi')
    plt.semilogy(a[:,0],np.maximum(a[:,3],floor),'^-',label='Soft-input Viterbi')
    plt.xlabel('Sample-domain SNR (dB)'); plt.ylabel('Information-bit BER')
    plt.title('Soft Information Improves Convolutionally Coded OFDM')
    plt.grid(True,which='both',alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'soft_viterbi_gain.png',dpi=180); plt.close()

if __name__=='__main__': main()
