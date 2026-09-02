from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

from commlab.config import OFDMConfig
from commlab.mimo import generate_mimo_multipath_taps, mimo_frequency_response, orthogonal_mimo_training_waveforms, apply_mimo_multipath_waveforms, estimate_mimo_channel_from_training, lmmse_shrink_mimo_channel
from commlab.metrics import normalized_mean_square_error as nmse

ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'


def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
    cfg=OFDMConfig(); rng=np.random.default_rng(703); snrs=(0,3,6,9,12,18,24); rows=[]
    active_bins=np.array([cfg.bin_index(k) for k in cfg.active_subcarriers])
    for snr in snrs:
        ls_vals=[]; mm_vals=[]
        for _ in range(180):
            taps=generate_mimo_multipath_taps(2,2,rng=rng); Htrue=mimo_frequency_response(taps,cfg.n_fft)[active_bins]
            tx=orthogonal_mimo_training_waveforms(cfg,2); clean=apply_mimo_multipath_waveforms(tx,taps)
            sigp=float(np.mean(np.abs(clean)**2)); nv=sigp/(10**(snr/10)); noise=np.sqrt(nv/2)*(rng.normal(size=clean.shape)+1j*rng.normal(size=clean.shape)); rx=clean+noise
            Hls=estimate_mimo_channel_from_training(rx,cfg,2)
            # Unit FFT means the per-bin noise variance is nv; estimate prior variance from the known channel family, not the noisy observation.
            chvar=float(np.mean(np.abs(Htrue)**2)); Hmm=lmmse_shrink_mimo_channel(Hls,nv,pilot_power=1.0,channel_variance=chvar)
            ls_vals.append(nmse(Htrue,Hls)); mm_vals.append(nmse(Htrue,Hmm))
        rows.append((snr,float(np.mean(ls_vals)),float(np.mean(mm_vals))))
        print(f'SNR={snr:2d} LS NMSE={rows[-1][1]:.4f} LMMSE={rows[-1][2]:.4f}')
    with open(DATA/'mimo_lmmse_estimation.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['training_snr_db','ls_nmse','lmmse_nmse']); w.writerows(rows)
    a=np.asarray(rows,float); plt.figure(figsize=(7.2,4.8)); plt.semilogy(a[:,0],a[:,1],'o-',label='Orthogonal-training LS'); plt.semilogy(a[:,0],a[:,2],'s-',label='Scalar-prior LMMSE'); plt.xlabel('Training SNR (dB)'); plt.ylabel('Channel NMSE'); plt.title('2x2 MIMO-OFDM Channel Estimation'); plt.grid(True,which='both',alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'mimo_lmmse_estimation_nmse.png',dpi=180); plt.close()

if __name__=='__main__': main()
