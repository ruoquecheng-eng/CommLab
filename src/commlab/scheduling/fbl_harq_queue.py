from collections import deque
import numpy as np

from commlab.information_theory.finite_blocklength import normal_approximation_error_probability
from commlab.link.link_adaptation import OuterLoopLinkAdaptation, select_mcs


def simulate_fbl_harq_queue(true_snr_db: np.ndarray, estimated_snr_db: np.ndarray,
                            arrivals: np.ndarray, thresholds_db, efficiencies,
                            blocklength: int = 120, target_bler: float = 1e-2,
                            payload_scale: float = 1.0, max_attempts: int = 4,
                            policy: str = "pf", use_olla: bool = True,
                            use_harq: bool = True, seed: int = 1,
                            delay_weight: float = 2.0) -> dict:
    """Multi-user finite-blocklength queue with Chase HARQ and OLLA.

    Each scheduled attempt consumes ``blocklength`` complex channel uses.  A
    packet's information payload is ``blocklength * efficiency * payload_scale``
    chosen on its first transmission.  Chase HARQ combines linear SNR while the
    FBL normal approximation maps combined SNR to packet-error probability.
    """
    T = np.asarray(true_snr_db, float); E = np.asarray(estimated_snr_db, float)
    A = np.asarray(arrivals, int); th = np.asarray(thresholds_db, float)
    effs = np.asarray(efficiencies, float)
    if T.ndim != 2 or E.shape != T.shape or A.shape != T.shape or np.any(A < 0):
        raise ValueError("invalid traces")
    if blocklength < 1 or max_attempts < 1 or policy not in {"pf", "delay_pf", "max_rate"}:
        raise ValueError("invalid simulator configuration")
    if len(th) != len(effs) or np.any(effs <= 0) or not (0 < target_bler < .5):
        raise ValueError("invalid MCS table")
    S, U = T.shape; rng = np.random.default_rng(seed)
    qs = [deque() for _ in range(U)]
    olla = [OuterLoopLinkAdaptation(target_bler=target_bler, nack_step_db=.18) for _ in range(U)]
    avg = np.ones(U); delivered = np.zeros(U); tx = np.zeros(U, int); nacks = np.zeros(U, int)
    delays = []; drops = 0; mcs_hist = []; backlog = np.zeros((S, U), int)
    for t in range(S):
        for u in range(U):
            for _ in range(int(A[t, u])):
                qs[u].append({"arrival": t, "attempts": 0, "snr_lin": 0.0,
                              "mcs": None, "eff": None, "payload": None})
        active = [u for u in range(U) if qs[u]]
        if active:
            metrics = []; choices = []
            for u in active:
                es = olla[u].effective_snr_db(E[t, u]) if use_olla else float(E[t, u])
                idx, eff = select_mcs(es, th, effs)
                # FBL-aware backoff based on the estimated first-shot reliability.
                while idx > 0 and float(normal_approximation_error_probability(
                        10 ** (es / 10), blocklength, effs[idx])) > target_bler:
                    idx -= 1
                score = float(effs[idx])
                if policy in {"pf", "delay_pf"}:
                    score /= max(avg[u], 1e-9)
                if policy == "delay_pf":
                    hol = t - qs[u][0]["arrival"] + 1
                    score *= 1.0 + float(delay_weight) * hol / 20.0
                metrics.append(score); choices.append(int(idx))
            j = int(np.argmax(metrics)); u = active[j]; pkt = qs[u][0]
            if pkt["mcs"] is None:
                pkt["mcs"] = choices[j]; pkt["eff"] = float(effs[choices[j]])
                pkt["payload"] = float(blocklength * pkt["eff"] * payload_scale)
            idx = int(pkt["mcs"]); pkt["attempts"] += 1; tx[u] += 1
            this = 10 ** (T[t, u] / 10)
            pkt["snr_lin"] = pkt["snr_lin"] + this if use_harq else this
            pe = float(normal_approximation_error_probability(pkt["snr_lin"], blocklength, pkt["eff"]))
            ack = bool(rng.random() >= pe)
            if use_olla: olla[u].update(ack)
            mcs_hist.append((t, u, idx, ack, pkt["attempts"], pe))
            if ack:
                qs[u].popleft(); delivered[u] += pkt["payload"]
                delays.append(t - pkt["arrival"] + 1); avg[u] = .98 * avg[u] + .02 * pkt["eff"]
            else:
                nacks[u] += 1; avg[u] *= .98
                if pkt["attempts"] >= max_attempts:
                    qs[u].popleft(); drops += 1
        backlog[t] = [len(q) for q in qs]
    d = np.asarray(delays, float); attempts = int(tx.sum())
    return {
        "goodput_bits_per_use": float(delivered.sum() / max(S * blocklength, 1)),
        "goodput_bits_per_slot": float(delivered.sum() / S),
        "nack_rate": float(nacks.sum() / max(attempts, 1)),
        "mean_delay_slots": float(np.mean(d)) if len(d) else np.nan,
        "p95_delay_slots": float(np.percentile(d, 95)) if len(d) else np.nan,
        "drops": int(drops), "completed_packets": int(len(d)),
        "pending_packets": int(sum(len(q) for q in qs)),
        "backlog_packets": backlog,
        "mean_attempts_per_completed": float(attempts / max(len(d), 1)),
        "final_olla_offset_db": np.array([o.offset_db for o in olla]),
        "mcs_history": mcs_hist,
    }
