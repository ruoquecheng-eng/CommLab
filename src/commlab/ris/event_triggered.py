import numpy as np

from commlab.ris.cellfree import coordinate_optimize_cellfree_ris, effective_cellfree_ris_channel
from commlab.mimo.cell_free import clustered_mrt_precoder, per_user_rates
from commlab.ris.two_timescale import apply_ris_phase_noise


def simulate_event_triggered_cellfree_ris(channel_sequence, snr_linear: float,
                                           bits: int = 2,
                                           rate_drop_threshold: float = 0.08,
                                           min_interval: int = 2,
                                           max_interval: int = 16,
                                           phase_noise_std_deg: float = 0.0,
                                           mask: np.ndarray | None = None,
                                           seed: int = 1) -> dict:
    """Event-triggered RIS refresh using observed held-phase rate degradation.

    The RIS is optimized at the first slot. Afterwards its phase profile is held
    until either (i) the observed sum rate with the held profile falls below a
    fraction of the post-update reference rate, or (ii) ``max_interval`` is
    reached. ``min_interval`` prevents pathological update chatter.

    AP precoding is always recomputed from the current effective channel, so the
    experiment isolates passive-RIS control overhead. The trigger is a practical
    probe-based heuristic, not a globally optimal partially observed controller.
    """
    seq = list(channel_sequence)
    if len(seq) < 2 or snr_linear <= 0 or bits < 1:
        raise ValueError("invalid event-triggered RIS setup")
    if not (0 <= rate_drop_threshold < 1) or min_interval < 1 or max_interval < min_interval:
        raise ValueError("invalid trigger parameters")
    N = np.asarray(seq[0][1]).shape[0]
    rng = np.random.default_rng(seed)

    phases, _ = coordinate_optimize_cellfree_ris(*seq[0], snr_linear, bits=bits,
                                                  iterations=1, mask=mask)
    last_update = 0
    updates = [0]
    held_rates = []
    ideal_rates = []
    trigger_values = []

    def eval_rates(ch, th):
        D, G, R = ch
        applied = apply_ris_phase_noise(th, phase_noise_std_deg, rng)
        H = effective_cellfree_ris_channel(D, G, R, applied)
        W = clustered_mrt_precoder(H, mask)
        return per_user_rates(H, W, snr_linear)

    ref_sum = float(eval_rates(seq[0], phases).sum())
    for t, ch in enumerate(seq):
        if t == 0:
            held = eval_rates(ch, phases)
        else:
            probe = eval_rates(ch, phases)
            probe_sum = float(probe.sum())
            age = t - last_update
            drop = max((ref_sum - probe_sum) / max(ref_sum, 1e-12), 0.0)
            should = (age >= min_interval and drop >= rate_drop_threshold) or age >= max_interval
            if should:
                phases, _ = coordinate_optimize_cellfree_ris(*ch, snr_linear, bits=bits,
                                                              iterations=1, mask=mask,
                                                              initial_phases=phases)
                last_update = t
                updates.append(t)
                held = eval_rates(ch, phases)
                ref_sum = float(held.sum())
            else:
                held = probe
            trigger_values.append(drop)
        ideal, _ = coordinate_optimize_cellfree_ris(*ch, snr_linear, bits=bits,
                                                    iterations=1, mask=mask)
        ideal_rates.append(eval_rates(ch, ideal))
        held_rates.append(held)

    H = np.asarray(held_rates)
    I = np.asarray(ideal_rates)
    return {
        "rates": H,
        "ideal_rates": I,
        "mean_sum_rate": float(H.sum(axis=1).mean()),
        "ideal_mean_sum_rate": float(I.sum(axis=1).mean()),
        "edge_rate": float(np.quantile(H, .05)),
        "updates": np.asarray(updates, int),
        "n_updates": int(len(updates)),
        "control_bits_per_slot": float(len(updates) * N * bits / len(seq)),
        "mean_update_interval": float((len(seq) - 1) / max(len(updates) - 1, 1)),
        "trigger_drop": np.asarray(trigger_values, float),
    }
