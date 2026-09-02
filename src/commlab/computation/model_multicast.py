import numpy as np


def _spectral_efficiency(snr_db): return np.log2(1+10**(np.asarray(snr_db)/10))


def simulate_layered_model_multicast(n_clients=24,model_bits=120_000,base_fraction=.45,
                                     mean_snr_db=5,snr_std_db=7,seed=0):
    """Downlink model distribution to heterogeneous edge clients.

    Compare common-rate multicast, per-client unicast, and scalable two-layer
    multicast. Utility is a transparent proxy: base layer gives 0.7 task utility,
    enhancement raises it to 1.0. Transmission time is normalized bits/(Hz*SE).
    """
    if not 0<base_fraction<1: raise ValueError('bad base fraction')
    rng=np.random.default_rng(seed+2505); snr=np.clip(rng.normal(mean_snr_db,snr_std_db,size=n_clients),-12,25)
    se=_spectral_efficiency(snr); eps=1e-9
    # One common code rate that all devices decode.
    common_time=model_bits/(np.min(se)+eps); common_utility=1.0
    # Independent unicasts; no spatial reuse in this simple baseline.
    unicast_time=float(np.sum(model_bits/(se+eps))); unicast_utility=1.0
    # Base reaches all; enhancement targets stronger half at its weakest supported rate.
    base_bits=model_bits*base_fraction; enh_bits=model_bits-base_bits
    median=np.median(snr); strong=snr>=median
    layered_time=base_bits/(np.min(se)+eps)+enh_bits/(np.min(se[strong])+eps)
    util=np.full(n_clients,.70); util[strong]=1.0
    return {'common_time':float(common_time),'unicast_time':float(unicast_time),'layered_time':float(layered_time),
            'common_mean_utility':float(common_utility),'unicast_mean_utility':float(unicast_utility),
            'layered_mean_utility':float(util.mean()),'strong_fraction':float(strong.mean()),
            'min_snr_db':float(snr.min()),'median_snr_db':float(np.median(snr))}
