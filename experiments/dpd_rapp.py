from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

from commlab.config import OFDMConfig
from commlab.modulation import QAMModem
from commlab.ofdm import OFDMTransceiver
from commlab.rf import rapp_amplifier, rapp_inverse_predistort, scale_for_input_backoff, occupied_guard_power_ratio_db
from commlab.metrics import evm_percent

ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'


def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
    cfg=OFDMConfig(cp_len=0); modem=QAMModem(64); ofdm=OFDMTransceiver(cfg); rng=np.random.default_rng(701)
    bits=rng.integers(0,2,1500*cfg.n_data*6,dtype=np.uint8); tx=ofdm.modulate(modem.modulate(bits)); occupied=np.concatenate((cfg.data_bins,cfg.pilot_bins))
    rows=[]
    for bo in (0,2,4,6,8,10):
        desired=scale_for_input_backoff(tx,bo,1.0)
        no=rapp_amplifier(desired,1.0,2.5)
        drive=rapp_inverse_predistort(desired,1.0,2.5,0.98)
        dpd=rapp_amplifier(drive,1.0,2.5)
        row=(bo,evm_percent(desired,no),evm_percent(desired,dpd),occupied_guard_power_ratio_db(no,occupied,cfg.n_fft),occupied_guard_power_ratio_db(dpd,occupied,cfg.n_fft),float(np.max(np.abs(drive))))
        rows.append(row); print('BO=%2d noEVM=%.2f%% dpdEVM=%.2f%% noLeak=%.1fdB dpdLeak=%.1fdB drivePeak=%.2f'%row)
    with open(DATA/'dpd_rapp.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['backoff_db','no_dpd_evm_pct','dpd_evm_pct','no_dpd_guard_db','dpd_guard_db','dpd_drive_peak']); w.writerows(rows)
    a=np.asarray(rows,float)
    plt.figure(figsize=(7.3,4.9)); plt.plot(a[:,0],a[:,1],'o-',label='PA only'); plt.plot(a[:,0],a[:,2],'s-',label='Known-model inverse DPD + PA'); plt.xlabel('Waveform backoff (dB)'); plt.ylabel('EVM (%)'); plt.title('Memoryless Rapp PA Linearization'); plt.grid(True,alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'dpd_evm.png',dpi=180); plt.close()
    plt.figure(figsize=(7.3,4.9)); plt.plot(a[:,0],a[:,3],'o-',label='PA only'); plt.plot(a[:,0],a[:,4],'s-',label='DPD + PA'); plt.xlabel('Waveform backoff (dB)'); plt.ylabel('Guard/occupied power (dB)'); plt.title('Model-Based DPD Reduces Spectral Regrowth'); plt.grid(True,alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'dpd_spectral_regrowth.png',dpi=180); plt.close()

if __name__=='__main__': main()
