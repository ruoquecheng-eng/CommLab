from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

from commlab.config import OFDMConfig
from commlab.mimo import (
    generate_mimo_multipath_taps, mimo_frequency_response, apply_mimo_multipath_waveforms,
    orthogonal_mimo_training_waveforms, estimate_mimo_channel_from_training,
    frequency_orthogonal_mimo_training_waveforms, estimate_mimo_cir_from_frequency_orthogonal_training,
)
from commlab.metrics import normalized_mean_square_error

ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'


def noisy(rx,nv,rng):
    return rx+np.sqrt(nv/2)*(rng.normal(size=rx.shape)+1j*rng.normal(size=rx.shape))


def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
    cfg=OFDMConfig(); rng=np.random.default_rng(707); active_bins=np.array([cfg.bin_index(k) for k in cfg.active_subcarriers]); rows=[]
    for snr in (0,3,6,9,12,18,24):
        nm_time=[]; nm_freq=[]
        for _ in range(180):
            taps=generate_mimo_multipath_taps(2,2,rng=rng); H=mimo_frequency_response(taps,cfg.n_fft)[active_bins]
            tx_t=orthogonal_mimo_training_waveforms(cfg,2); clean_t=apply_mimo_multipath_waveforms(tx_t,taps)
            tx_f,sets=frequency_orthogonal_mimo_training_waveforms(cfg,2); clean_f=apply_mimo_multipath_waveforms(tx_f,taps)
            # Define noise using active-pilot symbol energy = 1 per occupied carrier; same complex FFT-domain variance target.
            nv=10**(-snr/10)
            ht=estimate_mimo_channel_from_training(noisy(clean_t,nv,rng),cfg,2)
            hf=estimate_mimo_cir_from_frequency_orthogonal_training(noisy(clean_f,nv,rng),sets,taps.shape[-1],cfg,ridge=1e-8)
            nm_time.append(normalized_mean_square_error(H,ht)); nm_freq.append(normalized_mean_square_error(H,hf))
        rows.append((snr,float(np.mean(nm_time)),float(np.mean(nm_freq))))
        print(f'SNR={snr:2d} two-slot full-carrier LS={rows[-1][1]:.4f} one-slot freq-orth CIR-LS={rows[-1][2]:.4f}')
    with open(DATA/'mimo_pilot_efficiency.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['pilot_snr_db','two_slot_full_active_ls_nmse','one_slot_frequency_orthogonal_cir_ls_nmse']); w.writerows(rows)
    a=np.asarray(rows,float); plt.figure(figsize=(7.3,4.9)); plt.semilogy(a[:,0],a[:,1],'o-',label='2 training symbols: full-active LS'); plt.semilogy(a[:,0],a[:,2],'s-',label='1 symbol: frequency-orthogonal finite-CIR LS'); plt.xlabel('Pilot SNR (dB)'); plt.ylabel('MIMO channel NMSE'); plt.title('2x2 MIMO Pilot-Overhead Reduction'); plt.grid(True,which='both',alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'mimo_pilot_efficiency_nmse.png',dpi=180); plt.close()
    # Resource view: all 52 active carriers are training RE in each full-active time slot; one interleaved symbol uses the same 52 total RE once.
    with open(DATA/'mimo_pilot_overhead_summary.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['scheme','training_ofdm_symbols','pilot_resource_elements_total']); w.writerow(['time_orthogonal_full_active',2,2*len(cfg.active_subcarriers)]); w.writerow(['frequency_orthogonal_finite_cir',1,len(cfg.active_subcarriers)])

if __name__=='__main__': main()
