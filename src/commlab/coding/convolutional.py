import numpy as np


class ConvolutionalCode:
    """Rate-1/2, constraint-length-3 convolutional code with (7,5)_oct generators.

    Supports both hard-decision Hamming-metric Viterbi decoding and soft-input
    Viterbi decoding from per-coded-bit LLRs. LLR convention is
    log P(bit=0)/P(bit=1), so positive values favor zero.
    """

    def __init__(self):
        self.constraint_length = 3
        self.memory = 2
        self.n_states = 1 << self.memory
        self.rate = 0.5
        self._next = np.zeros((self.n_states, 2), dtype=np.int16)
        self._out = np.zeros((self.n_states, 2, 2), dtype=np.uint8)
        self._build_trellis()

    def _build_trellis(self) -> None:
        for state in range(self.n_states):
            u1 = (state >> 1) & 1
            u2 = state & 1
            for u0 in (0, 1):
                g0 = u0 ^ u1 ^ u2       # 111 = 7_oct
                g1 = u0 ^ u2            # 101 = 5_oct
                next_state = (u0 << 1) | u1
                self._next[state, u0] = next_state
                self._out[state, u0] = (g0, g1)

    def encode(self, bits: np.ndarray, terminate: bool = True) -> np.ndarray:
        src = np.asarray(bits, dtype=np.uint8).reshape(-1)
        if np.any(src > 1):
            raise ValueError("bits must contain only 0/1")
        if terminate:
            src = np.concatenate((src, np.zeros(self.memory, dtype=np.uint8)))

        state = 0
        out = np.empty(2 * len(src), dtype=np.uint8)
        j = 0
        for bit in src:
            out[j:j+2] = self._out[state, int(bit)]
            state = int(self._next[state, int(bit)])
            j += 2
        return out

    def _traceback(self, prev_state, prev_bit, metric, terminated, trim_tail):
        n_steps = prev_state.shape[0]
        state = 0 if terminated else int(np.argmin(metric))
        decoded = np.empty(n_steps, dtype=np.uint8)
        for t in range(n_steps - 1, -1, -1):
            decoded[t] = prev_bit[t, state]
            state = int(prev_state[t, state])
            if state < 0 and t > 0:
                raise RuntimeError("invalid Viterbi traceback")
        if terminated and trim_tail:
            if len(decoded) < self.memory:
                return np.empty(0, dtype=np.uint8)
            decoded = decoded[:-self.memory]
        return decoded

    def decode_hard(self, coded_bits: np.ndarray, terminated: bool = True, trim_tail: bool = True) -> np.ndarray:
        rx = np.asarray(coded_bits, dtype=np.uint8).reshape(-1)
        if len(rx) % 2:
            raise ValueError("coded bit length must be even")
        if np.any(rx > 1):
            raise ValueError("coded_bits must contain only 0/1")
        n_steps = len(rx) // 2
        pairs = rx.reshape(n_steps, 2)

        inf = 10**9
        metric = np.full(self.n_states, inf, dtype=np.int64)
        metric[0] = 0
        prev_state = np.full((n_steps, self.n_states), -1, dtype=np.int16)
        prev_bit = np.zeros((n_steps, self.n_states), dtype=np.uint8)

        for t in range(n_steps):
            new_metric = np.full(self.n_states, inf, dtype=np.int64)
            for state in range(self.n_states):
                if metric[state] >= inf:
                    continue
                for bit in (0, 1):
                    ns = int(self._next[state, bit])
                    branch = int(np.count_nonzero(self._out[state, bit] != pairs[t]))
                    cand = int(metric[state]) + branch
                    if cand < new_metric[ns]:
                        new_metric[ns] = cand
                        prev_state[t, ns] = state
                        prev_bit[t, ns] = bit
            metric = new_metric
        return self._traceback(prev_state, prev_bit, metric, terminated, trim_tail)

    def decode_soft(self, llrs: np.ndarray, terminated: bool = True, trim_tail: bool = True) -> np.ndarray:
        """Soft-input Viterbi decoder using coded-bit LLRs.

        For L=log(P0/P1), a convenient additive negative-log-likelihood branch
        metric is sum(logaddexp(0, -(1-2b)*L)). Constants common to all paths
        do not affect the survivor decisions.
        """
        L = np.asarray(llrs, dtype=float).reshape(-1)
        if len(L) % 2:
            raise ValueError("LLR length must be even")
        pairs = L.reshape(-1, 2)
        n_steps = len(pairs)

        metric = np.full(self.n_states, np.inf, dtype=float)
        metric[0] = 0.0
        prev_state = np.full((n_steps, self.n_states), -1, dtype=np.int16)
        prev_bit = np.zeros((n_steps, self.n_states), dtype=np.uint8)

        for t in range(n_steps):
            new_metric = np.full(self.n_states, np.inf, dtype=float)
            for state in range(self.n_states):
                if not np.isfinite(metric[state]):
                    continue
                for bit in (0, 1):
                    ns = int(self._next[state, bit])
                    expected = self._out[state, bit].astype(float)
                    signs = 1.0 - 2.0 * expected
                    branch = float(np.sum(np.logaddexp(0.0, -signs * pairs[t])))
                    cand = metric[state] + branch
                    if cand < new_metric[ns]:
                        new_metric[ns] = cand
                        prev_state[t, ns] = state
                        prev_bit[t, ns] = bit
            metric = new_metric
        return self._traceback(prev_state, prev_bit, metric, terminated, trim_tail)
