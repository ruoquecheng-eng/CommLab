import numpy as np


def simulate_aircomp_mean_aggregation(n_devices: int=20, vector_dim: int=32,
                                       snr_db: float=15.0, n_trials: int=500,
                                       inversion_threshold: float=0.35,
                                       max_power: float=1.0, seed: int=1) -> dict:
    """Analog over-the-air mean aggregation under Rayleigh fading.

    Three transparent baselines are evaluated on the same local vectors:

    ``orthogonal``
        Each device occupies one channel use and is zero-forcing equalized.
    ``full_inversion``
        All devices transmit simultaneously after exact channel inversion. The
        common receive gain is limited by the weakest channel.
    ``truncated_inversion``
        Devices below ``inversion_threshold`` stay silent; active devices invert
        their channels with a fixed common receive gain. This reduces deep-fade
        noise enhancement at the cost of aggregation/subsampling error.

    The target is the arithmetic mean of all device vectors. The abstraction
    intentionally omits synchronization, quantization, coding, and model-training
    dynamics; it isolates communication/computation MSE and channel-use cost.
    """
    if n_devices<2 or vector_dim<1 or n_trials<1 or snr_db<-50 or max_power<=0:
        raise ValueError("invalid AirComp setup")
    if inversion_threshold<=0:
        raise ValueError("inversion_threshold must be positive")
    rng=np.random.default_rng(seed)
    noise_var=max_power/(10**(snr_db/10))
    mse_o=[]; mse_f=[]; mse_t=[]; active_frac=[]; full_gain=[]
    eps=1e-12
    for _ in range(int(n_trials)):
        x=rng.normal(size=(n_devices,vector_dim))
        target=x.mean(axis=0)
        h=(rng.normal(size=n_devices)+1j*rng.normal(size=n_devices))/np.sqrt(2)
        # Orthogonal transmission: one independent noise vector per device.
        n=(rng.normal(size=(n_devices,vector_dim))+1j*rng.normal(size=(n_devices,vector_dim)))*np.sqrt(noise_var/2)
        y=h[:,None]*np.sqrt(max_power)*x+n
        xhat=np.real(y/(np.sqrt(max_power)*h[:,None]+eps))
        est_o=xhat.mean(axis=0)
        mse_o.append(np.mean((est_o-target)**2))

        # Full inversion: weakest user sets the common amplitude and therefore
        # controls the aggregate noise amplification.
        a=np.sqrt(max_power)*max(float(np.min(np.abs(h))),1e-5)
        nf=(rng.normal(size=vector_dim)+1j*rng.normal(size=vector_dim))*np.sqrt(noise_var/2)
        ysum=a*np.sum(x,axis=0)+nf
        est_f=np.real(ysum)/(a*n_devices)
        mse_f.append(np.mean((est_f-target)**2)); full_gain.append(a)

        active=np.abs(h)>=inversion_threshold
        ka=int(np.sum(active)); active_frac.append(ka/n_devices)
        if ka==0:
            est_t=np.zeros(vector_dim)
        else:
            a_t=np.sqrt(max_power)*inversion_threshold
            nt=(rng.normal(size=vector_dim)+1j*rng.normal(size=vector_dim))*np.sqrt(noise_var/2)
            yt=a_t*np.sum(x[active],axis=0)+nt
            # Estimate the active-device mean; relative to the all-device target
            # this includes a transparent participant-dropout error component.
            est_t=np.real(yt)/(a_t*ka)
        mse_t.append(np.mean((est_t-target)**2))
    return {
        "orthogonal_mse":float(np.mean(mse_o)),
        "full_inversion_mse":float(np.mean(mse_f)),
        "truncated_inversion_mse":float(np.mean(mse_t)),
        "orthogonal_median_mse":float(np.median(mse_o)),
        "full_inversion_median_mse":float(np.median(mse_f)),
        "truncated_inversion_median_mse":float(np.median(mse_t)),
        "full_inversion_p90_mse":float(np.quantile(mse_f,.90)),
        "mean_active_fraction":float(np.mean(active_frac)),
        "mean_full_inversion_gain":float(np.mean(full_gain)),
        "orthogonal_channel_uses_per_vector":int(n_devices),
        "aircomp_channel_uses_per_vector":1,
        "snr_db":float(snr_db),
        "inversion_threshold":float(inversion_threshold),
    }
