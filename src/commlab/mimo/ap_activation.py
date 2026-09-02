import numpy as np
from commlab.mimo.cell_free import clustered_mrt_precoder, per_user_rates


def strongest_ap_activation(beta: np.ndarray, n_active: int) -> np.ndarray:
    B=np.asarray(beta,float)
    if B.ndim!=2 or np.any(B<0) or not (1<=int(n_active)<=B.shape[1]):
        raise ValueError('invalid beta/active count')
    score=B.sum(axis=0)
    idx=np.argpartition(score,-int(n_active))[-int(n_active):]
    out=np.zeros(B.shape[1],bool); out[idx]=True
    return out


def coverage_aware_ap_activation(beta: np.ndarray, n_active: int) -> np.ndarray:
    """Greedy AP activation maximizing weakest accumulated large-scale gain."""
    B=np.asarray(beta,float)
    if B.ndim!=2 or np.any(B<0) or not (1<=int(n_active)<=B.shape[1]):
        raise ValueError('invalid beta/active count')
    K,M=B.shape; active=[]; acc=np.zeros(K)
    remaining=set(range(M))
    for _ in range(int(n_active)):
        best=None; best_key=None
        for m in remaining:
            cand=acc+B[:,m]
            key=(float(cand.min()),float(cand.mean()))
            if best_key is None or key>best_key:
                best_key=key; best=m
        active.append(best); remaining.remove(best); acc+=B[:,best]
    out=np.zeros(M,bool); out[active]=True
    return out


def rates_with_active_aps(H: np.ndarray, active_aps: np.ndarray, snr_linear: float) -> np.ndarray:
    A=np.asarray(H,np.complex128); active=np.asarray(active_aps,bool).reshape(-1)
    if A.ndim!=2 or len(active)!=A.shape[1] or not np.any(active):
        raise ValueError('invalid active AP mask')
    mask=np.tile(active[None,:],(A.shape[0],1))
    W=clustered_mrt_precoder(A,mask=mask)
    return per_user_rates(A,W,snr_linear)


def network_energy_efficiency(sum_rate: float, n_active: int, tx_power_w: float = 1.0,
                              circuit_power_per_ap_w: float = 0.15,
                              fixed_power_w: float = 0.5) -> float:
    if sum_rate<0 or n_active<1 or tx_power_w<=0 or circuit_power_per_ap_w<0 or fixed_power_w<0:
        raise ValueError('invalid power/rate')
    p=float(tx_power_w)+int(n_active)*float(circuit_power_per_ap_w)+float(fixed_power_w)
    return float(sum_rate/p)
