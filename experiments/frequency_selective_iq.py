from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

from commlab.config import OFDMConfig
from commlab.modulation import QAMModem
from commlab.ofdm import OFDMTransceiver
from commlab.channels import add_awgn
from commlab.impairments import (
    apply_frequency_selective_iq_imbalance, estimate_frequency_selective_iq_filters,
    compensate_frequency_selective_iq_ofdm, estimate_iq_coefficients, compensate_iq_imbalance,
)
from commlab.metrics import bit_error_rate, evm_percent

ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'


def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(708); cfg=OFDMConfig(); modem=QAMModem(64); ofdm=OFDMTransceiver(cfg)
    hd=np.array([1.0+0j,0.055*np.exp(.35j),0.022*np.exp(-.8j)])
    hi=np.array([0.095*np.exp(.55j),0.038*np.exp(-.5j),0.016*np.exp(.9j)])
    train=(rng.normal(size=20000)+1j*rng.normal(size=20000))/np.sqrt(2); train_rx=apply_frequency_selective_iq_imbalance(train,hd,hi); train_rx=add_awgn(train_rx,35,rng)
    # Frequency-flat baseline deliberately compresses the whole impairment into alpha,beta.
    a,b=estimate_iq_coefficients(train,train_rx)
    hdh,hih=estimate_frequency_selective_iq_filters(train,train_rx,3,ridge=1e-7)
    rows=[]
    for snr in (18,22,26,30,34):
        bits=rng.integers(0,2,500*cfg.n_data*6,dtype=np.uint8); ref=modem.modulate(bits); tx=ofdm.modulate(ref)
        rx=apply_frequency_selective_iq_imbalance(tx,hd,hi); rx=add_awgn(rx,snr,rng)
        raw,_=ofdm.demodulate(rx)
        flat_wave=compensate_iq_imbalance(rx,a,b); flat,_=ofdm.demodulate(flat_wave)
        fir_wave=compensate_frequency_selective_iq_ofdm(rx,hdh,hih,cfg.n_fft,cfg.cp_len); fir,_=ofdm.demodulate(fir_wave)
        row=(snr,bit_error_rate(bits,modem.demodulate(raw)),bit_error_rate(bits,modem.demodulate(flat)),bit_error_rate(bits,modem.demodulate(fir)),evm_percent(ref,raw),evm_percent(ref,flat),evm_percent(ref,fir)); rows.append(row)
        print('SNR=%2d rawBER=%.4g flatBER=%.4g FIR-BER=%.4g rawEVM=%.2f flatEVM=%.2f FIR-EVM=%.2f'%row)
    with open(DATA/'frequency_selective_iq.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['snr_db','raw_ber','flat_iq_comp_ber','fir_pairwise_comp_ber','raw_evm_pct','flat_iq_comp_evm_pct','fir_pairwise_comp_evm_pct']); w.writerows(rows)
    a=np.asarray(rows,float); floor=1/(500*cfg.n_data*6)
    plt.figure(figsize=(7.3,4.9)); plt.semilogy(a[:,0],np.maximum(a[:,1],floor),'o-',label='Uncompensated'); plt.semilogy(a[:,0],np.maximum(a[:,2],floor),'s-',label='Frequency-flat IQ compensation'); plt.semilogy(a[:,0],np.maximum(a[:,3],floor),'^-',label='FIR + mirror-pair compensation'); plt.xlabel('SNR (dB)'); plt.ylabel('BER'); plt.title('64-QAM OFDM with Frequency-Selective IQ Imbalance'); plt.grid(True,which='both',alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'frequency_selective_iq_ber.png',dpi=180); plt.close()
    plt.figure(figsize=(7.3,4.9)); plt.plot(a[:,0],a[:,4],'o-',label='Uncompensated'); plt.plot(a[:,0],a[:,5],'s-',label='Flat model'); plt.plot(a[:,0],a[:,6],'^-',label='FIR pairwise inverse'); plt.xlabel('SNR (dB)'); plt.ylabel('EVM (%)'); plt.title('Frequency-Selective IQ Compensation EVM'); plt.grid(True,alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'frequency_selective_iq_evm.png',dpi=180); plt.close()

if __name__=='__main__': main()
