import numpy as np

from .downlink_differential import _packet_success_probability


def simulate_selective_downlink_repair(
    n_clients=24,
    rounds=160,
    dim=32,
    mean_snr_db=2.0,
    snr_std_db=5.5,
    periodic_keyframe_interval=10,
    delta_fraction=0.18,
    policy="selective_importance",
    importance_snr_anticorrelation=0.55,
    selective_global_keyframe_interval=30,
    seed=0,
):
    """Differential model broadcast with ACK-aware selective state repair.

    Every round carries a chained differential packet. Missing one packet breaks
    that client's reconstruction chain. ``periodic_keyframe`` periodically sends
    a common full-model keyframe. Selective policies spend approximately the same
    *extra* normalized downlink budget on client-specific repair snapshots whose
    payload grows with the client's version gap.

    The repair snapshot is an educational abstraction for a compressed
    client-specific resynchronization message; it is not a standardized codec.
    """
    if policy not in {"periodic_keyframe", "selective_age", "selective_importance"}:
        raise ValueError("unknown policy")
    if n_clients < 1 or rounds < 3 or periodic_keyframe_interval < 2:
        raise ValueError("invalid setup")
    if selective_global_keyframe_interval < periodic_keyframe_interval:
        raise ValueError("selective global keyframe interval must be no shorter than periodic baseline")
    rng = np.random.default_rng(seed + 2801)

    base_snr = np.clip(rng.normal(mean_snr_db, snr_std_db, n_clients), -13, 24)
    z = (base_snr - base_snr.mean()) / (base_snr.std() + 1e-9)
    raw_imp = -importance_snr_anticorrelation * z + np.sqrt(max(1 - importance_snr_anticorrelation**2, 0.0)) * rng.normal(size=n_clients)
    importance = np.exp(0.55 * raw_imp)
    importance /= importance.mean()

    model = np.zeros(dim)
    vel = np.zeros(dim)
    models = [model.copy()]
    for _ in range(1, rounds):
        vel = 0.80 * vel + 0.06 * rng.normal(size=dim)
        model = model + vel
        models.append(model.copy())
    models = np.asarray(models)

    client_model = np.zeros((n_clients, dim))
    last_version = np.zeros(n_clients, dtype=int)
    chain_ok = np.ones(n_clients, dtype=bool)
    total_size = 0.0
    repair_credit = 0.0
    repair_tx = repair_success = keyframes = 0
    age_hist, weighted_age_hist, mse_hist, weighted_mse_hist, coverage_hist = [], [], [], [], []

    # Selective repair receives the same long-run *extra* budget as one full
    # common keyframe every ``periodic_keyframe_interval`` rounds.
    baseline_extra_budget_per_round = 1.0 / periodic_keyframe_interval
    selective_global_budget_per_round = 1.0 / selective_global_keyframe_interval
    extra_budget_per_round = baseline_extra_budget_per_round - selective_global_budget_per_round

    for t in range(1, rounds):
        common = 1.1 * np.sin(2 * np.pi * t / 61.0)
        # A common fade makes global resync timing nontrivial.
        if 62 <= t < 82:
            common -= 5.5
        snr_t = np.clip(base_snr + common + rng.normal(0, 0.65, n_clients), -15, 26)

        # Chained differential packet every round.
        p_delta = _packet_success_probability(snr_t, delta_fraction)
        ok = rng.random(n_clients) < p_delta
        total_size += delta_fraction
        applicable = ok & chain_ok & (last_version == t - 1)
        if np.any(applicable):
            client_model[applicable] += models[t] - models[t - 1]
            last_version[applicable] = t
        chain_ok[~applicable] = False

        if policy == "periodic_keyframe" and t % periodic_keyframe_interval == 0:
            p = _packet_success_probability(snr_t, 1.0)
            good = rng.random(n_clients) < p
            total_size += 1.0
            keyframes += 1
            client_model[good] = models[t]
            last_version[good] = t
            chain_ok[good] = True
        elif policy != "periodic_keyframe":
            # Selective policies still send a much rarer common keyframe to avoid
            # indefinite chain fragmentation. The remaining budget is saved for
            # targeted client repair, keeping long-run extra airtime close to the
            # periodic-keyframe baseline.
            if t % selective_global_keyframe_interval == 0:
                p = _packet_success_probability(snr_t, 1.0)
                good = rng.random(n_clients) < p
                total_size += 1.0
                keyframes += 1
                client_model[good] = models[t]
                last_version[good] = t
                chain_ok[good] = True
            repair_credit += extra_budget_per_round
            # Multiple targeted repairs are allowed if saved credit is available.
            for _ in range(n_clients):
                age = t - last_version
                broken = ~chain_ok
                if not np.any(broken):
                    break
                # Client-specific snapshot size grows with missing-version span,
                # but remains below one full broadcast packet.
                repair_size = np.minimum(0.72, 0.20 + 0.026 * age)
                p_repair = _packet_success_probability(snr_t, repair_size)
                score = age * p_repair / np.maximum(repair_size, 1e-9)
                if policy == "selective_importance":
                    score = score * importance
                score = np.where(broken, score, -np.inf)
                i = int(np.argmax(score))
                cost = float(repair_size[i])
                if not np.isfinite(score[i]) or repair_credit + 1e-12 < cost:
                    break
                repair_credit -= cost
                total_size += cost
                repair_tx += 1
                if rng.random() < p_repair[i]:
                    repair_success += 1
                    client_model[i] = models[t]
                    last_version[i] = t
                    chain_ok[i] = True

        err = np.mean((client_model - models[t]) ** 2, axis=1)
        age = t - last_version
        mse_hist.append(float(np.mean(err)))
        weighted_mse_hist.append(float(np.sum(importance * err) / np.sum(importance)))
        age_hist.append(float(np.mean(age)))
        weighted_age_hist.append(float(np.sum(importance * age) / np.sum(importance)))
        coverage_hist.append(float(np.sum(importance * (age <= 5)) / np.sum(importance)))

    return {
        "policy": policy,
        "mean_model_mse": float(np.mean(mse_hist)),
        "weighted_model_mse": float(np.mean(weighted_mse_hist)),
        "mean_version_age": float(np.mean(age_hist)),
        "weighted_version_age": float(np.mean(weighted_age_hist)),
        "weighted_fresh_coverage": float(np.mean(coverage_hist)),
        "normalized_downlink_size_per_round": float(total_size / (rounds - 1)),
        "repair_transmissions": int(repair_tx),
        "repair_success_fraction": float(repair_success / max(repair_tx, 1)),
        "keyframes": int(keyframes),
        "importance_snr_correlation": float(np.corrcoef(importance, base_snr)[0, 1]),
        "age_history": np.asarray(age_hist),
        "weighted_age_history": np.asarray(weighted_age_hist),
        "mse_history": np.asarray(mse_hist),
    }
