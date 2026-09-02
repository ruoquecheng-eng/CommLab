import numpy as np

from commlab.information_theory.finite_blocklength import normal_approximation_error_probability


def simulate_status_update_aoi(true_snr_db: np.ndarray, estimated_snr_db: np.ndarray,
                               blocklength: int = 100, rate: float = 1.0,
                               policy: str = "age_reliability",
                               retransmission: str = "fresh",
                               max_rounds: int = 3, seed: int = 1) -> dict:
    """Generate-at-will wireless status updates with Age of Information (AoI).

    One user is scheduled per slot. A successful fresh update resets that user's
    AoI to one slot; otherwise AoI increases. ``chase`` retransmission preserves
    the generation time of a failed update and combines SNR over attempts,
    exposing the classic reliability-versus-freshness tension of HARQ.

    Policies
    --------
    ``max_age``: serve the stalest user.
    ``max_snr``: serve the currently strongest estimated channel.
    ``age_reliability``: maximize age multiplied by estimated success probability.
    """
    T = np.asarray(true_snr_db, float)
    E = np.asarray(estimated_snr_db, float)
    if T.ndim != 2 or E.shape != T.shape or blocklength < 1 or rate < 0:
        raise ValueError("invalid AoI traces")
    if policy not in {"max_age", "max_snr", "age_reliability"}:
        raise ValueError("invalid AoI policy")
    if retransmission not in {"fresh", "chase"} or max_rounds < 1:
        raise ValueError("invalid retransmission setting")

    S, U = T.shape
    rng = np.random.default_rng(seed)
    age = np.ones(U, float)
    age_hist = np.zeros((S, U), float)
    successes = np.zeros(U, int)
    # Pending HARQ state per user. For fresh mode it is intentionally ignored.
    pending_gen = np.full(U, -1, int)
    pending_rounds = np.zeros(U, int)
    pending_true_snr = np.zeros(U, float)
    pending_est_snr = np.zeros(U, float)
    scheduled = np.zeros(U, int)
    peak_ages = []

    for t in range(S):
        if policy == "max_age":
            score = age.copy()
        elif policy == "max_snr":
            score = E[t].copy()
        else:
            est_lin = 10 ** (E[t] / 10)
            if retransmission == "chase":
                est_lin = est_lin + pending_est_snr
            pe = normal_approximation_error_probability(est_lin, blocklength, rate)
            score = age * (1.0 - pe)
        u = int(np.argmax(score))
        scheduled[u] += 1

        if retransmission == "fresh" or pending_gen[u] < 0:
            gen_time = t
            true_comb = 10 ** (T[t, u] / 10)
            est_comb = 10 ** (E[t, u] / 10)
            rounds = 1
        else:
            gen_time = int(pending_gen[u])
            true_comb = pending_true_snr[u] + 10 ** (T[t, u] / 10)
            est_comb = pending_est_snr[u] + 10 ** (E[t, u] / 10)
            rounds = int(pending_rounds[u] + 1)

        pe_true = float(normal_approximation_error_probability(true_comb, blocklength, rate))
        ack = bool(rng.random() >= pe_true)

        # Everyone gets one slot older; a successful update then resets the
        # scheduled receiver to the age of the delivered sample.
        age += 1.0
        if ack:
            peak_ages.append(float(age[u]))
            age[u] = float(t - gen_time + 1)
            successes[u] += 1
            pending_gen[u] = -1; pending_rounds[u] = 0
            pending_true_snr[u] = 0.0; pending_est_snr[u] = 0.0
        elif retransmission == "chase" and rounds < max_rounds:
            pending_gen[u] = gen_time; pending_rounds[u] = rounds
            pending_true_snr[u] = true_comb; pending_est_snr[u] = est_comb
        else:
            # Drop stale failed packet; next scheduling opportunity creates a
            # fresh sample. This avoids an indefinitely old HARQ packet.
            pending_gen[u] = -1; pending_rounds[u] = 0
            pending_true_snr[u] = 0.0; pending_est_snr[u] = 0.0

        age_hist[t] = age

    return {
        "mean_aoi": float(age_hist.mean()),
        "per_user_mean_aoi": age_hist.mean(axis=0),
        "p95_aoi": float(np.quantile(age_hist, .95)),
        "mean_peak_aoi": float(np.mean(peak_ages)) if peak_ages else np.nan,
        "delivery_rate_per_slot": float(successes.sum() / max(S, 1)),
        "successes": successes,
        "scheduled": scheduled,
        "age_history": age_hist,
    }
