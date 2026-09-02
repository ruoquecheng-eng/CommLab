import numpy as np


def sic_decode_powers(received_snr_linear: np.ndarray, sinr_threshold_linear: float) -> int:
    """Decode one collision group by ideal power-domain SIC.

    Users are ordered from strongest to weakest. If the current strongest user
    does not meet the SINR threshold, decoding stops; otherwise it is cancelled
    perfectly and the next user is attempted. Noise power is normalized to one.
    """
    p=np.sort(np.asarray(received_snr_linear,float).reshape(-1))[::-1]
    if np.any(p<0) or sinr_threshold_linear<=0:
        raise ValueError('invalid SIC inputs')
    decoded=0
    for i in range(len(p)):
        interference=float(np.sum(p[i+1:]))
        sinr=float(p[i]/(1.0+interference))
        if sinr < sinr_threshold_linear:
            break
        decoded+=1
    return decoded


def simulate_grant_free_random_access(n_devices: int, n_resources: int, n_slots: int,
                                      activity_probability: float,
                                      mean_snr_db: float=8.0,
                                      power_spread_db: float=6.0,
                                      sinr_threshold_db: float=2.0,
                                      mode: str='noma_sic', seed: int=1) -> dict:
    """Slotted grant-free uplink random access baseline.

    Active devices independently select one resource. ``oma_collision`` decodes
    only singleton resources. ``noma_sic`` permits collisions and applies ideal
    power-domain SIC. Log-normal received-power spread abstracts heterogeneous
    path loss / imperfect power control; no preamble or activity detector errors
    are modeled.
    """
    if n_devices<1 or n_resources<1 or n_slots<1 or not (0<=activity_probability<=1):
        raise ValueError('invalid random-access setup')
    if power_spread_db<0 or mode not in {'oma_collision','noma_sic'}:
        raise ValueError('invalid access mode')
    rng=np.random.default_rng(seed); th=10**(sinr_threshold_db/10); base=10**(mean_snr_db/10)
    attempts=0; decoded=0; occupied=0; collision_resources=0; decoded_per_slot=[]
    for _ in range(int(n_slots)):
        active=np.where(rng.random(n_devices)<activity_probability)[0]
        attempts+=len(active); slot_dec=0
        if len(active):
            res=rng.integers(0,n_resources,len(active))
            # Log-normal power spread around the configured average SNR.
            snr_db=mean_snr_db+rng.normal(0,power_spread_db,len(active))
            powers=10**(snr_db/10)
            for r in np.unique(res):
                idx=np.where(res==r)[0]; occupied+=1
                if len(idx)>1: collision_resources+=1
                if mode=='oma_collision':
                    d=int(len(idx)==1 and powers[idx[0]]>=th)
                else:
                    d=sic_decode_powers(powers[idx],th)
                slot_dec+=d
        decoded+=slot_dec; decoded_per_slot.append(slot_dec)
    offered=float(attempts/max(n_slots*n_resources,1))
    return {
        'offered_load_per_resource':offered,
        'throughput_packets_per_slot':float(decoded/n_slots),
        'throughput_packets_per_resource':float(decoded/max(n_slots*n_resources,1)),
        'success_probability':float(decoded/max(attempts,1)),
        'mean_decoded_per_slot':float(np.mean(decoded_per_slot)),
        'collision_resource_fraction':float(collision_resources/max(occupied,1)),
        'attempts':int(attempts),'decoded_packets':int(decoded),
    }
