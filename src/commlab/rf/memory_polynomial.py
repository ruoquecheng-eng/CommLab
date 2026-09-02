import numpy as np


def memory_polynomial_features(signal: np.ndarray, order: int = 5, memory_depth: int = 3) -> np.ndarray:
    """Return memory-polynomial basis x[n-m]|x[n-m]|^(p-1).

    Columns are ordered by memory tap first, then odd polynomial order
    p = 1, 3, ..., order. Samples before the beginning of the waveform are
    zero padded. This simple basis is widely used as an educational PA/DPD
    baseline for systems with nonlinear memory.
    """
    if order < 1 or order % 2 == 0:
        raise ValueError("order must be a positive odd integer")
    if memory_depth < 1:
        raise ValueError("memory_depth must be positive")
    x = np.asarray(signal, dtype=np.complex128).reshape(-1)
    odd_orders = list(range(1, order + 1, 2))
    cols = []
    for m in range(memory_depth):
        delayed = np.zeros_like(x)
        if m == 0:
            delayed[:] = x
        elif m < len(x):
            delayed[m:] = x[:-m]
        for p in odd_orders:
            cols.append(delayed * np.abs(delayed) ** (p - 1))
    return np.column_stack(cols)


def apply_memory_polynomial(
    signal: np.ndarray,
    coefficients: np.ndarray,
    order: int | None = None,
    memory_depth: int | None = None,
) -> np.ndarray:
    """Apply a memory polynomial with flattened or 2-D coefficients.

    A 2-D coefficient matrix has shape (memory_depth, n_odd_orders).
    A flat coefficient vector requires explicit ``order`` and ``memory_depth``.
    """
    c = np.asarray(coefficients, dtype=np.complex128)
    if c.ndim == 2:
        md, n_orders = c.shape
        inferred_order = 2 * n_orders - 1
        order = inferred_order if order is None else order
        memory_depth = md if memory_depth is None else memory_depth
        if order != inferred_order or memory_depth != md:
            raise ValueError("coefficient shape does not match order/memory_depth")
        flat = c.reshape(-1)
    elif c.ndim == 1:
        if order is None or memory_depth is None:
            raise ValueError("flat coefficients require order and memory_depth")
        n_orders = (order + 1) // 2
        if len(c) != memory_depth * n_orders:
            raise ValueError("coefficient length does not match model dimensions")
        flat = c
    else:
        raise ValueError("coefficients must be 1-D or 2-D")
    return memory_polynomial_features(signal, order, memory_depth) @ flat


