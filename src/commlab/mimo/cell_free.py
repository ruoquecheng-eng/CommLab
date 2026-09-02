import numpy as np


def large_scale_fading(ap_xy: np.ndarray, user_xy: np.ndarray, pathloss_exp: float = 3.2,
                       min_distance: float = 0.03, shadow_std_db: float = 4.0,
                       rng: np.random.Generator | None = None) -> np.ndarray:
    """Simple geometry-based large-scale fading for distributed APs.

    Coordinates are dimensionless (e.g. normalized square side length 1).
    Returns beta with shape (users, APs).  The absolute normalization is
    intentionally abstract; experiments calibrate the transmit SNR separately.
    """
    A=np.asarray(ap_xy,float); U=np.asarray(user_xy,float)
    if A.ndim!=2 or U.ndim!=2 or A.shape[1]!=2 or U.shape[1]!=2 or pathloss_exp<=0 or min_distance<=0:
        raise ValueError("invalid geometry/pathloss parameters")
    d=np.linalg.norm(U[:,None,:]-A[None,:,:],axis=2)
    d=np.maximum(d,float(min_distance))
    beta=d**(-float(pathloss_exp))
    if shadow_std_db>0:
        if rng is None: rng=np.random.default_rng()
        beta*=10**(rng.normal(0,float(shadow_std_db),beta.shape)/10)
    # Normalize to a robust network-wide reference so numbers remain well-scaled.
    beta/=max(float(np.median(beta)),1e-15)
    return beta


def user_centric_mask(beta: np.ndarray, aps_per_user: int) -> np.ndarray:
    """Boolean (users, APs) mask selecting each user's strongest APs."""
    B=np.asarray(beta,float)
    if B.ndim!=2 or np.any(B<0) or not (1<=int(aps_per_user)<=B.shape[1]):
        raise ValueError("invalid beta/cluster size")
    L=int(aps_per_user); mask=np.zeros(B.shape,bool)
    idx=np.argpartition(B,-L,axis=1)[:,-L:]
    rows=np.arange(B.shape[0])[:,None]; mask[rows,idx]=True
    return mask


def sample_cell_free_channel(beta: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Rayleigh small-scale channel H(users, APs) with variance beta."""
    B=np.asarray(beta,float)
    if B.ndim!=2 or np.any(B<0): raise ValueError("invalid beta")
    z=(rng.normal(size=B.shape)+1j*rng.normal(size=B.shape))/np.sqrt(2)
    return np.sqrt(B)*z


def clustered_mrt_precoder(H: np.ndarray, mask: np.ndarray | None = None,
                           total_power: float = 1.0) -> np.ndarray:
    """Distributed MRT with optional user-centric AP support mask.

    H is (users, APs), W is (APs, users).  Each user's beam is first normalized
    on its participating APs, then equal user power is imposed globally.
    """
    A=np.asarray(H,np.complex128)
    if A.ndim!=2 or total_power<=0: raise ValueError("invalid channel/power")
    K,M=A.shape
    if mask is None: S=np.ones((K,M),bool)
    else:
        S=np.asarray(mask,bool)
        if S.shape!=A.shape or np.any(np.sum(S,axis=1)==0): raise ValueError("invalid support mask")
    W=A.conj().T*S.T
    n=np.linalg.norm(W,axis=0,keepdims=True)
    W=W/np.maximum(n,1e-15)
    W*=np.sqrt(float(total_power)/K)
    return W


def per_user_rates(H: np.ndarray, W: np.ndarray, snr_linear: float) -> np.ndarray:
    A=np.asarray(H,np.complex128); B=np.asarray(W,np.complex128)
    if A.ndim!=2 or B.shape!=(A.shape[1],A.shape[0]) or snr_linear<=0: raise ValueError("invalid dimensions/SNR")
    G=A@B; P=np.abs(G)**2; desired=np.diag(P); interference=P.sum(axis=1)-desired
    sinr=desired/(interference+1/float(snr_linear))
    return np.log2(1+sinr)


def cluster_link_count(mask: np.ndarray) -> int:
    S=np.asarray(mask,bool)
    if S.ndim!=2: raise ValueError("mask must be 2-D")
    return int(S.sum())

def clustered_mrt_directions(H: np.ndarray, mask: np.ndarray | None = None) -> np.ndarray:
    """Unit-norm user beam directions before power allocation."""
    A=np.asarray(H,np.complex128)
    if A.ndim!=2: raise ValueError("H must be 2-D")
    K,M=A.shape
    S=np.ones((K,M),bool) if mask is None else np.asarray(mask,bool)
    if S.shape!=A.shape or np.any(S.sum(axis=1)==0): raise ValueError("invalid mask")
    V=A.conj().T*S.T
    return V/np.maximum(np.linalg.norm(V,axis=0,keepdims=True),1e-15)


def max_min_sinr_power_allocation(H: np.ndarray, directions: np.ndarray, snr_linear: float,
                                  total_power: float = 1.0, iterations: int = 60) -> tuple[np.ndarray,float]:
    """Max-min SINR power allocation for fixed beam directions.

    For target gamma, SINR constraints give p >= gamma F p + gamma u.
    The minimum feasible power is gamma (I-gamma F)^-1 u. Bisection finds
    the largest gamma whose total power does not exceed ``total_power``.
    """
    A=np.asarray(H,np.complex128); V=np.asarray(directions,np.complex128)
    if A.ndim!=2 or V.shape!=(A.shape[1],A.shape[0]) or snr_linear<=0 or total_power<=0:
        raise ValueError("invalid dimensions/power")
    G=np.abs(A@V)**2; d=np.diag(G)
    if np.any(d<=1e-15): return np.full(A.shape[0],total_power/A.shape[0]),0.0
    F=G/d[:,None]; np.fill_diagonal(F,0.0); u=(1/float(snr_linear))/d
    I=np.eye(A.shape[0])
    def req(gamma):
        try: p=np.linalg.solve(I-gamma*F,gamma*u)
        except np.linalg.LinAlgError: return None
        if np.any(~np.isfinite(p)) or np.any(p<0): return None
        return p
    lo=0.0; hi=1.0
    for _ in range(40):
        p=req(hi)
        if p is None or p.sum()>total_power: break
        lo=hi; hi*=2
    for _ in range(int(iterations)):
        mid=.5*(lo+hi); p=req(mid)
        if p is not None and p.sum()<=total_power: lo=mid
        else: hi=mid
    p=req(lo)
    if p is None: p=np.full(A.shape[0],total_power/A.shape[0])
    # Use leftover power proportionally; this cannot reduce any SINR.
    if p.sum()>0: p*=total_power/p.sum()
    return p,float(lo)


def rates_with_power(H: np.ndarray, directions: np.ndarray, power: np.ndarray, snr_linear: float) -> np.ndarray:
    A=np.asarray(H,np.complex128); V=np.asarray(directions,np.complex128); p=np.asarray(power,float).reshape(-1)
    if V.shape!=(A.shape[1],A.shape[0]) or len(p)!=A.shape[0] or np.any(p<0): raise ValueError("invalid power allocation")
    W=V*np.sqrt(p)[None,:]
    return per_user_rates(A,W,snr_linear)
