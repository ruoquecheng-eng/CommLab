import numpy as np


def iq_imbalance_coefficients(gain_imbalance_db: float = 0.0, phase_imbalance_deg: float = 0.0) -> tuple[complex, complex]:
    """Return widely-linear IQ coefficients ``alpha, beta``.

    The impairment is modeled as ``y = alpha*x + beta*conj(x)``. Gain
    imbalance is the I/Q branch gain ratio in dB; phase imbalance is the
    departure from ideal quadrature in degrees. Zero/zero returns identity.
    """
    ratio = 10.0 ** (float(gain_imbalance_db) / 20.0)
    g_i = np.sqrt(ratio)
    g_q = 1.0 / np.sqrt(ratio)
    phi = np.deg2rad(float(phase_imbalance_deg))
    alpha = 0.5 * (g_i * np.exp(-0.5j * phi) + g_q * np.exp(0.5j * phi))
    beta = 0.5 * (g_i * np.exp(-0.5j * phi) - g_q * np.exp(0.5j * phi))
    return complex(alpha), complex(beta)


def apply_iq_imbalance(signal: np.ndarray, gain_imbalance_db: float = 0.0, phase_imbalance_deg: float = 0.0) -> np.ndarray:
    x = np.asarray(signal, dtype=np.complex128)
    alpha, beta = iq_imbalance_coefficients(gain_imbalance_db, phase_imbalance_deg)
    return alpha * x + beta * np.conj(x)


def estimate_iq_coefficients(training_tx: np.ndarray, training_rx: np.ndarray) -> tuple[complex, complex]:
    """Least-squares estimate of the widely-linear IQ coefficients."""
    x = np.asarray(training_tx, dtype=np.complex128).reshape(-1)
    y = np.asarray(training_rx, dtype=np.complex128).reshape(-1)
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("training vectors must have equal length >= 2")
    A = np.column_stack((x, np.conj(x)))
    coeff, *_ = np.linalg.lstsq(A, y, rcond=None)
    return complex(coeff[0]), complex(coeff[1])


def compensate_iq_imbalance(signal: np.ndarray, alpha: complex, beta: complex) -> np.ndarray:
    """Invert a nonsingular widely-linear IQ impairment."""
    y = np.asarray(signal, dtype=np.complex128)
    denom = abs(alpha) ** 2 - abs(beta) ** 2
    if abs(denom) < 1e-12:
        raise ValueError("IQ impairment is singular or ill-conditioned")
    return (np.conj(alpha) * y - beta * np.conj(y)) / denom


def image_rejection_ratio_db(alpha: complex, beta: complex) -> float:
    """Idealized image-rejection ratio implied by the widely-linear model."""
    if abs(beta) == 0:
        return np.inf
    return 10.0 * np.log10(abs(alpha) ** 2 / abs(beta) ** 2)
