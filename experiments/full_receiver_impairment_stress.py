from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

from commlab.config import OFDMConfig
from commlab.modulation import QAMModem
from commlab.ofdm import OFDMTransceiver
from commlab.synchronization import repeated_half_preamble, detect_frame_start, estimate_cfo_from_repeated_halves, correct_cfo, estimate_common_phase_from_pilots, correct_common_phase
from commlab.impairments import apply_cfo, prepend_timing_offset, apply_iq_imbalance, apply_phase_noise, estimate_iq_coefficients, compensate_iq_imbalance
from commlab.metrics import evm_rms

ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'


def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(10007); cfg=OFDMConfig(); modem=QAMModem(16); ofdm=OFDMTransceiver(cfg); pre=repeated_half_preamble(cfg.n_fft,seed=77)
    n_sym=260; bits=rng.integers(0,2,n_sym*cfg.n_data*modem.bits_per_symbol,dtype=np.uint8); tx_data=modem.modulate(bits); payload=ofdm.modulate(tx_data); frame=np.concatenate((pre,payload))
    # Composite normalized baseband impairment stress case.
    y=apply_iq_imbalance(frame,2.0,8.0); y=apply_cfo(y,.12,cfg.n_fft); y=apply_phase_noise(y,.0025,rng); snr_db=24; nv=np.mean(np.abs(y)**2)/10**(snr_db/10); y += np.sqrt(nv/2)*(rng.normal(size=len(y))+1j*rng.normal(size=len(y))); rx=prepend_timing_offset(y,43)
    start,metric=detect_frame_start(rx,pre); aligned=rx[start:start+len(frame)]
    stages=[]
    def evaluate(name,wave):
        d,p=ofdm.demodulate(wave[len(pre):]); bh=modem.demodulate(d); ber=np.mean(bh!=bits); e=evm_rms(d,tx_data)
        stages.append((name,ber,e)); return d,p
    # With only frame timing corrected, all other impairments remain.
    d0,p0=evaluate('Frame timing only',aligned)
    eps=estimate_cfo_from_repeated_halves(aligned[:len(pre)],cfg.n_fft); cfo=correct_cfo(aligned,eps,cfg.n_fft)
    d1,p1=evaluate('+ coarse CFO',cfo)
    alpha,beta=estimate_iq_coefficients(pre,cfo[:len(pre)]); iq=compensate_iq_imbalance(cfo,alpha,beta)
    d2,p2=evaluate('+ IQ compensation',iq)
    # Pilots remove residual common phase drift from phase noise / CFO residue.
    phase=estimate_common_phase_from_pilots(p2.reshape(-1,len(cfg.pilot_values)),cfg); d3=correct_common_phase(d2,phase,cfg.n_data); bh=modem.demodulate(d3); stages.append(('+ pilot CPE tracking',np.mean(bh!=bits),evm_rms(d3,tx_data)))
    print(f'frame start true=43 estimate={start} metric={metric:.3f}; CFO true=.12 estimate={eps:.5f}')
    for x in stages: print(f'{x[0]:>22}: BER={x[1]:.4g}, EVM={100*x[2]:.2f}%')
    with open(DATA/'full_receiver_impairment_stress.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['stage','ber','evm_rms','frame_start_true','frame_start_estimated','cfo_true','cfo_estimated']);
        for name,b,e in stages: w.writerow([name,b,e,43,start,.12,eps])
    x=np.arange(len(stages)); plt.figure(figsize=(8,5)); plt.semilogy(x,[max(s[1],1e-6) for s in stages],'o-'); plt.xticks(x,[s[0] for s in stages],rotation=18,ha='right'); plt.ylabel('BER'); plt.title('Composite Receiver Stress Test: Cumulative Compensation'); plt.grid(True,which='both',alpha=.3); plt.tight_layout(); plt.savefig(FIG/'full_receiver_stress_ber.png',dpi=180); plt.close()
    plt.figure(figsize=(8,5)); plt.plot(x,[100*s[2] for s in stages],'o-'); plt.xticks(x,[s[0] for s in stages],rotation=18,ha='right'); plt.ylabel('RMS EVM (%)'); plt.title('Composite Receiver Stress Test: EVM Recovery'); plt.grid(alpha=.3); plt.tight_layout(); plt.savefig(FIG/'full_receiver_stress_evm.png',dpi=180); plt.close()

if __name__=='__main__': main()
