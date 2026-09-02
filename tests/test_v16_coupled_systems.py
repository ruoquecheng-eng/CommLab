import numpy as np

from commlab.ris.cellfree_imperfect import age_complex_channel, predicted_channel_samples, design_and_evaluate_aged_cellfree_ris
from commlab.scheduling.fbl_harq_queue import simulate_fbl_harq_queue
from commlab.sensing.closed_loop import simulate_sensing_on_demand
from commlab.mimo.fronthaul_energy import fronthaul_power_from_csi, simulate_cellfree_fronthaul_energy
from commlab.mimo.cell_free import large_scale_fading
from commlab.mimo.ap_activation import strongest_ap_activation


def test_age_complex_channel_zero_steps_exact():
    rng=np.random.default_rng(1); x=rng.normal(size=20)+1j*rng.normal(size=20)
    assert np.allclose(age_complex_channel(x,.9,0,rng),x)


def test_predicted_channel_samples_shape():
    rng=np.random.default_rng(2); a=np.ones((2,3),complex); b=np.ones((4,3),complex); c=np.ones((2,4),complex)
    s=predicted_channel_samples((a,b,c),.95,3,5,rng)
    assert len(s)==5 and s[0][0].shape==a.shape and s[0][1].shape==b.shape


def test_aged_ris_returns_valid_rate_vectors():
    rng=np.random.default_rng(3); K,M,N=2,3,4
    D=.2*(rng.normal(size=(K,M))+1j*rng.normal(size=(K,M)))/np.sqrt(2)
    G=.2*(rng.normal(size=(N,M))+1j*rng.normal(size=(N,M)))/np.sqrt(2)
    R=.2*(rng.normal(size=(K,N))+1j*rng.normal(size=(K,N)))/np.sqrt(2)
    cur=(age_complex_channel(D,.95,2,rng),age_complex_channel(G,.95,2,rng),age_complex_channel(R,.95,2,rng))
    out=design_and_evaluate_aged_cellfree_ris((D,G,R),cur,10.0,bits=1,iterations=1,robust_samples=3,rng=rng)
    for k in ["random_rates","naive_rates","robust_rates","ideal_rates"]:
        assert out[k].shape==(K,) and np.all(out[k]>=0)


def test_fbl_harq_queue_harq_reduces_drop_pressure():
    rng=np.random.default_rng(4); S,U=700,2
    true=rng.normal(0.0,1.2,(S,U)); est=true+1.5+rng.normal(0,.5,(S,U)); arr=(rng.random((S,U))<.12).astype(int)
    args=(true,est,arr,[-4,0,4,8],[.5,1,2,3])
    no=simulate_fbl_harq_queue(*args,blocklength=120,use_harq=False,use_olla=False,seed=5)
    ha=simulate_fbl_harq_queue(*args,blocklength=120,use_harq=True,use_olla=True,seed=5)
    assert ha["drops"] <= no["drops"]


def test_sensing_on_demand_uses_more_sensing_when_process_noise_grows():
    q=np.concatenate([np.full(40,.08),np.full(40,1.2)])
    r=simulate_sensing_on_demand(q,.5,[8,16,32,64],[0,.01,.02,.05,.1,.15,.2],.16)
    f=np.array([x["sensing_fraction"] for x in r["rows"]])
    assert f[40:].mean() >= f[:40].mean()


def test_fronthaul_power_decreases_with_update_interval():
    a=fronthaul_power_from_csi(64,4,1); b=fronthaul_power_from_csi(64,4,8)
    assert a > b > 0


def test_cellfree_fronthaul_energy_outputs_finite_metrics():
    rng=np.random.default_rng(6); aps=rng.uniform(0,1,(10,2)); users=rng.uniform(0,1,(4,2))
    beta=large_scale_fading(aps,users,shadow_std_db=0,rng=rng); active=strongest_ap_activation(beta,6)
    r=simulate_cellfree_fronthaul_energy(beta,active,4,4,.98,3.0,n_slots=30,seed=7)
    assert r["energy_efficiency"]>0 and r["fronthaul_power_w"]>0 and np.isfinite(r["edge_rate"])


def test_predictive_sensing_controller_is_finite():
    from commlab.sensing.closed_loop import simulate_predictive_sensing_on_demand
    q=np.r_[np.full(10,.1),np.full(10,.8)]
    r=simulate_predictive_sensing_on_demand(q,.5,[8,16,32],[0,.02,.05,.1],.15)
    assert np.isfinite(r['mean_net_rate']) and 0<=r['mean_sensing_fraction']<1
