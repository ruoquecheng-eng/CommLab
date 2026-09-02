from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

from commlab.config import OFDMConfig
from commlab.modulation import QAMModem
from commlab.ofdm import OFDMTransceiver
from commlab.channels import add_awgn
from commlab.impairments import apply_iq_imbalance, estimate_iq_coefficients, compensate_iq_imbalance, image_rejection_ratio_db
from commlab.metrics import bit_error_rate, evm_percent

ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'results'/'figures'; DATA=ROOT/'results'/'data'


def main():
    FIG.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
    cfg=OFDMConfig(); modem=QAMModem(64); ofdm=OFDMTransceiver(cfg); rng=np.random.default_rng(701)
    n_payload=500
    bits=rng.integers(0,2,n_payload*cfg.n_data*modem.bits_per_symbol,dtype=np.uint8)
    ref=modem.modulate(bits); payload=ofdm.modulate(ref)
    # Four known training OFDM symbols give a diverse complex baseband waveform.
    train_bits=rng.integers(0,2,4*cfg.n_data*2,dtype=np.uint8)
    train_wave=ofdm.modulate(QAMModem(4).modulate(train_bits))
    frame=np.concatenate((train_wave,payload)); rows=[]
    for gain_db,phase_deg in ((0,0),(0.5,2),(1,4),(2,7),(3,10),(4,15)):
        impaired=apply_iq_imbalance(frame,gain_db,phase_deg)
        rx=add_awgn(impaired,30.0,np.random.default_rng(7100+int(10*gain_db)+phase_deg))
        tr_rx=rx[:len(train_wave)]; pl_rx=rx[len(train_wave):]
        a,b=estimate_iq_coefficients(train_wave,tr_rx)
        comp=compensate_iq_imbalance(pl_rx,a,b)
        raw_syms,_=ofdm.demodulate(pl_rx); comp_syms,_=ofdm.demodulate(comp)
        row=(gain_db,phase_deg,image_rejection_ratio_db(a,b),
             bit_error_rate(bits,modem.demodulate(raw_syms)),bit_error_rate(bits,modem.demodulate(comp_syms)),
             evm_percent(ref,raw_syms),evm_percent(ref,comp_syms))
        rows.append(row); print('gain=%g dB phase=%g deg IRR=%.1f rawBER=%.4g compBER=%.4g rawEVM=%.2f compEVM=%.2f'%row)
    with open(DATA/'iq_imbalance_compensation.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['gain_imbalance_db','phase_imbalance_deg','estimated_irr_db','raw_ber','compensated_ber','raw_evm_pct','compensated_evm_pct']); w.writerows(rows)
    a=np.asarray(rows,float); floor=1/len(bits)
    plt.figure(figsize=(7.3,4.9)); plt.semilogy(a[:,0],np.maximum(a[:,3],floor),'o-',label='Uncompensated'); plt.semilogy(a[:,0],np.maximum(a[:,4],floor),'s-',label='Training-LS compensation'); plt.xlabel('I/Q gain imbalance (dB)'); plt.ylabel('BER'); plt.title('64-QAM OFDM: IQ Imbalance Compensation'); plt.grid(True,which='both',alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'iq_imbalance_ber.png',dpi=180); plt.close()
    plt.figure(figsize=(7.3,4.9)); plt.plot(a[:,0],a[:,5],'o-',label='Uncompensated'); plt.plot(a[:,0],a[:,6],'s-',label='Compensated'); plt.xlabel('I/Q gain imbalance (dB)'); plt.ylabel('EVM (%)'); plt.title('Widely-Linear IQ Compensation'); plt.grid(True,alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(FIG/'iq_imbalance_evm.png',dpi=180); plt.close()

if __name__=='__main__': main()
