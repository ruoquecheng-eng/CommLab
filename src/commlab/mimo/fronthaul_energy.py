import numpy as np

from commlab.mimo.cell_free import sample_cell_free_channel, clustered_mrt_precoder, per_user_rates
from commlab.mimo.fronthaul import quantize_complex_csi, gauss_markov_channel_step


def fronthaul_power_from_csi(n_links: int, bits_per_component: int, update_interval_slots: int,
                             energy_per_bit_j: float = 2e-6, slot_duration_s: float = 1e-3) -> float:
    """Abstract fronthaul power for periodic complex-CSI updates."""
    if n_links < 0 or bits_per_component < 1 or update_interval_slots < 1 or energy_per_bit_j < 0 or slot_duration_s <= 0:
        raise ValueError("invalid fronthaul-power parameters")
    bits_per_update = 2 * int(n_links) * int(bits_per_component)
    return float(bits_per_update * energy_per_bit_j / (int(update_interval_slots) * slot_duration_s))


def simulate_cellfree_fronthaul_energy(beta: np.ndarray, active_aps: np.ndarray,
                                       bits_per_component: int, update_interval_slots: int,
                                       correlation: float, snr_linear: float,
                                       n_slots: int = 400, seed: int = 1,
                                       tx_power_w: float = 1.0,
                                       circuit_power_per_ap_w: float = 0.12,
                                       fixed_power_w: float = 0.6,
                                       energy_per_fronthaul_bit_j: float = 2e-6,
                                       slot_duration_s: float = 1e-3) -> dict:
    """Dynamic Cell-Free link with stale/quantized CSI and fronthaul energy.

    APs outside ``active_aps`` neither transmit nor report CSI.  On update slots,
    active-link CSI is scalar-quantized; between updates the precoder is stale.
    """
    B = np.asarray(beta, float); active = np.asarray(active_aps, bool).reshape(-1)
    if B.ndim != 2 or len(active) != B.shape[1] or not np.any(active) or n_slots < 1 or snr_linear <= 0:
        raise ValueError("invalid network configuration")
    K, M = B.shape; rng = np.random.default_rng(seed); H = sample_cell_free_channel(B, rng)
    support = np.tile(active[None, :], (K, 1)); Hhat = np.zeros_like(H); W = None; rates = []
    for t in range(int(n_slots)):
        if t > 0:
            H = gauss_markov_channel_step(H, B, correlation, rng)
        if t % int(update_interval_slots) == 0 or W is None:
            Hhat.fill(0)
            Hhat[:, active] = quantize_complex_csi(H[:, active], bits_per_component)
            W = clustered_mrt_precoder(Hhat, support)
        rates.append(per_user_rates(H, W, snr_linear))
    R = np.asarray(rates)
    n_active = int(active.sum()); n_links = int(K * n_active)
    pfh = fronthaul_power_from_csi(n_links, bits_per_component, update_interval_slots,
                                   energy_per_fronthaul_bit_j, slot_duration_s)
    total_power = float(tx_power_w + n_active * circuit_power_per_ap_w + fixed_power_w + pfh)
    mean_sum = float(R.sum(axis=1).mean())
    return {
        "mean_user_rate": float(R.mean()), "edge_rate": float(np.quantile(R, .05)),
        "mean_sum_rate": mean_sum, "fronthaul_power_w": pfh,
        "total_power_w": total_power, "energy_efficiency": mean_sum / total_power,
        "rates": R,
    }
