"""Optional Streamlit front end for CommLab-OFDM.

Run after `pip install -e .[app]` with:
    streamlit run app/dashboard.py
"""
from pathlib import Path
import sys

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from commlab.channels import add_awgn, channel_frequency_response
from commlab.config import OFDMConfig
from commlab.impairments import apply_cfo, apply_phase_noise, apply_iq_imbalance, estimate_iq_coefficients, compensate_iq_imbalance, apply_sampling_clock_offset, compensate_sampling_clock_offset
from commlab.metrics import bit_error_rate, evm_percent
from commlab.modulation import QAMModem
from commlab.ofdm import OFDMTransceiver
from commlab.rf import rapp_amplifier, scale_for_input_backoff, rapp_inverse_predistort, fit_indirect_polynomial_dpd, apply_polynomial_dpd, apply_memory_polynomial, fit_indirect_memory_dpd, default_memory_pa_coefficients
from commlab.resource_allocation import waterfill_power_allocation, parallel_channel_capacity_bits
from commlab.synchronization import estimate_common_phase_from_pilots, correct_common_phase
from commlab.equalization import time_varying_ofdm_channel_matrix, linear_lmmse_ici_detect, cg_lmmse_ici_detect, ici_energy_fraction
from commlab.mimo import zf_detect, mmse_detect, ml_detect_small, k_best_detect, mmse_sic_detect, random_unit_codebook, mrt_beamformer, select_codebook_beam, miso_effective_gain, mu_mrt_precoder, mu_zf_precoder, downlink_sinr, favorable_propagation_metric, sparse_geometric_mimo_channel, full_digital_svd_rate, hybrid_dft_svd_rate, hybrid_omp_precoder, precoded_mimo_rate, semi_orthogonal_user_selection, strongest_norm_user_selection, large_scale_fading, user_centric_mask, sample_cell_free_channel, clustered_mrt_directions, rates_with_power, max_min_sinr_power_allocation, clustered_mrt_precoder, per_user_rates
from commlab.mimo.pilot_assignment import greedy_contamination_aware_assignment, random_pilot_assignment, lmmse_pilot_channel_estimate, normalized_channel_mse, pilot_contamination_cost
from commlab.mimo.ap_activation import strongest_ap_activation, coverage_aware_ap_activation, rates_with_active_aps, network_energy_efficiency
from commlab.mimo.fronthaul import quantize_complex_csi, csi_quantization_nmse, fronthaul_csi_bits
from commlab.mimo.fronthaul_energy import simulate_cellfree_fronthaul_energy
from commlab.mimo.async_csi import simulate_async_cellfree_csi
from commlab.mimo.predictive_csi import predictive_csi_quantization_trace
from commlab.mimo.joint_csi_control import simulate_joint_predictive_csi_control
from commlab.scheduling import proportional_fair_schedule, jain_fairness_index, simulate_packet_scheduler, simulate_cross_layer_link
from commlab.information_theory import complex_awgn_capacity, normal_approximation_rate
from commlab.link import OuterLoopLinkAdaptation, select_mcs, logistic_bler
from commlab.ris import optimal_ris_phases, quantize_phases, ris_effective_channel, ris_spectral_efficiency, ris_mu_sum_rate, coordinate_optimize_ris
from commlab.ris.cellfree import cellfree_ris_rates, coordinate_optimize_cellfree_ris
from commlab.ris.robust import perturb_complex_channel, sample_average_optimize_cellfree_ris
from commlab.ris.cellfree_imperfect import age_complex_channel, design_and_evaluate_aged_cellfree_ris
from commlab.ris.two_timescale import simulate_two_timescale_cellfree_ris
from commlab.ris.event_triggered import simulate_event_triggered_cellfree_ris
from commlab.sensing import C0, simulate_ofdm_sensing_channel, range_doppler_map, strongest_targets, ca_cfar_2d, simulate_ofdm_sensing_array_channel, range_doppler_array_cube, bartlett_angle_spectrum, bartlett_covariance_spectrum, music_angle_spectrum, estimate_source_count_mdl, KalmanAngleAccelerationTracker, ula_beam_gain, select_robust_ula_aperture
from commlab.sensing.joint_beamforming import joint_isac_beamformer, communication_rate, sensing_gain
from commlab.sensing.resource_scheduling import joint_sensing_comm_resource_selection
from commlab.sensing.closed_loop import simulate_sensing_on_demand, simulate_predictive_sensing_on_demand
from commlab.scheduling.short_packet import simulate_short_packet_goodput_trace
from commlab.scheduling.fbl_harq_queue import simulate_fbl_harq_queue
from commlab.scheduling.ir_harq_fbl import simulate_fbl_ir_harq_queue
from commlab.scheduling.deadline_harq import simulate_deadline_fbl_harq
from commlab.scheduling.aoi import simulate_status_update_aoi
from commlab.sensing.queue_control import simulate_queue_aware_isac_control
from commlab.sensing.budget_control import simulate_budget_constrained_sensing
from commlab.random_access.grant_free import simulate_grant_free_random_access
from commlab.random_access.irsa import simulate_irsa
from commlab.random_access import simulate_capture_irsa
from commlab.computation import simulate_aircomp_mean_aggregation, simulate_federated_aircomp, simulate_cellfree_aircomp, simulate_task_oriented_classification, effective_ris_aircomp_channel, optimize_ris_aircomp, aircomp_noise_mse_from_channel, simulate_selection_biased_fl, simulate_random_access_federated, simulate_multitask_task_oriented, optimize_robust_ris_aircomp, simulate_lcb_cellfree_aircomp, simulate_budgeted_compressed_fl, simulate_aircomp_hardware, simulate_layered_multitask_semantic, simulate_importance_aware_random_access_fl, simulate_two_timescale_ris_aircomp_fl, simulate_asynchronous_federated, simulate_byzantine_federated, simulate_private_aircomp_fl, simulate_semantic_resource_scheduling, simulate_split_inference, simulate_personalized_federated, simulate_straggler_resilience, simulate_federated_distillation, simulate_channel_aware_split, simulate_sign_aircomp, simulate_resilient_async_federated, simulate_clustered_personalization, simulate_private_hardware_aircomp, simulate_energy_aware_split, simulate_layered_model_multicast, simulate_differential_model_broadcast, simulate_progressive_split_inference, simulate_aircomp_selection_federated, simulate_energy_harvesting_aircomp_fl, simulate_importance_aware_model_multicast, simulate_adaptive_differential_broadcast, simulate_carbon_aware_federated, simulate_edge_model_caching, simulate_queued_progressive_split, simulate_importance_aware_multicast_repair, simulate_selective_downlink_repair, simulate_version_aware_edge_caching, simulate_fair_carbon_orchestration, simulate_progressive_split_admission, simulate_digital_twin_sync, simulate_task_aware_model_repair, simulate_congested_model_refresh, simulate_battery_carbon_fair_fl, simulate_twin_guided_model_prefetch, simulate_networked_control_scheduling, simulate_risk_sensitive_control, simulate_variable_rate_control, simulate_failure_aware_edge_orchestration, simulate_joint_cache_offload, simulate_cooperative_networked_control, simulate_safety_aware_control, simulate_channel_adaptive_depth, simulate_edge_failure_recovery, simulate_risk_aware_model_replication, simulate_component_selective_control, simulate_semantic_harq, simulate_mixed_control_inference, simulate_failure_domain_replication, simulate_checkpoint_aware_migration, simulate_safety_bit_allocation, simulate_predictive_failure_migration, simulate_chance_constrained_inference, simulate_control_uep, simulate_multi_connectivity_reliability, simulate_multiconnectivity_safety_control, simulate_unified_risk_orchestration, simulate_adaptive_risk_control, simulate_observable_resilience, simulate_offline_resilience_evaluation
from commlab.computation import simulate_propensity_robust_evaluation
from commlab.scheduling.network_slicing import simulate_embb_urllc_slicing
from commlab.scheduling.energy_aoi import simulate_energy_harvesting_aoi

st.set_page_config(page_title="CommLab-OFDM", layout="wide")
st.title("CommLab-OFDM Interactive Link Simulator")
st.caption("Educational link-level simulation platform; not a standards-compliant IEEE 802.11/5G implementation.")

mode = st.sidebar.selectbox("Lab", ["OFDM Link", "Phase Noise", "IQ Imbalance", "Sampling Clock", "Power Amplifier", "High-Doppler ICI", "2x2 MIMO Detection", "MIMO K-best", "MIMO MMSE-SIC", "Massive MU-MIMO", "MU-MIMO User Selection", "Hybrid Beamforming", "Hybrid OMP", "Cell-Free Network", "Cell-Free Pilot CSI", "Cell-Free Fronthaul CSI", "Cell-Free Fronthaul Energy", "Async Cell-Free CSI", "Predictive CSI Compression", "Cell-Free RIS", "Robust Cell-Free RIS", "Cell-Free RIS Aging", "Two-timescale RIS", "Cell-Free AP Energy", "Multi-user RIS", "Predictive ISAC Beam", "ISAC Joint Beam", "ISAC Sensing Budget", "Predictive Sensing-on-Demand", "Cross-layer OLLA/HARQ", "FBL HARQ Queue", "FBL IR-HARQ", "Queue-aware ISAC", "Short-Packet FBL", "RIS Link", "Limited Feedback Beamforming", "OFDMA Scheduling", "Queued OFDMA", "OLLA Link Adaptation", "OFDM Sensing / ISAC", "ISAC Angle", "ISAC MUSIC", "ISAC MUSIC + MDL", "Finite Blocklength", "Joint CSI Budget", "Deadline HARQ", "Age of Information", "Event-triggered RIS", "Budgeted ISAC", "Grant-free NOMA", "IRSA Random Access", "Capture IRSA", "AirComp Aggregation", "AirComp Federated Learning", "Cell-Free AirComp", "RIS AirComp", "Task-Oriented Communication", "Non-IID FL Client Selection", "Random-Access FL", "Robust RIS AirComp", "Cell-Free AirComp CSI Risk", "Multi-Task Semantic", "Budgeted Gradient FL", "AirComp Hardware", "Layered Semantic", "Importance Random-Access FL", "Two-timescale RIS FL", "Async Federated Learning", "Byzantine-Robust FL", "Private AirComp FL", "Semantic Resource Scheduler", "Split Inference", "Personalized FL", "Straggler-Resilient FL", "Federated Distillation", "Channel-Aware Split", "OTA Sign Aggregation", "Resilient Async FL", "Clustered Personalization", "Private Hardware AirComp", "Energy-Aware Split", "Layered Model Multicast", "Differential Model Broadcast", "Progressive Split Inference", "AirComp Selection Bias", "EH AirComp FL", "Importance-Aware Multicast", "Adaptive FL Downlink", "Carbon-Aware FL", "Edge Model Caching", "Queued Progressive Split", "Multicast Repair", "Selective Downlink Repair", "Version-Aware Model Cache", "Fair Carbon Orchestration", "Split Admission Control", "Digital Twin Sync", "Task-Aware Model Repair", "Congested Model Refresh", "Battery-Carbon Fair FL", "Twin-Guided Prefetch", "Networked Control", "Risk-Sensitive Control", "Variable-Rate Control", "Failure-Aware Edge", "Joint Cache-Offload", "Cooperative Control", "Safety-Aware Control", "Adaptive-Depth Inference", "Failure Recovery", "Risk-Aware Model Replication", "Component-Selective Control", "Semantic HARQ", "Mixed Control-Inference", "Failure-Domain Replication", "Checkpoint Service Migration", "Safety Bit Allocation", "Predictive Failure Migration", "Chance-Constrained Inference", "Control UEP", "Multi-Connectivity Reliability", "Multi-Connectivity Safety Control", "Unified Resilience Budget", "Adaptive Risk Control", "Observable Resilience", "Offline Resilience Evaluation", "Propensity-Robust OPE", "eMBB-URLLC Slicing", "Energy-Harvesting AoI", "Water-Filling"])
seed = st.sidebar.number_input("Random seed", min_value=0, value=2026, step=1)
rng = np.random.default_rng(seed)

if mode == "OFDM Link":
    order = st.sidebar.selectbox("Modulation", [4, 16, 64], format_func=lambda m: "QPSK" if m == 4 else f"{m}-QAM")
    snr_db = st.sidebar.slider("Sample-domain SNR (dB)", 0.0, 30.0, 15.0, 0.5)
    cfo = st.sidebar.slider("Normalized CFO (subcarrier spacings)", -0.25, 0.25, 0.0, 0.01)
    n_symbols = st.sidebar.slider("OFDM symbols", 10, 400, 100, 10)

    cfg = OFDMConfig()
    modem = QAMModem(order)
    ofdm = OFDMTransceiver(cfg)
    bits = rng.integers(0, 2, n_symbols * cfg.n_data * modem.bits_per_symbol, dtype=np.uint8)
    tx_symbols = modem.modulate(bits)
    tx = ofdm.modulate(tx_symbols)
    rx = apply_cfo(tx, cfo, cfg.n_fft)
    rx = add_awgn(rx, snr_db, rng)
    rx_symbols, _ = ofdm.demodulate(rx)
    bits_hat = modem.demodulate(rx_symbols)

    ber = bit_error_rate(bits, bits_hat)
    evm = evm_percent(tx_symbols, rx_symbols)
    c1, c2, c3 = st.columns(3)
    c1.metric("BER", f"{ber:.3e}")
    c2.metric("RMS EVM", f"{evm:.2f}%")
    c3.metric("Payload bits", f"{len(bits):,}")

    fig, ax = plt.subplots()
    show = min(3000, len(rx_symbols))
    ax.scatter(rx_symbols.real[:show], rx_symbols.imag[:show], s=7, alpha=0.35)
    ax.set_xlabel("In-phase"); ax.set_ylabel("Quadrature"); ax.set_title("Received Constellation")
    ax.grid(True); ax.axis("equal"); st.pyplot(fig)
    st.info("This lab intentionally leaves CFO uncorrected so the impairment is visible; the experiment suite contains synchronization and pilot-tracking receivers.")

elif mode == "Phase Noise":
    sigma = st.sidebar.slider("Phase innovation std (rad/sample)", 0.0, 0.025, 0.008, 0.0005)
    snr_db = st.sidebar.slider("SNR (dB)", 10.0, 35.0, 28.0, 0.5)
    cfg = OFDMConfig(); modem = QAMModem(64); ofdm = OFDMTransceiver(cfg)
    n_symbols = 180
    bits = rng.integers(0, 2, n_symbols * cfg.n_data * 6, dtype=np.uint8)
    ref = modem.modulate(bits); tx = ofdm.modulate(ref)
    rx = apply_phase_noise(tx, sigma, rng); rx = add_awgn(rx, snr_db, rng)
    data, pilots = ofdm.demodulate(rx)
    phase = estimate_common_phase_from_pilots(pilots, cfg)
    tracked = correct_common_phase(data, phase, cfg.n_data)
    raw_ber = bit_error_rate(bits, modem.demodulate(data)); tr_ber = bit_error_rate(bits, modem.demodulate(tracked))
    c1,c2,c3,c4=st.columns(4); c1.metric("Raw BER", f"{raw_ber:.3e}"); c2.metric("Tracked BER", f"{tr_ber:.3e}"); c3.metric("Raw EVM", f"{evm_percent(ref,data):.2f}%"); c4.metric("Tracked EVM", f"{evm_percent(ref,tracked):.2f}%")
    fig,ax=plt.subplots(); show=min(2500,len(tracked)); ax.scatter(data.real[:show],data.imag[:show],s=6,alpha=.2,label='Raw'); ax.scatter(tracked.real[:show],tracked.imag[:show],s=6,alpha=.2,label='Pilot CPE tracked'); ax.set_title('64-QAM Phase Noise'); ax.grid(True); ax.axis('equal'); ax.legend(); st.pyplot(fig)
    st.caption("Per-symbol pilot tracking removes common phase rotation, but strong within-symbol phase noise still creates ICI.")

elif mode == "IQ Imbalance":
    gain_db = st.sidebar.slider("I/Q gain imbalance (dB)", 0.0, 5.0, 2.0, 0.1)
    phase_deg = st.sidebar.slider("Quadrature phase error (deg)", 0.0, 20.0, 7.0, 0.5)
    cfg=OFDMConfig(); modem=QAMModem(64); ofdm=OFDMTransceiver(cfg)
    train_bits=rng.integers(0,2,4*cfg.n_data*2,dtype=np.uint8); train=ofdm.modulate(QAMModem(4).modulate(train_bits))
    bits=rng.integers(0,2,160*cfg.n_data*6,dtype=np.uint8); ref=modem.modulate(bits); payload=ofdm.modulate(ref)
    frame=np.concatenate((train,payload)); rx=apply_iq_imbalance(frame,gain_db,phase_deg); rx=add_awgn(rx,30.0,rng)
    a,b=estimate_iq_coefficients(train,rx[:len(train)]); raw,_=ofdm.demodulate(rx[len(train):]); comp,_=ofdm.demodulate(compensate_iq_imbalance(rx[len(train):],a,b))
    c1,c2,c3,c4=st.columns(4); c1.metric("Raw BER",f"{bit_error_rate(bits,modem.demodulate(raw)):.3e}"); c2.metric("Compensated BER",f"{bit_error_rate(bits,modem.demodulate(comp)):.3e}"); c3.metric("Raw EVM",f"{evm_percent(ref,raw):.2f}%"); c4.metric("Compensated EVM",f"{evm_percent(ref,comp):.2f}%")
    fig,ax=plt.subplots(); show=min(2500,len(raw)); ax.scatter(raw.real[:show],raw.imag[:show],s=6,alpha=.18,label='Impaired'); ax.scatter(comp.real[:show],comp.imag[:show],s=6,alpha=.18,label='LS compensated'); ax.grid(True); ax.axis('equal'); ax.legend(); ax.set_title('64-QAM IQ Imbalance'); st.pyplot(fig)
    st.caption("The receiver estimates a widely-linear y=αx+βx* model from known training and inverts it. This is a normalized baseband impairment model, not hardware calibration.")

elif mode == "Sampling Clock":
    ppm=st.sidebar.slider("Sampling-clock offset (ppm)",0,1000,250,25)
    cfg=OFDMConfig(); modem=QAMModem(64); ofdm=OFDMTransceiver(cfg); n_symbols=180
    bits=rng.integers(0,2,n_symbols*cfg.n_data*6,dtype=np.uint8); ref=modem.modulate(bits); tx=ofdm.modulate(ref)
    raw_wave=apply_sampling_clock_offset(tx,ppm); raw_wave=add_awgn(raw_wave,30.0,rng); corrected_wave=compensate_sampling_clock_offset(raw_wave,ppm)
    raw,_=ofdm.demodulate(raw_wave); cor,_=ofdm.demodulate(corrected_wave)
    c1,c2,c3,c4=st.columns(4); c1.metric("Raw BER",f"{bit_error_rate(bits,modem.demodulate(raw)):.3e}"); c2.metric("Known-SCO corrected BER",f"{bit_error_rate(bits,modem.demodulate(cor)):.3e}"); c3.metric("Raw EVM",f"{evm_percent(ref,raw):.2f}%"); c4.metric("Corrected EVM",f"{evm_percent(ref,cor):.2f}%")
    st.caption("The offline experiment estimates ppm from two separated training bursts. This interactive lab uses the selected ppm directly so it stays responsive.")

