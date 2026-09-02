import numpy as np
from .private_aircomp import clip_rows
from .aircomp_hardware import _soft_clip, _uniform_quantize_real


def simulate_private_hardware_aircomp(n_clients=16,dim=48,snr_db=22,clip_norm=1.0,
                                      privacy_noise_multiplier=.25,pa_saturation=2.0,
                                      adc_bits=6,agc=True,trials=200,seed=0):
    """One-shot AirComp gradient aggregation with privacy and RF impairments together.

    The target is the clipped-gradient average *before* privacy perturbation.
    This separates task distortion from intentional perturbation + channel/RF
    distortion. No formal differential-privacy guarantee is claimed.
    """
    rng=np.random.default_rng(seed+2503); nv=10**(-snr_db/10); ms=[]; clips=[]; overload=[]
    for _ in range(trials):
        G=clip_rows(rng.normal(size=(n_clients,dim)),clip_norm); target=G.mean(axis=0)
        Gp=G+privacy_noise_multiplier*clip_norm*rng.normal(size=G.shape)
        h=(rng.normal(size=n_clients)+1j*rng.normal(size=n_clients))/np.sqrt(2)
        a=max(float(np.min(np.abs(h))),.04); b=a/(h+1e-15)
        tx=b[:,None]*Gp; tx2=_soft_clip(tx,pa_saturation)
        clips.append(float(np.mean(np.abs(tx)>pa_saturation)))
        n=(rng.normal(size=dim)+1j*rng.normal(size=dim))*np.sqrt(nv/2)
        y=np.sum(h[:,None]*tx2,axis=0)+n
        gain=1.0
        if adc_bits is not None:
            if agc:
                rms=max(float(np.sqrt(np.mean(np.abs(y)**2))),1e-9); gain=.32/rms
            ya=y*gain
            overload.append(float(np.mean((np.abs(np.real(ya))>=1)|(np.abs(np.imag(ya))>=1))))
            y=(_uniform_quantize_real(np.real(ya),adc_bits,1.0)+1j*_uniform_quantize_real(np.imag(ya),adc_bits,1.0))/gain
        else: overload.append(0.0)
        est=np.real(y)/(a*n_clients); ms.append(float(np.mean((est-target)**2)))
    return {'mean_mse':float(np.mean(ms)),'median_mse':float(np.median(ms)),'p90_mse':float(np.quantile(ms,.9)),
            'privacy_noise_multiplier':float(privacy_noise_multiplier),'adc_bits':adc_bits,
            'mean_pa_clip_fraction':float(np.mean(clips)),'mean_adc_overload_fraction':float(np.mean(overload))}
