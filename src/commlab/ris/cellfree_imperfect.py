import numpy as np

from commlab.mimo.fronthaul import quantize_complex_csi
from commlab.ris.cellfree import coordinate_optimize_cellfree_ris, cellfree_ris_rates
from commlab.ris.robust import sample_average_optimize_cellfree_ris


def age_complex_channel(x: np.ndarray, correlation: float, steps: int,
                        rng: np.random.Generator) -> np.ndarray:
    """Age a proper-complex channel while preserving its empirical power.

    This is a compact Gauss-Markov abstraction for delayed CSI.  It is not a
    geometry/Jakes Doppler model; ``correlation**steps`` is the effective CSI
    correlation between acquisition and use.
    """
    a = np.asarray(x, np.complex128)
    if a.size == 0 or not (0 <= correlation <= 1) or steps < 0:
        raise ValueError("invalid channel-aging parameters")
    r = float(correlation) ** int(steps)
    if steps == 0 or r == 1.0:
        return a.copy()
    p = float(np.mean(np.abs(a) ** 2))
    z = (rng.normal(size=a.shape) + 1j * rng.normal(size=a.shape)) / np.sqrt(2)
    return r * a + np.sqrt(max(1.0 - r * r, 0.0)) * np.sqrt(max(p, 1e-15)) * z


def quantize_ris_cellfree_csi(h_direct: np.ndarray, g_ap_ris: np.ndarray,
                               h_ris_user: np.ndarray, bits: int):
    if bits < 1:
        raise ValueError("bits must be positive")
    return (
        quantize_complex_csi(h_direct, bits),
        quantize_complex_csi(g_ap_ris, bits),
        quantize_complex_csi(h_ris_user, bits),
    )


def predicted_channel_samples(stale_channels, correlation: float, steps: int,
                              n_samples: int, rng: np.random.Generator):
    """Draw a conditional-style ensemble around stale CSI for robust RIS design."""
    if n_samples < 1 or not (0 <= correlation <= 1) or steps < 0:
        raise ValueError("invalid prediction setup")
    r = float(correlation) ** int(steps)
    out = []
    for _ in range(int(n_samples)):
        sample = []
        for x in stale_channels:
            a = np.asarray(x, np.complex128)
            p = float(np.mean(np.abs(a) ** 2))
            z = (rng.normal(size=a.shape) + 1j * rng.normal(size=a.shape)) / np.sqrt(2)
            sample.append(r * a + np.sqrt(max(1-r*r, 0.0)) * np.sqrt(max(p, 1e-15)) * z)
        out.append(tuple(sample))
    return out


def design_and_evaluate_aged_cellfree_ris(stale_channels, current_channels,
                                           snr_linear: float, bits: int = 2,
                                           iterations: int = 2,
                                           correlation: float = 0.98,
                                           delay_steps: int = 1,
                                           csi_quant_bits: int = 6,
                                           robust_samples: int = 8,
                                           rng: np.random.Generator | None = None,
                                           mask: np.ndarray | None = None) -> dict:
    """Compare stale-CSI, uncertainty-robust and ideal-current RIS designs.

    RIS phase resolution (``bits``) is distinct from fronthaul CSI quantization
    (``csi_quant_bits``).  Robust design uses a finite predicted ensemble and is
    intentionally a sample-average coordinate-ascent baseline.
    """
    if rng is None:
        rng = np.random.default_rng(1)
    if snr_linear <= 0 or robust_samples < 1:
        raise ValueError("invalid evaluation setup")
    Ds, Gs, Rs = quantize_ris_cellfree_csi(*stale_channels, csi_quant_bits)
    Dc, Gc, Rc = current_channels
    naive, _ = coordinate_optimize_cellfree_ris(Ds, Gs, Rs, snr_linear, bits=bits,
                                                 iterations=iterations, mask=mask)
    samples = predicted_channel_samples((Ds, Gs, Rs), correlation, delay_steps,
                                        robust_samples, rng)
    robust, _ = sample_average_optimize_cellfree_ris(samples, snr_linear, bits=bits,
                                                     iterations=iterations, mask=mask)
    ideal, _ = coordinate_optimize_cellfree_ris(Dc, Gc, Rc, snr_linear, bits=bits,
                                                 iterations=iterations, mask=mask)
    zero = np.zeros(np.asarray(Gc).shape[0])
    rr = np.random.default_rng(12345)
    random_phase = rr.uniform(-np.pi, np.pi, len(zero))
    def rates(th):
        return cellfree_ris_rates(Dc, Gc, Rc, th, snr_linear, mask)
    return {
        "random_rates": rates(random_phase),
        "naive_rates": rates(naive),
        "robust_rates": rates(robust),
        "ideal_rates": rates(ideal),
        "naive_phases": naive,
        "robust_phases": robust,
        "ideal_phases": ideal,
    }
