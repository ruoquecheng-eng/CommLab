from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt
from commlab.config import OFDMConfig
from commlab.modulation import QAMModem
from commlab.ofdm import OFDMTransceiver
from commlab.rf import scale_for_input_backoff, apply_memory_polynomial, fit_memory_polynomial, apply_generalized_memory, fit_generalized_memory, default_generalized_memory_pa_coefficients
from commlab.metrics import evm_percent
ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'

def align(ref,y,discard=20):
    r=np.asarray(ref)[discard:]; z=np.asarray(y)[discard:]; g=np.vdot(z,r)/max(np.vdot(z,z).real,1e-30); out=np.asarray(y).copy(); out[discard:]=g*z; return out

def nmse_db(ref,est,discard=8):
    r=np.asarray(ref)[discard:]; e=np.asarray(est)[discard:]-r; return 10*np.log10(np.sum(abs(e)**2)/max(np.sum(abs(r)**2),1e-30))

def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True); rng=np.random.default_rng(818); cfg=OFDMConfig(cp_len=0); modem=QAMModem(64); ofdm=OFDMTransceiver(cfg); true_c=default_generalized_memory_pa_coefficients()
    tb=rng.integers(0,2,900*cfg.n_data*6,dtype=np.uint8); train=scale_for_input_backoff(ofdm.modulate(modem.modulate(tb)),8); train_y=apply_generalized_memory(train,true_c)
    # Forward model identification on same-order models.
    mp_forward=fit_memory_polynomial(train,train_y,order=5,memory_depth=3,ridge=1e-6)
    gmp_forward=fit_generalized_memory(train,train_y,order=5,memory_depth=3,cross_lags=2,ridge=1e-6)
    # Indirect inverse fits.
    mp_inv=fit_memory_polynomial(train_y,train,order=7,memory_depth=4,ridge=2e-5)
    gmp_inv=fit_generalized_memory(train_y,train,order=7,memory_depth=4,cross_lags=2,ridge=2e-5)
    rows=[]
    for bo in (6,8,10,12):
        bits=rng.integers(0,2,300*cfg.n_data*6,dtype=np.uint8); desired=scale_for_input_backoff(ofdm.modulate(modem.modulate(bits)),bo)
        pa=apply_generalized_memory(desired,true_c)
        mp_drive=apply_memory_polynomial(desired,mp_inv,order=7,memory_depth=4); mp_out=apply_generalized_memory(mp_drive,true_c)
        gmp_drive=apply_generalized_memory(desired,gmp_inv,order=7,memory_depth=4,cross_lags=2); gmp_out=apply_generalized_memory(gmp_drive,true_c)
        e0=evm_percent(desired[20:],align(desired,pa)[20:]); e1=evm_percent(desired[20:],align(desired,mp_out)[20:]); e2=evm_percent(desired[20:],align(desired,gmp_out)[20:]); rows.append((bo,e0,e1,e2)); print(f'BO={bo} PA={e0:.2f}% MP-DPD={e1:.2f}% GMP-DPD={e2:.2f}%')
    # Held-out forward-model error at calibration operating point.
    vb=rng.integers(0,2,300*cfg.n_data*6,dtype=np.uint8); vx=scale_for_input_backoff(ofdm.modulate(modem.modulate(vb)),8); vy=apply_generalized_memory(vx,true_c)
    mp_nmse=nmse_db(vy,apply_memory_polynomial(vx,mp_forward)); gmp_nmse=nmse_db(vy,apply_generalized_memory(vx,gmp_forward)); print('forward model NMSE dB MP/GMP',mp_nmse,gmp_nmse)
    with open(DATA/'generalized_memory_dpd.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['backoff_db','pa_only_evm_pct','standard_memory_dpd_evm_pct','cross_term_gmp_dpd_evm_pct']); w.writerows(rows); w.writerow(['forward_model_nmse_db','',mp_nmse,gmp_nmse])
    a=np.asarray(rows,float); plt.figure(figsize=(7.3,4.9)); plt.plot(a[:,0],a[:,1],'o-',label='Cross-memory PA only'); plt.plot(a[:,0],a[:,2],'s-',label='Standard MP indirect DPD'); plt.plot(a[:,0],a[:,3],'^-',label='Cross-term GMP indirect DPD'); plt.xlabel('Input back-off (dB)'); plt.ylabel('EVM (%)'); plt.title('Cross-Memory PA: Standard MP vs Generalized MP DPD'); plt.grid(True,alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'generalized_memory_dpd_evm.png',dpi=180); plt.close()
if __name__=='__main__': main()
