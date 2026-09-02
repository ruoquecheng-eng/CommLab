import numpy as np


def jain_fairness_index(values: np.ndarray) -> float:
    x=np.asarray(values,dtype=float).reshape(-1)
    den=len(x)*float(np.sum(x*x))
    return 0.0 if den<=0 else float(np.sum(x)**2/den)


def proportional_fair_schedule(
    achievable_rate: np.ndarray,
    beta: float = 0.98,
    initial_throughput: float = 1e-3,
) -> tuple[np.ndarray,np.ndarray,np.ndarray]:
    """Schedule one user per resource using the proportional-fair metric.

    ``achievable_rate`` shape is (slots, users, resources). Resource r in slot t
    is assigned to argmax_u R[t,u,r]/T[u]. Throughput state uses exponential
    averaging ``T <- beta*T + (1-beta)*slot_rate``.
    Returns (assignments, slot_user_rates, final_average_throughput).
    """
    R=np.asarray(achievable_rate,dtype=float)
    if R.ndim!=3 or np.any(R<0) or not (0<beta<1) or initial_throughput<=0:
        raise ValueError("invalid PF scheduling inputs")
    n_slots,n_users,n_res=R.shape
    T=np.full(n_users,float(initial_throughput))
    alloc=np.empty((n_slots,n_res),dtype=int)
    achieved=np.zeros((n_slots,n_users),dtype=float)
    for t in range(n_slots):
        metric=R[t]/T[:,None]
        who=np.argmax(metric,axis=0); alloc[t]=who
        slot=np.zeros(n_users,dtype=float)
        for u in range(n_users):
            mask=who==u
            if np.any(mask): slot[u]=float(np.sum(R[t,u,mask]))
        achieved[t]=slot
        T=beta*T+(1-beta)*slot
    return alloc,achieved,T
