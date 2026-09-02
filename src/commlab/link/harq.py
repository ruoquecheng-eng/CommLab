import numpy as np


def _bits_to_int(bits: np.ndarray) -> int:
    v=0
    for b in np.asarray(bits,dtype=np.uint8).reshape(-1): v=(v<<1)|int(b)
    return v


def crc16_ccitt(bits: np.ndarray, init: int = 0xFFFF, polynomial: int = 0x1021) -> int:
    """Bitwise CRC-16-CCITT remainder, MSB first."""
    reg=int(init)&0xFFFF
    b=np.asarray(bits,dtype=np.uint8).reshape(-1)
    if np.any(b>1): raise ValueError("bits must be binary")
    for bit in b:
        top=((reg>>15)&1)^int(bit)
        reg=((reg<<1)&0xFFFF)
        if top: reg ^= int(polynomial)
    return reg


def append_crc16(bits: np.ndarray) -> np.ndarray:
    b=np.asarray(bits,dtype=np.uint8).reshape(-1)
    crc=crc16_ccitt(b)
    c=np.array([(crc>>s)&1 for s in range(15,-1,-1)],dtype=np.uint8)
    return np.concatenate((b,c))


def check_crc16(frame_bits: np.ndarray) -> bool:
    f=np.asarray(frame_bits,dtype=np.uint8).reshape(-1)
    if len(f)<16: return False
    data=f[:-16]; got=_bits_to_int(f[-16:])
    return crc16_ccitt(data)==got


class ChaseCombiner:
    """Accumulate independent soft observations for Chase HARQ combining."""
    def __init__(self, length: int):
        if length<1: raise ValueError("length must be positive")
        self.llr=np.zeros(int(length),dtype=float); self.transmissions=0

    def add(self, llr: np.ndarray) -> np.ndarray:
        x=np.asarray(llr,dtype=float).reshape(-1)
        if len(x)!=len(self.llr): raise ValueError("LLR length mismatch")
        self.llr += x; self.transmissions += 1
        return self.llr.copy()

    def reset(self):
        self.llr.fill(0.0); self.transmissions=0
