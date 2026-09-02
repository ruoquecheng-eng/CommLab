import numpy as np


def waterfill_power_allocation(
    channel_power_gain: np.ndarray,
    total_power: float,
    noise_power: float,
    tol: float = 1e-12,
) -> np.ndarray:
    """Allocate power across parallel Gaussian subchannels by water-filling."""
    g = np.asarray(channel_power_gain, dtype=float).reshape(-1)
    if np.any(g < 0) or total_power < 0 or noise_power <= 0:
        raise ValueError("invalid gain/power parameters")
    if total_power == 0 or np.all(g == 0):
        return np.zeros_like(g)
    inv_snr = np.where(g > 0, noise_power / g, np.inf)
    finite = inv_snr[np.isfinite(inv_snr)]
    lo = float(np.min(finite))
    hi = float(np.max(finite) + total_power + 1.0)
    # Increase high bound until it supports enough total power.
    while np.sum(np.maximum(hi - inv_snr, 0.0)) < total_power:
        hi *= 2.0
    for _ in range(200):
        mu = 0.5 * (lo + hi)
        p = np.maximum(mu - inv_snr, 0.0)
        if abs(np.sum(p) - total_power) <= tol * max(1.0, total_power):
            break
        if np.sum(p) > total_power:
            hi = mu
        else:
            lo = mu
    p = np.maximum(0.5 * (lo + hi) - inv_snr, 0.0)
    if np.sum(p) > 0:
        p *= total_power / np.sum(p)
    return p


def parallel_channel_capacity_bits(
    channel_power_gain: np.ndarray,
    power_allocation: np.ndarray,
    noise_power: float,
) -> float:
    g = np.asarray(channel_power_gain, dtype=float).reshape(-1)
    p = np.asarray(power_allocation, dtype=float).reshape(-1)
    if g.shape != p.shape:
        raise ValueError("gain and allocation shapes must match")
    return float(np.sum(np.log2(1.0 + g * p / noise_power)))
