import numpy as np


def generalized_memory_features(signal: np.ndarray, order: int = 5, memory_depth: int = 3, cross_lags: int = 2) -> np.ndarray:
    """Causal generalized-memory-polynomial basis with lagging envelope terms.

    Main branch: x[n-m]|x[n-m]|^(p-1), p=1,3,...,P.
    Cross branch: x[n-m]|x[n-m-l]|^(p-1), p=3,5,...,P, l=1..L.
    This is a compact educational GMP variant, not a claim of a unique GMP
    convention used by all RF toolchains.
    """
    if order<1 or order%2==0 or memory_depth<1 or cross_lags<0: raise ValueError('invalid GMP dimensions')
    x=np.asarray(signal,dtype=np.complex128).reshape(-1); N=len(x)
    odd=list(range(1,order+1,2)); nonlin=odd[1:]; cols=[]
    delayed=[]
    for d in range(memory_depth+cross_lags):
        z=np.zeros_like(x)
        if d==0: z[:]=x
        elif d<N: z[d:]=x[:-d]
        delayed.append(z)
    for m in range(memory_depth):
        xm=delayed[m]
        for p in odd: cols.append(xm*np.abs(xm)**(p-1))
    for m in range(memory_depth):
        xm=delayed[m]
        for lag in range(1,cross_lags+1):
            env=delayed[m+lag]
            for p in nonlin: cols.append(xm*np.abs(env)**(p-1))
    return np.column_stack(cols)


def apply_generalized_memory(signal: np.ndarray, coefficients: np.ndarray, order: int = 5, memory_depth: int = 3, cross_lags: int = 2) -> np.ndarray:
    Phi=generalized_memory_features(signal,order,memory_depth,cross_lags); c=np.asarray(coefficients,dtype=np.complex128).reshape(-1)
    if Phi.shape[1]!=len(c): raise ValueError('coefficient length mismatch')
    return Phi@c


def fit_generalized_memory(model_input: np.ndarray, model_output: np.ndarray, order: int = 5, memory_depth: int = 3, cross_lags: int = 2, ridge: float = 1e-7) -> np.ndarray:
    x=np.asarray(model_input,dtype=np.complex128).reshape(-1); y=np.asarray(model_output,dtype=np.complex128).reshape(-1)
    if len(x)!=len(y): raise ValueError('training length mismatch')
    Phi=generalized_memory_features(x,order,memory_depth,cross_lags); d=memory_depth+cross_lags-1; P=Phi[d:]; t=y[d:]
    G=P.conj().T@P+float(ridge)*np.eye(P.shape[1]); return np.linalg.solve(G,P.conj().T@t)


def default_generalized_memory_pa_coefficients(order: int = 5, memory_depth: int = 3, cross_lags: int = 2) -> np.ndarray:
    if (order,memory_depth,cross_lags)!=(5,3,2): raise ValueError('default coefficients are defined for order=5, memory_depth=3, cross_lags=2')
    # 9 main coefficients then 12 causal cross-envelope coefficients.
    main=np.array([
        1+0j,-.17+.04j,.022-.008j,
        .09+.025j,-.03+.01j,.004+.001j,
        -.03+.015j,.010-.003j,0j,
    ],complex)
    cross=np.array([
        -.045+.016j,.010-.004j, -.022+.008j,.006+.002j,
        .025+.008j,-.006+.003j, .012-.004j,-.003+.001j,
        -.010+.004j,.002+0j, -.006+.002j,.001+0j,
    ],complex)
    return np.concatenate((main,cross))
