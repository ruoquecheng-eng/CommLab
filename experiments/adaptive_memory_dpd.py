from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt
from commlab.config import OFDMConfig
from commlab.modulation import QAMModem
from commlab.ofdm import OFDMTransceiver
from commlab.rf import apply_memory_polynomial, fit_indirect_memory_dpd, MemoryPolynomialRLS, MemoryPolynomialEWLS, default_memory_pa_coefficients, scale_for_input_backoff
from commlab.metrics import evm_percent
ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'

def align(ref,y,discard=20):
    r=np.asarray(ref)[discard:]; z=np.asarray(y)[discard:]; g=np.vdot(z,r)/max(np.vdot(z,z).real,1e-30); out=np.asarray(y).copy(); out[discard:]=g*z; return out

def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(813); cfg=OFDMConfig(cp_len=0); modem=QAMModem(64); ofdm=OFDMTransceiver(cfg)
    c0=default_memory_pa_coefficients(); c1=c0.copy(); c1[0,1]*=1.35; c1[0,2]*=1.4; c1[1,0]*=1.25; c1[1,1]*=1.4; c1[2,0]*=.75
    # Calibrate a static inverse on the initial PA.
    b=rng.integers(0,2,600*cfg.n_data*6,dtype=np.uint8); base=scale_for_input_backoff(ofdm.modulate(modem.modulate(b)),8,1.0); y0=apply_memory_polynomial(base,c0)
    static=fit_indirect_memory_dpd(base,y0,order=7,memory_depth=4,ridge=1e-5)
    adaptive=MemoryPolynomialEWLS(order=7,memory_depth=4,forgetting_factor=.35,ridge=5e-3,initial_coefficients=static)
    rows=[]; n_blocks=18
    for blk in range(n_blocks):
        a=blk/(n_blocks-1); c=(1-a)*c0+a*c1
        bits=rng.integers(0,2,180*cfg.n_data*6,dtype=np.uint8); desired=scale_for_input_backoff(ofdm.modulate(modem.modulate(bits)),8,1.0)
        pa_raw=apply_memory_polynomial(desired,c)
        static_out=apply_memory_polynomial(apply_memory_polynomial(desired,static),c)
        adap_coeff=adaptive.coefficients; adap_drive=apply_memory_polynomial(desired,adap_coeff); adap_out=apply_memory_polynomial(adap_drive,c)
        e_raw=evm_percent(desired[20:],align(desired,pa_raw)[20:]); e_static=evm_percent(desired[20:],align(desired,static_out)[20:]); e_adap=evm_percent(desired[20:],align(desired,adap_out)[20:])
        # Indirect learning from current PA input/output; subsample for streaming cost.
        adaptive.update(adap_out,adap_drive,stride=3)
        rows.append((blk,a,e_raw,e_static,e_adap)); print(f'block={blk:02d} drift={a:.2f} raw={e_raw:.2f}% static={e_static:.2f}% adaptive={e_adap:.2f}%')
    with open(DATA/'adaptive_memory_dpd.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['block','drift_fraction','pa_only_evm_pct','static_dpd_evm_pct','adaptive_ewls_dpd_evm_pct']); w.writerows(rows)
    a=np.asarray(rows,float); plt.figure(figsize=(7.5,4.9)); plt.plot(a[:,0],a[:,2],'o-',label='PA only'); plt.plot(a[:,0],a[:,3],'s-',label='Static DPD calibrated at block 0'); plt.plot(a[:,0],a[:,4],'^-',label='Adaptive block-EWLS DPD'); plt.xlabel('Block / PA drift time'); plt.ylabel('EVM (%)'); plt.title('Tracking a Drifting Memory-Polynomial PA'); plt.grid(True,alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'adaptive_memory_dpd_tracking.png',dpi=180); plt.close()
if __name__=='__main__': main()