elif mode == "Power Amplifier":
    ibo = st.sidebar.slider("Input back-off (dB)", 0.0, 12.0, 4.0, 0.5)
    smoothness = st.sidebar.slider("Rapp smoothness", 1.0, 5.0, 2.0, 0.5)
    dpd_mode = st.sidebar.selectbox("DPD", ["None", "Known Rapp inverse", "Data-fitted polynomial"])
    cfg = OFDMConfig(); modem = QAMModem(16); ofdm = OFDMTransceiver(cfg)
    n_symbols = 200
    bits = rng.integers(0, 2, n_symbols * cfg.n_data * 4, dtype=np.uint8)
    tx_symbols = modem.modulate(bits)
    wave = ofdm.modulate(tx_symbols)
    driven = scale_for_input_backoff(wave, ibo)
    if dpd_mode == "Known Rapp inverse":
        pa_in = rapp_inverse_predistort(driven, smoothness=smoothness)
    elif dpd_mode == "Data-fitted polynomial":
        tr_bits=rng.integers(0,2,250*cfg.n_data*4,dtype=np.uint8); tr=scale_for_input_backoff(ofdm.modulate(modem.modulate(tr_bits)),ibo); tr_y=rapp_amplifier(tr,smoothness=smoothness); coeff=fit_indirect_polynomial_dpd(tr,tr_y,order=9); pa_in=apply_polynomial_dpd(driven,coeff)
    else:
        pa_in = driven
    out = rapp_amplifier(pa_in, smoothness=smoothness)
    rx_symbols, _ = ofdm.demodulate(out)
    g = np.vdot(tx_symbols, rx_symbols) / np.vdot(tx_symbols, tx_symbols)
    rx_corrected = rx_symbols / g
    ber = bit_error_rate(bits, modem.demodulate(rx_corrected))
    evm = evm_percent(tx_symbols, rx_corrected)
    c1, c2 = st.columns(2); c1.metric("BER", f"{ber:.3e}"); c2.metric("EVM", f"{evm:.2f}%")
    fig, ax = plt.subplots(); show=min(2500,len(rx_corrected))
    ax.scatter(rx_corrected.real[:show], rx_corrected.imag[:show], s=7, alpha=.35)
    ax.set_title("16-QAM after Rapp PA (gain normalized)"); ax.grid(True); ax.axis('equal'); st.pyplot(fig)
    st.caption("Lower back-off drives the PA closer to saturation. The DPD selector includes both an idealized known-model inverse and a data-fitted memoryless polynomial indirect-learning baseline; neither is hardware-calibrated.")

elif mode == "High-Doppler ICI":
    dop=st.sidebar.slider("Moving-path Doppler (subcarrier spacings)",0.0,2.5,1.5,0.1)
    snr_db=st.sidebar.slider("SNR (dB)",8.0,28.0,18.0,1.0)
    modem=QAMModem(4); nfft=64; cp=16
    taps=np.array([1.0,0.52*np.exp(.35j),0.24*np.exp(-.5j)],complex); taps/=np.linalg.norm(taps)
    H=time_varying_ofdm_channel_matrix(taps,np.array([0,3,8]),np.array([0.,dop,-.55*dop]),nfft,cp)
    bits=rng.integers(0,2,nfft*2,dtype=np.uint8); x=modem.modulate(bits); nv=10**(-snr_db/10); y=H@x+np.sqrt(nv/2)*(rng.normal(size=nfft)+1j*rng.normal(size=nfft))
    estimates={"One-tap":linear_lmmse_ici_detect(y,H,nv,bandwidth=0),"Banded ±2":linear_lmmse_ici_detect(y,H,nv,bandwidth=2),"Full ICI":linear_lmmse_ici_detect(y,H,nv)}
    cols=st.columns(4); cols[0].metric("ICI energy",f"{100*ici_energy_fraction(H):.1f}%")
    for c,(name,xh) in zip(cols[1:],estimates.items()): c.metric(name+" BER",f"{bit_error_rate(bits,modem.demodulate(xh)):.3e}")
    fig,ax=plt.subplots(); im=ax.imshow(20*np.log10(np.abs(H)+1e-5),aspect="auto",origin="lower",vmin=-55); ax.set_title("OFDM effective channel |H| (dB)"); ax.set_xlabel("Tx subcarrier"); ax.set_ylabel("Rx subcarrier"); fig.colorbar(im,ax=ax); st.pyplot(fig)
    st.caption("Doppler spreads energy away from the diagonal. Banded/full LMMSE explicitly models ICI instead of assuming one independent scalar channel per subcarrier.")

elif mode == "2x2 MIMO Detection":
    snr_db=st.sidebar.slider("SNR (dB)",0.0,24.0,12.0,1.0); n=2500; modem=QAMModem(4)
    labels=np.arange(4,dtype=np.uint8)[:,None]; bitslab=((labels >> np.array([1,0])) & 1).astype(np.uint8); const=modem.modulate(bitslab.reshape(-1))
    H=(rng.normal(size=(n,2,2))+1j*rng.normal(size=(n,2,2)))/np.sqrt(2); idx=rng.integers(0,4,size=(n,2)); x=const[idx]; nv=10**(-snr_db/10); y=np.einsum("bij,bj->bi",H,x)+np.sqrt(nv/2)*(rng.normal(size=(n,2))+1j*rng.normal(size=(n,2)))
    est={"ZF":zf_detect(y,H),"MMSE":mmse_detect(y,H,nv),"ML":ml_detect_small(y,H,const)}; true=bitslab[idx].reshape(-1); cols=st.columns(3)
    for c,(name,xh) in zip(cols,est.items()): nearest=np.argmin(abs(xh[...,None]-const[None,None,:]),axis=-1); ber=np.mean(bitslab[nearest].reshape(-1)!=true); c.metric(name+" BER",f"{ber:.3e}")
    st.caption("Exhaustive ML checks all 4^2=16 QPSK transmit vectors per channel use. It is a small-system performance reference, not a scalable massive-MIMO detector.")

elif mode == "MIMO K-best":
    snr_db=st.sidebar.slider("SNR (dB)",4.0,24.0,14.0,1.0); kval=st.sidebar.select_slider("K-best survivors",options=[1,2,4,8,16],value=4); n=900; modem=QAMModem(16)
    labels=np.arange(16,dtype=np.uint8)[:,None]; bitslab=((labels >> np.arange(3,-1,-1)) & 1).astype(np.uint8); const=modem.modulate(bitslab.reshape(-1))
    H=(rng.normal(size=(n,2,2))+1j*rng.normal(size=(n,2,2)))/np.sqrt(2); idx=rng.integers(0,16,size=(n,2)); x=const[idx]; nv=10**(-snr_db/10); y=np.einsum("bij,bj->bi",H,x)+np.sqrt(nv/2)*(rng.normal(size=(n,2))+1j*rng.normal(size=(n,2)))
    est={"MMSE":mmse_detect(y,H,nv),f"K-best K={kval}":k_best_detect(y,H,const,kval),"Exhaustive ML":ml_detect_small(y,H,const)}; true=bitslab[idx].reshape(-1); cols=st.columns(3)
    for c,(name,xh) in zip(cols,est.items()): nearest=np.argmin(abs(xh[...,None]-const[None,None,:]),axis=-1); c.metric(name+" BER",f"{np.mean(bitslab[nearest].reshape(-1)!=true):.3e}")
    st.caption("QR K-best retains only K partial tree paths per layer. Increasing K approaches exhaustive ML while increasing search work.")

elif mode == "MIMO MMSE-SIC":
    snr_db=st.sidebar.slider("SNR (dB)",4.0,24.0,14.0,1.0); n=1200; modem=QAMModem(16)
    labels=np.arange(16,dtype=np.uint8)[:,None]; bitslab=((labels >> np.arange(3,-1,-1)) & 1).astype(np.uint8); const=modem.modulate(bitslab.reshape(-1))
    H=(rng.normal(size=(n,2,2))+1j*rng.normal(size=(n,2,2)))/np.sqrt(2); idx=rng.integers(0,16,size=(n,2)); x=const[idx]; nv=10**(-snr_db/10); y=np.einsum("bij,bj->bi",H,x)+np.sqrt(nv/2)*(rng.normal(size=(n,2))+1j*rng.normal(size=(n,2)))
    est={"MMSE":mmse_detect(y,H,nv),"Ordered MMSE-SIC":mmse_sic_detect(y,H,const,nv),"K-best K=4":k_best_detect(y,H,const,4)}; true=bitslab[idx].reshape(-1); cols=st.columns(3)
    for c,(name,xh) in zip(cols,est.items()): nearest=np.argmin(abs(xh[...,None]-const[None,None,:]),axis=-1); c.metric(name+" BER",f"{np.mean(bitslab[nearest].reshape(-1)!=true):.3e}")
    st.caption("Ordered MMSE-SIC re-filters and cancels one detected stream at a time, bridging linear MMSE and tree search while exposing error-propagation risk.")

elif mode == "Massive MU-MIMO":
    nt=st.sidebar.select_slider("Base-station antennas",options=[4,8,16,32,64],value=16); users=4; snr_db=st.sidebar.slider("Downlink SNR (dB)",-5.0,20.0,10.0,1.0); trials=500; sr_m=[]; sr_z=[]; corr=[]
    for _ in range(trials):
        H=(rng.normal(size=(users,nt))+1j*rng.normal(size=(users,nt)))/np.sqrt(2); snr=10**(snr_db/10); sr_m.append(np.sum(np.log2(1+downlink_sinr(H,mu_mrt_precoder(H),snr)))); sr_z.append(np.sum(np.log2(1+downlink_sinr(H,mu_zf_precoder(H),snr)))); corr.append(favorable_propagation_metric(H))
    c1,c2,c3=st.columns(3); c1.metric("MRT sum rate",f"{np.mean(sr_m):.2f}"); c2.metric("ZF sum rate",f"{np.mean(sr_z):.2f}"); c3.metric("Mean user correlation",f"{np.mean(corr):.3f}")
    st.caption("As the array grows, independently faded user channels become more nearly orthogonal; ZF can then suppress multiuser interference with less noise/power penalty.")

elif mode == "Hybrid Beamforming":
    rf=st.sidebar.select_slider("RF chains",options=[2,3,4,6,8],value=4); snr_db=st.sidebar.slider("SNR (dB)",-5.0,20.0,10.0,1.0); trials=350; hy=[]; fd=[]
    for _ in range(trials):
        H,_,_=sparse_geometric_mimo_channel(8,32,4,rng); hy.append(hybrid_dft_svd_rate(H,10**(snr_db/10),2,rf)); fd.append(full_digital_svd_rate(H,10**(snr_db/10),2))
    c1,c2,c3=st.columns(3); c1.metric("Hybrid mean rate",f"{np.mean(hy):.2f}"); c2.metric("Full-digital mean rate",f"{np.mean(fd):.2f}"); c3.metric("Rate retained",f"{100*np.mean(np.array(hy)/np.array(fd)):.1f}%")
    st.caption("Sparse 32x8 geometric MIMO with DFT analog beam selection and two digital streams. RF-chain count approximates front-end complexity; this is not a calibrated hybrid-array implementation.")

elif mode == "Limited Feedback Beamforming":
    fb=st.sidebar.slider("CSI feedback bits",1,8,4,1); snr_db=st.sidebar.slider("SNR (dB)",-5.0,20.0,5.0,1.0); n=12000; nt=4
    h=(rng.normal(size=(n,nt))+1j*rng.normal(size=(n,nt)))/np.sqrt(2); snr=10**(snr_db/10); perfect=miso_effective_gain(h,mrt_beamformer(h)); W=random_unit_codebook(nt,2**fb,np.random.default_rng(1000+fb)); w,_=select_codebook_beam(h,W); quant=miso_effective_gain(h,w); single=np.abs(h[:,0])**2
    c1,c2,c3=st.columns(3); c1.metric("Single-Tx rate",f"{np.mean(np.log2(1+snr*single)):.2f}"); c2.metric("Quantized BF rate",f"{np.mean(np.log2(1+snr*quant)):.2f}"); c3.metric("Perfect MRT rate",f"{np.mean(np.log2(1+snr*perfect)):.2f}")
    st.caption("A finite random unit-vector codebook models limited CSI feedback. More feedback bits reduce the loss relative to perfect-CSI maximum-ratio transmission.")

elif mode == "OFDMA Scheduling":
    slots=st.sidebar.slider("Slots",50,400,160,10); beta=st.sidebar.slider("PF averaging beta",0.80,0.995,0.98,0.005); users=4; carriers=48; means=np.array([3.,7.,11.,15.]); z=np.zeros((slots,users,carriers)); z[0]=rng.normal(size=(users,carriers))
    for t in range(1,slots): z[t]=.92*z[t-1]+np.sqrt(1-.92**2)*rng.normal(size=(users,carriers))
    rate=np.log2(1+10**((means[None,:,None]+3*z)/10)); alloc,ach,T=proportional_fair_schedule(rate,beta=beta); thr=ach.mean(axis=0)
    c1,c2=st.columns(2); c1.metric("PF sum rate",f"{thr.sum():.1f}"); c2.metric("Jain fairness",f"{jain_fairness_index(thr):.3f}")
    fig,ax=plt.subplots(); im=ax.imshow(alloc[:min(slots,100)].T,aspect='auto',interpolation='nearest'); ax.set_xlabel('Slot'); ax.set_ylabel('Subcarrier'); ax.set_title('PF user allocation'); fig.colorbar(im,ax=ax,label='User'); st.pyplot(fig)
    st.caption("Each resource is assigned by achievable-rate / historical-throughput metric, exposing multiuser throughput/fairness trade-offs.")

elif mode == "Queued OFDMA":
    slots=st.sidebar.slider("Slots",100,800,300,50); load=st.sidebar.slider("Mean packet arrivals/user/slot",0.1,0.9,0.55,0.05)
    policy=st.sidebar.selectbox("Scheduler",["round_robin","max_rate","pf","delay_pf"],format_func=lambda x:{"round_robin":"Round Robin","max_rate":"Max Rate","pf":"Proportional Fair","delay_pf":"Delay-aware PF"}[x])
    users=4; resources=8; avg_db=np.array([0.,4.,8.,12.]); fading=rng.exponential(size=(slots,users,resources)); cap=1400*np.log2(1+10**(avg_db[None,:,None]/10)*fading); arrivals=rng.poisson(load,size=(slots,users))
    q=simulate_packet_scheduler(cap,arrivals,packet_size_bits=10000,policy=policy,beta=.98,delay_weight=3,target_delay_slots=15)
    c1,c2,c3,c4=st.columns(4); c1.metric("Throughput",f"{q['total_delivered_bits']/slots:.0f} bit/slot"); c2.metric("Fairness",f"{jain_fairness_index(q['delivered_bits']):.3f}"); c3.metric("Mean delay",f"{q['mean_delay_slots']:.1f} slots"); c4.metric("P95 delay",f"{q['p95_delay_slots']:.1f} slots")
    fig,ax=plt.subplots(); ax.plot(np.sum(q['backlog_bits'],axis=1)/1e6); ax.set_xlabel('Slot'); ax.set_ylabel('Queued payload (Mbit)'); ax.set_title(f'{policy} backlog'); ax.grid(True,alpha=.3); st.pyplot(fig)
    st.caption("This is an abstract MAC/link scheduler with FIFO packets and heterogeneous fading rates, not a 3GPP scheduler implementation.")

