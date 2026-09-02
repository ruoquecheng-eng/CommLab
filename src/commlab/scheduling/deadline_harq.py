from collections import deque
import numpy as np

from commlab.scheduling.ir_harq_fbl import block_fading_ir_error_probability
from commlab.link.link_adaptation import OuterLoopLinkAdaptation, select_mcs


def simulate_deadline_fbl_harq(true_snr_db: np.ndarray, estimated_snr_db: np.ndarray,
                               arrivals: np.ndarray, thresholds_db, efficiencies,
                               deadline_slots: int = 6, round_blocklength: int = 80,
                               mode: str = "ir", max_rounds: int = 4,
                               policy: str = "risk", target_bler: float = 1e-2,
                               use_olla: bool = True, seed: int = 1) -> dict:
    """Deadline-aware short-packet scheduling with FBL HARQ.

    The simulator retains a FIFO queue per user, but the scheduler can prioritize
    packets by deadline instead of only channel quality.

    Policies
    --------
    ``pf``
        Proportional-fair spectral-efficiency score.
    ``edf``
        Earliest-deadline-first, with estimated rate as a tie-breaker.
    ``risk``
        Urgency times estimated next-transmission success probability and payload.

    Packets that reach their deadline before successful decoding are expired and
    counted separately from HARQ max-round drops. This exposes reliability /
    timeliness trade-offs rather than hiding all failures in a single drop count.
    """
    T = np.asarray(true_snr_db, float)
    E = np.asarray(estimated_snr_db, float)
    A = np.asarray(arrivals, int)
    th = np.asarray(thresholds_db, float)
    eff = np.asarray(efficiencies, float)
    if T.ndim != 2 or E.shape != T.shape or A.shape != T.shape or np.any(A < 0):
        raise ValueError("invalid traces")
    if deadline_slots < 1 or round_blocklength < 1 or max_rounds < 1:
        raise ValueError("invalid packet timing")
    if mode not in {"ir", "chase"} or policy not in {"pf", "edf", "risk"}:
        raise ValueError("invalid HARQ/scheduler mode")
    if len(th) != len(eff) or np.any(eff <= 0):
        raise ValueError("invalid MCS table")

    S, U = T.shape
    rng = np.random.default_rng(seed)
    queues = [deque() for _ in range(U)]
    olla = [OuterLoopLinkAdaptation(target_bler=target_bler, nack_step_db=.18) for _ in range(U)]
    avg = np.ones(U, float)
    delivered_bits = 0.0
    used = 0
    attempts = 0
    nacks = 0
    maxround_drops = 0
    deadline_drops = 0
    delays = []
    backlog = np.zeros((S, U), int)
    tx_history = []

    def expire(t: int):
        nonlocal deadline_drops
        for q in queues:
            while q and t - q[0]["arrival"] >= deadline_slots:
                q.popleft(); deadline_drops += 1

    for t in range(S):
        expire(t)
        for u in range(U):
            for _ in range(int(A[t, u])):
                queues[u].append({"arrival": t, "mcs": None, "eff": None, "bits": None,
                                  "true_snrs": [], "est_snrs": [], "rounds": 0})
        active = [u for u in range(U) if queues[u]]
        if active:
            scores = []
            for u in active:
                p = queues[u][0]
                es = olla[u].effective_snr_db(E[t, u]) if use_olla else float(E[t, u])
                idx, e = select_mcs(es, th, eff)
                slack = max(deadline_slots - (t - p["arrival"]), 1)
                if policy == "pf":
                    score = float(e) / max(avg[u], 1e-9)
                elif policy == "edf":
                    score = 1e3 / slack + float(e)
                else:
                    # Estimate the reliability if this user is scheduled now.
                    prev = list(p["est_snrs"])
                    cur = 10 ** (es / 10)
                    est_snrs = prev + [cur]
                    pe = block_fading_ir_error_probability(
                        est_snrs if mode == "ir" else [float(np.sum(est_snrs))],
                        np.full(len(est_snrs), round_blocklength) if mode == "ir" else [round_blocklength],
                        float(round_blocklength * e if p["bits"] is None else p["bits"]),
                    )
                    urgency = 1.0 + 3.0 / slack
                    score = urgency * (1.0 - pe) * float(e) / max(avg[u], .25)
                scores.append((score, u, int(idx), float(e)))
            _, u, idx, e = max(scores, key=lambda x: x[0])
            p = queues[u][0]
            if p["mcs"] is None:
                p["mcs"] = idx; p["eff"] = e; p["bits"] = round_blocklength * e
            p["rounds"] += 1; attempts += 1; used += round_blocklength
            true_lin = 10 ** (T[t, u] / 10)
            est_eff = olla[u].effective_snr_db(E[t, u]) if use_olla else float(E[t, u])
            p["true_snrs"].append(true_lin); p["est_snrs"].append(10 ** (est_eff / 10))
            if mode == "ir":
                pe = block_fading_ir_error_probability(p["true_snrs"],
                                                        np.full(len(p["true_snrs"]), round_blocklength),
                                                        p["bits"])
            else:
                pe = block_fading_ir_error_probability([float(np.sum(p["true_snrs"]))],
                                                        [round_blocklength], p["bits"])
            ack = bool(rng.random() >= pe)
            if use_olla:
                olla[u].update(ack)
            tx_history.append((t, u, p["rounds"], float(pe), ack, deadline_slots - (t - p["arrival"])))
            if ack:
                queues[u].popleft(); delivered_bits += p["bits"]
                delays.append(t - p["arrival"] + 1)
                avg[u] = .98 * avg[u] + .02 * p["eff"]
            else:
                nacks += 1; avg[u] *= .98
                if p["rounds"] >= max_rounds:
                    queues[u].popleft(); maxround_drops += 1
        expire(t + 1)
        backlog[t] = [len(q) for q in queues]

    d = np.asarray(delays, float)
    total_arrivals = int(A.sum())
    misses = deadline_drops + maxround_drops
    return {
        "goodput_bits_per_channel_use": float(delivered_bits / max(used, 1)),
        "delivered_bits": float(delivered_bits),
        "completed_packets": int(len(d)),
        "deadline_drops": int(deadline_drops),
        "maxround_drops": int(maxround_drops),
        "deadline_miss_rate": float(misses / max(total_arrivals, 1)),
        "nack_rate": float(nacks / max(attempts, 1)),
        "mean_delay_slots": float(np.mean(d)) if len(d) else np.nan,
        "p95_delay_slots": float(np.percentile(d, 95)) if len(d) else np.nan,
        "pending_packets": int(sum(len(q) for q in queues)),
        "channel_uses": int(used),
        "backlog_packets": backlog,
        "tx_history": tx_history,
    }
