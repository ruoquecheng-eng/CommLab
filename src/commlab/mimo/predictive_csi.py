import numpy as np

from commlab.mimo.fronthaul import quantize_complex_csi, gauss_markov_channel_step


def predictive_csi_quantization_trace(beta: np.ndarray, correlation: float,
                                      bits_per_component: int, n_slots: int=300,
                                      seed: int=1) -> dict:
    """Compare absolute CSI quantization with differential predictive coding.

    The predictor is the known Gauss-Markov mean ``rho * Hhat[t-1]``.  The AP
    quantizes only the innovation relative to that predictor.  Both methods use
    the same scalar bit depth per complex component; entropy coding is not
    modeled, so this isolates distortion reduction from temporal prediction.
    """
    B=np.asarray(beta,float)
    if B.ndim!=2 or np.any(B<0) or not (0<=correlation<=1) or bits_per_component<1 or n_slots<2:
        raise ValueError('invalid predictive CSI setup')
    rng=np.random.default_rng(seed)
    z=(rng.normal(size=B.shape)+1j*rng.normal(size=B.shape))/np.sqrt(2)
    H=np.sqrt(B)*z
    abs_hat=quantize_complex_csi(H,bits_per_component)
    pred_hat=abs_hat.copy()
    abs_nmse=[]; pred_nmse=[]; innovation_power=[]
    for _ in range(int(n_slots)):
        den=max(float(np.sum(np.abs(H)**2)),1e-15)
        abs_nmse.append(float(np.sum(np.abs(H-abs_hat)**2)/den))
        pred_nmse.append(float(np.sum(np.abs(H-pred_hat)**2)/den))
        H=gauss_markov_channel_step(H,B,correlation,rng)
        abs_hat=quantize_complex_csi(H,bits_per_component)
        predictor=float(correlation)*pred_hat
        innovation=H-predictor
        innovation_power.append(float(np.mean(np.abs(innovation)**2)))
        pred_hat=predictor+quantize_complex_csi(innovation,bits_per_component)
    return {'absolute_nmse':np.asarray(abs_nmse),'predictive_nmse':np.asarray(pred_nmse),
            'mean_absolute_nmse':float(np.mean(abs_nmse)),'mean_predictive_nmse':float(np.mean(pred_nmse)),
            'mean_innovation_power':float(np.mean(innovation_power))}
