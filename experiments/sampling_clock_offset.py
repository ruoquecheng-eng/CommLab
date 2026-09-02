from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

from commlab.config import OFDMConfig
from commlab.modulation import QAMModem
from commlab.ofdm import OFDMTransceiver
from commlab.channels import add_awgn
from commlab.impairments import apply_sampling_clock_offset, compensate_sampling_clock_offset, estimate_sampling_clock_ppm_from_two_training
from commlab.metrics import bit_error_rate, evm_percent
from commlab.synchronization import estimate_affine_phase_from_pilots, correct_affine_phase

ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'


def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
    cfg=OFDMConfig(); modem=QAMModem(64); ofdm=OFDMTransceiver(cfg); rng=np.random.default_rng(721)
    n_sym=900; bits=rng.integers(0,2,n_sym*cfg.n_data*modem.bits_per_symbol,dtype=np.uint8); ref=modem.modulate(bits); tx=ofdm.modulate(ref)
    # separate calibration record with two widely-separated known bursts
    L=255; training=np.exp(1j*np.pi*rng.integers(0,2,L))
    sep=60000; calib=np.zeros(sep+L+500,dtype=complex); calib[200:200+L]=training; calib[200+sep:200+sep+L]=training
    rows=[]
    for ppm in (0,50,100,250,500,750,1000):
        calib_rx=apply_sampling_clock_offset(calib,ppm)
        est,peaks=estimate_sampling_clock_ppm_from_two_training(calib_rx,training,200,200+sep,150)
        impaired=apply_sampling_clock_offset(tx,ppm); impaired=add_awgn(impaired,30.0,np.random.default_rng(7300+ppm))
        raw,pil=ofdm.demodulate(impaired)
        ai,bs=estimate_affine_phase_from_pilots(pil,cfg); tracked=correct_affine_phase(raw,ai,bs,cfg)
        corrected=compensate_sampling_clock_offset(impaired,est); cor,_=ofdm.demodulate(corrected)
        row=(ppm,est,bit_error_rate(bits,modem.demodulate(raw)),bit_error_rate(bits,modem.demodulate(tracked)),bit_error_rate(bits,modem.demodulate(cor)),evm_percent(ref,raw),evm_percent(ref,tracked),evm_percent(ref,cor))
        rows.append(row); print('ppm=%4d est=%8.2f rawBER=%.4g pilotBER=%.4g resampBER=%.4g rawEVM=%.2f pilotEVM=%.2f resampEVM=%.2f'%row)
    with open(DATA/'sampling_clock_offset.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['true_ppm','estimated_ppm','raw_ber','pilot_affine_phase_ber','estimated_sco_resampling_ber','raw_evm_pct','pilot_affine_phase_evm_pct','resampling_evm_pct']); w.writerows(rows)
    a=np.asarray(rows,float); floor=1/len(bits)
    plt.figure(figsize=(7.3,4.9)); plt.semilogy(a[:,0],np.maximum(a[:,2],floor),'o-',label='Uncorrected'); plt.semilogy(a[:,0],np.maximum(a[:,3],floor),'^-',label='Pilot affine-phase tracking'); plt.semilogy(a[:,0],np.maximum(a[:,4],floor),'s-',label='Estimated SCO + cubic resampling'); plt.xlabel('Sampling-clock offset (ppm)'); plt.ylabel('BER'); plt.title('64-QAM OFDM Sampling-Clock Offset'); plt.grid(True,which='both',alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'sampling_clock_ber.png',dpi=180); plt.close()
    plt.figure(figsize=(7.3,4.9)); plt.plot(a[:,0],a[:,1]-a[:,0],'o-'); plt.axhline(0,color='k',lw=.8); plt.xlabel('True SCO (ppm)'); plt.ylabel('Estimation error (ppm)'); plt.title('Two-Training-Burst SCO Estimation'); plt.grid(True,alpha=.3); plt.tight_layout(); plt.savefig(FIG/'sampling_clock_estimation.png',dpi=180); plt.close()

if __name__=='__main__': main()
