from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

from commlab.config import OFDMConfig
from commlab.modulation import QAMModem
from commlab.ofdm import OFDMTransceiver
from commlab.rf import (
    apply_memory_polynomial, fit_indirect_memory_dpd, default_memory_pa_coefficients,
    scale_for_input_backoff, occupied_guard_power_ratio_db,
)
from commlab.metrics import evm_percent

ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'


def align_complex_gain(ref, y, discard=16):
    r=np.asarray(ref)[discard:]; z=np.asarray(y)[discard:]
    g=np.vdot(z,r)/max(np.vdot(z,z).real,1e-30)
    out=np.asarray(y).copy(); out[discard:]=g*z
    return out


def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
    cfg=OFDMConfig(cp_len=0); modem=QAMModem(64); ofdm=OFDMTransceiver(cfg); rng=np.random.default_rng(701)
    pa_c=default_memory_pa_coefficients(); occ=np.concatenate((cfg.data_bins,cfg.pilot_bins))
    train_bits=rng.integers(0,2,3200*cfg.n_data*6,dtype=np.uint8)
    test_bits=rng.integers(0,2,1800*cfg.n_data*6,dtype=np.uint8)
    train0=ofdm.modulate(modem.modulate(train_bits)); test0=ofdm.modulate(modem.modulate(test_bits))
    rows=[]
    for bo in (4,6,8,10,12):
        train=scale_for_input_backoff(train0,bo,1.0); tr_y=apply_memory_polynomial(train,pa_c)
        dpd_c=fit_indirect_memory_dpd(train,tr_y,order=9,memory_depth=4,ridge=1e-4)
        desired=scale_for_input_backoff(test0,bo,1.0)
        pa_only=apply_memory_polynomial(desired,pa_c)
        drive=apply_memory_polynomial(desired,dpd_c)
        pred=apply_memory_polynomial(drive,pa_c)
        pa_a=align_complex_gain(desired,pa_only); pred_a=align_complex_gain(desired,pred)
        e0=evm_percent(desired[24:],pa_a[24:]); e1=evm_percent(desired[24:],pred_a[24:])
        l0=occupied_guard_power_ratio_db(pa_a[len(pa_a)%cfg.n_fft:],occ,cfg.n_fft)
        l1=occupied_guard_power_ratio_db(pred_a[len(pred_a)%cfg.n_fft:],occ,cfg.n_fft)
        rows.append((bo,e0,e1,l0,l1))
        print(f'BO={bo:2d} dB memory-PA EVM={e0:.2f}% DPD={e1:.2f}% guard={l0:.1f}->{l1:.1f} dB')
    with open(DATA/'memory_polynomial_dpd.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['backoff_db','pa_only_evm_pct','memory_dpd_evm_pct','pa_guard_db','dpd_guard_db']); w.writerows(rows)
    a=np.asarray(rows,float)
    plt.figure(figsize=(7.3,4.9)); plt.plot(a[:,0],a[:,1],'o-',label='Memory PA only'); plt.plot(a[:,0],a[:,2],'s-',label='Indirect-learning memory DPD'); plt.xlabel('Input back-off (dB)'); plt.ylabel('EVM (%)'); plt.title('Memory-Polynomial PA: Offline Indirect-Learning DPD'); plt.grid(True,alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'memory_polynomial_dpd_evm.png',dpi=180); plt.close()
    plt.figure(figsize=(7.3,4.9)); plt.plot(a[:,0],a[:,3],'o-',label='Memory PA only'); plt.plot(a[:,0],a[:,4],'s-',label='Memory DPD'); plt.xlabel('Input back-off (dB)'); plt.ylabel('Guard / occupied power (dB)'); plt.title('Memory DPD and Spectral Regrowth'); plt.grid(True,alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'memory_polynomial_dpd_guard.png',dpi=180); plt.close()

if __name__=='__main__': main()