elif mode == "OLLA Link Adaptation":
    bias=st.sidebar.slider("SNR-estimator bias (dB)",-4.0,4.0,2.5,.25); target=st.sidebar.slider("Target BLER",0.02,0.30,0.10,.01); slots=st.sidebar.slider("Slots",500,5000,2000,250)
    thresholds=np.array([-3,1,5,9,13],float); eff=np.array([.5,1.,2.,3.,4.5]); olla=OuterLoopLinkAdaptation(target_bler=target,nack_step_db=.22)
    state=8.; nack=[]; offsets=[]; good=[]
    for _ in range(slots):
        state=.96*state+.04*8+rng.normal(scale=.7); true=float(np.clip(state,-5,20)); est=true+bias+rng.normal(scale=1.2); idx,se=select_mcs(olla.effective_snr_db(est),thresholds,eff); fail=bool(rng.random()<logistic_bler(true,thresholds[idx],width_db=.9,midpoint_bler=target)); olla.update(not fail); nack.append(fail); offsets.append(olla.offset_db); good.append(0 if fail else se)
    c1,c2,c3=st.columns(3); c1.metric("Observed BLER",f"{np.mean(nack[int(.2*slots):]):.3f}"); c2.metric("Mean goodput",f"{np.mean(good[int(.2*slots):]):.2f} bit/use"); c3.metric("Final SNR backoff",f"{offsets[-1]:.2f} dB")
    fig,ax=plt.subplots(); win=min(200,max(20,slots//10)); ax.plot(np.convolve(np.asarray(nack,float),np.ones(win)/win,mode='valid'),label='rolling BLER'); ax.axhline(target,ls='--',label='target'); ax.set_xlabel('Slot'); ax.set_ylabel('BLER'); ax.set_title('ACK/NACK-driven OLLA'); ax.grid(True,alpha=.3); ax.legend(); st.pyplot(fig)
    st.caption("A positive offset is a conservative SNR backoff. NACKs increase it; ACKs decrease it so the long-run drift is zero near the target BLER.")

elif mode == "OFDM Sensing / ISAC":
    sensing_snr=st.sidebar.slider("Sensing SNR (dB)",-20.0,20.0,0.0,1.0); nsc=64; nsym=64; df=60e3; Ts=1/df; fc=24e9; modem=QAMModem(4); dr=C0/(2*nsc*df); dv=C0/(2*fc*nsym*Ts)
    targets=[(6*dr,-7*dv,1+0j),(15*dr,8*dv,.08*np.exp(.5j))]; bits=rng.integers(0,2,nsym*nsc*2,dtype=np.uint8); X=modem.modulate(bits).reshape(nsym,nsc); clean=simulate_ofdm_sensing_channel(X,df,Ts,targets,fc); nv=np.mean(np.abs(clean)**2)/10**(sensing_snr/10); Y=clean+np.sqrt(nv/2)*(rng.normal(size=clean.shape)+1j*rng.normal(size=clean.shape)); rd,r,v=range_doppler_map(Y,X,df,Ts,fc,window=False); det,_=ca_cfar_2d(rd,training=(4,4),guard=(1,1),pfa=1e-3); peaks=strongest_targets(rd,r,v,2,guard_cells=(2,2))
    c1,c2,c3=st.columns(3); c1.metric("Range-bin spacing",f"{dr:.1f} m"); c2.metric("Velocity-bin spacing",f"{dv:.2f} m/s"); c3.metric("CFAR detections",int(np.count_nonzero(det)))
    fig,ax=plt.subplots(); db=20*np.log10(np.abs(rd)/np.max(np.abs(rd))+1e-12); im=ax.imshow(db,origin='lower',aspect='auto',extent=[r[0],r[-1],v[0],v[-1]],vmin=-40,vmax=0); ii,jj=np.nonzero(det); ax.scatter(r[jj],v[ii],s=24,facecolors='none',edgecolors='white'); ax.set_xlabel('Range (m)'); ax.set_ylabel('Radial velocity (m/s)'); ax.set_title('Communication-Centric OFDM Range-Doppler / CA-CFAR'); fig.colorbar(im,ax=ax,label='dB'); st.pyplot(fig)
    st.caption("The same known QPSK-OFDM grid is divided out before 2-D processing. This is a normalized monostatic sensing model, not a calibrated radar/hardware implementation.")

elif mode == "ISAC Angle":
    nrx=st.sidebar.select_slider("Receive antennas",options=[4,8,16],value=8); sep=st.sidebar.slider("Target angular separation (deg)",10.0,50.0,36.0,2.0); nsc=64; nsym=64; df=30e3; Ts=1/df; fc=24e9; dr=C0/(2*nsc*df); dv=C0/(2*fc*nsym*Ts); X=np.ones((nsym,nsc),complex); a1=-sep/2; a2=sep/2
    Y=simulate_ofdm_sensing_array_channel(X,df,Ts,[(5*dr,3*dv,a1,1+0j),(5*dr,3*dv,a2,.85+.1j)],fc,n_rx=nrx,noise_var=10**(-18/10),rng=rng); cube=range_doppler_array_cube(Y,X,df,Ts,window=False); vel=np.fft.fftshift(np.fft.fftfreq(nsym,d=Ts))*C0/(2*fc); iv=np.argmin(abs(vel-3*dv)); p=bartlett_angle_spectrum(cube[:,iv,5],np.linspace(-60,60,481)); ang=np.linspace(-60,60,481)
    fig,ax=plt.subplots(); ax.plot(ang,10*np.log10(p/np.max(p)+1e-12)); ax.axvline(a1,ls='--'); ax.axvline(a2,ls='--'); ax.set_ylim(-40,1); ax.set_xlabel('Angle (deg)'); ax.set_ylabel('Normalized Bartlett power (dB)'); ax.set_title('OFDM-ISAC receive-array angle spectrum'); ax.grid(True,alpha=.3); st.pyplot(fig)
    st.caption("Two targets occupy the same range-Doppler cell; only the receive-array spatial aperture separates them. This is conventional Bartlett beamforming, not super-resolution MUSIC/ESPRIT.")

elif mode == "ISAC MUSIC":
    nrx=10; snaps=st.sidebar.slider("Spatial snapshots",20,160,80,10); sep=st.sidebar.slider("Angular separation (deg)",6.0,24.0,12.0,1.0); grid=np.linspace(-30,30,1201); a1=-sep/2; a2=sep/2; A=np.column_stack([np.exp(1j*np.pi*np.arange(nrx)*np.sin(np.deg2rad(a1)))/np.sqrt(nrx),np.exp(1j*np.pi*np.arange(nrx)*np.sin(np.deg2rad(a2)))/np.sqrt(nrx)]); S=(rng.normal(size=(2,snaps))+1j*rng.normal(size=(2,snaps)))/np.sqrt(2); Xsp=A@S+.10*(rng.normal(size=(nrx,snaps))+1j*rng.normal(size=(nrx,snaps)))/np.sqrt(2); pb=bartlett_covariance_spectrum(Xsp,grid); pm=music_angle_spectrum(Xsp,2,grid,diagonal_loading=1e-6)
    fig,ax=plt.subplots(); ax.plot(grid,10*np.log10(pb/np.max(pb)+1e-12),label='Bartlett'); ax.plot(grid,10*np.log10(pm/np.max(pm)+1e-12),label='MUSIC'); ax.axvline(a1,ls='--',alpha=.4); ax.axvline(a2,ls='--',alpha=.4); ax.set_ylim(-45,1); ax.set_xlabel('Angle (deg)'); ax.set_ylabel('Normalized spectrum (dB)'); ax.set_title('Multi-snapshot DOA: Bartlett vs MUSIC'); ax.grid(True,alpha=.3); ax.legend(); st.pyplot(fig)
    st.caption("MUSIC assumes two sources and independent enough snapshots to estimate a rank-2 signal subspace. This lab intentionally exposes those assumptions rather than treating MUSIC as a universal angle estimator.")

elif mode == "Cell-Free Network":
    aps_n=st.sidebar.select_slider("Distributed APs",options=[8,12,16,24,32],value=24); users_n=st.sidebar.slider("Users",2,10,6,1); cluster=st.sidebar.slider("APs per user",1,aps_n,min(4,aps_n),1); snr_db=st.sidebar.slider("Network SNR (dB)",-10.0,10.0,-2.0,.5)
    aps=rng.uniform(0,1,(aps_n,2)); users=rng.uniform(0,1,(users_n,2)); beta=large_scale_fading(aps,users,3.0,.05,3.0,rng); H=sample_cell_free_channel(beta,rng); mask=user_centric_mask(beta,cluster); V=clustered_mrt_directions(H,mask); peq=np.full(users_n,1/users_n); pmm,_=max_min_sinr_power_allocation(H,V,10**(snr_db/10)); req=rates_with_power(H,V,peq,10**(snr_db/10)); rmm=rates_with_power(H,V,pmm,10**(snr_db/10))
    c1,c2,c3=st.columns(3); c1.metric("Equal-power mean rate",f"{req.mean():.2f}"); c2.metric("Equal-power min rate",f"{req.min():.2f}"); c3.metric("Max-min min rate",f"{rmm.min():.2f}")
    fig,ax=plt.subplots(); ax.scatter(aps[:,0],aps[:,1],marker='^',label='AP'); ax.scatter(users[:,0],users[:,1],marker='o',label='User');
    for u in range(users_n):
        for a in np.where(mask[u])[0]: ax.plot([users[u,0],aps[a,0]],[users[u,1],aps[a,1]],alpha=.18)
    ax.set_aspect('equal'); ax.set_title('User-centric AP clusters'); ax.legend(); st.pyplot(fig)
    st.caption("Transparent distributed-MRT abstraction: user-centric clustering reduces AP-user coordination links; max-min power control sacrifices average rate to raise the weakest stream. It is not a 3GPP cell-free implementation.")

elif mode == "Multi-user RIS":
    nris=st.sidebar.select_slider("RIS elements",options=[8,12,16,24],value=12); bitsq=st.sidebar.selectbox("Phase bits",[1,2,3],index=1); snr_db=st.sidebar.slider("SNR (dB)",0.0,20.0,10.0,.5); K,Nt=3,4
    D=.22*(rng.normal(size=(K,Nt))+1j*rng.normal(size=(K,Nt)))/np.sqrt(2); G=(rng.normal(size=(nris,Nt))+1j*rng.normal(size=(nris,Nt)))/np.sqrt(2*nris); R=(rng.normal(size=(K,nris))+1j*rng.normal(size=(K,nris)))/np.sqrt(2*nris); init=rng.uniform(-np.pi,np.pi,nris); snr=10**(snr_db/10); raw=ris_mu_sum_rate(D,G,R,init,snr); _,hist=coordinate_optimize_ris(D,G,R,snr,bits=bitsq,iterations=2,initial_phases=init)
    c1,c2,c3=st.columns(3); c1.metric("Random phase sum-rate",f"{raw:.2f}"); c2.metric("Optimized sum-rate",f"{hist[-1]:.2f}"); c3.metric("Relative gain",f"{100*(hist[-1]/raw-1):.1f}%")
    fig,ax=plt.subplots(); ax.plot(range(len(hist)),hist,marker='o'); ax.set_xticks(range(len(hist))); ax.set_xlabel('Coordinate sweep'); ax.set_ylabel('3-user ZF sum rate'); ax.grid(True,alpha=.3); st.pyplot(fig)
    st.caption("Finite-bit coordinate ascent alternates passive RIS element updates with recomputed digital ZF precoding. It is a transparent local-search baseline, not a global optimum claim.")

elif mode == "Predictive ISAC Beam":
    sigma=st.sidebar.slider("Angle uncertainty (deg)",0.2,10.0,2.0,.2); candidates=[8,16,32,64]; best,vals=select_robust_ula_aperture(sigma,candidates,10**(-2/10)); c1,c2=st.columns(2); c1.metric("Robust active aperture",best); c2.metric("Expected rate",f"{vals[best]:.2f} bit/s/Hz")
    fig,ax=plt.subplots(); ax.bar([str(n) for n in candidates],[vals[n] for n in candidates]); ax.set_xlabel('Active ULA elements'); ax.set_ylabel('Expected rate'); ax.set_title('Beam gain vs angular uncertainty'); st.pyplot(fig)
    st.caption("A narrow large-aperture beam has more array gain but is more sensitive to pointing error. This lab chooses aperture from a Gaussian angle-uncertainty model; the offline v1.3 experiment additionally compares reactive, constant-velocity, and constant-acceleration prediction over time.")

elif mode == "RIS Link":
    nris=st.sidebar.select_slider("RIS elements",options=[4,8,16,32,64,128],value=32)
    bitsq=st.sidebar.selectbox("Phase control",[1,2,3,6],index=2,format_func=lambda b:f"{b}-bit")
    snr_db=st.sidebar.slider("SNR (dB)",-5.0,20.0,10.0,.5)
    a=(rng.normal(size=nris)+1j*rng.normal(size=nris))/np.sqrt(2); b=(rng.normal(size=nris)+1j*rng.normal(size=nris))/np.sqrt(2); hd=.25*(rng.normal()+1j*rng.normal())/np.sqrt(2)
    th=optimal_ris_phases(a,b,hd); tq=quantize_phases(th,bitsq); tr=rng.uniform(-np.pi,np.pi,nris); amp=.025; snr=10**(snr_db/10)
    rr=ris_spectral_efficiency(ris_effective_channel(a,b,tr,hd,amp),snr); rq=ris_spectral_efficiency(ris_effective_channel(a,b,tq,hd,amp),snr); ro=ris_spectral_efficiency(ris_effective_channel(a,b,th,hd,amp),snr)
    c1,c2,c3=st.columns(3); c1.metric("Random phases",f"{rr:.2f} bit/s/Hz"); c2.metric(f"{bitsq}-bit RIS",f"{rq:.2f}"); c3.metric("Continuous phase",f"{ro:.2f}")
    st.caption("Unit-modulus SISO RIS baseline with normalized path gain. It illustrates coherent phase alignment and quantization loss; no geometry-specific path-loss or hardware insertion loss is claimed.")

elif mode == "MU-MIMO User Selection":
    candidates=st.sidebar.slider("Candidate users",8,48,24,4); served=st.sidebar.slider("Users served",2,8,4,1); nt=max(8,served); snr_db=st.sidebar.slider("Downlink SNR (dB)",0.0,20.0,10.0,.5)
    H=(rng.normal(size=(candidates,nt))+1j*rng.normal(size=(candidates,nt)))/np.sqrt(2); gains=10**(rng.normal(0,3,candidates)/20); H*=gains[:,None]
    idx_s=semi_orthogonal_user_selection(H,served,.5); idx_n=strongest_norm_user_selection(H,served); idx_r=rng.choice(candidates,served,replace=False)
    labels=[]; rates=[]; corrs=[]
    for name,idx in [('Random',idx_r),('Strongest',idx_n),('SUS',idx_s)]:
        S=H[idx]; W=mu_zf_precoder(S); rates.append(np.sum(np.log2(1+downlink_sinr(S,W,10**(snr_db/10))))); corrs.append(favorable_propagation_metric(S)); labels.append(name)
    c1,c2,c3=st.columns(3); [c.metric(labels[i],f"{rates[i]:.2f} bit/s/Hz",f"corr {corrs[i]:.2f}") for i,c in enumerate([c1,c2,c3])]
    fig,ax=plt.subplots(); ax.bar(labels,rates); ax.set_ylabel('ZF sum rate (bit/s/Hz)'); ax.set_title('Overloaded candidate-user selection'); st.pyplot(fig)
    st.caption("SUS trades pure channel norm for spatial compatibility before ZF precoding; this is a compact flat-fading scheduler, not a standards MAC scheduler.")

elif mode == "Hybrid OMP":
    nrf=st.sidebar.slider("Tx RF chains",2,8,4,1); H,_,_=sparse_geometric_mimo_channel(8,32,5,rng); F=hybrid_omp_precoder(H,2,nrf); ro=precoded_mimo_rate(H,F,10,2); rf=full_digital_svd_rate(H,10,2)
    c1,c2=st.columns(2); c1.metric("OMP hybrid",f"{ro:.2f} bit/s/Hz"); c2.metric("Full digital SVD",f"{rf:.2f}",f"{100*ro/rf:.1f}% retained")
    st.caption("OMP greedily approximates the dominant right-singular subspace using phase-only DFT atoms. The receive side remains fully digital in this interactive baseline.")

elif mode == "ISAC MUSIC + MDL":
    nrx=10; snaps=st.sidebar.slider("Snapshots",20,300,80,10); snr_db=st.sidebar.slider("Per-source SNR (dB)",-10.0,15.0,0.0,.5); true_angles=[-18,2,23]; A=np.column_stack([np.exp(1j*np.pi*np.arange(nrx)*np.sin(np.deg2rad(a)))/np.sqrt(nrx) for a in true_angles]); S=np.sqrt(10**(snr_db/10))*(rng.normal(size=(3,snaps))+1j*rng.normal(size=(3,snaps)))/np.sqrt(2); Xsp=A@S+(rng.normal(size=(nrx,snaps))+1j*rng.normal(size=(nrx,snaps)))/np.sqrt(2); khat,score=estimate_source_count_mdl(Xsp,max_sources=6); grid=np.linspace(-40,40,1201); pm=music_angle_spectrum(Xsp,max(khat,1),grid)
    c1,c2=st.columns(2); c1.metric("True sources",3); c2.metric("MDL estimate",khat)
    fig,ax=plt.subplots(); ax.plot(grid,10*np.log10(pm/pm.max()+1e-12)); [ax.axvline(a,ls='--',alpha=.35) for a in true_angles]; ax.set_xlabel('Angle (deg)'); ax.set_ylabel('MUSIC spectrum (dB)'); ax.set_ylim(-45,1); ax.grid(True,alpha=.3); st.pyplot(fig)
    st.caption("MDL estimates the signal-subspace dimension from covariance eigenvalues before MUSIC. It assumes spatially white noise and adequate snapshots.")

elif mode == "Finite Blocklength":
    snr_db=st.sidebar.slider("SNR (dB)",-5.0,25.0,10.0,.5); eps=st.sidebar.select_slider("Target packet error probability",options=[1e-1,1e-2,1e-3,1e-4,1e-5],value=1e-3); n=st.sidebar.slider("Blocklength (complex uses)",50,5000,300,50)
    snr=10**(snr_db/10); cap=float(complex_awgn_capacity(snr)); rate=float(normal_approximation_rate(snr,n,eps)); c1,c2,c3=st.columns(3); c1.metric("Shannon capacity",f"{cap:.3f} bit/use"); c2.metric("Finite-length approx.",f"{rate:.3f} bit/use"); c3.metric("Rate penalty",f"{cap-rate:.3f} bit/use")
    ns=np.unique(np.logspace(np.log10(50),np.log10(10000),80).astype(int)); rr=normal_approximation_rate(snr,ns,eps); fig,ax=plt.subplots(); ax.semilogx(ns,rr,label='Normal approximation'); ax.axhline(cap,ls='--',label='Shannon'); ax.axvline(n,alpha=.4); ax.set_xlabel('Blocklength'); ax.set_ylabel('bit / complex use'); ax.set_title('Coding delay vs achievable rate'); ax.grid(True,which='both',alpha=.3); ax.legend(); st.pyplot(fig)
    st.caption("Normal approximation only: it quantifies the finite-blocklength penalty but does not predict a specific LDPC/polar implementation exactly.")

elif mode == "Cell-Free Pilot CSI":
    K=st.sidebar.slider("Users",4,16,10,1); M=st.sidebar.slider("APs",8,32,24,4); tau=st.sidebar.slider("Orthogonal pilots",2,K,min(5,K),1); pilot_snr_db=st.sidebar.slider("Pilot SNR (dB)",-5.0,25.0,10.0,.5)
    aps=rng.uniform(0,1,(M,2)); users=rng.uniform(0,1,(K,2)); beta=large_scale_fading(aps,users,3.1,.05,3.0,rng); H=sample_cell_free_channel(beta,rng); mask=user_centric_mask(beta,min(6,M))
    out=[]
    for name,pil in [("Random",random_pilot_assignment(K,tau,rng)),("Contamination-aware",greedy_contamination_aware_assignment(beta,tau))]:
        Hh=lmmse_pilot_channel_estimate(H,beta,pil,10**(pilot_snr_db/10),rng); W=clustered_mrt_precoder(Hh,mask); r=per_user_rates(H,W,1.0); out.append((name,pilot_contamination_cost(beta,pil),normalized_channel_mse(H,Hh),np.quantile(r,.05)))
    c1,c2=st.columns(2); c1.metric("Random NMSE",f"{out[0][2]:.3f}"); c2.metric("Aware NMSE",f"{out[1][2]:.3f}")
    fig,ax=plt.subplots(); ax.bar([x[0] for x in out],[x[3] for x in out]); ax.set_ylabel('5%-tile user rate'); ax.set_title('Pilot reuse and cell-edge performance'); st.pyplot(fig)
    st.caption("Per-AP LMMSE estimation explicitly includes co-pilot users. The greedy assignment minimizes large-scale-fading overlap; it is a transparent heuristic, not globally optimal joint pilot/AP optimization.")

elif mode == "Cell-Free RIS":
    K=4; M=10; N=st.sidebar.select_slider("RIS elements",options=[8,12,16,24],value=16); bitsq=st.sidebar.selectbox("RIS phase bits",[1,2,3],index=1); snr_db=st.sidebar.slider("SNR (dB)",0.0,15.0,7.0,.5)
    D=.34*(rng.normal(size=(K,M))+1j*rng.normal(size=(K,M)))/np.sqrt(2); G=.22*(rng.normal(size=(N,M))+1j*rng.normal(size=(N,M)))/np.sqrt(2); R=.22*(rng.normal(size=(K,N))+1j*rng.normal(size=(K,N)))/np.sqrt(2); init=rng.uniform(-np.pi,np.pi,N); snr=10**(snr_db/10)
    rr=cellfree_ris_rates(D,G,R,init,snr); ts,hs=coordinate_optimize_cellfree_ris(D,G,R,snr,bits=bitsq,iterations=2,objective='sum_rate',initial_phases=init); tm,hm=coordinate_optimize_cellfree_ris(D,G,R,snr,bits=bitsq,iterations=2,objective='min_rate',initial_phases=init); rs=cellfree_ris_rates(D,G,R,ts,snr); rm=cellfree_ris_rates(D,G,R,tm,snr)
    c1,c2,c3=st.columns(3); c1.metric("Random RIS sum-rate",f"{rr.sum():.2f}"); c2.metric("Sum-rate optimized",f"{rs.sum():.2f}"); c3.metric("Min-rate optimized weakest",f"{rm.min():.2f}")
    fig,ax=plt.subplots(); ax.plot(hs,marker='o',label='sum-rate objective'); ax.plot(hm,marker='o',label='min-rate objective'); ax.set_xlabel('Coordinate sweep'); ax.set_ylabel('Objective'); ax.legend(); ax.grid(True,alpha=.3); st.pyplot(fig)
    st.caption("A single finite-resolution RIS modifies the distributed-AP channel; coordinate ascent can target aggregate throughput or the weakest user, exposing a fairness/throughput trade-off.")

elif mode == "Cell-Free AP Energy":
    M=32; K=8; n=st.sidebar.slider("Active APs",4,M,12,4); snr_db=st.sidebar.slider("Network SNR (dB)",-8.0,5.0,-3.0,.5); aps=rng.uniform(0,1,(M,2)); users=rng.uniform(0,1,(K,2)); beta=large_scale_fading(aps,users,3.0,.05,2.5,rng); H=sample_cell_free_channel(beta,rng)
    vals=[]
    for name,active in [("Strongest",strongest_ap_activation(beta,n)),("Coverage-aware",coverage_aware_ap_activation(beta,n))]:
        r=rates_with_active_aps(H,active,10**(snr_db/10)); vals.append((name,r.mean(),np.quantile(r,.05),network_energy_efficiency(r.sum(),n,1,.12,.6)))
    c1,c2=st.columns(2); c1.metric("Strongest EE",f"{vals[0][3]:.2f}"); c2.metric("Coverage-aware 5% rate",f"{vals[1][2]:.2f}")
    fig,ax=plt.subplots(); x=np.arange(2); ax.bar(x-.18,[v[1] for v in vals],.36,label='mean'); ax.bar(x+.18,[v[2] for v in vals],.36,label='5%-tile'); ax.set_xticks(x,[v[0] for v in vals]); ax.legend(); ax.set_ylabel('Rate'); st.pyplot(fig)
    st.caption("A simple circuit-power model creates an energy-efficiency optimum before all APs are active. Coverage-aware activation can protect weak users when the active set is very sparse.")

elif mode == "ISAC Joint Beam":
    N=32; sensing_angle=st.sidebar.slider("Sensing angle (deg)",-60.0,60.0,25.0,1.0); weight=st.sidebar.slider("Communication weight",0.0,1.0,.5,.05); snr_db=st.sidebar.slider("Comm SNR (dB)",-10.0,15.0,0.0,.5); h=np.sqrt(N)*np.exp(-1j*np.pi*np.arange(N)*np.sin(np.deg2rad(-20.0)))/np.sqrt(N); w=joint_isac_beamformer(h,sensing_angle,weight); rate=communication_rate(h,w,10**(snr_db/10)); sg=sensing_gain(w,sensing_angle)
    c1,c2=st.columns(2); c1.metric("Communication rate",f"{rate:.2f} bit/s/Hz"); c2.metric("Sensing beam gain",f"{sg:.3f}")
    ws=np.linspace(0,1,41); rr=[]; gg=[]
    for a in ws:
        ww=joint_isac_beamformer(h,sensing_angle,a); rr.append(communication_rate(h,ww,10**(snr_db/10))); gg.append(sensing_gain(ww,sensing_angle))
    fig,ax=plt.subplots(); ax.plot(gg,rr,marker='.'); ax.scatter([sg],[rate],s=70); ax.set_xlabel('Sensing gain'); ax.set_ylabel('Communication rate'); ax.set_title('Joint ISAC beam Pareto curve'); ax.grid(True,alpha=.3); st.pyplot(fig)
    st.caption("The beam is the principal eigenvector of a weighted communication/sensing quadratic utility. It is a compact Pareto baseline, not a full waveform-constrained ISAC optimizer.")

elif mode == "Cross-layer OLLA/HARQ":
    slots=st.sidebar.slider("Slots",500,5000,2000,250); users=4; use_delay=st.sidebar.checkbox("Delay-aware PF",True); true=np.zeros((slots,users)); means=np.array([-1.,2.,5.,8.]); true[0]=means+rng.normal(size=users)
    for t in range(1,slots): true[t]=means+.94*(true[t-1]-means)+rng.normal(0,.75,users)
    est=true+2+rng.normal(0,1.1,(slots,users)); arr=(rng.random((slots,users))<np.array([.05,.07,.09,.11])[None,:]).astype(int); r=simulate_cross_layer_link(true,est,arr,[-4,0,4,8,12],[.5,1,2,3,4],policy='delay_pf' if use_delay else 'pf',use_olla=True,use_harq=True,max_attempts=4,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Goodput",f"{r['goodput_bits_per_slot']/1000:.2f} kbit/slot"); c2.metric("NACK rate",f"{r['nack_rate']:.3f}"); c3.metric("P95 delay",f"{r['p95_delay_slots']:.1f} slots")
    fig,ax=plt.subplots(); ax.plot(r['backlog_packets'].sum(axis=1)); ax.set_xlabel('Slot'); ax.set_ylabel('Queued packets'); ax.set_title('Event-driven queue/HARQ/OLLA loop'); ax.grid(True,alpha=.3); st.pyplot(fig)
    st.caption("System-level abstraction: biased SNR estimates drive MCS, ACK/NACK adapts OLLA, Chase HARQ accumulates evidence, and PF/delay-PF selects queued users. It is not standards rate matching.")

elif mode == "Cell-Free Fronthaul CSI":
    K=8; M=24; L=st.sidebar.select_slider("APs per user",options=[4,8,12,24],value=8); bits=st.sidebar.select_slider("CSI bits / real component",options=[2,3,4,6,8],value=4); snr_db=st.sidebar.slider("Network SNR (dB)",-5.0,15.0,10.0,.5)
    aps=rng.uniform(0,1,(M,2)); users=rng.uniform(.05,.95,(K,2)); beta=large_scale_fading(aps,users,3.2,.04,2.0,rng); H=sample_cell_free_channel(beta,rng); mask=user_centric_mask(beta,L); Hq=quantize_complex_csi(H,bits); W=clustered_mrt_precoder(Hq,mask); rates=per_user_rates(H,W,10**(snr_db/10)); nm=csi_quantization_nmse(H,Hq); load=fronthaul_csi_bits(mask,bits)
    c1,c2,c3=st.columns(3); c1.metric("CSI NMSE",f"{nm:.3e}"); c2.metric("5%-tile rate",f"{np.quantile(rates,.05):.2f}"); c3.metric("CSI bits/update",f"{load:.0f}")
    st.caption("Uniform scalar CSI quantization plus user-centric clustering gives a transparent CSI-fidelity/fronthaul baseline; it is not a standards feedback codebook.")

elif mode == "Robust Cell-Free RIS":
    K,M,N=3,6,16; nmse=st.sidebar.slider("CSI uncertainty NMSE",0.0,.25,.10,.01); snr_db=st.sidebar.slider("SNR (dB)",0.0,15.0,10.0,.5); D=.22*(rng.normal(size=(K,M))+1j*rng.normal(size=(K,M)))/np.sqrt(2); G=.19*(rng.normal(size=(N,M))+1j*rng.normal(size=(N,M)))/np.sqrt(2); R=.19*(rng.normal(size=(K,N))+1j*rng.normal(size=(K,N)))/np.sqrt(2); snr=10**(snr_db/10)
    Dn=perturb_complex_channel(D,nmse,rng); Gn=perturb_complex_channel(G,nmse,rng); Rn=perturb_complex_channel(R,nmse,rng); naive,_=coordinate_optimize_cellfree_ris(Dn,Gn,Rn,snr,bits=2,iterations=2); samples=[(perturb_complex_channel(Dn,nmse,rng),perturb_complex_channel(Gn,nmse,rng),perturb_complex_channel(Rn,nmse,rng)) for _ in range(6)]; robust,_=sample_average_optimize_cellfree_ris(samples,snr,bits=2,iterations=2)
    rn=cellfree_ris_rates(D,G,R,naive,snr).sum(); rr=cellfree_ris_rates(D,G,R,robust,snr).sum(); c1,c2=st.columns(2); c1.metric("Naive noisy-CSI rate",f"{rn:.2f}"); c2.metric("Sample-average robust rate",f"{rr:.2f}")
    st.caption("Robust coordinate ascent optimizes average utility over a small CSI uncertainty ensemble. It is a sample-average baseline, not a globally optimal robust-RIS solver.")

elif mode == "ISAC Sensing Budget":
    prior=st.sidebar.slider("Prior angle std (deg)",.2,12.0,4.0,.2); snrpe=st.sidebar.slider("Per-element SNR",.02,.5,.18,.01); out=joint_sensing_comm_resource_selection(prior,[8,16,32,64],[0,.01,.02,.04,.06,.1,.15,.2,.3],snrpe,reference_std_deg=2.2); b=out['best']; c1,c2,c3=st.columns(3); c1.metric("Sensing overhead",f"{100*b['sensing_fraction']:.1f}%"); c2.metric("Active elements",b['elements']); c3.metric("Net rate",f"{b['net_rate']:.2f}")
    rows=[r for r in out['rows'] if r['elements']==b['elements']]; fig,ax=plt.subplots(); ax.plot([100*r['sensing_fraction'] for r in rows],[r['net_rate'] for r in rows],marker='o'); ax.set_xlabel('Sensing overhead (%)'); ax.set_ylabel('Net communication rate'); ax.grid(True,alpha=.3); st.pyplot(fig)
    st.caption("More sensing reduces angle uncertainty but consumes payload time. The optimizer jointly chooses sensing fraction and active ULA aperture.")

elif mode == "Short-Packet FBL":
    n=st.sidebar.select_slider("Blocklength",options=[80,120,200,400,800],value=120); bias=st.sidebar.slider("SNR-estimate bias (dB)",0.0,4.0,2.2,.2); N=4000; true=rng.normal(5.0,3.0,N); est=true+bias+rng.normal(0,.9,N); args=(true,est,[-3,1,5,9],[.5,1,2,3]); a=simulate_short_packet_goodput_trace(*args,n,target_bler=1e-2,fbl_aware=False,use_olla=False,seed=int(seed)); b=simulate_short_packet_goodput_trace(*args,n,target_bler=1e-2,fbl_aware=True,use_olla=False,seed=int(seed)); c=simulate_short_packet_goodput_trace(*args,n,target_bler=1e-2,fbl_aware=True,use_olla=True,seed=int(seed)); cols=st.columns(3)
    for col,name,r in zip(cols,['Open-loop','FBL-aware','FBL+OLLA'],[a,b,c]): col.metric(name,f"{r['goodput_bits_per_use']:.2f} bit/use",delta=f"NACK {100*r['nack_rate']:.1f}%")
    st.caption("Successful short blocks deliver nR bits; failed blocks deliver zero. The finite-blocklength normal approximation drives reliability, while OLLA adapts to systematic SNR-estimation bias.")


elif mode == "Cell-Free Fronthaul Energy":
    M,K=24,8; n=st.sidebar.select_slider("Active APs",options=[8,12,16,24],value=16); bits=st.sidebar.select_slider("CSI bits/component",options=[3,4,6],value=6); interval=st.sidebar.select_slider("CSI update interval",options=[1,2,4,8,16,32],value=4); rho=st.sidebar.slider("Channel correlation",.94,.999,.98,.001)
    aps=rng.uniform(0,1,(M,2)); users=rng.uniform(.05,.95,(K,2)); beta=large_scale_fading(aps,users,3.1,.04,2.0,rng); active=strongest_ap_activation(beta,n)
    r=simulate_cellfree_fronthaul_energy(beta,active,bits,interval,rho,10.0,n_slots=250,seed=int(seed),energy_per_fronthaul_bit_j=5e-7)
    c1,c2,c3=st.columns(3); c1.metric("5%-tile rate",f"{r['edge_rate']:.2f}"); c2.metric("Fronthaul power",f"{r['fronthaul_power_w']:.3f} W"); c3.metric("Energy efficiency",f"{r['energy_efficiency']:.2f}")
    st.caption("Periodic quantized CSI updates consume modeled fronthaul energy while stale CSI degrades MRT. The optimum depends on mobility, AP count, quantization and update interval.")

elif mode == "Cell-Free RIS Aging":
    K,M,N=3,6,10; delay=st.sidebar.slider("CSI age (steps)",0,20,5,1); rho=st.sidebar.slider("Per-step correlation",.90,1.0,.98,.005); qbits=st.sidebar.select_slider("CSI bits/component",options=[2,3,4,6,8],value=4)
    D=.20*(rng.normal(size=(K,M))+1j*rng.normal(size=(K,M)))/np.sqrt(2); G=.18*(rng.normal(size=(N,M))+1j*rng.normal(size=(N,M)))/np.sqrt(2); R=.18*(rng.normal(size=(K,N))+1j*rng.normal(size=(K,N)))/np.sqrt(2)
    cur=(age_complex_channel(D,rho,delay,rng),age_complex_channel(G,rho,delay,rng),age_complex_channel(R,rho,delay,rng))
    out=design_and_evaluate_aged_cellfree_ris((D,G,R),cur,10.0,bits=2,iterations=1,correlation=rho,delay_steps=delay,csi_quant_bits=qbits,robust_samples=6,rng=rng)
    names=['Random','Stale CSI','Robust predicted','Ideal current']; vals=[out['random_rates'].sum(),out['naive_rates'].sum(),out['robust_rates'].sum(),out['ideal_rates'].sum()]
    fig,ax=plt.subplots(); ax.bar(names,vals); ax.set_ylabel('Sum-rate'); ax.tick_params(axis='x',rotation=18); ax.set_title('RIS control under CSI aging'); fig.tight_layout(); st.pyplot(fig)
    st.caption("The sample-average robust design is not guaranteed to dominate stale-CSI coordinate ascent; severe aging can flatten or mis-model the utility landscape.")

elif mode == "Predictive Sensing-on-Demand":
    maneuver=st.sidebar.slider("Maneuver process-noise scale",.2,1.8,1.0,.1); q=np.r_[np.full(50,.08),np.linspace(.2,maneuver,60),np.full(50,.12)]; args=(q,.5,[8,16,32,64],[0,.01,.02,.04,.06,.1,.15,.2,.3],.16,2.2); my=simulate_sensing_on_demand(*args); pr=simulate_predictive_sensing_on_demand(*args,lookahead_weight=.9); fx=simulate_sensing_on_demand(q,.5,[8,16,32,64],[0],.16,2.2,fixed_sensing_fraction=.05)
    c1,c2,c3=st.columns(3); c1.metric("Myopic net rate",f"{my['mean_net_rate']:.2f}"); c2.metric("2-step predictive",f"{pr['mean_net_rate']:.2f}"); c3.metric("Fixed 5%",f"{fx['mean_net_rate']:.2f}")
    fig,ax=plt.subplots(); ax.plot([100*x['sensing_fraction'] for x in my['rows']],label='myopic'); ax.plot([100*x['sensing_fraction'] for x in pr['rows']],label='2-step'); ax.set_ylabel('Sensing overhead (%)'); ax.set_xlabel('Slot'); ax.legend(); ax.grid(True,alpha=.3); st.pyplot(fig)
    st.caption("Two-step lookahead assigns more sensing before/through maneuver uncertainty, but remains a small heuristic rather than a globally optimal POMDP/RL controller.")

elif mode == "FBL HARQ Queue":
    n=st.sidebar.select_slider("Blocklength",options=[80,120,240,480],value=120); harq=st.sidebar.checkbox("Chase HARQ",True); olla=st.sidebar.checkbox("OLLA",True); S=2500; U=4; means=np.array([-2.,1.,4.,7.]); true=np.zeros((S,U)); true[0]=means+rng.normal(size=U)
    for t in range(1,S): true[t]=means+.95*(true[t-1]-means)+rng.normal(0,.8,U)
    est=true+2+rng.normal(0,1,(S,U)); arr=(rng.random((S,U))<np.array([.035,.05,.065,.08])[None,:]).astype(int); r=simulate_fbl_harq_queue(true,est,arr,[-4,0,4,8,12],[.5,1,2,3,4],blocklength=n,target_bler=.03,use_harq=harq,use_olla=olla,policy='delay_pf',seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Goodput",f"{r['goodput_bits_per_use']:.3f} bit/use"); c2.metric("NACK",f"{100*r['nack_rate']:.1f}%"); c3.metric("P95 delay",f"{r['p95_delay_slots']:.1f} slots")
    fig,ax=plt.subplots(); ax.plot(r['backlog_packets'].sum(axis=1)); ax.set_xlabel('Slot'); ax.set_ylabel('Queued packets'); ax.grid(True,alpha=.3); st.pyplot(fig)
    st.caption("Finite-blocklength reliability drives packet ACK/NACK; Chase HARQ trades additional channel uses for reliability, while OLLA changes the operating point under biased SNR estimates.")

elif mode == "Async Cell-Free CSI":
    M,K=16,6; budget=st.sidebar.select_slider("AP refreshes/slot",options=[1,2,4,8],value=4); rho_fast=st.sidebar.slider("Fastest AP correlation",.90,.99,.94,.005)
    aps=rng.uniform(0,1,(M,2)); users=rng.uniform(0,1,(K,2)); beta=large_scale_fading(aps,users,3.1,.04,2.0,rng); mask=user_centric_mask(beta,5); rho=np.linspace(rho_fast,.997,M)
    rr=simulate_async_cellfree_csi(beta,mask,rho,8.0,updates_per_slot=budget,n_slots=120,policy='round_robin',seed=int(seed)); bu=simulate_async_cellfree_csi(beta,mask,rho,8.0,updates_per_slot=budget,n_slots=120,policy='bounded_uncertainty',seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("RR edge rate",f"{rr['edge_rate']:.2f}"); c2.metric("Bounded-uncertainty edge",f"{bu['edge_rate']:.2f}"); c3.metric("CSI NMSE change",f"{rr['mean_csi_nmse']:.3f} → {bu['mean_csi_nmse']:.3f}")
    st.caption("A pure global-MSE scheduler can starve low-power APs; the bounded-uncertainty policy imposes a maximum CSI age before using uncertainty priority.")

elif mode == "Predictive CSI Compression":
    rho=st.sidebar.slider("Channel correlation",.70,.999,.98,.001); bits=st.sidebar.select_slider("Bits/component",options=[2,3,4,6],value=3); beta=np.exp(rng.normal(0,1,(6,16))); o=predictive_csi_quantization_trace(beta,rho,bits,n_slots=220,seed=int(seed))
    gain=10*np.log10(o['mean_absolute_nmse']/max(o['mean_predictive_nmse'],1e-15)); c1,c2,c3=st.columns(3); c1.metric("Absolute CSI NMSE",f"{o['mean_absolute_nmse']:.3e}"); c2.metric("Innovation NMSE",f"{o['mean_predictive_nmse']:.3e}"); c3.metric("Prediction gain",f"{gain:.1f} dB")
    st.caption("Both schemes use the same scalar bit depth. Predictive coding quantizes the Gauss-Markov innovation rather than the full channel; entropy coding and standards feedback framing are not modeled.")

elif mode == "Two-timescale RIS":
    interval=st.sidebar.select_slider("RIS update interval",options=[1,2,4,8],value=4); phase_std=st.sidebar.slider("RIS phase-noise std (deg)",0.0,10.0,3.0,.5); K,M,N=2,4,4; seq=[]; D=.25*(rng.normal(size=(K,M))+1j*rng.normal(size=(K,M)))/np.sqrt(2); G=.2*(rng.normal(size=(N,M))+1j*rng.normal(size=(N,M)))/np.sqrt(2); R=.25*(rng.normal(size=(K,N))+1j*rng.normal(size=(K,N)))/np.sqrt(2)
    for _ in range(20):
        D=age_complex_channel(D,.985,1,rng); G=age_complex_channel(G,.985,1,rng); R=age_complex_channel(R,.985,1,rng); seq.append((D.copy(),G.copy(),R.copy()))
    o=simulate_two_timescale_cellfree_ris(seq,10.0,bits=1,ris_update_interval=interval,history_window=5,phase_noise_std_deg=phase_std,seed=int(seed)); c1,c2,c3=st.columns(3); c1.metric("Fast RIS rate",f"{o['fast']['mean_sum_rate']:.2f}"); c2.metric("Two-timescale rate",f"{o['two_timescale']['mean_sum_rate']:.2f}"); c3.metric("Control bits/slot",f"{o['ris_control_bits_per_slot_two_timescale']:.2f}")
    st.caption("AP precoding is updated from the current effective channel every slot; only RIS phase control is slowed. This isolates passive-control overhead rather than claiming full two-timescale CSI reduction.")

elif mode == "FBL IR-HARQ":
    snr=st.sidebar.slider("Mean SNR (dB)",-4.0,8.0,0.0,.5); rng2=np.random.default_rng(int(seed)); S=700; true=rng2.normal(snr,1,(S,1)); est=true+rng2.normal(0,.3,(S,1)); arr=(rng2.random((S,1))<.22).astype(int)
    ch=simulate_fbl_ir_harq_queue(true,est,arr,[-100],[1.5],round_blocklength=80,mode='chase',use_olla=False,policy='max_rate',seed=int(seed)); ir=simulate_fbl_ir_harq_queue(true,est,arr,[-100],[1.5],round_blocklength=80,mode='ir',use_olla=False,policy='max_rate',seed=int(seed)); c1,c2,c3=st.columns(3); c1.metric("Chase goodput",f"{ch['goodput_bits_per_channel_use']:.3f}"); c2.metric("IR goodput",f"{ir['goodput_bits_per_channel_use']:.3f}"); c3.metric("IR mean rounds",f"{ir['mean_rounds_per_completed']:.2f}")
    st.caption("IR adds new redundancy and increases total effective blocklength; Chase repeats a codeword and combines SNR. The error model is a finite-blocklength normal approximation, not a standards HARQ decoder.")

elif mode == "Queue-aware ISAC":
    load=st.sidebar.slider("Arrival load/user (bit/slot)",30,120,90,5); S,U=100,2; proc=np.r_[np.full(25,.08),np.linspace(.08,1.0,20),np.full(25,1.0),np.linspace(1.0,.1,15),np.full(15,.1)]; arrivals=np.maximum(0,rng.poisson(load,(S,U))).astype(float); rates=np.clip(rng.normal(180,25,(S,U)),90,260)
    tr=simulate_queue_aware_isac_control(proc,arrivals,rates,.5,[8,16,32],[0,.03,.08,.15],.16,sensing_value_weight=1500,queue_aware=False); qa=simulate_queue_aware_isac_control(proc,arrivals,rates,.5,[8,16,32],[0,.03,.08,.15],.16,sensing_value_weight=1500,queue_aware=True); c1,c2,c3=st.columns(3); c1.metric("Tracking-only sensing",f"{100*tr['mean_sensing_fraction']:.1f}%"); c2.metric("Queue-aware sensing",f"{100*qa['mean_sensing_fraction']:.1f}%"); c3.metric("Backlog",f"{tr['final_backlog_bits']:.0f} → {qa['final_backlog_bits']:.0f} bit")
    st.caption("Queue pressure can justify sacrificing sensing accuracy for payload service. This is a myopic value-of-information baseline, not an optimal cross-layer POMDP.")

elif mode == "Joint CSI Budget":
    M,K=12,5; budget=st.sidebar.select_slider("Fronthaul budget (bit/slot)",options=[48,72,96,128,160],value=96); rho=st.sidebar.slider("Channel correlation",.92,.999,.98,.001); beta=np.exp(rng.normal(0,1,(K,M))); mask=user_centric_mask(beta,5)
    vals=[]
    for pol in ["round_robin","uncertainty_fixed","joint"]:
        o=simulate_joint_predictive_csi_control(beta,mask,rho,8.0,budget,n_slots=100,policy=pol,fixed_bits=5,seed=int(seed)); vals.append((pol,o['mean_csi_nmse'],o['edge_rate'],o['mean_fronthaul_bits_per_slot']))
    c1,c2,c3=st.columns(3); [c.metric(v[0],f"NMSE {v[1]:.3f}",f"edge {v[2]:.2f}") for c,v in zip([c1,c2,c3],vals)]
    fig,ax=plt.subplots(); ax.bar([v[0] for v in vals],[v[1] for v in vals]); ax.set_ylabel('Mean CSI NMSE'); ax.tick_params(axis='x',rotation=15); fig.tight_layout(); st.pyplot(fig)
    st.caption("The joint policy decides both which AP innovations to refresh and how many scalar bits to spend under one hard fronthaul budget.")

elif mode == "Deadline HARQ":
    load=st.sidebar.slider("Arrival probability/user/slot",.04,.24,.16,.01); S,U=450,4; means=np.array([-1.,1.,3.,5.]); true=rng.normal(means,2,(S,U)); est=true+1.5+rng.normal(0,1,(S,U)); arr=(rng.random((S,U))<load).astype(int); vals=[]
    for pol in ['pf','edf','risk']:
        o=simulate_deadline_fbl_harq(true,est,arr,[-5,-1,3,7],[.5,1,1.8,2.6],deadline_slots=6,round_blocklength=80,mode='ir',policy=pol,seed=int(seed)); vals.append((pol,o['goodput_bits_per_channel_use'],o['deadline_miss_rate'],o['p95_delay_slots']))
    cols=st.columns(3)
    for c,v in zip(cols,vals): c.metric(v[0],f"{v[1]:.2f} bit/use",f"miss {100*v[2]:.1f}%")
    st.caption("EDF prioritizes hard timeliness; the risk score mixes deadline urgency, estimated FBL success probability and PF-style service balance.")

elif mode == "Age of Information":
    rate=st.sidebar.slider("Status rate (bit/use)",.4,1.5,1.0,.1); S,U=700,5; means=np.array([-2.,0.,2.,4.,6.]); true=rng.normal(means,3,(S,U)); est=true+rng.normal(0,1,(S,U)); vals=[]
    for pol in ['max_age','max_snr','age_reliability']:
        o=simulate_status_update_aoi(true,est,blocklength=90,rate=rate,policy=pol,retransmission='chase',seed=int(seed)); vals.append((pol,o['mean_aoi'],o['p95_aoi']))
    fig,ax=plt.subplots(); ax.bar([v[0] for v in vals],[v[1] for v in vals]); ax.set_ylabel('Mean AoI (slots)'); ax.tick_params(axis='x',rotation=15); fig.tight_layout(); st.pyplot(fig)
    st.caption("Max-SNR can maximize successful transmissions while starving weak users and producing extremely stale information; AoI explicitly measures freshness.")

elif mode == "Event-triggered RIS":
    threshold=st.sidebar.slider("Rate-drop trigger",.01,.25,.08,.01); K,M,N=2,3,4; D=.25*(rng.normal(size=(K,M))+1j*rng.normal(size=(K,M)))/np.sqrt(2); G=.25*(rng.normal(size=(N,M))+1j*rng.normal(size=(N,M)))/np.sqrt(2); R=.25*(rng.normal(size=(K,N))+1j*rng.normal(size=(K,N)))/np.sqrt(2); seq=[]
    for t in range(36):
        rho=.995 if t<12 or t>=24 else .90
        def step(x):
            z=(rng.normal(size=x.shape)+1j*rng.normal(size=x.shape))/np.sqrt(2); return rho*x+np.sqrt(1-rho*rho)*np.sqrt(np.mean(np.abs(x)**2))*z
        D=step(D); G=step(G); R=step(R); seq.append((D.copy(),G.copy(),R.copy()))
    o=simulate_event_triggered_cellfree_ris(seq,10,bits=2,rate_drop_threshold=threshold,min_interval=2,max_interval=12,seed=int(seed)); c1,c2=st.columns(2); c1.metric("Mean sum-rate",f"{o['mean_sum_rate']:.2f}"); c2.metric("Control overhead",f"{o['control_bits_per_slot']:.2f} bit/slot",f"{o['n_updates']} updates")
    st.caption("The RIS refreshes only after observed held-phase utility degrades or a maximum age is reached; fast-channel periods naturally trigger denser control.")

elif mode == "Budgeted ISAC":
    budget=st.sidebar.slider("Long-term sensing budget",.01,.15,.05,.01); proc=np.r_[np.full(30,.05),np.linspace(.1,1.0,40),np.full(30,.8),np.full(30,.08)]; o=simulate_budget_constrained_sensing(proc,.5,[8,16,32,64],[0,.02,.05,.08,.12,.16],.08,budget,information_weight=3.0,dual_step=.8); c1,c2,c3=st.columns(3); c1.metric("Actual sensing",f"{100*o['mean_sensing_fraction']:.1f}%"); c2.metric("Angle std",f"{o['mean_posterior_std_deg']:.2f}°"); c3.metric("Payload rate",f"{o['mean_payload_rate']:.2f}")
    fig,ax=plt.subplots(); ax.plot(proc,label='process uncertainty'); ax.plot(4*o['sensing_fraction'],label='4× sensing fraction'); ax.legend(); ax.grid(True,alpha=.3); st.pyplot(fig)
    st.caption("A cumulative token budget forces long-run sensing use below the configured ceiling while concentrating sensing in high-uncertainty intervals.")

elif mode == "IRSA Random Access":
    G=st.sidebar.slider("Offered load G",.05,1.20,.65,.05)
    vals=[]
    for name,dist,sic in [("ALOHA",{1:1.0},False),("Rep-3",{3:1.0},False),("IRSA",{2:.50,3:.28,8:.22},True)]:
        o=simulate_irsa(100,G,220,dist,sic,seed=int(seed)); vals.append((name,o))
    cols=st.columns(3)
    for c,(name,o) in zip(cols,vals): c.metric(name,f"{o['throughput_packets_per_slot']:.3f} pkt/slot",f"PLR {100*o['packet_loss_rate']:.1f}%")
    st.caption("IRSA iteratively peels singleton packets and their replicas from a frame graph. The model is collision/SIC-only: capture, activity detection and residual cancellation are outside scope.")

elif mode == "AirComp Aggregation":
    snr=st.sidebar.slider("Aggregation SNR (dB)",0.0,30.0,12.0,1.0); th=st.sidebar.slider("Inversion threshold |h|",.08,.9,.22,.02)
    o=simulate_aircomp_mean_aggregation(20,24,snr,350,th,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Orthogonal median MSE",f"{o['orthogonal_median_mse']:.3e}","20 channel uses"); c2.metric("Full inversion median MSE",f"{o['full_inversion_median_mse']:.3e}","1 channel use"); c3.metric("Truncated AirComp median MSE",f"{o['truncated_inversion_median_mse']:.3e}",f"active {100*o['mean_active_fraction']:.1f}%")
    st.caption("Analog superposition computes a mean in one shared channel use. Full inversion is sensitive to the weakest fade; truncation trades noise robustness against device dropout.")

elif mode == "Capture IRSA":
    G=st.sidebar.slider("Offered load G",.1,1.2,.75,.05); spread=st.sidebar.slider("Received-power spread (dB)",0.0,12.0,8.0,.5)
    base=simulate_capture_irsa(G,100,120,power_spread_db=0,sinr_threshold_db=3,seed=int(seed)); cap=simulate_capture_irsa(G,100,120,power_spread_db=spread,sinr_threshold_db=3,seed=int(seed))
    c1,c2=st.columns(2); c1.metric("Singleton/IRSA baseline",f"{base['throughput']:.3f} pkt/slot",f"PLR {100*base['packet_loss_rate']:.1f}%"); c2.metric("Capture-aware SIC",f"{cap['throughput']:.3f} pkt/slot",f"PLR {100*cap['packet_loss_rate']:.1f}%")
    st.caption("Collided replicas are decoded only when the strongest unresolved packet clears a SINR threshold. With no received-power structure, capture gives little or no gain; power separation creates additional SIC opportunities.")

elif mode == "AirComp Federated Learning":
    snr=st.sidebar.slider("Aggregation SNR (dB)",0.0,25.0,10.0,1.0); th=st.sidebar.slider("Truncation threshold |h|",.1,1.0,.35,.05)
    vals=[]
    for m in ['ideal','orthogonal','full_inversion','truncated']:
        vals.append((m,simulate_federated_aircomp(rounds=70,mode=m,snr_db=snr,inversion_threshold=th,seed=int(seed))))
    fig,ax=plt.subplots();
    for m,o in vals: ax.semilogy(o['loss_history'],label=m.replace('_',' '))
    ax.set_xlabel('Federated round'); ax.set_ylabel('Global loss'); ax.grid(True,alpha=.3); ax.legend(); st.pyplot(fig)
    c1,c2,c3=st.columns(3); c1.metric("Orthogonal uses",vals[1][1]['channel_uses']); c2.metric("AirComp uses",vals[2][1]['channel_uses']); c3.metric("Truncated active clients",f"{100*vals[3][1]['mean_active_fraction']:.1f}%")
    st.caption("A convex federated linear-regression toy problem couples analog aggregation error to learning convergence. It is an educational FL baseline, not a neural-network benchmark.")

elif mode == "Cell-Free AirComp":
    naps=st.sidebar.select_slider("Distributed APs",options=[1,2,4,8,16],value=8); snr=st.sidebar.slider("Aggregation SNR (dB)",0.0,25.0,12.0,1.0)
    o=simulate_cellfree_aircomp(n_aps=naps,n_devices=12,vector_dim=20,snr_db=snr,n_trials=140,seed=int(seed),n_random=120)
    c1,c2,c3=st.columns(3); c1.metric("Best single-AP MSE",f"{o['single_ap_median_mse']:.3e}"); c2.metric("Cell-Free MSE",f"{o['cellfree_median_mse']:.3e}"); c3.metric("Weakest-gain lift",f"{o['cellfree_mean_weakest_gain']/max(o['single_ap_mean_weakest_gain'],1e-12):.2f}×")
    st.caption("A centralized unit-norm combiner is selected from a transparent candidate set to improve the weakest device projection before analog aggregation. Perfect CSI and coherent distributed reception are assumed.")

elif mode == "RIS AirComp":
    K,N=10,20; bitsq=st.sidebar.selectbox("RIS phase bits",[1,2,3],index=1); snr=st.sidebar.slider("Aggregation SNR (dB)",0.0,20.0,8.0,1.0)
    rr=np.random.default_rng(int(seed)); hd=.12*(rr.normal(size=K)+1j*rr.normal(size=K))/np.sqrt(2); Fd=(rr.normal(size=(K,N))+1j*rr.normal(size=(K,N)))/np.sqrt(2*N); gb=(rr.normal(size=N)+1j*rr.normal(size=N))/np.sqrt(2*N)
    pr=np.exp(1j*2*np.pi*rr.random(N)); ps=optimize_ris_aircomp(hd,Fd,gb,bitsq,2,'sumgain')[0]; pm=optimize_ris_aircomp(hd,Fd,gb,bitsq,2,'maxmin')[0]
    vals=[]
    for name,pv in [('random',pr),('sum gain',ps),('max-min',pm)]:
        hh=effective_ris_aircomp_channel(hd,Fd,gb,pv); mm=aircomp_noise_mse_from_channel(hh,snr,20,180,seed=int(seed)+3); vals.append((name,float(np.min(np.abs(hh))),mm['median_mse']))
    fig,ax=plt.subplots(); ax.bar([v[0] for v in vals],[v[1] for v in vals]); ax.set_ylabel('Weakest device |h|'); ax.set_title('RIS Objective for AirComp'); st.pyplot(fig)
    st.caption("AirComp is bottlenecked by the weakest effective device channel. Maximizing total channel power can therefore be inferior to a direct max-min RIS objective.")

elif mode == "Task-Oriented Communication":
    snr=st.sidebar.slider("SNR (dB)",-5.0,20.0,10.0,1.0); dim=st.sidebar.select_slider("Source dimension",options=[4,8,16,32],value=16)
    o=simulate_task_oriented_classification(dim=dim,n_samples=10000,separation=2.0,snr_db=snr,seed=int(seed)); c1,c2,c3=st.columns(3); c1.metric("Raw-feature accuracy",f"{100*o['raw_accuracy']:.2f}%",f"{o['raw_channel_uses']} uses"); c2.metric("Task-statistic accuracy",f"{100*o['task_accuracy']:.2f}%",f"{o['task_channel_uses']} use"); c3.metric("Task/source compression",f"{o['compression_ratio']:.0f}×")
    st.write({'raw reconstruction MSE':o['raw_reconstruction_mse'],'task-statistic reconstruction MSE':o['task_reconstruction_mse']})
    st.caption("Toy Gaussian binary classification: the transmitted scalar is a known sufficient statistic for the task. It illustrates task utility versus source fidelity; it is not a learned semantic codec.")


elif mode == "Non-IID FL Client Selection":
    disp=st.sidebar.slider("Long-term group channel disparity (dB)",0.0,14.0,8.0,1.0)
    vals=[]
    for pol in ['random','channel','age_channel','gradient_channel']:
        o=simulate_selection_biased_fl(pol,rounds=100,n_select=4,channel_disparity_db=disp,age_weight=2.0,seed=int(seed)); vals.append((pol,o))
    fig,ax=plt.subplots(); ax.bar([v[0] for v in vals],[v[1]['final_global_loss'] for v in vals]); ax.set_ylabel('Final global objective'); ax.set_title('Non-IID FL under Communication-Driven Participation'); ax.tick_params(axis='x',rotation=15); fig.tight_layout(); st.pyplot(fig)
    st.write({p:{'participation Jain':round(o['participation_jain'],3),'strong-group share':round(o['plus_selection_fraction'],3),'weakest selected gain':round(o['mean_selected_weakest_gain'],3)} for p,o in vals})
    st.caption("Two client groups have different local optima and correlated long-term channel quality. Strong-link selection can improve instantaneous AirComp quality while biasing the global learning objective; participation-age weighting partially restores fairness.")

elif mode == "Random-Access FL":
    slots=st.sidebar.slider("Random-access frame slots",6,28,18,2); ncl=st.sidebar.slider("Clients",10,30,20,2)
    a=simulate_random_access_federated('aloha',n_clients=ncl,frame_slots=slots,rounds=35,participation_prob=.8,heterogeneity=1.5,seed=int(seed))
    r=simulate_random_access_federated('irsa',n_clients=ncl,frame_slots=slots,rounds=35,participation_prob=.8,heterogeneity=1.5,seed=int(seed))
    c1,c2=st.columns(2); c1.metric('ALOHA decoded clients',f"{100*a['mean_decoded_fraction']:.1f}%",f"loss {a['final_loss']:.3g}"); c2.metric('IRSA decoded clients',f"{100*r['mean_decoded_fraction']:.1f}%",f"loss {r['final_loss']:.3g}")
    st.caption("Only successfully decoded client updates enter the federated round. The chosen IRSA degree distribution has a load threshold: under severe overload, repetition can make access collapse worse before iterative SIC becomes beneficial in a lighter regime.")

elif mode == "Robust RIS AirComp":
    err=st.sidebar.slider("Relative CSI uncertainty",0.0,.6,.25,.05); K,N=8,12; rr=np.random.default_rng(int(seed))
    hd=(rr.normal(size=K)+1j*rr.normal(size=K))/np.sqrt(2)*.2; Fd=(rr.normal(size=(K,N))+1j*rr.normal(size=(K,N)))/np.sqrt(2*N); gb=(rr.normal(size=N)+1j*rr.normal(size=N))/np.sqrt(2*N)
    hdh=hd+(rr.normal(size=K)+1j*rr.normal(size=K))/np.sqrt(2)*err*.2; Fh=Fd+(rr.normal(size=(K,N))+1j*rr.normal(size=(K,N)))/np.sqrt(2)*err/np.sqrt(N); gh=gb+(rr.normal(size=N)+1j*rr.normal(size=N))/np.sqrt(2)*err/np.sqrt(N)
    pn=optimize_ris_aircomp(hdh,Fh,gh,2,3,'maxmin')[0]; pr=optimize_robust_ris_aircomp(hdh,Fh,gh,err,2,3,48,.25,int(seed)+1)[0]
    gn=float(np.min(np.abs(effective_ris_aircomp_channel(hd,Fd,gb,pn)))); gr=float(np.min(np.abs(effective_ris_aircomp_channel(hd,Fd,gb,pr))))
    c1,c2=st.columns(2); c1.metric('Naive true weakest gain',f'{gn:.3f}'); c2.metric('Uncertainty-sampled gain',f'{gr:.3f}')
    st.caption("Robust sample-average coordinate ascent optimizes a lower quantile of the weakest effective device channel. It is a heuristic: moderate uncertainty can benefit, while severe/model-mismatched uncertainty can still make it worse than the point-estimate design.")

elif mode == "Cell-Free AirComp CSI Risk":
    e=st.sidebar.slider("Worst AP CSI error std",.05,.8,.5,.05); o=simulate_lcb_cellfree_aircomp(n_aps=8,n_devices=10,snr_db=15,max_csi_error=e,n_trials=100,z=.5,seed=int(seed))
    c1,c2=st.columns(2); c1.metric('Naive p90 aggregation MSE',f"{o['naive_p90_mse']:.3e}"); c2.metric('LCB p90 aggregation MSE',f"{o['lcb_p90_mse']:.3e}")
    st.caption("APs have heterogeneous CSI uncertainty. A lower-confidence-bound combiner penalizes uncertain projected links; it is designed for tail risk and can sacrifice median performance when uncertainty is small.")

elif mode == "Multi-Task Semantic":
    angle=st.sidebar.slider("Task-direction separation (deg)",0,90,60,5); snr=st.sidebar.slider("Semantic-link SNR (dB)",-5.0,20.0,10.0,1.0); o=simulate_multitask_task_oriented(dim=16,n_samples=12000,task_angle_deg=angle,snr_db=snr,seed=int(seed))
    names=['Raw 16-D','Task-specific 2-D','Shared rank-1','Shared rank-2']; acc=[o['raw_mean_accuracy'],o['task_specific_mean_accuracy'],o['shared_rank1_mean_accuracy'],o['shared_rank2_mean_accuracy']]; uses=[16,2,1,2]
    fig,ax=plt.subplots(); ax.scatter(uses,acc,s=80); [ax.annotate(n,(u,a),xytext=(5,5),textcoords='offset points') for n,u,a in zip(names,uses,acc)]; ax.set(xscale='log',xlabel='Channel uses for both tasks',ylabel='Mean task accuracy',title='Multi-Task Semantic Sharing'); ax.grid(alpha=.3); fig.tight_layout(); st.pyplot(fig)
    st.caption("Two classification tasks depend on different linear source directions. One shared scalar is efficient when tasks align but becomes a bottleneck as task-relevant subspaces separate; a rank-two shared representation preserves both tasks with two channel uses.")

elif mode == "Budgeted Gradient FL":
    budget=st.sidebar.select_slider("Gradient-coordinate budget / round",options=[16,24,32,48,64],value=32); nsel=st.sidebar.slider("Selected clients",1,12,4,1); alloc=st.sidebar.selectbox("Compression allocation",["equal","residual"]); ef=st.sidebar.checkbox("Error feedback",True)
    o=simulate_budgeted_compressed_fl(n_clients=12,n_select=nsel,coordinate_budget=budget,dim=32,rounds=100,heterogeneity=1.2,learning_rate=.08,error_feedback=ef,clustered=True,allocation=alloc,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Final objective",f"{o['final_loss']:.3f}"); c2.metric("Parameter error",f"{o['parameter_error']:.3f}"); c3.metric("Coordinates / round",o['coordinates_per_round'])
    st.caption("A fixed uplink coordinate budget must be split across participating non-IID clients. Selecting more clients improves statistical coverage but forces stronger per-client sparsification; error feedback recycles dropped coordinates across rounds.")

elif mode == "AirComp Hardware":
    bits=st.sidebar.select_slider("ADC bits / I-Q",options=[2,3,4,6,8],value=4); sat=st.sidebar.slider("PA saturation magnitude",.6,3.5,1.4,.1); agc=st.sidebar.checkbox("Receiver AGC",True)
    o=simulate_aircomp_hardware(n_devices=16,vector_dim=64,snr_db=24,pa_saturation=sat,adc_bits=bits,agc=agc,n_trials=250,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Median aggregation MSE",f"{o['median_mse']:.3e}"); c2.metric("PA clip fraction",f"{100*o['mean_pa_clip_fraction']:.2f}%"); c3.metric("ADC overload",f"{100*o['mean_adc_overload_fraction']:.2f}%")
    st.caption("Educational analog-aggregation hardware stress test: channel inversion is followed by transmit magnitude clipping and a finite-resolution I/Q ADC. AGC can recover converter dynamic range but cannot undo PA clipping.")

elif mode == "Layered Semantic":
    angle=st.sidebar.slider("Task-direction separation (deg)",0,90,60,5); th=st.sidebar.slider("Enhancement confidence threshold",0.0,1.2,.5,.05); snr=st.sidebar.slider("Semantic-link SNR (dB)",-5.0,20.0,10.0,1.0)
    o=simulate_layered_multitask_semantic(dim=16,n_samples=12000,task_angle_deg=angle,snr_db=snr,confidence_threshold=th,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Base layer",f"{100*o['base_accuracy']:.1f}%","1 use"); c2.metric("Adaptive",f"{100*o['adaptive_accuracy']:.1f}%",f"{o['adaptive_mean_uses']:.2f} uses"); c3.metric("Two layers",f"{100*o['full_accuracy']:.1f}%","2 uses")
    st.caption("A common semantic projection is transmitted first; the orthogonal enhancement layer is requested only when the base-layer task margins are too small. This is an analytic progressive-representation baseline, not a neural semantic codec.")

elif mode == "Importance Random-Access FL":
    slots=st.sidebar.slider("Shared slots / FL round",10,28,18,2); mode2=st.sidebar.selectbox("Repetition policy",["uniform","importance"]); o=simulate_importance_aware_random_access_fl(n_clients=16,frame_slots=slots,rounds=30,participation_prob=.9,heterogeneity=1.2,mode=mode2,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Decoded clients",f"{100*o['mean_decoded_fraction']:.1f}%"); c2.metric("Decoded gradient mass",f"{100*o['mean_decoded_gradient_mass']:.1f}%"); c3.metric("Mean repetition",f"{o['mean_repetition_degree']:.2f}")
    st.caption("Importance-aware repetition assigns degrees 2/3/4 using gradient-norm ranks. It can protect high-utility updates at moderate load, but extra collision structure cannot rescue a severely overloaded random-access frame.")

elif mode == "Two-timescale RIS FL":
    rho=st.sidebar.select_slider("Channel correlation",options=[.95,.98,.995],value=.98); interval=st.sidebar.select_slider("RIS update interval (rounds)",options=[1,2,4,8,16,32,70],value=4); o=simulate_two_timescale_ris_aircomp_fl(n_clients=8,n_ris=10,rounds=70,update_interval=interval,rho=rho,bits=2,snr_db=12,learning_rate=.08,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Final learning loss",f"{o['final_loss']:.3f}"); c2.metric("Mean weakest gain",f"{o['mean_weakest_gain']:.3f}"); c3.metric("RIS control",f"{o['control_bits_per_round']:.2f} bit/round")
    st.caption("The finite-bit RIS is updated on a slower timescale than FL/AirComp channel inversion. Slow mobility permits large control savings; faster fading shrinks the acceptable RIS update interval.")

elif mode == "Async Federated Learning":
    dm=st.sidebar.slider("Mean gradient staleness",0.0,8.0,4.0,.5); strat=st.sidebar.selectbox("Stale-update strategy",["naive","decay","quadratic_corrected"])
    o=simulate_asynchronous_federated(strategy=strat,rounds=120,max_delay=12,delay_mean=dm,heterogeneity=1.2,learning_rate=.09,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Final loss",f"{o['final_loss']:.4f}"); c2.metric("Mean delay",f"{o['mean_delay']:.2f}"); c3.metric("Gradient cosine",f"{o['mean_stale_current_cosine']:.3f}")
    fig,ax=plt.subplots(); ax.plot(o['loss_history']); ax.set(xlabel='Server update',ylabel='Global loss',title='Asynchronous Federated Learning'); ax.grid(alpha=.3); st.pyplot(fig)
    st.caption("Clients compute updates on delayed model snapshots. Decay downweights stale gradients; the quadratic correction is exact only for this ridge-regression baseline and is not a general neural-network correction.")

elif mode == "Byzantine-Robust FL":
    frac=st.sidebar.slider("Byzantine client fraction",0.0,.40,.20,.02); method=st.sidebar.selectbox("Aggregator",["mean","median","trimmed_mean"])
    o=simulate_byzantine_federated(method=method,byzantine_fraction=frac,attack_scale=6,rounds=80,heterogeneity=.9,seed=int(seed))
    c1,c2=st.columns(2); c1.metric("Final loss",f"{o['final_loss']:.3e}"); c2.metric("Byzantine clients",o['byzantine_clients'])
    fig,ax=plt.subplots(); ax.plot(o['loss_history']); ax.set_yscale('log'); ax.set(xlabel='FL round',ylabel='Global loss',title='Robust Aggregation under Sign-Flip/Scaling Attack'); st.pyplot(fig)
    st.caption("Coordinate median and trimmed mean resist moderate outlier fractions but have breakdown limits. This is a transparent attack/aggregation baseline, not a complete adversarial-security system.")

elif mode == "Private AirComp FL":
    sig=st.sidebar.slider("Client Gaussian noise multiplier",0.0,1.5,.25,.05); snr=st.sidebar.slider("AirComp SNR (dB)",0.0,25.0,15.0,1.0)
    o=simulate_private_aircomp_fl(rounds=70,snr_db=snr,privacy_noise_multiplier=sig,clip_norm=.8,learning_rate=.09,seed=int(seed))
    c1,c2=st.columns(2); c1.metric("Final learning loss",f"{o['final_loss']:.4f}"); c2.metric("Aggregation MSE",f"{o['mean_aggregation_mse']:.3e}")
    st.caption("Clipped client gradients receive Gaussian perturbations before analog aggregation. The multiplier is a DP-style privacy-noise knob; no epsilon/delta guarantee is claimed without a sampling/accounting model.")

elif mode == "Semantic Resource Scheduler":
    r=st.sidebar.slider("Resources / slot",3,10,6,1); strat=st.sidebar.selectbox("Scheduling objective",["channel","importance","value_per_resource","urgency_aware"])
    o=simulate_semantic_resource_scheduling(resources_per_slot=r,strategy=strat,slots=350,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Task utility / slot",f"{o['task_utility']:.3f}"); c2.metric("Expired packets",o['expired']); c3.metric("Resource utilization",f"{100*o['resource_utilization']:.1f}%")
    st.caption("Semantic packets have heterogeneous task importance, resource cost and expiry. Channel-first, importance-first and urgency-aware policies expose when task value should override instantaneous link quality.")

elif mode == "Split Inference":
    snr=st.sidebar.slider("Residual-feature SNR (dB)",-5.0,20.0,10.0,1.0); th=st.sidebar.slider("Local confidence threshold",.5,.98,.75,.02)
    a=simulate_split_inference(mode='adaptive',snr_db=snr,confidence_threshold=th,n_samples=10000,seed=int(seed)); l=simulate_split_inference(mode='local',snr_db=snr,n_samples=10000,seed=int(seed)); e=simulate_split_inference(mode='edge',snr_db=snr,n_samples=10000,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Local-only",f"{100*l['accuracy']:.1f}%",f"{l['mean_latency_ms']:.2f} ms"); c2.metric("Adaptive",f"{100*a['accuracy']:.1f}%",f"{a['mean_channel_uses']:.2f} uses"); c3.metric("Full edge",f"{100*e['accuracy']:.1f}%",f"{e['mean_channel_uses']:.0f} uses")
    st.caption("A local early classifier offloads residual features only for low-confidence samples. Channel uses and end-to-end latency are abstract proxies; no particular edge-computing protocol is claimed.")

elif mode == "Resilient Async FL":
    frac=st.sidebar.slider("Byzantine fraction",0.0,.30,.13,.01); delay=st.sidebar.slider("Mean staleness",0.0,8.0,4.0,.5)
    vals=[]
    for strat in ['naive_mean','median','stale_robust']:
        vals.append((strat,simulate_resilient_async_federated(strategy=strat,byzantine_fraction=frac,delay_mean=delay,rounds=90,seed=int(seed))))
    cols=st.columns(3)
    for c,(name,o) in zip(cols,vals): c.metric(name,f"loss {o['final_loss']:.4f}",f"accept {100*o['mean_accept_fraction']:.1f}%")
    st.caption("Stale and Byzantine updates coexist. Coordinate median is intentionally retained as a strong simple baseline; the conflict/staleness heuristic is not assumed to dominate it.")

elif mode == "Clustered Personalization":
    sep=st.sidebar.slider("Cluster separation",0.0,1.5,.8,.1); err=st.sidebar.slider("Cluster assignment error",0.0,.5,.1,.05)
    o=simulate_clustered_personalization(cluster_separation=sep,cluster_assignment_error=err,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Global MSE",f"{o['global_mse']:.3f}"); c2.metric("Cluster model MSE",f"{o['cluster_mse']:.3f}"); c3.metric("Local MSE",f"{o['local_mse']:.3f}")
    st.caption("Structured non-IID clients share one of two cluster models. Incorrect grouping exposes when hierarchical personalization can be worse than fully local fitting.")

elif mode == "Private Hardware AirComp":
    priv=st.sidebar.slider("Privacy-noise multiplier",0.0,1.0,.25,.05); bits=st.sidebar.select_slider("ADC bits",options=[3,4,6,8],value=6); sat=st.sidebar.slider("PA saturation",.5,3.0,1.5,.1)
    o=simulate_private_hardware_aircomp(privacy_noise_multiplier=priv,adc_bits=bits,pa_saturation=sat,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Median aggregation MSE",f"{o['median_mse']:.3e}"); c2.metric("P90 MSE",f"{o['p90_mse']:.3e}"); c3.metric("PA clip fraction",f"{100*o['mean_pa_clip_fraction']:.2f}%")
    st.caption("Intentional client perturbation, analog PA clipping, AWGN, AGC and finite-resolution ADC are evaluated in the same AirComp aggregation chain.")

elif mode == "Energy-Aware Split":
    snr=st.sidebar.slider("Mean link SNR (dB)",-5.0,20.0,6.0,1.0); ddl=st.sidebar.slider("Deadline (ms)",1.5,3.5,2.2,.1); pol=st.sidebar.selectbox("Policy",['static','deadline_aware','energy_aware'])
    o=simulate_energy_aware_split(mean_snr_db=snr,deadline_ms=ddl,policy=pol,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("On-time accuracy",f"{100*o['on_time_accuracy']:.1f}%"); c2.metric("Mean device energy",f"{o['mean_energy_mj']:.3f} mJ"); c3.metric("Mean latency",f"{o['mean_latency_ms']:.2f} ms")
    st.caption("Residual-feature offload is selected using confidence, deadline feasibility and a simple expected-gain-per-joule score. Energy values are normalized system proxies, not calibrated handset measurements.")

elif mode == "Layered Model Multicast":
    spread=st.sidebar.slider("Client SNR spread (dB)",1.0,12.0,7.0,.5); bf=st.sidebar.slider("Base-model fraction",.2,.8,.45,.05)
    o=simulate_layered_model_multicast(snr_std_db=spread,base_fraction=bf,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Common multicast time",f"{o['common_time']:.0f}"); c2.metric("Layered multicast time",f"{o['layered_time']:.0f}",f"utility {o['layered_mean_utility']:.2f}"); c3.metric("Serial unicast time",f"{o['unicast_time']:.0f}")
    st.caption("A base model is decoded by all clients while an enhancement layer targets the stronger half. This exposes the weakest-user bottleneck in heterogeneous downlink model distribution.")

elif mode == "Differential Model Broadcast":
    k=st.sidebar.select_slider("Keyframe interval",options=[2,4,8,12,20,30],value=8); scheme=st.sidebar.selectbox("Downlink coding",["full","chained_delta","anchored_delta"])
    o=simulate_differential_model_broadcast(keyframe_interval=k,scheme=scheme,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Mean client-model MSE",f"{o['mean_model_mse']:.3f}"); c2.metric("Mean model age",f"{o['mean_version_age']:.1f} rounds"); c3.metric("Normalized DL size/round",f"{o['normalized_downlink_size_per_round']:.3f}")
    st.caption("Periodic full-model keyframes are combined with small differential updates. Chained deltas lose synchronization after a missed packet; anchor-relative deltas can recover from isolated missed updates if the keyframe was received. This is an educational mixed-timescale baseline, not a bit-exact implementation of a published codec.")

elif mode == "Progressive Split Inference":
    snr=st.sidebar.slider("Mean residual-link SNR (dB)",-5.0,18.0,5.0,1.0); ddl=st.sidebar.slider("Deadline (ms)",1.4,3.5,2.2,.1); pol=st.sidebar.selectbox("Policy",["local","full","confidence","adaptive"])
    o=simulate_progressive_split_inference(mean_snr_db=snr,deadline_ms=ddl,policy=pol,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("On-time accuracy",f"{100*o['on_time_accuracy']:.1f}%",f"raw {100*o['accuracy']:.1f}%"); c2.metric("Residual uses",f"{o['mean_channel_uses']:.2f}/{o['full_residual_uses']}"); c3.metric("Mean latency",f"{o['mean_latency_ms']:.2f} ms",f"miss {100*o['deadline_miss_rate']:.1f}%")
    st.caption("Residual features are sent in task-importance order and can terminate early. The adaptive policy uses confidence, link quality, energy proxy and hard deadline feasibility before requesting another feature chunk.")

elif mode == "AirComp Selection Bias":
    gap=st.sidebar.slider("Long-term channel/data-group disparity (dB)",0.0,14.0,8.0,1.0); strat=st.sidebar.selectbox("Client selection",["all","random","channel","diversity"])
    o=simulate_aircomp_selection_federated(strategy=strat,channel_disparity_db=gap,rounds=80,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Final global loss",f"{o['final_global_loss']:.3f}"); c2.metric("Analog MSE",f"{o['mean_analog_mse_to_selected_mean']:.2e}"); c3.metric("Selection-bias MSE",f"{o['mean_selection_bias_mse']:.3f}",f"+group share {100*o['plus_selection_fraction']:.1f}%")
    st.caption("Channel-only selection can make the OTA sum physically cleaner while systematically excluding a non-IID client group. Gradient-diversity selection trades some weakest-link quality for statistical coverage.")

elif mode == "EH AirComp FL":
    hs=st.sidebar.slider("Energy-harvest scale",.05,.8,.35,.05); pol=st.sidebar.selectbox("Scheduler",["channel","energy_channel","age_energy"])
    o=simulate_energy_harvesting_aircomp_fl(policy=pol,harvest_scale=hs,rounds=100,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Final global loss",f"{o['final_global_loss']:.3f}"); c2.metric("Participation Jain",f"{o['participation_jain']:.3f}"); c3.metric("Energy-outage slots",f"{100*o['energy_outage_slot_fraction']:.1f}%")
    st.caption("Each OTA update consumes one harvested energy unit from a finite battery. When energy is scarce, battery causality dominates; when energy is plentiful, age-aware scheduling prevents strong-channel clients from monopolizing participation.")

elif mode == "Importance-Aware Multicast":
    anti=st.sidebar.slider("Importance/SNR anticorrelation",0.0,.95,.6,.05); pen=st.sidebar.slider("Airtime penalty",1e-6,8e-6,4e-6,1e-6,format="%.0e")
    o=simulate_importance_aware_model_multicast(importance_anticorrelation=anti,airtime_penalty=pen,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("SNR-layered weighted utility",f"{o['snr_half_weighted_utility']:.3f}"); c2.metric("Importance-aware utility",f"{o['importance_weighted_utility']:.3f}"); c3.metric("DL time ratio",f"{o['importance_time']/o['snr_half_time']:.3f}×")
    st.caption("The base layer reaches all devices; the enhancement multicast rate is chosen using client task importance as well as airtime. When high-value clients are weak links, pure SNR-layering can be task-suboptimal.")

elif mode == "Adaptive FL Downlink":
    block=st.sidebar.slider("Common blockage penalty (dB)",0.0,12.0,7.0,.5); pol=st.sidebar.selectbox("Keyframe controller",["fixed","budgeted_age"]); budget=st.sidebar.slider("Target normalized DL size",.30,.45,.36,.01)
    o=simulate_adaptive_differential_broadcast(policy=pol,fixed_keyframe_interval=5,age_threshold=24,target_downlink_size=budget,blockage_db=block,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Mean model age",f"{o['mean_version_age']:.1f} rounds"); c2.metric("Client model MSE",f"{o['mean_model_mse']:.3f}"); c3.metric("DL size / round",f"{o['normalized_downlink_size_per_round']:.3f}",f"{o['keyframes']} keyframes")
    st.caption("The budgeted-age controller spends full-model resynchronization packets only when client version age is high and the running downlink budget permits it. It is an educational age-aware keyframe policy, not the published MTDC algorithm.")

elif mode == "Carbon-Aware FL":
    cw=st.sidebar.slider("Carbon weight",0.0,2.0,.75,.05); pol=st.sidebar.selectbox("Client orchestration",["random","utility","carbon","balanced"],index=3)
    o=simulate_carbon_aware_federated(policy=pol,carbon_weight=cw,fairness_weight=1.0,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Excess FL loss",f"{o['excess_loss']:.4f}"); c2.metric("Carbon proxy",f"{o['total_carbon_proxy']:.1f}"); c3.metric("Participation Jain",f"{o['participation_jain']:.3f}")
    st.caption("Regional carbon intensity is time varying and deliberately correlated with data groups. Carbon-only scheduling can therefore reduce emissions proxy while creating statistical selection bias; the balanced policy trades utility, carbon cost, and participation age.")

elif mode == "Edge Model Caching":
    k=st.sidebar.select_slider("Recache interval",options=[40,80,160,320,640,1280],value=160); pol=st.sidebar.selectbox("Cache policy",["static","lru","periodic_popularity","periodic_value"],index=3)
    o=simulate_edge_model_caching(policy=pol,recache_interval=k,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Mean inference latency",f"{o['mean_latency_ms']:.1f} ms"); c2.metric("Cache hit rate",f"{100*o['cache_hit_rate']:.1f}%"); c3.metric("Backhaul traffic",f"{o['backhaul_mb']:.0f} MB",f"{o['cache_updates']} cache updates")
    st.caption("Slow-timescale AI-model caching is coupled to fast per-request edge/cloud routing. Cache fills are charged to backhaul traffic, so very reactive policies can have good hit rates yet poor system cost.")

elif mode == "Queued Progressive Split":
    load=st.sidebar.slider("Inference arrivals / slot",.2,1.2,.65,.05); pol=st.sidebar.selectbox("Shared-radio scheduler",["fifo","edf","value","urgency_value","completion_aware"],index=4)
    o=simulate_queued_progressive_split(arrival_rate=load,policy=pol,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("On-time task utility",f"{100*o['on_time_task_utility']:.1f}%"); c2.metric("Deadline miss",f"{100*o['deadline_miss_rate']:.1f}%"); c3.metric("Mean backlog",f"{o['mean_backlog']:.1f}")
    st.caption("Multiple progressive inference requests share one radio server. Naive value/deadline preemption can fragment partially served requests; completion-aware scheduling explicitly rewards jobs already close to a usable decision.")

elif mode == "Multicast Repair":
    anti=st.sidebar.slider("Importance/SNR anticorrelation",0.0,.95,.75,.05); pol=st.sidebar.selectbox("Repair policy",["no_repair","important_repair","all_repair"],index=1)
    o=simulate_importance_aware_multicast_repair(policy=pol,importance_anticorrelation=anti,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Weighted task utility",f"{100*o['weighted_task_utility']:.1f}%"); c2.metric("Model coverage",f"{100*o['mean_model_coverage']:.1f}%"); c3.metric("Airtime / full-common",f"{o['time_ratio_to_full']:.2f}×")
    st.caption("An aggressive multicast serves strong clients quickly. Selective unicast repair then prioritizes missed high-value clients under the conservative full-common airtime budget; repairing every weak client can be far more expensive.")

elif mode == "Selective Downlink Repair":
    snr=st.sidebar.slider("Mean client SNR (dB)",-4.0,14.0,8.0,.5); pol=st.sidebar.selectbox("Repair policy",["periodic_keyframe","selective_age","selective_importance"],index=2)
    o=simulate_selective_downlink_repair(policy=pol,mean_snr_db=snr,importance_snr_anticorrelation=.9,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Weighted version age",f"{o['weighted_version_age']:.1f} rounds"); c2.metric("Weighted model MSE",f"{o['weighted_model_mse']:.3f}"); c3.metric("DL size / round",f"{o['normalized_downlink_size_per_round']:.3f}")
    st.caption("Selective repair spends nearly the same long-run resynchronization budget as periodic common keyframes. It helps when desynchronization is sparse; when many clients lose the differential chain together, a common keyframe can be more efficient.")

elif mode == "Version-Aware Model Cache":
    pol=st.sidebar.selectbox("Cache policy",["popularity","latency_value","version_value","lru"],index=2); budget=st.sidebar.slider("Refresh budget / epoch (MB)",80.0,700.0,180.0,20.0)
    o=simulate_version_aware_edge_caching(policy=pol,refresh_budget_mb=budget,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Task utility",f"{o['mean_task_utility']:.3f}"); c2.metric("Served version age",f"{o['mean_served_version_age']:.1f}"); c3.metric("Backhaul",f"{o['backhaul_mb']:.0f} MB")
    st.caption("A cache hit can still be stale. Version-aware refresh spends a hard transfer budget on model fills or differential refreshes according to expected task-value gain per MB.")

elif mode == "Fair Carbon Orchestration":
    dw=st.sidebar.slider("Virtual-debt weight",.5,12.0,8.0,.5); cw=st.sidebar.slider("Carbon weight",0.0,2.0,1.0,.1); pol=st.sidebar.selectbox("Policy",["random","carbon","age_balanced","virtual_debt"],index=3)
    o=simulate_fair_carbon_orchestration(policy=pol,carbon_weight=cw,debt_weight=dw,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Excess FL loss",f"{o['excess_loss']:.4f}"); c2.metric("Participation Jain",f"{o['participation_jain']:.3f}"); c3.metric("Carbon proxy",f"{o['total_carbon_proxy']:.1f}")
    st.caption("Virtual participation debt is persistent state: clients that remain underserved accumulate scheduling pressure. Higher debt weight protects long-run participation but can force service in dirtier carbon periods.")

elif mode == "Split Admission Control":
    load=st.sidebar.slider("Inference arrivals / slot",.2,1.7,.9,.05); pol=st.sidebar.selectbox("Admission policy",["admit_all","backlog_gate","backpressure"],index=2)
    o=simulate_progressive_split_admission(policy=pol,arrival_rate=load,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("On-time task utility",f"{100*o['on_time_task_utility']:.1f}%"); c2.metric("Deadline miss",f"{100*o['deadline_miss_rate']:.1f}%"); c3.metric("Admitted refinements",f"{100*o['admission_fraction']:.1f}%")
    st.caption("Under overload, not every low-confidence sample should enter the enhancement queue. Backpressure compares expected task gain with current congestion; rejected requests finish locally rather than becoming late radio work.")

elif mode == "Digital Twin Sync":
    pol=st.sidebar.selectbox("Sync policy",["periodic","error_full","semantic_delta"],index=2); th=st.sidebar.slider("State-error trigger",.5,6.0,1.5,.5); interval=st.sidebar.select_slider("Periodic interval",options=[2,4,8,12,16,24],value=8)
    o=simulate_digital_twin_sync(policy=pol,error_threshold=th,periodic_interval=interval,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Position RMSE",f"{o['position_rmse']:.3f}"); c2.metric("AoII proxy",f"{o['mean_aoii']:.2f}"); c3.metric("Radio load / slot",f"{o['normalized_radio_load_per_slot']:.4f}")
    st.caption("The edge twin predicts between updates. Event-triggered semantic deltas transmit only when prediction error becomes significant; smaller innovation packets are easier to deliver but introduce quantization error.")

elif mode == "Task-Aware Model Repair":
    burst=st.sidebar.slider("Task-demand burst strength",.5,4.0,2.4,.1); pol=st.sidebar.selectbox("Repair priority",["age_only","static_importance","task_aware"],index=2)
    o=simulate_task_aware_model_repair(policy=pol,burst_strength=burst,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Task utility / ideal",f"{100*o['task_utility_ratio']:.1f}%"); c2.metric("Task-weighted model age",f"{o['mean_active_task_model_age']:.1f} rounds"); c3.metric("DL size / round",f"{o['normalized_downlink_size_per_round']:.3f}")
    st.caption("Repairs share the same saved downlink budget. The task-aware policy favors clients that are stale and currently serving valuable inference demand; when workload is nearly static, that extra state tracking need not help.")

elif mode == "Congested Model Refresh":
    svc=st.sidebar.slider("Backhaul service (MB/request)",.5,9.0,2.8,.1); pol=st.sidebar.selectbox("Refresh policy",["eager","periodic_value","congestion_aware"],index=2)
    o=simulate_congested_model_refresh(policy=pol,backhaul_service_mb_per_request=svc,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Task utility",f"{o['mean_task_utility']:.3f}"); c2.metric("Served model age",f"{o['mean_served_version_age']:.2f}"); c3.metric("P95 refresh queue",f"{o['p95_backhaul_queue_mb']:.0f} MB")
    st.caption("Refresh jobs complete only after queued model bytes cross the backhaul. Eager freshness can therefore create its own staleness by flooding the refresh queue; the congestion-aware heuristic is deliberately allowed to leave refresh opportunities unused.")

elif mode == "Battery-Carbon Fair FL":
    h=st.sidebar.slider("Energy-harvest scale",.10,1.10,.50,.05); pol=st.sidebar.selectbox("Client orchestration",["random_feasible","carbon_only","debt_carbon","debt_battery_carbon"],index=3)
    o=simulate_battery_carbon_fair_fl(policy=pol,harvest_scale=h,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Excess FL loss",f"{o['excess_loss']:.4f}"); c2.metric("Participation Jain",f"{o['participation_jain']:.3f}"); c3.metric("Underfilled rounds",f"{100*o['underfilled_round_fraction']:.1f}%")
    st.caption("Selection obeys battery energy causality. When harvesting is extremely scarce, all policies are constrained by feasibility; once energy is available, carbon-only selection can reintroduce persistent data/participation bias.")

elif mode == "Twin-Guided Prefetch":
    noise=st.sidebar.slider("Twin prediction uncertainty",.1,1.8,.5,.1); pol=st.sidebar.selectbox("Prefetch policy",["reactive","predictive","uncertainty_gated"],index=2)
    o=simulate_twin_guided_model_prefetch(policy=pol,twin_noise_std=noise,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Inference latency",f"{o['mean_inference_latency_ms']:.1f} ms"); c2.metric("Cache hit",f"{100*o['cache_hit_rate']:.1f}%"); c3.metric("Model backhaul",f"{o['total_backhaul_mb']:.0f} MB")
    st.caption("The digital twin predicts which operating-mode model will be needed next. Blind speculation can churn the cache when the inferred transition direction is noisy; uncertainty gating suppresses low-confidence prefetches.")

elif mode == "Networked Control":
    snr=st.sidebar.slider("Mean sensor-link SNR (dB)",-5.0,10.0,2.0,.5); pol=st.sidebar.selectbox("Sensor scheduler",["round_robin","max_age","max_error","control_value"],index=3)
    o=simulate_networked_control_scheduling(policy=pol,mean_snr_db=snr,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Closed-loop cost",f"{o['mean_control_cost']:.3f}"); c2.metric("Mean information age",f"{o['mean_information_age']:.2f}"); c3.metric("Max state excursion",f"{o['max_state_excursion']:.2f}")
    st.caption("Several mildly unstable plants share one wireless sensor slot. Max-Age minimizes freshness but ignores plant instability and estimation mismatch; control-value scheduling prioritizes updates by expected physical-loop benefit rather than age alone.")

elif mode == "Risk-Sensitive Control":
    shock=st.sidebar.slider("Rare-shock severity",.3,2.2,1.4,.1); pol=st.sidebar.selectbox("Scheduler",["mean_value","risk_value"],index=1)
    o=simulate_risk_sensitive_control(policy=pol,mean_snr_db=-3,shock_multiplier=shock,risk_weight=1.0,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Mean cost",f"{o['mean_control_cost']:.1f}"); c2.metric("CVaR95",f"{o['cvar95_control_cost']:.1f}"); c3.metric("Mean age",f"{o['mean_information_age']:.1f}")
    st.caption("Rare process shocks create a tail-risk objective. The risk-value heuristic can protect the CVaR regime, but it is intentionally not assumed to dominate mean-value scheduling for mild or extreme shock settings.")

elif mode == "Variable-Rate Control":
    snr=st.sidebar.slider("Mean sensor-link SNR (dB)",-3.0,8.0,0.0,.5); pol=st.sidebar.selectbox("State-update policy",["fixed_low","fixed_high","adaptive"],index=2)
    o=simulate_variable_rate_control(policy=pol,mean_snr_db=snr,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Mean control cost",f"{o['mean_control_cost']:.3g}"); c2.metric("Payload",f"{o['mean_payload_bits_per_slot']:.2f} bit/slot"); c3.metric("Delivery",f"{100*o['update_success_rate']:.1f}%")
    st.caption("The controller sends quantized state innovations. More bits improve state precision but reduce packet deliverability; the adaptive policy uses link quality and control mismatch to choose 3/6/10-bit updates.")

elif mode == "Failure-Aware Edge":
    load=st.sidebar.slider("Offered task load",.5,2.0,1.2,.1); pol=st.sidebar.selectbox("Orchestrator",["latency_only","trust_aware","risk_aware"],index=2)
    o=simulate_failure_aware_edge_orchestration(policy=pol,load=load,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Mean latency",f"{o['mean_latency_ms']:.1f} ms"); c2.metric("P95 latency",f"{o['p95_latency_ms']:.1f} ms"); c3.metric("Failure",f"{100*o['failure_rate']:.1f}%")
    st.caption("Fast edge nodes are deliberately less reliable. Risk-aware placement includes queue, recovery and trust penalties, exposing latency versus execution-failure trade-offs without using a learned policy.")

elif mode == "Joint Cache-Offload":
    cap=st.sidebar.slider("Cache capacity / edge (MB)",220,760,520,20); pol=st.sidebar.selectbox("Policy",["nearest","cache_first","joint"],index=2)
    o=simulate_joint_cache_offload(cache_capacity_mb=cap,policy=pol,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Mean latency",f"{o['mean_latency_ms']:.1f} ms"); c2.metric("Cache hit",f"{100*o['cache_hit_rate']:.1f}%"); c3.metric("Backhaul/request",f"{o['backhaul_mb_per_request']:.1f} MB")
    st.caption("Slow cache placement and fast inference offloading are coupled. Cache-first routing can create edge-queue concentration even with excellent hit rate; the joint heuristic prices radio delay, queue and model misses together.")

elif mode == "Cooperative Control":
    snr=st.sidebar.slider("Mean shared-link SNR (dB)",-5.0,6.0,-2.0,.5); pol=st.sidebar.selectbox("Scheduler",["max_age","local_error","system_value"],index=2)
    o=simulate_cooperative_networked_control(policy=pol,mean_snr_db=snr,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("System cost",f"{o['mean_system_cost']:.3g}"); c2.metric("Formation error",f"{o['mean_formation_error']:.3g}"); c3.metric("Mean age",f"{o['mean_information_age']:.1f}")
    st.caption("A chain of coupled agents shares one feedback slot. System-value scheduling estimates the global formation-error reduction from each update; its benefit is largest when communication is severely constrained.")

elif mode == "Safety-Aware Control":
    snr=st.sidebar.slider("Mean feedback SNR (dB)",-6.0,5.0,-1.0,.5); pol=st.sidebar.selectbox("Scheduler",["max_age","max_error","safety_value"],index=2)
    o=simulate_safety_aware_control(policy=pol,mean_snr_db=snr,slots=2200,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Safety violations",f"{100*o['safety_violation_rate']:.2f}%"); c2.metric("Mean control cost",f"{o['mean_control_cost']:.3f}"); c3.metric("Mean information age",f"{o['mean_information_age']:.1f}")
    st.caption("Plants have unequal safety envelopes. Safety-value scheduling prioritizes normalized proximity to the state boundary rather than age alone; this is an educational linear-control baseline, not a certified barrier-function controller.")

elif mode == "Adaptive-Depth Inference":
    snr=st.sidebar.slider("Mean feature-link SNR (dB)",-5.0,12.0,2.0,.5); ddl=st.sidebar.slider("Latency budget (ms)",2.0,4.5,3.0,.1); pol=st.sidebar.selectbox("Runtime policy",["fixed_light","fixed_deep","adaptive"],index=2)
    o=simulate_channel_adaptive_depth(n_tasks=3500,policy=pol,mean_snr_db=snr,latency_budget_ms=ddl,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("On-time task accuracy",f"{100*o['on_time_accuracy']:.1f}%"); c2.metric("Feature precision",f"{o['mean_feature_bits']:.2f} bits"); c3.metric("Mean model depth",f"{o['mean_model_depth']:.2f}")
    st.caption("A transparent analytic task model jointly selects feature precision and edge inference depth under a latency budget. It is an IC²/early-exit baseline, not a trained DNN benchmark.")

elif mode == "Failure Recovery":
    pf=st.sidebar.slider("Edge failure probability",0.0,.30,.10,.01); pol=st.sidebar.selectbox("Recovery policy",["restart","checkpoint","replicate"],index=1)
    o=simulate_edge_failure_recovery(n_tasks=5000,policy=pol,failure_probability=pf,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("P95 completion",f"{o['p95_latency_ms']:.1f} ms"); c2.metric("Compute load",f"{o['compute_load_ratio']:.2f}×"); c3.metric("Recovery traffic",f"{o['recovery_traffic_mb_per_task']:.2f} MB/task")
    st.caption("Restart, periodic checkpoint migration and dual execution expose a recovery-latency versus compute/network-overhead frontier under stochastic edge failures.")

elif mode == "Risk-Aware Model Replication":
    budget=st.sidebar.slider("Replica storage budget (MB)",1540,4200,2400,100); pol=st.sidebar.selectbox("Placement objective",["popularity","risk_aware"],index=1)
    o=simulate_risk_aware_model_replication(n_requests=7000,policy=pol,storage_budget_mb=budget,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Raw model outage",f"{100*o['model_outage_rate']:.2f}%"); c2.metric("Task-weighted outage",f"{100*o['task_weighted_outage_rate']:.2f}%"); c3.metric("Mean replicas/model",f"{o['mean_replication_factor']:.2f}")
    st.caption("Popularity-only replication protects frequent models; risk-aware placement additionally protects low-frequency high-criticality models. Storage and failure probabilities are abstract proxies.")

elif mode == "Component-Selective Control":
    snr=st.sidebar.slider("Mean component-link SNR (dB)",-6.0,10.0,0.0,.5); pol=st.sidebar.selectbox("State update policy",["round_robin","all_low","value_component"],index=2)
    o=simulate_component_selective_control(slots=2200,policy=pol,mean_snr_db=snr,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Mean control cost",f"{o['mean_control_cost']:.3f}"); c2.metric("P95 cost",f"{o['p95_control_cost']:.3f}"); c3.metric("Payload",f"{o['mean_payload_bits_per_slot']:.1f} bit/slot")
    st.caption("A vector state shares a tiny feedback budget. Value-component scheduling updates the state coordinate with the largest control-weighted mismatch rather than transmitting every component equally.")

elif mode == "Semantic HARQ":
    snr=st.sidebar.slider("Mean semantic-link SNR (dB)",-6.0,10.0,0.0,.5); pol=st.sidebar.selectbox("Retransmission policy",["no_harq","channel_harq","task_harq"],index=2)
    o=simulate_semantic_harq(n_samples=10000,policy=pol,mean_snr_db=snr,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Accuracy",f"{100*o['accuracy']:.1f}%"); c2.metric("Hard-sample accuracy",f"{100*o['hard_sample_accuracy']:.1f}%"); c3.metric("Channel uses",f"{o['mean_channel_uses']:.2f}/sample")
    st.caption("Task-HARQ retransmits low-confidence samples rather than only low-SNR samples. This is a scalar task-statistic/MRC baseline, not standards HARQ or a learned semantic codec.")

elif mode == "Mixed Control-Inference":
    load=st.sidebar.slider("Inference arrival probability",.05,.90,.45,.05); pol=st.sidebar.selectbox("Shared-radio scheduler",["control_first","inference_first","age_first","task_value"],index=3)
    o=simulate_mixed_control_inference(slots=3500,policy=pol,inference_arrival=load,mean_snr_db=0,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Control cost",f"{o['mean_control_cost']:.3f}"); c2.metric("Inference utility/slot",f"{o['inference_utility_per_slot']:.3f}"); c3.metric("Safety violations",f"{100*o['safety_violation_rate']:.2f}%")
    st.caption("One radio slot is shared by physical-control feedback and deadline-limited edge inference. Task-value scheduling compares downstream value instead of treating the two traffic classes as interchangeable packets.")

elif mode == "Failure-Domain Replication":
    budget=st.sidebar.slider("Replica storage budget (MB)",1600,4500,2800,100); pol=st.sidebar.selectbox("Placement policy",["popularity","independent_risk","domain_aware"],index=2)
    o=simulate_failure_domain_replication(n_requests=9000,policy=pol,storage_budget_mb=budget,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Task-weighted outage",f"{100*o['task_weighted_outage_rate']:.2f}%"); c2.metric("Failure domains/model",f"{o['mean_failure_domains_per_model']:.2f}"); c3.metric("Mean replicas/model",f"{o['mean_replication_factor']:.2f}")
    st.caption("Replicas on nodes sharing a rack/site/power domain are correlated protection. Domain-aware placement spends storage on failure diversity rather than assuming independent node outages.")

elif mode == "Checkpoint Service Migration":
    mob=st.sidebar.slider("Mobility probability / step",.01,.30,.10,.01); pol=st.sidebar.selectbox("Migration policy",["cold_reactive","periodic_checkpoint","predictive_checkpoint"],index=1)
    o=simulate_checkpoint_aware_migration(steps=4500,policy=pol,mobility=mob,checkpoint_interval=8,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Mean latency",f"{o['mean_latency_ms']:.1f} ms"); c2.metric("Cold migrations",f"{100*o['cold_migration_rate']:.1f}%"); c3.metric("State traffic",f"{o['migration_traffic_mb_per_step']:.2f} MB/step")
    st.caption("Stateful edge services can react cold, checkpoint neighboring edges, or speculate using mobility prediction. The predictor is deliberately imperfect so speculative state transfer is not free.")

elif mode == "Safety Bit Allocation":
    snr=st.sidebar.slider("Mean state-link SNR (dB)",-6.0,10.0,1.0,.5); pol=st.sidebar.selectbox("State coding policy",["uniform_low","single_high","risk_bitalloc"],index=2)
    o=simulate_safety_bit_allocation(slots=2800,policy=pol,mean_snr_db=snr,bit_budget=10,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Control cost",f"{o['mean_control_cost']:.3f}"); c2.metric("Safety violations",f"{100*o['safety_violation_rate']:.2f}%"); c3.metric("Payload",f"{o['mean_payload_bits_per_slot']:.1f} bit/slot")
    st.caption("All state components receive coarse observability first; remaining bits refine safety-critical components. Low-SNR regimes can still favor uniform coarse updates because deliverability dominates precision.")

elif mode == "Predictive Failure Migration":
    noise=st.sidebar.slider("Forecast-noise scale",0.0,1.2,.25,.05); pol=st.sidebar.selectbox("Migration policy",["sticky","reactive","predictive_risk"],index=2)
    o=simulate_predictive_failure_migration(steps=2600,policy=pol,forecast_noise=noise,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Mean latency",f"{o['mean_latency_ms']:.1f} ms"); c2.metric("Deadline miss",f"{100*o['deadline_miss_rate']:.2f}%"); c3.metric("Migration rate",f"{100*o['migration_rate']:.1f}%")
    st.caption("A noisy degradation forecast can trigger proactive service migration before failure. The same mechanism can overreact: forecast error raises migration traffic/churn and eventually reverses the mean-latency gain.")

elif mode == "Chance-Constrained Inference":
    jitter=st.sidebar.slider("Latency-jitter scale",0.0,1.0,.5,.05); pol=st.sidebar.selectbox("Admission policy",["mean_latency","chance"],index=1)
    o=simulate_chance_constrained_inference(n_tasks=7000,policy=pol,jitter_scale=jitter,deadline_ms=50,reliability_target=.99,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Admission",f"{100*o['admission_rate']:.1f}%"); c2.metric("Admitted deadline miss",f"{100*o['deadline_miss_rate']:.2f}%"); c3.metric("On-time utility",f"{o['on_time_utility_per_task']:.3f}")
    st.caption("Mean-latency admission ignores the completion-time tail. Chance admission explicitly budgets P(T <= deadline), trading offload/admission rate for deadline reliability; rejected jobs use a smaller local fallback.")

elif mode == "Control UEP":
    snr=st.sidebar.slider("Mean state-link SNR (dB)",-6.0,12.0,-1.0,.5); pol=st.sidebar.selectbox("Protection",["equal","critical_uep"],index=1)
    o=simulate_control_uep(slots=2600,policy=pol,mean_snr_db=snr,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Control cost",f"{o['mean_control_cost']:.3f}"); c2.metric("Critical miss",f"{100*o['critical_component_miss_rate']:.1f}%"); c3.metric("Radio budget",f"{o['mean_repetitions_per_slot']:.0f} reps/slot")
    st.caption("Both policies use the same five-repetition budget. UEP concentrates repetition on the high-value state component; its advantage is largest when the radio is communication limited and vanishes as one-shot delivery becomes reliable.")

elif mode == "Multi-Connectivity Reliability":
    rho=st.sidebar.slider("Link-failure correlation",0.0,.95,.25,.05); pol=st.sidebar.selectbox("Duplication policy",["single","full_duplicate","adaptive"],index=2)
    thr=st.sidebar.slider("Adaptive risk threshold",.02,.60,.172,.01,disabled=(pol!="adaptive"))
    o=simulate_multi_connectivity_reliability(n_packets=16000,policy=pol,correlation=rho,seed=int(seed),duplication_threshold=thr)
    c1,c2,c3=st.columns(3); c1.metric("Packet outage",f"{100*o['packet_outage_rate']:.2f}%"); c2.metric("Radio use",f"{o['mean_transmissions_per_packet']:.2f} tx/pkt"); c3.metric("Duplication",f"{100*o['duplication_rate']:.1f}%")
    st.caption("Dual-path packet duplication gains reliability only from diversity that is actually independent. The adaptive threshold exposes a reliability-resource Pareto frontier using pre-transmission link-quality estimates only; no realized-outcome genie is used.")

elif mode == "Multi-Connectivity Safety Control":
    rho=st.sidebar.slider("Link-failure correlation",0.0,.95,.35,.05); pol=st.sidebar.selectbox("Control packet policy",["single","full_duplicate","adaptive_duplicate"],index=2)
    o=simulate_multiconnectivity_safety_control(slots=2400,policy=pol,correlation=rho,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Safety violations",f"{100*o['safety_violation_rate']:.2f}%"); c2.metric("Control cost",f"{o['mean_control_cost']:.3f}"); c3.metric("Radio use",f"{o['mean_transmissions_per_slot']:.2f} tx/slot")
    st.caption("This lab couples v3.2 multi-connectivity to the v3.1 safety-control branch. Reliability is judged by downstream state-bound violations and control cost, not packet outage alone.")

elif mode == "Unified Resilience Budget":
    budget=st.sidebar.slider("Resilience credits / task",0.0,2.2,.75,.05)
    pol=st.sidebar.selectbox("Orchestration policy",["reactive","radio_first","edge_first","risk_budget","risk_budget_unweighted","uncertainty_gated"],index=3)
    noise=st.sidebar.slider("Edge forecast-noise scale",0.0,2.0,.4,.05)
    snr=st.sidebar.slider("Mean radio SNR (dB)",-5.0,16.0,6.0,.5)
    rho=st.sidebar.slider("Radio-path correlation",0.0,.95,.25,.05)
    edge=st.sidebar.slider("Edge-risk scale",.3,2.5,1.0,.1)
    o=simulate_unified_risk_orchestration(n_tasks=1500,policy=pol,budget_per_task=budget,forecast_noise=noise,mean_snr_db=snr,radio_correlation=rho,edge_risk_scale=edge,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Weighted deadline miss",f"{100*o['task_weighted_deadline_miss_rate']:.2f}%"); c2.metric("Mean latency",f"{o['mean_latency_ms']:.1f} ms"); c3.metric("Credits spent",f"{o['resilience_credits_per_task']:.2f}/task")
    c4,c5,c6=st.columns(3); c4.metric("Radio",f"{o['mean_transmissions_per_task']:.2f} tx/task"); c5.metric("Replica execution",f"{100*o['replica_execution_rate']:.1f}%"); c6.metric("Proactive migration",f"{100*o['proactive_migration_rate']:.1f}%")
    st.caption("v3.3 jointly prices proactive migration, cross-failure-domain execution replicas and dual-link packet duplication with a synthetic resilience-credit budget. Credits are only a decision-accounting device; physical radio, compute and migration-traffic metrics remain separate. Policies use forecasts and pre-transmission link estimates, never realized failures as genie information.")

elif mode == "Adaptive Risk Control":
    pol=st.sidebar.selectbox("Closed-loop policy",["point_greedy","static_guard","adaptive_global","adaptive_local","oracle"],index=3)
    drift=st.sidebar.slider("Distribution-drift strength",0.0,1.8,1.2,.1)
    budget=st.sidebar.slider("Resilience credits / task",0.0,1.6,1.0,.05)
    target=st.sidebar.slider("Requested miss target",.04,.20,.10,.01)
    delay=st.sidebar.select_slider("Outcome-feedback delay",options=[1,8,32,96,256,512],value=8)
    eta=st.sidebar.slider("Risk-debt adaptation rate",0.0,.16,.015,.005,disabled=not pol.startswith("adaptive"))
    o=simulate_adaptive_risk_control(n_tasks=2200,policy=pol,target_miss_rate=target,
        budget_per_task=budget,adaptation_rate=eta,feedback_delay=delay,
        drift_strength=drift,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Post-drift weighted miss",f"{100*o['post_drift_task_weighted_miss_rate']:.1f}%"); c2.metric("Critical-class miss",f"{100*o['post_drift_critical_miss_rate']:.1f}%"); c3.metric("CVaR95 latency",f"{o['cvar95_latency_ms']:.1f} ms")
    c4,c5,c6=st.columns(3); c4.metric("Credits spent",f"{o['resilience_credits_per_task']:.2f}/task"); c5.metric("Active risk debt",f"{o['mean_active_risk_debt']:.3f}"); c6.metric("Action switching",f"{100*o['action_switch_rate']:.1f}%")
    st.caption("v3.4 closes the loop around v3.3 resilience actions: only delayed historical misses update a global or per-criticality risk debt. The oracle sees hidden synthetic probabilities for analysis, never realized outcomes. The feedback rule is inspired by adaptive risk control but is not presented as a conformal guarantee.")

elif mode == "Observable Resilience":
    pol=st.sidebar.selectbox("Feedback policy",["outcome_only","component_telemetry","audit_feedback","hybrid_feedback","oracle_components"],index=3)
    drift=st.sidebar.selectbox("Drift source",["none","radio","edge","mixed"],index=3)
    budget=st.sidebar.slider("Resilience credits / task",0.0,1.6,.9,.05)
    telemetry=st.sidebar.slider("Component-telemetry availability",0.0,1.0,.8,.05)
    audit=st.sidebar.slider("Routine-task audit probability",0.0,.5,.05,.01)
    delay=st.sidebar.select_slider("Feedback delay",options=[1,8,32,96,256,512],value=8)
    rho=st.sidebar.slider("Radio-path correlation",0.0,1.0,.25,.05)
    o=simulate_observable_resilience(n_tasks=2400,policy=pol,drift_mode=drift,budget_per_task=budget,
        telemetry_probability=telemetry,audit_rate=audit,feedback_delay=delay,
        radio_correlation=rho,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Protected weighted miss",f"{100*o['task_weighted_protected_miss_rate']:.1f}%"); c2.metric("Unprotected miss",f"{100*o['unprotected_counterfactual_miss_rate']:.1f}%"); c3.metric("Masked primary failures",f"{100*o['masked_fraction_of_base_failures']:.1f}%")
    c4,c5,c6=st.columns(3); c4.metric("Component observations",f"{100*o['component_observation_rate']:.1f}%"); c5.metric("Safe audits",f"{100*o['audit_fraction']:.1f}%"); c6.metric("Credits spent",f"{o['resilience_credits_per_task']:.2f}/task")
    st.caption("v3.5 exposes action-dependent feedback: duplication and cross-domain replicas can hide primary component failures from an outcome-only controller. Component telemetry and routine-only audits improve observability, but they are not guaranteed to improve decisions. Hidden unprotected outcomes are evaluation-only; critical tasks are never audited.")

elif mode == "Offline Resilience Evaluation":
    logger=st.sidebar.selectbox("Logging policy",["safe_explore","conservative","deterministic"],index=0)
    target=st.sidebar.selectbox("Target policy",["baseline","sparse","balanced","aggressive","unsafe_critical_probe"],index=2)
    estimator=st.sidebar.selectbox("OPE estimator",["dm","ips","snips","dr","clipped_dr"],index=3)
    explore=st.sidebar.slider("Exploration floor",.005,.30,.08,.005,disabled=(logger=="deterministic"))
    recency=st.sidebar.select_slider("Most-recent log fraction",options=[.1,.2,.4,.7,1.0],value=1.0)
    drift=st.sidebar.slider("Distribution-drift strength",0.0,2.0,1.0,.1)
    nonlinear=st.sidebar.slider("Unmodeled nonlinearity",0.0,2.5,1.0,.1)
    clip=st.sidebar.slider("DR weight clip",2.0,120.0,12.0,2.0,disabled=(estimator!="clipped_dr"))
    o=simulate_offline_resilience_evaluation(n_tasks=6000,logging_policy=logger,target_policy=target,
        estimator=estimator,exploration_rate=explore,recency_fraction=recency,drift_strength=drift,
        nonlinearity=nonlinear,clip_weight=clip,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Estimated weighted miss",f"{100*o['estimated_weighted_miss']:.2f}%"); c2.metric("Paired oracle (evaluation only)",f"{100*o['oracle_weighted_miss']:.2f}%"); c3.metric("Absolute OPE error",f"{100*o['absolute_error']:.2f} pp")
    c4,c5,c6=st.columns(3); c4.metric("Effective sample",f"{100*o['effective_sample_fraction']:.1f}%"); c5.metric("Max importance weight",f"{o['max_importance_weight']:.1f}"); c6.metric("Unsupported target mass",f"{100*o['support_violation_mass']:.1f}%")
    if not o["identifiable"]: st.error("Target policy leaves the logging policy's support. This numerical estimate is extrapolation, not an identified off-policy value.")
    st.caption("v3.6 logs known action propensities and compares direct, importance-weighted, self-normalized, doubly robust and clipped-DR estimates. Critical logging tasks are always protected. Confidence intervals are synthetic influence-value diagnostics, not high-confidence policy-improvement certificates.")

elif mode == "Propensity-Robust OPE":
    prop=st.sidebar.selectbox("Propensity source",["recorded_true","recorded_nominal","stale_recorded","estimated_full","estimated_crossfit","misspecified"],index=4)
    estimator=st.sidebar.selectbox("OPE estimator",["ips","snips","dr","clipped_dr"],index=2)
    target=st.sidebar.selectbox("Target policy",["baseline","sparse","balanced","aggressive"],index=2)
    hidden=st.sidebar.slider("Hidden-confounding strength",0.0,2.0,.8,.1)
    drift=st.sidebar.slider("Logging-policy drift",0.0,2.0,1.0,.1)
    gamma=st.sidebar.slider("Sensitivity gamma",1.0,10.0,2.0,.25)
    o=simulate_propensity_robust_evaluation(n_tasks=5000,propensity_mode=prop,estimator=estimator,
        target_policy=target,hidden_confounding=hidden,propensity_drift=drift,
        sensitivity_gamma=gamma,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Estimated weighted miss",f"{100*o['estimated_weighted_miss']:.2f}%"); c2.metric("Paired oracle (evaluation only)",f"{100*o['oracle_weighted_miss']:.2f}%"); c3.metric("Absolute OPE error",f"{100*o['absolute_error']:.2f} pp")
    c4,c5,c6=st.columns(3); c4.metric("Propensity MAE",f"{100*o['propensity_mae']:.1f} pp"); c5.metric("Sensitivity interval",f"{100*o['sensitivity_low']:.1f}% - {100*o['sensitivity_high']:.1f}%"); c6.metric("Required row-wise gamma",f"{o['required_sensitivity_gamma']:.1f}")
    if gamma<o["required_sensitivity_gamma"]: st.warning("The chosen odds envelope does not contain every hidden synthetic logging propensity. Aggregate interval coverage can still occur, but it is not row-wise protection.")
    st.caption("v3.7 separates known, stale, estimated and misspecified logging propensities. Cross-fitting reduces reuse of the same sample but cannot recover omitted confounders. The displayed odds envelope is an empirical stress diagnostic, not a sharp marginal-sensitivity bound or a causal confidence interval.")

elif mode == "eMBB-URLLC Slicing":
    lam=st.sidebar.slider("URLLC arrivals / mini-slot",.05,2.5,.9,.05); vals=[]
    for pol in ['reserved','adaptive_reserve','preemptive']:
        o=simulate_embb_urllc_slicing(3500,24,lam,3,2,.995,pol,fixed_reserved_prbs=6,seed=int(seed)); vals.append((pol,o))
    cols=st.columns(3)
    for c,(p,o) in zip(cols,vals): c.metric(p,f"eMBB {o['embb_throughput_bits_per_minislot']:.1f}",f"URLLC miss {100*o['urllc_deadline_miss_rate']:.2f}%")
    st.caption("Reserved slicing pays idle-resource waste; preemption protects random URLLC arrivals by puncturing eMBB; adaptive reservation uses an EWMA arrival forecast. This is an abstract mini-slot scheduler, not a 3GPP implementation.")

elif mode == "Energy-Harvesting AoI":
    hp=st.sidebar.slider("Harvest probability scale",.05,.75,.25,.02); S,U=1200,5; means=np.array([-1.,1.,3.,5.,7.]); T=rng.normal(means,2.5,(S,U)); probs=np.clip(hp*np.array([.65,.8,1.,1.15,1.3]),0,.95); vals=[]
    for pol in ['max_age','max_snr','age_reliability','energy_aware']:
        o=simulate_energy_harvesting_aoi(T,probs,3,90,1.0,pol,seed=int(seed)); vals.append((pol,o))
    fig,ax=plt.subplots(); ax.bar([v[0] for v in vals],[v[1]['mean_aoi'] for v in vals]); ax.set_ylabel('Mean AoI (slots)'); ax.tick_params(axis='x',rotation=15); fig.tight_layout(); st.pyplot(fig)
    st.caption("Each status transmission consumes one harvested energy unit. Channel-greedy service can maximize deliveries while starving weak users and worsening freshness.")

elif mode == "Grant-free NOMA":
    activity=st.sidebar.slider("Device activity probability",.01,.25,.10,.01); spread=st.sidebar.slider("Received-power spread (dB)",0.0,14.0,8.0,.5); vals=[]
    for m in ['oma_collision','noma_sic']:
        o=simulate_grant_free_random_access(120,24,600,activity,10,spread,2,m,seed=int(seed)); vals.append((m,o['throughput_packets_per_slot'],o['success_probability']))
    c1,c2=st.columns(2); c1.metric("OMA collision",f"{vals[0][1]:.2f} pkt/slot",f"success {100*vals[0][2]:.1f}%"); c2.metric("Ideal SIC NOMA",f"{vals[1][1]:.2f} pkt/slot",f"success {100*vals[1][2]:.1f}%")
    st.caption("Grant-free devices choose resources autonomously. The NOMA branch uses ideal power-domain SIC; activity detection, preamble errors and imperfect cancellation are intentionally outside scope.")

elif mode == "Personalized FL":
    h=st.sidebar.slider("Client heterogeneity",0.0,1.5,.6,.1); alpha=st.sidebar.slider("Personalization blend α",0.0,1.0,.6,.05)
    o=simulate_personalized_federated(heterogeneity=h,personalization=alpha,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Global test MSE",f"{o['mean_global_test_mse']:.3f}"); c2.metric("Personalized MSE",f"{o['mean_personalized_test_mse']:.3f}"); c3.metric("Local-only MSE",f"{o['mean_local_test_mse']:.3f}")
    st.caption("A pooled global ridge model is blended with each client's small-sample local model. Low heterogeneity favors sharing; high heterogeneity favors stronger specialization, while full local fitting pays estimation variance.")

elif mode == "Straggler-Resilient FL":
    pstr=st.sidebar.slider("Straggler probability",0.0,.35,.15,.01); red=st.sidebar.select_slider("MDS redundancy",options=[0,2,4,8],value=4)
    u=simulate_straggler_resilience(strategy='uncoded',straggler_probability=pstr,rounds=8000,seed=int(seed)); c=simulate_straggler_resilience(strategy='mds',redundancy=red,straggler_probability=pstr,rounds=8000,seed=int(seed)) if red else u
    c1,c2,c3=st.columns(3); c1.metric("Uncoded P95",f"{u['p95_latency_ms']:.1f} ms"); c2.metric("Coded P95",f"{c['p95_latency_ms']:.1f} ms"); c3.metric("Compute load",f"{c['compute_load_ratio']:.2f}×")
    st.caption("MDS-style coded computing is modeled as recovery after any K of K+r worker results. It is a transparent round-latency abstraction, not a specific gradient-code implementation.")

elif mode == "Federated Distillation":
    probes=st.sidebar.select_slider("Public probe logits / client",options=[4,6,8,12,16,24],value=8); snr=st.sidebar.slider("Logit upload SNR (dB)",-5.0,25.0,10.0,1.0)
    o=simulate_federated_distillation(public_probes=probes,snr_db=snr,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Model-average accuracy",f"{100*o['model_average_accuracy']:.1f}%"); c2.metric("Distilled accuracy",f"{100*o['distilled_accuracy']:.1f}%"); c3.metric("Upload scalars",f"{o['distill_upload_scalars']} vs {o['model_upload_scalars']}")
    st.caption("Clients upload predictions on shared public probes rather than full linear model vectors. The server distills a student; this is a toy knowledge-transfer baseline with a shared public probe set.")

elif mode == "Channel-Aware Split":
    snr=st.sidebar.slider("Mean residual-link SNR (dB)",-5.0,20.0,5.0,1.0); ddl=st.sidebar.slider("Inference deadline (ms)",1.4,3.5,1.8,.1)
    stc=simulate_channel_aware_split(policy='static',mean_snr_db=snr,deadline_ms=ddl,seed=int(seed)); cha=simulate_channel_aware_split(policy='channel_aware',mean_snr_db=snr,deadline_ms=ddl,seed=int(seed))
    c1,c2,c3=st.columns(3); c1.metric("Static on-time accuracy",f"{100*stc['on_time_accuracy']:.1f}%",f"miss {100*stc['deadline_miss_rate']:.1f}%"); c2.metric("Channel-aware on-time",f"{100*cha['on_time_accuracy']:.1f}%",f"miss {100*cha['deadline_miss_rate']:.1f}%"); c3.metric("Channel-aware uses",f"{cha['mean_channel_uses']:.2f}")
    st.caption("Offload decisions account for local confidence, instantaneous link quality and whether residual-feature transmission can finish before the deadline. Late predictions are not counted as on-time task success.")

elif mode == "OTA Sign Aggregation":
    nc=st.sidebar.select_slider("Clients",options=[3,5,9,15,31,63],value=31); snr=st.sidebar.slider("OTA sign SNR (dB)",-8.0,15.0,5.0,1.0); bad=st.sidebar.slider("Sign-flipping clients",0.0,.45,.0,.05)
    o=simulate_sign_aircomp(n_clients=nc,snr_db=snr,byzantine_fraction=bad,trials=1000,seed=int(seed))
    c1,c2=st.columns(2); c1.metric("Majority-sign error",f"{100*o['sign_error_rate']:.2f}%"); c2.metric("Mean vote margin",f"{o['mean_vote_margin']:.2f}")
    st.caption("Each client transmits one BPSK gradient sign per coordinate and wireless superposition implements a noisy majority vote. More clients provide statistical gain, but sign-flipping participants can erode the majority margin.")

else:
    snr_db = st.sidebar.slider("Nominal SNR (dB)", -10.0, 30.0, 0.0, 1.0)
    cfg = OFDMConfig()
    taps = np.zeros(16, dtype=np.complex128)
    taps[[0,2,5,9,15]] = [1.0, 0.62*np.exp(.3j), 0.42*np.exp(-.9j), 0.27*np.exp(1.4j), 0.14*np.exp(-.2j)]
    taps /= np.linalg.norm(taps)
    H = channel_frequency_response(taps, cfg.n_fft)[cfg.data_bins]
    gains = np.abs(H)**2
    noise = 10**(-snr_db/10)
    total = float(len(gains))
    peq = np.full(len(gains), 1.0)
    pwf = waterfill_power_allocation(gains, total, noise)
    ceq = parallel_channel_capacity_bits(gains, peq, noise)/len(gains)
    cwf = parallel_channel_capacity_bits(gains, pwf, noise)/len(gains)
    c1,c2,c3=st.columns(3); c1.metric("Equal-power capacity", f"{ceq:.3f}"); c2.metric("Water-filled capacity", f"{cwf:.3f}"); c3.metric("Active carriers", int(np.count_nonzero(pwf>1e-8)))
    signed=np.asarray(cfg.data_subcarriers); order=np.argsort(signed)
    fig,ax1=plt.subplots(); ax1.plot(signed[order],10*np.log10(gains[order]+1e-12),'o-'); ax1.set_xlabel('Subcarrier'); ax1.set_ylabel('Gain (dB)')
    ax2=ax1.twinx(); ax2.step(signed[order],pwf[order],where='mid'); ax2.set_ylabel('Allocated power'); ax1.set_title('Channel and Water-Filled Power Allocation'); st.pyplot(fig)
    st.caption("At low SNR, water-filling concentrates power on stronger parallel subchannels; at high SNR it approaches equal allocation.")
