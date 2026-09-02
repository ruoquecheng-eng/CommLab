from collections import deque
import numpy as np
from commlab.link.link_adaptation import OuterLoopLinkAdaptation, select_mcs, logistic_bler


def simulate_cross_layer_link(
    true_snr_db: np.ndarray,
    estimated_snr_db: np.ndarray,
    arrivals: np.ndarray,
    thresholds_db,
    efficiencies,
    payload_bits: int = 12000,
    policy: str = 'pf',
    target_bler: float = 0.1,
    use_olla: bool = True,
    use_harq: bool = True,
    max_attempts: int = 4,
    seed: int = 1,
    beta: float = 0.98,
    delay_weight: float = 2.0,
) -> dict:
    """Event-driven packet scheduler with OLLA and abstract Chase HARQ.

    One resource opportunity is available per slot. A packet keeps the MCS used
    on its first attempt. Chase combining accumulates linear-SNR evidence across
    retransmissions. This is a transparent system-level abstraction, not a
    standards HARQ/rate-matching implementation.
    """
    T = np.asarray(true_snr_db, float)
    E = np.asarray(estimated_snr_db, float)
    A = np.asarray(arrivals, int)
    if T.ndim != 2 or E.shape != T.shape or A.shape != T.shape or np.any(A < 0):
        raise ValueError('arrays must be (slots,users) with matching shapes')
    if policy not in {'max_rate', 'pf', 'delay_pf'} or payload_bits < 1 or max_attempts < 1:
        raise ValueError('invalid simulator parameters')
    S, U = T.shape
    rng = np.random.default_rng(seed)
    qs = [deque() for _ in range(U)]
    olla = [OuterLoopLinkAdaptation(target_bler=target_bler) for _ in range(U)]
    avg = np.ones(U, float)
    delivered = np.zeros(U, float)
    tx_count = np.zeros(U, int); nack_count = np.zeros(U, int)
    delays = []; drops = 0; mcs_hist = []; offset_hist = np.zeros((S, U), float)
    backlog = np.zeros((S, U), int)
    for t in range(S):
        for u in range(U):
            for _ in range(int(A[t, u])):
                qs[u].append({'arrival': t, 'attempts': 0, 'snr_lin': 0.0, 'mcs': None, 'eff': None})
        active = np.array([len(q) > 0 for q in qs], bool)
        if np.any(active):
            metric = np.full(U, -np.inf)
            for u in np.where(active)[0]:
                eff_snr = olla[u].effective_snr_db(E[t, u]) if use_olla else E[t, u]
                idx, eff = select_mcs(eff_snr, thresholds_db, efficiencies)
                val = eff
                if policy in {'pf', 'delay_pf'}:
                    val /= max(avg[u], 1e-9)
                if policy == 'delay_pf':
                    hol = t - qs[u][0]['arrival'] + 1
                    val *= 1.0 + float(delay_weight) * hol / 20.0
                metric[u] = val
            u = int(np.argmax(metric))
            pkt = qs[u][0]
            if pkt['mcs'] is None:
                eff_snr = olla[u].effective_snr_db(E[t, u]) if use_olla else E[t, u]
                idx, eff = select_mcs(eff_snr, thresholds_db, efficiencies)
                pkt['mcs'] = idx; pkt['eff'] = eff
            idx = int(pkt['mcs']); eff = float(pkt['eff'])
            pkt['attempts'] += 1; tx_count[u] += 1
            this_lin = 10 ** (T[t, u] / 10)
            pkt['snr_lin'] = pkt['snr_lin'] + this_lin if use_harq else this_lin
            comb_db = 10 * np.log10(max(pkt['snr_lin'], 1e-15))
            p_fail = logistic_bler(comb_db, np.asarray(thresholds_db, float)[idx], midpoint_bler=target_bler)
            ack = bool(rng.random() >= p_fail)
            if use_olla:
                olla[u].update(ack)
            mcs_hist.append((t, u, idx, eff, ack, pkt['attempts'], comb_db))
            if ack:
                qs[u].popleft(); delivered[u] += payload_bits; delays.append(t - pkt['arrival'] + 1)
                avg[u] = beta * avg[u] + (1-beta) * eff
            else:
                nack_count[u] += 1
                if pkt['attempts'] >= max_attempts:
                    qs[u].popleft(); drops += 1
                avg[u] = beta * avg[u]
        offset_hist[t] = [x.offset_db for x in olla]
        backlog[t] = [len(q) for q in qs]
    d = np.asarray(delays, float)
    return {
        'delivered_bits': delivered,
        'total_delivered_bits': float(delivered.sum()),
        'transmissions': tx_count,
        'nacks': nack_count,
        'completed_packets': int(len(delays)),
        'dropped_packets': int(drops),
        'pending_packets': int(sum(len(q) for q in qs)),
        'mean_delay_slots': float(np.mean(d)) if len(d) else float('nan'),
        'p95_delay_slots': float(np.percentile(d, 95)) if len(d) else float('nan'),
        'packet_delays': d,
        'backlog_packets': backlog,
        'olla_offset_db': offset_hist,
        'mcs_history': mcs_hist,
        'goodput_bits_per_slot': float(delivered.sum()/S),
        'nack_rate': float(nack_count.sum()/max(tx_count.sum(),1)),
    }
