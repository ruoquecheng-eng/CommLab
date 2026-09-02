import numpy as np


def ldpc_incremental_redundancy_schedule(k: int, n: int, parity_chunks: int = 4) -> list[np.ndarray]:
    """Create a transparent systematic-first incremental-redundancy schedule.

    Round 1 sends all ``k`` systematic bits plus the first parity chunk.
    Subsequent rounds reveal disjoint parity chunks. This is an educational
    puncturing/rate-matching baseline, not a 3GPP/DVB redundancy-version map.
    """
    k = int(k); n = int(n); parity_chunks = int(parity_chunks)
    if not (0 < k < n) or parity_chunks < 1:
        raise ValueError("invalid code dimensions/parity_chunks")
    parity = np.arange(k, n, dtype=int)
    chunks = [c.astype(int) for c in np.array_split(parity, parity_chunks) if len(c)]
    schedule=[]
    if chunks:
        schedule.append(np.concatenate((np.arange(k, dtype=int), chunks[0])))
        schedule.extend(chunks[1:])
    else:
        schedule.append(np.arange(k, dtype=int))
    return schedule


class IncrementalRedundancyCombiner:
    """Soft buffer for punctured/redundancy-version HARQ.

    The buffer stores a full mother-code LLR vector. Newly transmitted code-bit
    positions are inserted; repeated positions are soft-combined by addition.
    Unobserved positions remain zero-LLR (erasures) for the decoder.
    """
    def __init__(self, mother_length: int):
        if mother_length < 1:
            raise ValueError("mother_length must be positive")
        self.length = int(mother_length)
        self.llr = np.zeros(self.length, dtype=float)
        self.observations = np.zeros(self.length, dtype=np.int32)
        self.transmissions = 0
        self.transmitted_bits = 0

    def add(self, indices: np.ndarray, llrs: np.ndarray) -> np.ndarray:
        idx=np.asarray(indices,dtype=int).reshape(-1)
        val=np.asarray(llrs,dtype=float).reshape(-1)
        if len(idx)!=len(val) or np.any(idx<0) or np.any(idx>=self.length):
            raise ValueError("invalid IR indices/LLRs")
        np.add.at(self.llr, idx, val)
        np.add.at(self.observations, idx, 1)
        self.transmissions += 1
        self.transmitted_bits += len(idx)
        return self.llr.copy()

    @property
    def observed_fraction(self) -> float:
        return float(np.mean(self.observations > 0))

    def reset(self) -> None:
        self.llr.fill(0.0); self.observations.fill(0)
        self.transmissions=0; self.transmitted_bits=0


def systematic_circular_rv_indices(k: int, n: int, out_len: int, rv: int,
                                   rv_count: int = 4) -> np.ndarray:
    """Project-specific circular-buffer redundancy-version mapping.

    Every transmission repeats the systematic ``k`` bits and selects the
    remaining ``out_len-k`` bits from a circular parity buffer. Different RVs
    use evenly spaced starting offsets. This is intentionally transparent and
    *not* a 3GPP/DVB rate matcher, but it captures the two useful HARQ ideas:
    systematic evidence can be re-combined while parity observations evolve
    between redundancy versions.
    """
    k=int(k); n=int(n); out_len=int(out_len); rv=int(rv); rv_count=int(rv_count)
    if not (0 < k < n) or out_len < k or out_len > n or rv_count < 1:
        raise ValueError("invalid circular RV dimensions")
    p=n-k; need=out_len-k
    sys=np.arange(k,dtype=int)
    if need==0:
        return sys
    start=(rv % rv_count) * p // rv_count
    parity=k + ((start + np.arange(need,dtype=int)) % p)
    return np.concatenate((sys,parity))
