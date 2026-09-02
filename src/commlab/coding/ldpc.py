import numpy as np


class SparseAccumulatorLDPC:
    """Small educational rate-1/2 sparse linear block code with Min-Sum BP.

    The parity-check matrix has H=[A|B], where each information column in A
    has configurable sparse weight and B is a lower-bidiagonal accumulator.
    This is a reproducible LDPC/accumulator construction intended for algorithm
    experiments, not a 3GPP/DVB standards code.
    """
    def __init__(self, k: int = 96, info_col_weight: int = 3, seed: int = 1701):
        if k < 8 or info_col_weight < 2 or info_col_weight >= k:
            raise ValueError("invalid LDPC dimensions")
        self.k = int(k); self.m = int(k); self.n = self.k + self.m; self.rate = self.k/self.n
        rng=np.random.default_rng(seed)
        A=np.zeros((self.m,self.k),dtype=np.uint8)
        # balanced randomized row choices for each information column
        for j in range(self.k):
            rows=rng.choice(self.m,size=info_col_weight,replace=False)
            A[rows,j]=1
        B=np.eye(self.m,dtype=np.uint8)
        B[1:, :-1] ^= np.eye(self.m-1,dtype=np.uint8)
        self.H=np.concatenate((A,B),axis=1)
        self.A=A
        self.check_neighbors=[np.flatnonzero(self.H[i]).astype(int) for i in range(self.m)]
        self.var_neighbors=[np.flatnonzero(self.H[:,j]).astype(int) for j in range(self.n)]

    def encode(self, info_bits: np.ndarray) -> np.ndarray:
        u=np.asarray(info_bits,dtype=np.uint8).reshape(-1)
        if len(u)!=self.k or np.any(u>1):
            raise ValueError(f"info_bits must contain exactly {self.k} binary bits")
        s=(self.A@u)&1
        p=np.empty(self.m,dtype=np.uint8); p[0]=s[0]
        for i in range(1,self.m): p[i]=s[i]^p[i-1]
        c=np.concatenate((u,p))
        if np.any((self.H@c)&1):
            raise RuntimeError("encoder produced invalid codeword")
        return c

    def syndrome(self, bits: np.ndarray) -> np.ndarray:
        b=np.asarray(bits,dtype=np.uint8).reshape(-1)
        if len(b)!=self.n: raise ValueError("invalid codeword length")
        return (self.H@b)&1

    def decode_min_sum(self, llr: np.ndarray, max_iter: int = 40, normalized_factor: float = 0.8) -> tuple[np.ndarray,int,bool]:
        """Normalized Min-Sum belief propagation; positive LLR favors bit 0."""
        L=np.asarray(llr,dtype=float).reshape(-1)
        if len(L)!=self.n: raise ValueError("invalid LLR length")
        # Dense edge message arrays are compact enough for this small code.
        q=np.zeros((self.m,self.n),dtype=float); r=np.zeros_like(q)
        for i,vars_i in enumerate(self.check_neighbors): q[i,vars_i]=L[vars_i]
        hard=np.zeros(self.n,dtype=np.uint8)
        for it in range(1,max_iter+1):
            # check -> variable
            for i,vars_i in enumerate(self.check_neighbors):
                vals=q[i,vars_i]
                absvals=np.abs(vals); signs=np.where(vals<0,-1.0,1.0)
                sign_all=np.prod(signs)
                if len(vals)==1:
                    r[i,vars_i[0]]=normalized_factor*50.0*sign_all
                    continue
                min1_idx=int(np.argmin(absvals)); min1=absvals[min1_idx]
                tmp=absvals.copy(); tmp[min1_idx]=np.inf; min2=float(np.min(tmp))
                for local,j in enumerate(vars_i):
                    mag=min2 if local==min1_idx else min1
                    r[i,j]=normalized_factor*sign_all*signs[local]*mag
            posterior=L.copy()
            for j,checks_j in enumerate(self.var_neighbors): posterior[j]+=np.sum(r[checks_j,j])
            hard=(posterior<0).astype(np.uint8)
            if not np.any((self.H@hard)&1):
                return hard[:self.k],it,True
            # variable -> check extrinsic
            for j,checks_j in enumerate(self.var_neighbors):
                total=posterior[j]
                for i in checks_j: q[i,j]=total-r[i,j]
        return hard[:self.k],max_iter,False