def fit_memory_polynomial(
    model_input: np.ndarray,
    model_output: np.ndarray,
    order: int = 5,
    memory_depth: int = 3,
    ridge: float = 1e-8,
    discard: int | None = None,
) -> np.ndarray:
    """Least-squares identification of a memory polynomial model."""
    x = np.asarray(model_input, dtype=np.complex128).reshape(-1)
    y = np.asarray(model_output, dtype=np.complex128).reshape(-1)
    if len(x) != len(y):
        raise ValueError("input and output training lengths must match")
    Phi = memory_polynomial_features(x, order, memory_depth)
    d = memory_depth - 1 if discard is None else int(discard)
    Phi_fit = Phi[d:]
    y_fit = y[d:]
    G = Phi_fit.conj().T @ Phi_fit + float(ridge) * np.eye(Phi_fit.shape[1])
    c = np.linalg.solve(G, Phi_fit.conj().T @ y_fit)
    return c.reshape(memory_depth, (order + 1) // 2)


def fit_indirect_memory_dpd(
    pa_input: np.ndarray,
    pa_output: np.ndarray,
    order: int = 7,
    memory_depth: int = 4,
    ridge: float = 1e-7,
) -> np.ndarray:
    """Indirect-learning DPD fit: PA output -> PA input.

    The fitted postdistorter is reused as the predistorter. This is an
    educational offline indirect-learning baseline rather than an online
    adaptive hardware DPD loop.
    """
    return fit_memory_polynomial(
        pa_output,
        pa_input,
        order=order,
        memory_depth=memory_depth,
        ridge=ridge,
    )


def default_memory_pa_coefficients() -> np.ndarray:
    """A deterministic, moderately nonlinear 3-tap PA model for experiments."""
    c = np.zeros((3, 3), dtype=np.complex128)  # orders 1,3,5
    c[0, 0] = 1.00 + 0.00j
    c[0, 1] = -0.18 + 0.045j
    c[0, 2] = 0.025 - 0.010j
    c[1, 0] = 0.10 + 0.035j
    c[1, 1] = -0.035 + 0.012j
    c[1, 2] = 0.005 + 0.002j
    c[2, 0] = -0.035 + 0.020j
    c[2, 1] = 0.012 - 0.004j
    return c


def rls_fit_memory_polynomial(
    model_input: np.ndarray,
    model_output: np.ndarray,
    order: int = 7,
    memory_depth: int = 4,
    forgetting_factor: float = 0.995,
    delta: float = 100.0,
    initial_coefficients: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Recursive least-squares identification of a complex memory polynomial.

    Returns ``(coefficients, error_trace)``. The regression convention is
    ``d[n] ≈ phi[n] @ c`` and uses exponentially weighted complex RLS. This is
    intended for streaming/adaptive DPD experiments where PA characteristics
    drift between blocks.
    """
    if not (0.0 < forgetting_factor <= 1.0) or delta <= 0:
        raise ValueError("invalid RLS forgetting factor or delta")
    x=np.asarray(model_input,dtype=np.complex128).reshape(-1)
    d=np.asarray(model_output,dtype=np.complex128).reshape(-1)
    if len(x)!=len(d):
        raise ValueError("input and output lengths must match")
    Phi=memory_polynomial_features(x,order,memory_depth)
    ncoef=Phi.shape[1]
    if initial_coefficients is None:
        c=np.zeros(ncoef,dtype=np.complex128)
    else:
        c=np.asarray(initial_coefficients,dtype=np.complex128).reshape(-1).copy()
        if len(c)!=ncoef:
            raise ValueError("initial coefficient length mismatch")
    P=float(delta)*np.eye(ncoef,dtype=np.complex128)
    errs=np.empty(len(x),dtype=float)
    start=memory_depth-1
    for n in range(len(x)):
        if n < start:
            errs[n]=np.nan
            continue
        phi=Phi[n]
        Pphi=P@phi.conj()
        den=complex(forgetting_factor)+np.dot(phi,Pphi)
        k=Pphi/den
        e=d[n]-np.dot(phi,c)
        c += k*e
        P=(P-np.outer(k,phi)@P)/float(forgetting_factor)
        # enforce Hermitian symmetry against accumulated roundoff
        P=0.5*(P+P.conj().T)
        errs[n]=abs(e)**2
    return c.reshape(memory_depth,(order+1)//2),errs


class MemoryPolynomialRLS:
    """Stateful complex RLS estimator for streaming memory-polynomial models."""
    def __init__(self, order: int = 7, memory_depth: int = 4, forgetting_factor: float = 0.995, delta: float = 100.0, initial_coefficients: np.ndarray | None = None):
        if order < 1 or order % 2 == 0 or memory_depth < 1 or not (0 < forgetting_factor <= 1) or delta <= 0:
            raise ValueError("invalid RLS model parameters")
        self.order=int(order); self.memory_depth=int(memory_depth); self.forgetting_factor=float(forgetting_factor)
        self.ncoef=self.memory_depth*((self.order+1)//2)
        if initial_coefficients is None: self.c=np.zeros(self.ncoef,dtype=np.complex128)
        else:
            self.c=np.asarray(initial_coefficients,dtype=np.complex128).reshape(-1).copy()
            if len(self.c)!=self.ncoef: raise ValueError("initial coefficient length mismatch")
        self.P=float(delta)*np.eye(self.ncoef,dtype=np.complex128)

    @property
    def coefficients(self) -> np.ndarray:
        return self.c.reshape(self.memory_depth,(self.order+1)//2).copy()

    def update(self, model_input: np.ndarray, model_output: np.ndarray, stride: int = 1) -> np.ndarray:
        x=np.asarray(model_input,dtype=np.complex128).reshape(-1); d=np.asarray(model_output,dtype=np.complex128).reshape(-1)
        if len(x)!=len(d) or stride < 1: raise ValueError("invalid RLS training block")
        Phi=memory_polynomial_features(x,self.order,self.memory_depth); errs=[]
        for n in range(self.memory_depth-1,len(x),int(stride)):
            phi=Phi[n]; Pphi=self.P@phi.conj(); den=complex(self.forgetting_factor)+np.dot(phi,Pphi); k=Pphi/den
            e=d[n]-np.dot(phi,self.c); self.c += k*e
            self.P=(self.P-np.outer(k,phi)@self.P)/self.forgetting_factor; self.P=.5*(self.P+self.P.conj().T); errs.append(abs(e)**2)
        return np.asarray(errs,float)


class MemoryPolynomialEWLS:
    """Block exponentially-weighted least-squares memory-polynomial estimator.

    Maintains exponentially discounted sufficient statistics instead of the
    sample-wise inverse covariance recursion. This is slower to react than RLS
    but substantially more numerically stable for drifting DPD experiments.
    """
    def __init__(self, order: int = 7, memory_depth: int = 4, forgetting_factor: float = 0.85, ridge: float = 1e-3, initial_coefficients: np.ndarray | None = None):
        if order < 1 or order % 2 == 0 or memory_depth < 1 or not (0 < forgetting_factor <= 1) or ridge <= 0:
            raise ValueError("invalid EWLS parameters")
        self.order=int(order); self.memory_depth=int(memory_depth); self.forgetting_factor=float(forgetting_factor); self.ridge=float(ridge)
        self.ncoef=self.memory_depth*((self.order+1)//2)
        self.R=self.ridge*np.eye(self.ncoef,dtype=np.complex128)
        self.p=np.zeros(self.ncoef,dtype=np.complex128)
        if initial_coefficients is not None:
            c=np.asarray(initial_coefficients,dtype=np.complex128).reshape(-1)
            if len(c)!=self.ncoef: raise ValueError("initial coefficient length mismatch")
            # Encode prior as a ridge-weighted pseudo-observation.
            self.p += self.ridge*c
        self.c=np.linalg.solve(self.R,self.p)

    @property
    def coefficients(self):
        return self.c.reshape(self.memory_depth,(self.order+1)//2).copy()

    def update(self, model_input: np.ndarray, model_output: np.ndarray, stride: int = 1) -> np.ndarray:
        x=np.asarray(model_input,dtype=np.complex128).reshape(-1); d=np.asarray(model_output,dtype=np.complex128).reshape(-1)
        if len(x)!=len(d) or stride<1: raise ValueError("invalid EWLS training block")
        Phi=memory_polynomial_features(x,self.order,self.memory_depth)[self.memory_depth-1::stride]
        targ=d[self.memory_depth-1::stride]
        lam=self.forgetting_factor
        self.R=lam*self.R + Phi.conj().T@Phi + self.ridge*np.eye(self.ncoef)
        self.p=lam*self.p + Phi.conj().T@targ
        self.c=np.linalg.solve(self.R,self.p)
        err=targ-Phi@self.c
        return np.abs(err)**2
