from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

from commlab.config import OFDMConfig
from commlab.modulation import QAMModem
from commlab.ofdm import OFDMTransceiver
from commlab.impairments import apply_phase_noise
from commlab.channels import add_awgn
from commlab.synchronization import estimate_common_phase_from_pilots, correct_common_phase
from commlab.metrics import bit_error_rate, evm_percent

ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'


def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
    cfg=OFDMConfig(); modem=QAMModem(64); ofdm=OFDMTransceiver(cfg)
    rng=np.random.default_rng(601); n_sym=500
    bits=rng.integers(0,2,n_sym*cfg.n_data*modem.bits_per_symbol,dtype=np.uint8); ref=modem.modulate(bits)
    tx=ofdm.modulate(ref); rows=[]
    for sigma in (0.0,0.001,0.0025,0.005,0.01,0.02):
        impaired=apply_phase_noise(tx,sigma,np.random.default_rng(6100+int(sigma*1e6)))
        rx=add_awgn(impaired,28.0,np.random.default_rng(6200+int(sigma*1e6)))
        data,pilots=ofdm.demodulate(rx)
        phase=estimate_common_phase_from_pilots(pilots,cfg)
        tracked=correct_common_phase(data,phase,cfg.n_data)
        raw_ber=bit_error_rate(bits,modem.demodulate(data)); tr_ber=bit_error_rate(bits,modem.demodulate(tracked))
        raw_e=evm_percent(ref,data); tr_e=evm_percent(ref,tracked)
        rows.append((sigma,raw_ber,tr_ber,raw_e,tr_e)); print(f'sigma={sigma:.4f} rawBER={raw_ber:.4g} trackBER={tr_ber:.4g} rawEVM={raw_e:.2f}% trackEVM={tr_e:.2f}%')
    with open(DATA/'phase_noise_tracking.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['innovation_std_rad','raw_ber','pilot_cpe_ber','raw_evm_pct','pilot_cpe_evm_pct']); w.writerows(rows)
    a=np.asarray(rows,float); floor=1/len(bits)
    plt.figure(figsize=(7.3,4.9)); plt.semilogy(a[:,0],np.maximum(a[:,1],floor),'o-',label='No phase tracking'); plt.semilogy(a[:,0],np.maximum(a[:,2],floor),'s-',label='Pilot CPE tracking'); plt.xlabel('Phase innovation std (rad/sample)'); plt.ylabel('BER'); plt.title('64-QAM OFDM under Wiener Phase Noise'); plt.grid(True,which='both',alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'phase_noise_ber.png',dpi=180); plt.close()
    plt.figure(figsize=(7.3,4.9)); plt.plot(a[:,0],a[:,3],'o-',label='No tracking'); plt.plot(a[:,0],a[:,4],'s-',label='Pilot CPE tracking'); plt.xlabel('Phase innovation std (rad/sample)'); plt.ylabel('EVM (%)'); plt.title('Pilot Tracking Removes CPE but Not All ICI'); plt.grid(True,alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'phase_noise_evm.png',dpi=180); plt.close()

if __name__=='__main__': main()
