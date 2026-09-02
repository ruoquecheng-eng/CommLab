from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

from commlab.config import OFDMConfig
from commlab.modulation import QAMModem
from commlab.ofdm import OFDMTransceiver
from commlab.channels import apply_multipath, add_awgn, channel_frequency_response
from commlab.estimation import estimate_data_channel_ls, estimate_channel_time_domain_ls
from commlab.equalization import zf_equalize
from commlab.metrics import bit_error_rate, normalized_mean_square_error

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "results" / "figures"
DATA = ROOT / "results" / "data"


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    positions = (-24, -20, -16, -12, -8, -4, 4, 8, 12, 16, 20, 24)
    cfg = OFDMConfig(pilot_subcarriers=positions, pilot_values=tuple(1+0j for _ in positions))
    modem = QAMModem(16)
    ofdm = OFDMTransceiver(cfg)
    rng = np.random.default_rng(901)
    n_symbols = 900
    bits = rng.integers(0, 2, n_symbols * cfg.n_data * 4, dtype=np.uint8)
    tx_symbols = modem.modulate(bits)
    tx = ofdm.modulate(tx_symbols)

    taps = np.zeros(9, dtype=np.complex128)
    taps[[0,2,5,8]] = [1.0, 0.45*np.exp(0.3j), 0.30*np.exp(-0.7j), 0.18*np.exp(1.0j)]
    taps /= np.linalg.norm(taps)
    H = channel_frequency_response(taps, cfg.n_fft)[cfg.data_bins]
    H_true = np.tile(H, (n_symbols,1))

    rows = []
    for snr in np.arange(0,31,5):
        rx = add_awgn(apply_multipath(tx, taps), float(snr), np.random.default_rng(9200+int(snr)))
        data, pilots = ofdm.demodulate(rx)
        data = data.reshape(n_symbols, cfg.n_data)
        h_interp = estimate_data_channel_ls(pilots, cfg)
        h_td = estimate_channel_time_domain_ls(pilots, max_channel_len=9, config=cfg)

        e_perfect = zf_equalize(data, H[None,:]).reshape(-1)
        e_interp = zf_equalize(data, h_interp).reshape(-1)
        e_td = zf_equalize(data, h_td).reshape(-1)
        ber_p = bit_error_rate(bits, modem.demodulate(e_perfect))
        ber_i = bit_error_rate(bits, modem.demodulate(e_interp))
        ber_t = bit_error_rate(bits, modem.demodulate(e_td))
        nmse_i = normalized_mean_square_error(H_true, h_interp)
        nmse_t = normalized_mean_square_error(H_true, h_td)
        rows.append((snr, ber_p, ber_i, ber_t, nmse_i, nmse_t))
        print(f"SNR={snr:2d} | BER perfect={ber_p:.5g} interp={ber_i:.5g} TD-LS={ber_t:.5g} | NMSE {nmse_i:.4g}/{nmse_t:.4g}")

    with open(DATA / "channel_estimation_methods.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["snr_db", "perfect_csi_ber", "interp_ls_ber", "time_domain_ls_ber", "interp_ls_nmse", "time_domain_ls_nmse"])
        w.writerows(rows)

    a=np.asarray(rows)
    floor=1/len(bits)
    plt.figure(figsize=(7.2,4.8))
    plt.semilogy(a[:,0], np.maximum(a[:,1],floor), '^-', label='Perfect CSI')
    plt.semilogy(a[:,0], np.maximum(a[:,2],floor), 'o-', label='Pilot LS + linear interpolation')
    plt.semilogy(a[:,0], np.maximum(a[:,3],floor), 's-', label='Finite-CIR time-domain LS')
    plt.xlabel('Sample-domain SNR (dB)'); plt.ylabel('BER')
    plt.title('16-QAM OFDM: Model-Based Channel Estimation')
    plt.grid(True,which='both',alpha=.3); plt.legend(); plt.tight_layout()
    plt.savefig(FIG/'channel_estimation_methods_ber.png',dpi=180); plt.close()

    plt.figure(figsize=(7.2,4.8))
    plt.semilogy(a[:,0], a[:,4], 'o-', label='Pilot interpolation LS')
    plt.semilogy(a[:,0], a[:,5], 's-', label='Finite-CIR time-domain LS')
    plt.xlabel('Sample-domain SNR (dB)'); plt.ylabel('Channel NMSE')
    plt.title('Using Finite Channel Memory Removes the Interpolation Error Floor')
    plt.grid(True,which='both',alpha=.3); plt.legend(); plt.tight_layout()
    plt.savefig(FIG/'channel_estimation_methods_nmse.png',dpi=180); plt.close()

if __name__=='__main__':
    main()
