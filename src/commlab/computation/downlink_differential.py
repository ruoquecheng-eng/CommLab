import numpy as np


def _packet_success_probability(snr_db, normalized_size, margin_scale=0.55):
    """Smooth outage proxy for one downlink model packet.

    ``normalized_size=1`` denotes a full-model packet. Smaller differential
    packets are easier to deliver. This is a transparent abstraction, not a
    standard link-to-system mapping.
    """
    se=np.log2(1+10**(np.asarray(snr_db,dtype=float)/10))
    required=normalized_size/margin_scale
    return 1/(1+np.exp(-2.2*(se-required)))


def simulate_differential_model_broadcast(n_clients=24, rounds=120, dim=32,
                                           mean_snr_db=2.0, snr_std_db=5.0,
                                           keyframe_interval=8,
                                           delta_fraction=.18,
                                           scheme='anchored_delta', seed=0):
    """Wireless global-model dissemination with packet losses.

    Schemes
    -------
    full:
        Send a full model every round. Each successful packet independently
        resynchronizes a client.
    chained_delta:
        Send a full keyframe every ``keyframe_interval`` rounds and otherwise a
        small delta against the immediately preceding round. Missing one delta
        breaks the reconstruction chain until the next keyframe.
    anchored_delta:
        Send periodic keyframes. Intermediate packets encode the current model
        relative to the last keyframe, so a client that owns the keyframe can
        recover after an isolated missed delta. Packet size grows mildly with
        anchor age. This is an educational mixed-timescale baseline, not a
        reproduction of any specific published codec.
    """
    if scheme not in {'full','chained_delta','anchored_delta'}: raise ValueError('unknown scheme')
    if keyframe_interval<1 or rounds<2 or n_clients<1: raise ValueError('invalid setup')
    rng=np.random.default_rng(seed+2603)
    snr=np.clip(rng.normal(mean_snr_db,snr_std_db,size=n_clients),-12,22)
    # Smooth server-model trajectory with temporally correlated increments.
    model=np.zeros(dim); velocity=np.zeros(dim); models=[model.copy()]
    for _ in range(1,rounds):
        velocity=.78*velocity+.06*rng.normal(size=dim)
        model=model+velocity
        models.append(model.copy())
    models=np.asarray(models)

    client_model=np.zeros((n_clients,dim)); last_version=np.zeros(n_clients,dtype=int)
    has_anchor=np.ones(n_clients,dtype=bool); chain_ok=np.ones(n_clients,dtype=bool)
    anchor_round=0; total_size=0.0; success_count=0; mse=[]; age=[]; packet_sizes=[]

    for t in range(1,rounds):
        keyframe=(scheme=='full') or (t%keyframe_interval==0)
        if keyframe:
            size=1.0; anchor_round=t
        elif scheme=='chained_delta':
            size=delta_fraction
        else:
            # Anchoring deltas to an older keyframe improves loss recovery, but
            # the payload grows because the cumulative model displacement grows.
            a=t-anchor_round
            size=delta_fraction*(1+.07*max(a-1,0))
        p=_packet_success_probability(snr,size)
        ok=rng.random(n_clients)<p
        total_size+=size; packet_sizes.append(size)
        success_count+=int(ok.sum())

        if scheme=='full':
            client_model[ok]=models[t]; last_version[ok]=t
        elif keyframe:
            client_model[ok]=models[t]; last_version[ok]=t
            has_anchor[ok]=True; chain_ok[ok]=True
            has_anchor[~ok]=False; chain_ok[~ok]=False
        elif scheme=='chained_delta':
            applicable=ok & chain_ok & (last_version==t-1)
            if np.any(applicable):
                client_model[applicable]+=models[t]-models[t-1]
                last_version[applicable]=t
            chain_ok[~applicable]=False
        else:
            applicable=ok & has_anchor
            if np.any(applicable):
                # The receiver reconstructs the current model from its retained
                # keyframe plus the current anchor-relative differential packet.
                client_model[applicable]=models[t]
                last_version[applicable]=t

        err=np.mean((client_model-models[t])**2,axis=1)
        mse.append(float(np.mean(err))); age.append(float(np.mean(t-last_version)))

    return {
        'scheme':scheme,'keyframe_interval':int(keyframe_interval),
        'mean_model_mse':float(np.mean(mse)),'final_model_mse':float(mse[-1]),
        'mean_version_age':float(np.mean(age)),'final_version_age':float(age[-1]),
        'normalized_downlink_size_per_round':float(total_size/(rounds-1)),
        'mean_packet_size':float(np.mean(packet_sizes)),
        'packet_success_fraction':float(success_count/((rounds-1)*n_clients)),
        'mse_history':np.asarray(mse),'age_history':np.asarray(age),
    }
