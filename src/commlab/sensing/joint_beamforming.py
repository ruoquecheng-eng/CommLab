import numpy as np


def ula_steering(n_elements: int, angle_deg: float) -> np.ndarray:
    if n_elements < 1:
        raise ValueError('positive array size required')
    n = np.arange(int(n_elements))
    a = np.exp(1j * np.pi * n * np.sin(np.deg2rad(float(angle_deg))))
    return a / np.sqrt(n_elements)


def joint_isac_beamformer(channel: np.ndarray, sensing_angle_deg: float,
                          weight_comm: float) -> np.ndarray:
    """Principal-eigenvector beam for a weighted communication/sensing utility.

    The communication term rewards |h w|^2 and sensing rewards |a^H w|^2.
    Weight 1 gives MRT; weight 0 gives the sensing steering vector.
    """
    h = np.asarray(channel, np.complex128).reshape(-1)
    if len(h) < 1 or not (0 <= weight_comm <= 1) or np.linalg.norm(h) <= 0:
        raise ValueError('invalid channel/weight')
    a = ula_steering(len(h), sensing_angle_deg)
    hc = h.conj() / np.linalg.norm(h)
    Q = float(weight_comm) * np.outer(hc, hc.conj()) + (1-float(weight_comm)) * np.outer(a, a.conj())
    vals, vecs = np.linalg.eigh(Q)
    w = vecs[:, int(np.argmax(vals))]
    return w / np.linalg.norm(w)


def communication_rate(channel: np.ndarray, beam: np.ndarray, snr_linear: float) -> float:
    h = np.asarray(channel, np.complex128).reshape(-1); w = np.asarray(beam, np.complex128).reshape(-1)
    if len(h) != len(w) or snr_linear <= 0:
        raise ValueError('invalid dimensions/SNR')
    return float(np.log2(1 + float(snr_linear) * np.abs(h @ w) ** 2))


def sensing_gain(beam: np.ndarray, angle_deg: float) -> float:
    w = np.asarray(beam, np.complex128).reshape(-1)
    a = ula_steering(len(w), angle_deg)
    return float(np.abs(np.vdot(a, w)) ** 2)
