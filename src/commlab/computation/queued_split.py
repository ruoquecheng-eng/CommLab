import heapq
import numpy as np


def simulate_queued_progressive_split(
    slots=2200,
    arrival_rate=0.72,
    n_users=8,
    policy="urgency_value",
    deadline_slots=9,
    local_accuracy=0.76,
    seed=0,
):
    """Multi-user progressive split inference over one shared radio server.

    Requests that are not confidently handled locally enter a shared radio
    queue. Each request has up to three progressive enhancement chunks. Serving
    a chunk consumes one slot and probabilistically improves task correctness.
    Expired requests fall back to their current prediction; late correctness is
    never counted as on-time success.

    Policies: FIFO, EDF, value-per-chunk, and urgency_value.
    """
    if policy not in {"fifo", "edf", "value", "urgency_value", "completion_aware"}:
        raise ValueError("unknown policy")
    if not (0 <= arrival_rate <= 2.5) or deadline_slots < 2:
        raise ValueError("invalid load")
    rng = np.random.default_rng(seed + 2704)
    user_snr = np.clip(rng.normal(4.0, 5.0, size=n_users), -8, 18)
    pending = []
    seq = 0
    completed = 0
    on_time_correct = 0
    on_time_weighted_utility = 0.0
    total_task_value = 0.0
    expired = 0
    radio_uses = 0
    delays = []
    backlog_hist = []

    # Each request stores: arrival, deadline, user, confidence, correctness prob,
    # next chunk, initial task value. We simulate expected task improvement and
    # then sample final correctness on completion/expiry.
    for t in range(slots):
        n_arr = rng.poisson(arrival_rate)
        for _ in range(n_arr):
            user = int(rng.integers(n_users))
            difficulty = rng.beta(2.0, 2.4)
            conf = np.clip(1 - difficulty + rng.normal(0, .07), 0.05, 0.98)
            task_value = float(0.5 + 1.2 * difficulty)
            total_task_value += task_value
            # High-confidence samples exit locally and consume no radio.
            if conf >= 0.84:
                completed += 1
                good = int(rng.random() < (0.70 + 0.28 * conf))
                on_time_correct += good
                on_time_weighted_utility += task_value * good
                delays.append(0)
                continue
            # Mixed task classes have heterogeneous deadlines. This prevents
            # EDF from degenerating to FIFO and models control/interactive/best-
            # effort inference requests sharing the same radio server.
            dscale = rng.choice([0.65, 1.0, 1.35], p=[0.28, 0.47, 0.25])
            dslots = max(3, int(round(deadline_slots * dscale)))
            req = {
                "seq": seq,
                "arrival": t,
                "deadline": t + dslots,
                "user": user,
                "conf": float(conf),
                "p_correct": float(local_accuracy * (0.78 + 0.22 * conf)),
                "chunk": 0,
                "value": task_value,
            }
            seq += 1; pending.append(req)

        # Expire before scheduling the current slot if deadline already passed.
        still = []
        for r in pending:
            if t > r["deadline"]:
                completed += 1; expired += 1
                # Correct but expired results do not count toward on-time metric.
                delays.append(t - r["arrival"])
            else:
                still.append(r)
        pending = still

        if pending:
            def priority(r):
                remaining = max(r["deadline"] - t + 1, 1)
                snr = user_snr[r["user"]]
                succ = 1 - np.exp(-10 ** (snr / 10) / 2.5)
                marginal = (1 - r["p_correct"]) * (0.42 / (1 + 0.35 * r["chunk"])) * succ * r["value"]
                if policy == "fifo": return (-r["arrival"],)
                if policy == "edf": return (-r["deadline"],)
                if policy == "value": return (marginal,)
                if policy == "urgency_value": return (marginal / remaining,)
                # Progressive inference has setup/completion locality: spreading
                # chunks over many requests can leave all of them unfinished.
                # Reward partially served jobs while retaining task-value and
                # slack awareness.
                completion = r["chunk"] / 3.0
                age_term = (t - r["arrival"]) / max((r["deadline"] - r["arrival"]), 1)
                return (marginal / remaining + 0.20 * completion + 0.035 * age_term,)

            if policy in {"fifo", "edf"}:
                # For negative time scores, max() returns earliest timestamp.
                idx = max(range(len(pending)), key=lambda i: priority(pending[i]))
            else:
                idx = max(range(len(pending)), key=lambda i: priority(pending[i]))
            r = pending.pop(idx)
            radio_uses += 1
            snr = user_snr[r["user"]] + rng.normal(0, 1.2)
            succ = 1 - np.exp(-10 ** (snr / 10) / 2.5)
            if rng.random() < succ:
                improvement = (1 - r["p_correct"]) * (0.52 / (1 + 0.28 * r["chunk"]))
                r["p_correct"] = min(0.995, r["p_correct"] + improvement)
            r["chunk"] += 1
            # Stop after 3 chunks or high confidence; otherwise requeue.
            if r["chunk"] >= 3 or r["p_correct"] >= 0.90:
                completed += 1
                good = int(rng.random() < r["p_correct"])
                on_time_correct += good
                on_time_weighted_utility += r["value"] * good
                delays.append(t - r["arrival"] + 1)
            else:
                pending.append(r)
        backlog_hist.append(len(pending))

    # Pending requests at horizon are treated as unfinished/deadline misses.
    expired += len(pending); completed += len(pending)
    delays.extend([slots - r["arrival"] for r in pending])
    return {
        "policy": policy,
        "completed_requests": int(completed),
        "on_time_accuracy": float(on_time_correct / max(completed, 1)),
        "on_time_task_utility": float(on_time_weighted_utility / max(total_task_value, 1e-12)),
        "deadline_miss_rate": float(expired / max(completed, 1)),
        "mean_radio_uses_per_request": float(radio_uses / max(completed, 1)),
        "mean_delay_slots": float(np.mean(delays) if delays else 0.0),
        "p95_delay_slots": float(np.quantile(delays, .95) if delays else 0.0),
        "mean_backlog": float(np.mean(backlog_hist)),
        "final_backlog": int(len(pending)),
    }
