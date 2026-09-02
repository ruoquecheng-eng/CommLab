from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

from commlab.coding import ConvolutionalCode
from commlab.config import OFDMConfig
from commlab.modulation import QAMModem
from commlab.ofdm import OFDMTransceiver
from commlab.channels import add_awgn, noise_power_for_snr
from commlab.impairments import add_complex_tone_interference, detect_narrowband_outliers
from commlab.metrics import bit_error_rate

ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'


def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
    cfg=OFDMConfig(); modem=QAMModem(4); ofdm=OFDMTransceiver(cfg); code=ConvolutionalCode(); rng=np.random.default_rng(741)
    info=rng.integers(0,2,20000,dtype=np.uint8); coded=code.encode(info)
    block=cfg.n_data*2; pad=(-len(coded))%block; padded=np.pad(coded,(0,pad)); tx=ofdm.modulate(modem.modulate(padded))
    # Jam a known occupied data subcarrier. Receiver does not use this index directly;
    # it detects persistent power outliers and converts them into soft erasures.
    target_data_index=35; target_sc=cfg.data_subcarriers[target_data_index]; f=target_sc/cfg.n_fft
    rows=[]
    for sir in (15,10,5,0,-5):
        jam=add_complex_tone_interference(tx,f,sir,phase_rad=.37)
        nv=noise_power_for_snr(jam,18.0); rx=add_awgn(jam,18.0,np.random.default_rng(7500+sir))
        syms,_=ofdm.demodulate(rx); grid=syms.reshape(-1,cfg.n_data)
        detected=detect_narrowband_outliers(grid,4.0)
        llr=modem.llr_maxlog(syms,nv).reshape(-1,cfg.n_data,2)
        raw_dec=code.decode_soft(llr.reshape(-1)[:len(coded)])
        erased=llr.copy(); erased[:,detected,:]=0.0
        er_dec=code.decode_soft(erased.reshape(-1)[:len(coded)])
        row=(sir,int(target_data_index in set(detected.tolist())),len(detected),bit_error_rate(info,raw_dec),bit_error_rate(info,er_dec))
        rows.append(row); print('SIR=%3d detected_target=%d nflag=%d rawBER=%.4g erasureBER=%.4g'%row)
    with open(DATA/'narrowband_interference.csv','w',newline='') as fcsv:
        w=csv.writer(fcsv); w.writerow(['sir_db','target_detected','n_flagged','raw_soft_viterbi_ber','soft_erasure_viterbi_ber']); w.writerows(rows)
    a=np.asarray(rows,float); floor=1/len(info)
    plt.figure(figsize=(7.3,4.9)); plt.semilogy(a[:,0],np.maximum(a[:,3],floor),'o-',label='Soft Viterbi'); plt.semilogy(a[:,0],np.maximum(a[:,4],floor),'s-',label='Detected-carrier soft erasure'); plt.gca().invert_xaxis(); plt.xlabel('Signal-to-interference ratio (dB)'); plt.ylabel('Information-bit BER'); plt.title('Coded OFDM under Narrowband Interference'); plt.grid(True,which='both',alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'narrowband_interference_ber.png',dpi=180); plt.close()

if __name__=='__main__': main()
