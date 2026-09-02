from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

from commlab.config import OFDMConfig
from commlab.modulation import QAMModem
from commlab.ofdm import OFDMTransceiver
from commlab.channels import apply_doppler_multipath, add_awgn, channel_frequency_response
from commlab.equalization import zf_equalize
from commlab.estimation import estimate_data_channel_ls, estimate_channel_time_domain_ls
from commlab.metrics import bit_error_rate, evm_percent

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "results" / "figures"
DATA = ROOT / "results" / "data"


def genie_symbol_channels(taps, delays, path_nu, cfg, n_symbols):
    """Instantaneous frequency response at each OFDM symbol midpoint."""
    out = np.empty((n_symbols, cfg.n_fft), dtype=np.complex128)
    for m in range(n_symbols):
        center_n = m * cfg.symbol_len + cfg.cp_len + cfg.n_fft / 2.0
        coeff = taps * np.exp(1j * 2*np.pi * path_nu * center_n / cfg.n_fft)
        h = np.zeros(delays.max()+1, dtype=np.complex128)
        h[delays] = coeff
        out[m] = channel_frequency_response(h, cfg.n_fft)
    return out


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    pilot_positions = (-24, -20, -16, -12, -8, -4, 4, 8, 12, 16, 20, 24)
    cfg = OFDMConfig(pilot_subcarriers=pilot_positions, pilot_values=tuple(1+0j for _ in pilot_positions))
    modem = QAMModem(4)
    ofdm = OFDMTransceiver(cfg)
    rng = np.random.default_rng(701)
    n_symbols = 350
    bits = rng.integers(0, 2, n_symbols * cfg.n_data * 2, dtype=np.uint8)
    tx_symbols = modem.modulate(bits)
    tx = ofdm.modulate(tx_symbols)

    delays = np.array([0, 3, 8])
    taps = np.array([np.sqrt(0.65), np.sqrt(0.25)*np.exp(0.4j), np.sqrt(0.10)*np.exp(-0.8j)])
    static_taps = np.zeros(delays.max()+1, dtype=np.complex128)
    static_taps[delays] = taps
    H0 = channel_frequency_response(static_taps, cfg.n_fft)
    H0_data = H0[cfg.data_bins]

    nus = np.array([0.0, 0.001, 0.0025, 0.005, 0.01, 0.02, 0.04])
    rows = []
    for nu in nus:
        path_nu = np.array([nu, -0.55*nu, 0.8*nu])
        faded = apply_doppler_multipath(tx, taps, delays, path_nu, cfg.n_fft)
        rx = add_awgn(faded, 24.0, np.random.default_rng(7100 + int(nu*100000)))
        data, pilots = ofdm.demodulate(rx)
        data = data.reshape(n_symbols, cfg.n_data)
        pilots = pilots.reshape(n_symbols, len(cfg.pilot_bins))

        # Baseline: channel frozen at frame start.
        eq_static = zf_equalize(data, H0_data[None,:]).reshape(-1)
        ber_static = bit_error_rate(bits, modem.demodulate(eq_static))
        evm_static = evm_percent(tx_symbols, eq_static)

        # Practical tracker: re-estimate frequency-selective channel every symbol from 12 pilots.
        H_ls = estimate_data_channel_ls(pilots, cfg)
        eq_ls = zf_equalize(data, H_ls).reshape(-1)
        ber_ls = bit_error_rate(bits, modem.demodulate(eq_ls))
        evm_ls = evm_percent(tx_symbols, eq_ls)

        # Model-based tracker: infer a finite 9-tap CIR from the 12 pilots.
        H_td = estimate_channel_time_domain_ls(pilots, max_channel_len=9, config=cfg)
        eq_td = zf_equalize(data, H_td).reshape(-1)
        ber_td = bit_error_rate(bits, modem.demodulate(eq_td))
        evm_td = evm_percent(tx_symbols, eq_td)

        # Genie one-tap tracker: exact instantaneous H at each symbol center.
        Ht = genie_symbol_channels(taps, delays, path_nu, cfg, n_symbols)[:, cfg.data_bins]
        eq_genie = zf_equalize(data, Ht).reshape(-1)
        ber_genie = bit_error_rate(bits, modem.demodulate(eq_genie))
        evm_genie = evm_percent(tx_symbols, eq_genie)

        rows.append((nu, ber_static, ber_ls, ber_td, ber_genie, evm_static, evm_ls, evm_td, evm_genie))
        print(
            f"nu={nu:7.4f} Δf | BER static={ber_static:.4g} interp-LS={ber_ls:.4g} "
            f"TD-LS={ber_td:.4g} genie={ber_genie:.4g} | EVM {evm_static:.1f}/{evm_ls:.1f}/{evm_td:.1f}/{evm_genie:.1f}%"
        )

    with open(DATA / "doppler_ici.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "max_normalized_doppler", "static_ber", "pilot_interp_ls_ber", "time_domain_ls_ber", "genie_per_symbol_ber",
            "static_evm_percent", "pilot_interp_ls_evm_percent", "time_domain_ls_evm_percent", "genie_evm_percent"
        ])
        w.writerows(rows)

    a = np.asarray(rows)
    floor = 1/len(bits)
    plt.figure(figsize=(7.2, 4.8))
    plt.semilogy(a[:,0], np.maximum(a[:,1], floor), "o-", label="Frame-start static H")
    plt.semilogy(a[:,0], np.maximum(a[:,2], floor), "s-", label="Per-symbol 12-pilot LS")
    plt.semilogy(a[:,0], np.maximum(a[:,3], floor), "d-", label="Finite-CIR time-domain LS")
    plt.semilogy(a[:,0], np.maximum(a[:,4], floor), "^-", label="Genie per-symbol H")
    plt.xlabel("Maximum normalized Doppler (fraction of subcarrier spacing)")
    plt.ylabel("BER")
    plt.title("Time-Varying Multipath: Tracking Error vs Residual ICI")
    plt.grid(True, which="both", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG / "doppler_ici_ber.png", dpi=180)
    plt.close()

    plt.figure(figsize=(7.2, 4.8))
    plt.plot(a[:,0], a[:,5], "o-", label="Frame-start static H")
    plt.plot(a[:,0], a[:,6], "s-", label="Per-symbol 12-pilot interpolation")
    plt.plot(a[:,0], a[:,7], "d-", label="Finite-CIR time-domain LS")
    plt.plot(a[:,0], a[:,8], "^-", label="Genie per-symbol H")
    plt.xlabel("Maximum normalized Doppler")
    plt.ylabel("EVM (%)")
    plt.title("Even Perfect Per-Symbol Tracking Cannot Remove Within-Symbol ICI")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG / "doppler_ici_evm.png", dpi=180)
    plt.close()


if __name__ == "__main__":
    main()
