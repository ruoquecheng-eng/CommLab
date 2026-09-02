from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

from commlab.config import OFDMConfig
from commlab.modulation import QAMModem
from commlab.ofdm import OFDMTransceiver
from commlab.mimo import (
    orthogonal_mimo_training_waveforms, estimate_mimo_channel_from_training, active_to_data_mimo_channel,
    generate_mimo_multipath_taps, apply_mimo_multipath_waveforms, mimo_frequency_response,
    detect_mimo_ofdm_data, detect_mimo_ofdm_data_from_frequency_response,
)
from commlab.metrics import bit_error_rate

ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'


def add_shared_awgn(x,snr_db,rng):
    p=float(np.mean(np.abs(x)**2)); nv=p/(10**(snr_db/10)); n=np.sqrt(nv/2)*(rng.normal(size=x.shape)+1j*rng.normal(size=x.shape)); return x+n,nv


def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
    cfg=OFDMConfig(); modem=QAMModem(4); ofdm=OFDMTransceiver(cfg); rows=[]
    for snr in (4,8,12,16,20,24):
        errs_p=errs_e=total=0
        nmse=[]
        for trial in range(24):
            rng=np.random.default_rng(8000+100*snr+trial); taps=generate_mimo_multipath_taps(2,2,rng=rng)
            train=orthogonal_mimo_training_waveforms(cfg,2); rxt=apply_mimo_multipath_waveforms(train,taps); rxt,_=add_shared_awgn(rxt,snr,rng)
            hact=estimate_mimo_channel_from_training(rxt,cfg,2); hdata=active_to_data_mimo_channel(hact,cfg)
            true=mimo_frequency_response(taps,cfg.n_fft)[cfg.data_bins]; nmse.append(np.sum(np.abs(hdata-true)**2)/np.sum(np.abs(true)**2))
            n_sym=30; bits=[]; waves=[]
            for _ in range(2):
                b=rng.integers(0,2,n_sym*cfg.n_data*2,dtype=np.uint8); bits.append(b); waves.append(ofdm.modulate(modem.modulate(b)))
            rx=apply_mimo_multipath_waveforms(np.stack(waves),taps); rx,nv=add_shared_awgn(rx,snr,rng)
            perf=detect_mimo_ofdm_data(rx,taps,cfg,'mmse',nv); est=detect_mimo_ofdm_data_from_frequency_response(rx,hdata,cfg,'mmse',nv)
            for t in range(2):
                bp=modem.demodulate(perf[...,t].reshape(-1)); be=modem.demodulate(est[...,t].reshape(-1)); errs_p += np.count_nonzero(bits[t]!=bp); errs_e += np.count_nonzero(bits[t]!=be); total += len(bits[t])
        row=(snr,errs_p/total,errs_e/total,float(np.mean(nmse))); rows.append(row); print('SNR=%2d perfect=%.5g estimated=%.5g Hnmse=%.4g'%row)
    with open(DATA/'mimo_channel_estimation.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['snr_db','perfect_csi_ber','training_ls_ber','channel_nmse']); w.writerows(rows)
    a=np.asarray(rows,float); floor=1/(24*30*cfg.n_data*4)
    plt.figure(figsize=(7.3,4.9)); plt.semilogy(a[:,0],np.maximum(a[:,1],floor),'o-',label='Perfect CSI MMSE'); plt.semilogy(a[:,0],np.maximum(a[:,2],floor),'s-',label='Orthogonal-training LS + MMSE'); plt.xlabel('SNR (dB)'); plt.ylabel('BER'); plt.title('2x2 MIMO-OFDM: Perfect vs Estimated CSI'); plt.grid(True,which='both',alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'mimo_channel_estimation_ber.png',dpi=180); plt.close()
    plt.figure(figsize=(7.3,4.9)); plt.semilogy(a[:,0],a[:,3],'o-'); plt.xlabel('Training SNR (dB)'); plt.ylabel('Channel NMSE'); plt.title('2x2 MIMO Orthogonal Training LS Accuracy'); plt.grid(True,which='both',alpha=.3); plt.tight_layout(); plt.savefig(FIG/'mimo_channel_estimation_nmse.png',dpi=180); plt.close()

if __name__=='__main__': main()
