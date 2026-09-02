import math
import numpy as np


def _normal_cdf(x):
    # Scalar/array normal CDF without adding a SciPy dependency to this module.
    x = np.asarray(x, dtype=float)
    return np.vectorize(lambda v: .5 * (1.0 + math.erf(v / math.sqrt(2.0))))(x)


def simulate_chance_constrained_inference(
    n_tasks=12000,
    policy="chance",
    jitter_scale=0.45,
    deadline_ms=42.0,
    reliability_target=0.99,
    seed=0,
):
    """Deadline-aware edge inference admission with explicit tail uncertainty.

    ``mean_latency`` admits when the predicted mean completion time fits the
    deadline. ``chance`` admits only when a Gaussian latency model predicts
    P(T <= deadline) >= ``reliability_target``. Rejected tasks execute a smaller
    local fallback. Raw utility and on-time utility are both reported so a
    policy cannot hide deadline failures behind nominal accuracy.
    """
    if policy not in {"mean_latency", "chance"}:
        raise ValueError("unknown policy")
    if n_tasks < 100 or jitter_scale < 0 or not (0.5 < reliability_target < 1):
        raise ValueError("invalid setup")

    rng = np.random.default_rng(seed + 3212)
    difficulty = rng.beta(2.2, 2.0, n_tasks)
    radio_state = rng.normal(0, 1, n_tasks)
    compute_state = rng.normal(0, 1, n_tasks)

    # Offload is more accurate, but its latency has a stochastic tail.
    local_acc = np.clip(.69 + .16 * (1 - difficulty), .60, .88)
    edge_acc = np.clip(.87 + .09 * (1 - difficulty), .80, .97)
    value = .65 + 1.25 * difficulty

    mean_latency = 25.0 + 5.0 * difficulty + 2.8 * np.maximum(-radio_state, 0) + 2.0 * np.maximum(compute_state, 0)
    sigma = 1.8 + jitter_scale * (7.0 + 4.0 * difficulty)
    p_on_time_pred = _normal_cdf((deadline_ms - mean_latency) / np.maximum(sigma, 1e-9))

    if policy == "mean_latency":
        admit = mean_latency <= deadline_ms
    else:
        admit = p_on_time_pred >= reliability_target

    actual_latency = mean_latency + sigma * rng.normal(size=n_tasks)
    actual_latency = np.maximum(actual_latency, 1.0)
    on_time = actual_latency <= deadline_ms

    correct_edge = rng.random(n_tasks) < edge_acc
    correct_local = rng.random(n_tasks) < local_acc
    chosen_correct = np.where(admit, correct_edge, correct_local)
    # Local fallback is assumed to meet this edge deadline abstraction.
    chosen_on_time = np.where(admit, on_time, True)

    raw_utility = value * chosen_correct
    ontime_utility = value * chosen_correct * chosen_on_time
    admitted = int(admit.sum())
    admitted_miss = int(np.sum(admit & ~on_time))

    return {
        "policy": policy,
        "jitter_scale": float(jitter_scale),
        "admission_rate": float(admit.mean()),
        "rejection_rate": float(1 - admit.mean()),
        "deadline_miss_rate": float(admitted_miss / max(admitted, 1)),
        "overall_late_fraction": float(admitted_miss / n_tasks),
        "raw_utility_per_task": float(raw_utility.mean()),
        "on_time_utility_per_task": float(ontime_utility.mean()),
        "mean_admitted_latency_ms": float(actual_latency[admit].mean()) if admitted else 0.0,
        "p95_admitted_latency_ms": float(np.quantile(actual_latency[admit], .95)) if admitted else 0.0,
        "predicted_on_time_probability_mean": float(p_on_time_pred[admit].mean()) if admitted else 1.0,
    }
