import numpy as np


def _soft_clip(z, saturation):
    if saturation is None: return z
    if saturation<=0: raise ValueError('saturation must be positive')
    a=np.abs(z); scale=np.ones_like(a); mask=a>saturation
    scale[mask]=saturation/(a[mask]+1e-15)
    return z*scale


def _uniform_quantize_real(x,bits,full_scale):
    if bits is None: return x
    if bits<1 or full_scale<=0: raise ValueError('invalid ADC setup')
    levels=2**int(bits); step=2*full_scale/levels
    xc=np.clip(x,-full_scale,full_scale-step)
    return (np.floor((xc+full_scale)/step)+.5)*step-full_scale


def simulate_aircomp_hardware(n_devices=16, vector_dim=64, snr_db=20,
                              pa_saturation=2.0, adc_bits=6, agc=True,
                              n_trials=300, seed=0):
    """Full-inversion AirComp with PA clipping and finite-resolution ADC.

    Each device uses channel inversion with coefficient magnitude <=1.  The
    transmit waveform then passes through a memoryless magnitude limiter.  At
    the receiver, an optional per-vector AGC scales the complex aggregate into
    the ADC range before uniform I/Q quantization.  This is an educational RF
    impairment model, not a calibrated converter/PA implementation.
    """
    if n_devices<2 or vector_dim<2 or n_trials<1: raise ValueError('bad AirComp setup')
    rng=np.random.default_rng(seed); nv=1/(10**(snr_db/10)); ms=[]; clips=[]; adcs=[]
    for _ in range(n_trials):
        x=rng.normal(size=(n_devices,vector_dim)); target=x.mean(axis=0)
        h=(rng.normal(size=n_devices)+1j*rng.normal(size=n_devices))/np.sqrt(2)
        a=max(float(np.min(np.abs(h))),1e-4)
        b=a/(h+1e-15)
        tx=b[:,None]*x
        tx2=_soft_clip(tx,pa_saturation)
        clips.append(float(np.mean(np.abs(tx)>pa_saturation)) if pa_saturation is not None else 0.0)
        n=(rng.normal(size=vector_dim)+1j*rng.normal(size=vector_dim))*np.sqrt(nv/2)
        y=np.sum(h[:,None]*tx2,axis=0)+n
        if adc_bits is not None:
            if agc:
                rms=max(float(np.sqrt(np.mean(np.abs(y)**2))),1e-8)
                gain=.32/rms  # target RMS relative to normalized +/-1 ADC range
            else:
                gain=1.0
            ya=y*gain
            yr=_uniform_quantize_real(np.real(ya),adc_bits,1.0)
            yi=_uniform_quantize_real(np.imag(ya),adc_bits,1.0)
            adcs.append(float(np.mean((np.abs(np.real(ya))>=1)|(np.abs(np.imag(ya))>=1))))
            y=(yr+1j*yi)/gain
        else:
            adcs.append(0.0)
        est=np.real(y)/(a*n_devices)
        ms.append(float(np.mean((est-target)**2)))
    return {
        'mean_mse':float(np.mean(ms)),'median_mse':float(np.median(ms)),
        'p90_mse':float(np.percentile(ms,90)),
        'mean_pa_clip_fraction':float(np.mean(clips)),
        'mean_adc_overload_fraction':float(np.mean(adcs)),
        'adc_bits':None if adc_bits is None else int(adc_bits),
        'agc':bool(agc),'pa_saturation':None if pa_saturation is None else float(pa_saturation),
    }
