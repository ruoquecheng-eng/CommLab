import numpy as np


def _is_power_of_two(n: int) -> bool:
    return n > 0 and (n & (n - 1)) == 0


def bec_reliability_order(n: int, erasure_prob: float = 0.5) -> np.ndarray:
    """Return polar bit-channel indices from most to least reliable.

    Reliability is constructed by Bhattacharyya recursion for a BEC design
    channel. This is deterministic and transparent, but it is not a 3GPP NR
    reliability sequence and is documented as an educational baseline.
    """
    if not _is_power_of_two(n) or not (0.0 < erasure_prob < 1.0):
        raise ValueError("n must be a power of two and 0<p<1")
    z=np.array([float(erasure_prob)])
    while len(z)<n:
        z=np.column_stack((2*z-z*z,z*z)).reshape(-1)
    return np.argsort(z)


def polar_transform(bits: np.ndarray) -> np.ndarray:
    """Apply Arikan F^(tensor log2 N) transform over GF(2)."""
    x=np.asarray(bits,dtype=np.uint8).reshape(-1).copy()
    n=len(x)
    if not _is_power_of_two(n) or np.any(x>1):
        raise ValueError("input length must be a power of two binary vector")
    step=1
    while step<n:
        for i in range(0,n,2*step):
            x[i:i+step] ^= x[i+step:i+2*step]
        step*=2
    return x


class PolarCode:
    """Small educational rate-selectable polar code with min-sum SC decoding.

    The information set uses BEC-derived channel reliability. This keeps the
    construction self-contained and reproducible, but it is intentionally not
    presented as a standards-compliant 5G NR polar code.
    """
    def __init__(self, n: int = 128, k: int = 64, design_erasure: float = 0.5):
        if not _is_power_of_two(n) or not (0 < k < n):
            raise ValueError("require power-of-two n and 0<k<n")
        self.n=int(n); self.k=int(k); self.rate=self.k/self.n
        order=bec_reliability_order(self.n,design_erasure)
        self.info_indices=np.sort(order[:self.k])
        self.frozen=np.ones(self.n,dtype=bool); self.frozen[self.info_indices]=False

    def encode(self, info_bits: np.ndarray) -> np.ndarray:
        u=np.zeros(self.n,dtype=np.uint8)
        b=np.asarray(info_bits,dtype=np.uint8).reshape(-1)
        if len(b)!=self.k or np.any(b>1):
            raise ValueError(f"info_bits must contain exactly {self.k} bits")
        u[self.info_indices]=b
        return polar_transform(u)

    @staticmethod
    def _f(a: np.ndarray, b: np.ndarray) -> np.ndarray:
        # Min-sum approximation to box-plus; stable and sufficient for this lab.
        return np.sign(a)*np.sign(b)*np.minimum(np.abs(a),np.abs(b))

    @staticmethod
    def _g(a: np.ndarray, b: np.ndarray, x_left: np.ndarray) -> np.ndarray:
        return b + (1.0-2.0*x_left.astype(float))*a

    def _decode_node(self, llr: np.ndarray, start: int) -> tuple[np.ndarray,np.ndarray]:
        m=len(llr)
        if m==1:
            bit=0 if self.frozen[start] or llr[0]>=0 else 1
            u=np.array([bit],dtype=np.uint8)
            return u,u.copy()
        half=m//2
        left_llr=self._f(llr[:half],llr[half:])
        u_l,x_l=self._decode_node(left_llr,start)
        right_llr=self._g(llr[:half],llr[half:],x_l)
        u_r,x_r=self._decode_node(right_llr,start+half)
        u=np.concatenate((u_l,u_r))
        x=np.concatenate((x_l^x_r,x_r))
        return u,x

    def decode_sc(self, llr: np.ndarray) -> np.ndarray:
        L=np.asarray(llr,dtype=float).reshape(-1)
        if len(L)!=self.n:
            raise ValueError(f"LLR vector must have length {self.n}")
        u,_=self._decode_node(L,0)
        return u[self.info_indices]
