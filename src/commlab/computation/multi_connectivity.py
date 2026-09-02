import numpy as np


def _correlated_link_success(rng, p1, p2, correlation):
    """Bernoulli pair with an interpretable common-randomness correlation knob."""
    n = len(p1)
    shared = rng.random(n) < correlation
    u0 = rng.random(n)
    u1 = rng.random(n)
    u2 = rng.random(n)
    a = np.where(shared, u0, u1)
    b = np.where(shared, u0, u2)
    return a < p1, b < p2


def simulate_multi_connectivity_reliability(
    n_packets=30000,
    policy="adaptive",
    correlation=0.25,
    mean_snr_db=-1.0,
    seed=0,
    duplication_threshold=0.172,
):
    """Single-link, full duplication, and adaptive dual-link reliability.

    Link outcomes use a common-randomness mixture to expose correlated failure.
    Adaptive duplication uses only a pre-transmission primary-link quality
    estimate; it does not inspect the realized packet outcome.
    """
    if policy not in {"single", "full_duplicate", "adaptive"}:
        raise ValueError("unknown policy")
    if n_packets < 100 or not (0 <= correlation <= 1) or duplication_threshold < 0:
        raise ValueError("invalid setup")

    rng = np.random.default_rng(seed + 3214)
    slow = rng.normal(0, 2.4, n_packets)
    q1 = mean_snr_db + slow + rng.normal(0, 1.1, n_packets)
    q2 = mean_snr_db + .8 * slow + .7 + rng.normal(0, 1.3, n_packets)
    g1 = 10 ** (q1 / 10)
    g2 = 10 ** (q2 / 10)
    p1 = 1 - np.exp(-g1 / 2.15)
    p2 = 1 - np.exp(-g2 / 2.35)
    s1, s2 = _correlated_link_success(rng, p1, p2, correlation)

    # No outcome genie: duplication is chosen from the quality estimate only.
    if policy == "single":
        dup = np.zeros(n_packets, dtype=bool)
    elif policy == "full_duplicate":
        dup = np.ones(n_packets, dtype=bool)
    else:
        # Chosen to duplicate approximately the lower 70-75% of primary-link
        # states in the baseline SNR region; exact rate is trace dependent.
        dup = ((1 - p1) * p2) > duplication_threshold

    delivered = s1 | (dup & s2)
    tx = 1 + dup.astype(int)
    # Duplicated paths race; single-path packets incur the primary delay.
    d1 = 5.5 + 8.0 / np.maximum(g1, .12) + rng.exponential(1.4, n_packets)
    d2 = 6.0 + 8.2 / np.maximum(g2, .12) + rng.exponential(1.5, n_packets)
    delay = np.where(dup, np.minimum(d1, d2), d1)
    delay = delay[delivered]

    return {
        "policy": policy,
        "correlation": float(correlation),
        "packet_outage_rate": float(1 - delivered.mean()),
        "packet_delivery_rate": float(delivered.mean()),
        "mean_transmissions_per_packet": float(tx.mean()),
        "duplication_rate": float(dup.mean()),
        "duplication_threshold": float(duplication_threshold),
        "mean_success_latency_ms": float(delay.mean()) if len(delay) else float("nan"),
        "p95_success_latency_ms": float(np.quantile(delay, .95)) if len(delay) else float("nan"),
    }
