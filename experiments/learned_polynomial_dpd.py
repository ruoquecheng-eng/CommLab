from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

from commlab.config import OFDMConfig
from commlab.modulation import QAMModem
from commlab.ofdm import OFDMTransceiver
from commlab.rf import rapp_amplifier, rapp_inverse_predistort, scale_for_input_backoff, occupied_guard_power_ratio_db, fit_indirect_polynomial_dpd, apply_polynomial_dpd
from commlab.metrics import evm_percent

ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'


def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
    cfg=OFDMConfig(cp_len=0); modem=QAMModem(64); ofdm=OFDMTransceiver(cfg); rng=np.random.default_rng(811)
    train_bits=rng.integers(0,2,2500*cfg.n_data*6,dtype=np.uint8); train=ofdm.modulate(modem.modulate(train_bits))
    test_bits=rng.integers(0,2,1200*cfg.n_data*6,dtype=np.uint8); test=ofdm.modulate(modem.modulate(test_bits)); occ=np.concatenate((cfg.data_bins,cfg.pilot_bins))
    rows=[]
    for bo in (2,4,6,8,10):
        tr=scale_for_input_backoff(train,bo,1.0); tr_y=rapp_amplifier(tr,1.0,2.5); coeff=fit_indirect_polynomial_dpd(tr,tr_y,order=9,ridge=1e-6)
        desired=scale_for_input_backoff(test,bo,1.0)
        no=rapp_amplifier(desired,1.0,2.5)
        analytic=rapp_amplifier(rapp_inverse_predistort(desired,1.0,2.5,.98),1.0,2.5)
        learned_drive=apply_polynomial_dpd(desired,coeff); learned=rapp_amplifier(learned_drive,1.0,2.5)
        row=(bo,evm_percent(desired,no),evm_percent(desired,learned),evm_percent(desired,analytic),occupied_guard_power_ratio_db(no,occ,cfg.n_fft),occupied_guard_power_ratio_db(learned,occ,cfg.n_fft),occupied_guard_power_ratio_db(analytic,occ,cfg.n_fft))
        rows.append(row); print('BO=%2d noEVM=%.2f learned=%.2f analytic=%.2f noLeak=%.1f learnedLeak=%.1f analyticLeak=%.1f'%row)
    with open(DATA/'learned_polynomial_dpd.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['backoff_db','pa_only_evm_pct','learned_poly_dpd_evm_pct','known_inverse_evm_pct','pa_only_guard_db','learned_poly_guard_db','known_inverse_guard_db']); w.writerows(rows)
    a=np.asarray(rows,float)
    plt.figure(figsize=(7.3,4.9)); plt.plot(a[:,0],a[:,1],'o-',label='PA only'); plt.plot(a[:,0],a[:,2],'^-',label='Data-fitted polynomial DPD'); plt.plot(a[:,0],a[:,3],'s-',label='Known Rapp inverse'); plt.xlabel('Back-off (dB)'); plt.ylabel('EVM (%)'); plt.title('Known-Model vs Data-Fitted Memoryless DPD'); plt.grid(True,alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'learned_dpd_evm.png',dpi=180); plt.close()
    plt.figure(figsize=(7.3,4.9)); plt.plot(a[:,0],a[:,4],'o-',label='PA only'); plt.plot(a[:,0],a[:,5],'^-',label='Polynomial DPD'); plt.plot(a[:,0],a[:,6],'s-',label='Known inverse'); plt.xlabel('Back-off (dB)'); plt.ylabel('Guard/occupied power (dB)'); plt.title('Data-Fitted DPD and Spectral Regrowth'); plt.grid(True,alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'learned_dpd_spectral.png',dpi=180); plt.close()

if __name__=='__main__': main()
