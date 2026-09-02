import numpy as np

from commlab.mimo.cell_free import sample_cell_free_channel, clustered_mrt_precoder, per_user_rates
from commlab.mimo.fronthaul import gauss_markov_channel_step, quantize_complex_csi


def csi_prediction_mse_score(beta: np.ndarray, ages: np.ndarray, correlation: np.ndarray,
                             mask: np.ndarray | None = None) -> np.ndarray:
    """Expected stale-CSI MSE score per AP under Gauss-Markov aging.

    For an AP with age ``a`` and one-step correlation ``rho``, a stale channel
    has expected innovation power proportional to ``1-rho**(2a)``.  The score
    weights that uncertainty by the large-scale fading of users served by the AP.
    It is an interpretable scheduling heuristic, not an optimal POMDP policy.
    """
    B=np.asarray(beta,float); a=np.asarray(ages,int).reshape(-1); r=np.asarray(correlation,float).reshape(-1)
    if B.ndim!=2 or len(a)!=B.shape[1] or len(r)!=B.shape[1] or np.any(a<0) or np.any((r<0)|(r>1)):
        raise ValueError('invalid CSI-age inputs')
    S=np.ones(B.shape,bool) if mask is None else np.asarray(mask,bool)
    if S.shape!=B.shape: raise ValueError('invalid support mask')
    uncertainty=1.0-np.power(r,2*a)
    return (B*S).sum(axis=0)*uncertainty


def select_csi_refresh_aps(beta: np.ndarray, ages: np.ndarray, correlation: np.ndarray,
                           budget: int, policy: str='uncertainty', mask: np.ndarray | None=None,
                           rr_start: int=0) -> np.ndarray:
    """Select AP indices to refresh under a per-slot AP-update budget."""
    M=np.asarray(beta).shape[1]
    if not (1<=int(budget)<=M) or policy not in {'uncertainty','bounded_uncertainty','round_robin'}:
        raise ValueError('invalid refresh policy')
    b=int(budget)
    if policy=='round_robin':
        return (int(rr_start)+np.arange(b))%M
    score=csi_prediction_mse_score(beta,ages,correlation,mask)
    if policy=='bounded_uncertainty':
        # Prevent low-power AP starvation while retaining uncertainty priority.
        max_age=max(2,int(np.ceil(M/b))*2)
        overdue=np.where(np.asarray(ages)>=max_age)[0]
        chosen=[]
        if len(overdue):
            order=overdue[np.argsort(-np.asarray(ages)[overdue],kind='stable')]
            chosen=list(order[:b])
        if len(chosen)<b:
            remain=np.array([m for m in range(M) if m not in chosen],int)
            order=remain[np.lexsort((remain,-score[remain]))]
            chosen.extend(order[:b-len(chosen)].tolist())
        return np.asarray(chosen,int)
    # Stable tie-breaking by index keeps deterministic tests/reproducibility.
    return np.lexsort((np.arange(M),-score))[:b]


def simulate_async_cellfree_csi(beta: np.ndarray, mask: np.ndarray,
                                correlation: float | np.ndarray, snr_linear: float,
                                bits_per_component: int=6, updates_per_slot: int=4,
                                n_slots: int=300, policy: str='uncertainty', seed: int=1) -> dict:
    """Cell-Free downlink with asynchronous AP-local CSI refresh.

    All APs acquire CSI at slot 0. Afterwards only ``updates_per_slot`` APs may
    refresh in each slot.  Between refreshes the CPU reuses stale quantized CSI.
    ``uncertainty`` scheduling prioritizes APs with the largest expected aging
    error weighted by the large-scale power of users they serve.  ``round_robin``
    is a fixed-budget baseline with identical update count.
    """
    B=np.asarray(beta,float); S=np.asarray(mask,bool)
    if B.ndim!=2 or S.shape!=B.shape or np.any(B<0) or snr_linear<=0 or n_slots<2:
        raise ValueError('invalid asynchronous Cell-Free setup')
    K,M=B.shape
    if np.isscalar(correlation): r=np.full(M,float(correlation))
    else: r=np.asarray(correlation,float).reshape(-1)
    if len(r)!=M or np.any((r<0)|(r>1)): raise ValueError('invalid AP correlations')
    if not (1<=updates_per_slot<=M): raise ValueError('invalid update budget')
    rng=np.random.default_rng(seed)
    H=sample_cell_free_channel(B,rng)
    Hhat=np.zeros_like(H)
    Hhat[S]=quantize_complex_csi(H[S],bits_per_component)
    ages=np.zeros(M,int); rr=0
    rates=[]; update_hist=[]; age_hist=[]; nmse_hist=[]
    for t in range(int(n_slots)):
        if t>0:
            # AP-specific temporal correlation.
            for m in range(M):
                H[:,m]=gauss_markov_channel_step(H[:,m],B[:,m],r[m],rng)
            ages+=1
            idx=select_csi_refresh_aps(B,ages,r,updates_per_slot,policy,S,rr)
            if policy=='round_robin': rr=(rr+updates_per_slot)%M
            for m in idx:
                served=S[:,m]
                Hhat[served,m]=quantize_complex_csi(H[served,m],bits_per_component)
                Hhat[~served,m]=0
                ages[m]=0
            update_hist.append(np.asarray(idx,int))
        else:
            update_hist.append(np.arange(M,dtype=int))
        W=clustered_mrt_precoder(Hhat,S)
        rates.append(per_user_rates(H,W,snr_linear))
        err=np.sum(np.abs((H-Hhat)[S])**2)
        den=max(np.sum(np.abs(H[S])**2),1e-15)
        nmse_hist.append(float(err/den)); age_hist.append(ages.copy())
    R=np.asarray(rates); A=np.asarray(age_hist)
    return {
        'rates':R,
        'mean_user_rate':float(R.mean()),
        'edge_rate':float(np.quantile(R,.05)),
        'mean_sum_rate':float(R.sum(axis=1).mean()),
        'mean_csi_nmse':float(np.mean(nmse_hist)),
        'mean_ap_age':float(A.mean()),
        'p95_ap_age':float(np.quantile(A,.95)),
        'ages':A,
        'update_history':update_hist,
        'updates_per_slot':int(updates_per_slot),
    }
