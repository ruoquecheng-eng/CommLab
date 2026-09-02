import numpy as np


def _projected_norm(h: np.ndarray, selected: np.ndarray) -> float:
    x=np.asarray(h,dtype=np.complex128).reshape(-1)
    if selected.size==0: return float(np.vdot(x,x).real)
    Q,_=np.linalg.qr(selected.conj().T,mode='reduced')
    r=x-Q@(Q.conj().T@x)
    return float(np.vdot(r,r).real)


def semi_orthogonal_user_selection(H: np.ndarray, n_select: int, alpha: float = 0.45) -> np.ndarray:
    """Greedy semi-orthogonal user selection for a MU-MISO downlink.

    H shape is (candidate_users, tx_antennas). At every step candidates with
    normalized correlation above ``alpha`` to any selected user are rejected;
    among the remainder, the largest orthogonal-projection norm is selected.
    If the strict pool empties, the least-correlated remaining user is used so
    the routine always returns ``n_select`` users when possible.
    """
    A=np.asarray(H,dtype=np.complex128)
    s=int(n_select)
    if A.ndim!=2 or not (1<=s<=min(A.shape[0],A.shape[1])) or not (0<alpha<=1):
        raise ValueError("invalid SUS inputs")
    norms=np.linalg.norm(A,axis=1)
    if np.any(norms<1e-15): raise ValueError("zero-norm user channel")
    chosen=[int(np.argmax(norms))]
    remaining=set(range(A.shape[0])); remaining.remove(chosen[0])
    while len(chosen)<s:
        S=A[chosen]
        strict=[]
        for i in remaining:
            corr=np.abs(S@A[i].conj())/(np.linalg.norm(S,axis=1)*norms[i])
            if np.all(corr<=alpha): strict.append(i)
        pool=strict if strict else list(remaining)
        if not pool: break
        if strict:
            score=[_projected_norm(A[i],S) for i in pool]
            pick=pool[int(np.argmax(score))]
        else:
            # Graceful fallback: favor low maximum correlation, then norm.
            vals=[]
            for i in pool:
                corr=np.abs(S@A[i].conj())/(np.linalg.norm(S,axis=1)*norms[i])
                vals.append((-float(np.max(corr)),float(norms[i])))
            pick=pool[max(range(len(pool)),key=lambda j: vals[j])]
        chosen.append(int(pick)); remaining.remove(pick)
    return np.asarray(chosen,dtype=int)


def strongest_norm_user_selection(H: np.ndarray, n_select: int) -> np.ndarray:
    A=np.asarray(H,dtype=np.complex128); s=int(n_select)
    if A.ndim!=2 or not (1<=s<=A.shape[0]): raise ValueError("invalid inputs")
    return np.argsort(np.linalg.norm(A,axis=1))[-s:][::-1]
