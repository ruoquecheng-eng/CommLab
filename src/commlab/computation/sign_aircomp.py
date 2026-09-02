import numpy as np


def simulate_sign_aircomp(n_clients=15,dim=256,snr_db=0.0,client_gradient_noise=.9,
                          byzantine_fraction=0.0,trials=2000,seed=0):
    """One-bit OTA majority-sign aggregation baseline.

    Each client transmits one BPSK sign per gradient coordinate. Wireless
    superposition computes a noisy majority vote. This is a signSGD-style toy
    model, not a coded digital AirComp protocol.
    """
    if n_clients<3 or dim<1 or not 0<=byzantine_fraction<.5: raise ValueError('invalid setup')
    rng=np.random.default_rng(seed); errs=[]; margins=[]
    nb=int(round(n_clients*byzantine_fraction)); nv=10**(-snr_db/10)
    for _ in range(trials):
        g=rng.normal(size=dim); true=np.sign(g); true[true==0]=1
        local=g[None,:]+client_gradient_noise*rng.normal(size=(n_clients,dim))
        s=np.sign(local); s[s==0]=1
        if nb: s[:nb]*=-1
        analog=s.sum(axis=0)+np.sqrt(nv*n_clients)*rng.normal(size=dim)
        est=np.sign(analog); est[est==0]=1
        errs.append(np.mean(est!=true)); margins.append(np.mean(np.abs(s.sum(axis=0))))
    return {'sign_error_rate':float(np.mean(errs)),'mean_vote_margin':float(np.mean(margins)),
            'n_clients':int(n_clients),'snr_db':float(snr_db),'byzantine_fraction':float(byzantine_fraction)}
