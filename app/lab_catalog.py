from __future__ import annotations

from collections.abc import Iterable

ALL_LABS = tuple(["OFDM Link", "Phase Noise", "IQ Imbalance", "Sampling Clock", "Power Amplifier", "High-Doppler ICI", "2x2 MIMO Detection", "MIMO K-best", "MIMO MMSE-SIC", "Massive MU-MIMO", "MU-MIMO User Selection", "Hybrid Beamforming", "Hybrid OMP", "Cell-Free Network", "Cell-Free Pilot CSI", "Cell-Free Fronthaul CSI", "Cell-Free Fronthaul Energy", "Async Cell-Free CSI", "Predictive CSI Compression", "Cell-Free RIS", "Robust Cell-Free RIS", "Cell-Free RIS Aging", "Two-timescale RIS", "Cell-Free AP Energy", "Multi-user RIS", "Predictive ISAC Beam", "ISAC Joint Beam", "ISAC Sensing Budget", "Predictive Sensing-on-Demand", "Cross-layer OLLA/HARQ", "FBL HARQ Queue", "FBL IR-HARQ", "Queue-aware ISAC", "Short-Packet FBL", "RIS Link", "Limited Feedback Beamforming", "OFDMA Scheduling", "Queued OFDMA", "OLLA Link Adaptation", "OFDM Sensing / ISAC", "ISAC Angle", "ISAC MUSIC", "ISAC MUSIC + MDL", "Finite Blocklength", "Joint CSI Budget", "Deadline HARQ", "Age of Information", "Event-triggered RIS", "Budgeted ISAC", "Grant-free NOMA", "IRSA Random Access", "Capture IRSA", "AirComp Aggregation", "AirComp Federated Learning", "Cell-Free AirComp", "RIS AirComp", "Task-Oriented Communication", "Non-IID FL Client Selection", "Random-Access FL", "Robust RIS AirComp", "Cell-Free AirComp CSI Risk", "Multi-Task Semantic", "Budgeted Gradient FL", "AirComp Hardware", "Layered Semantic", "Importance Random-Access FL", "Two-timescale RIS FL", "Async Federated Learning", "Byzantine-Robust FL", "Private AirComp FL", "Semantic Resource Scheduler", "Split Inference", "Personalized FL", "Straggler-Resilient FL", "Federated Distillation", "Channel-Aware Split", "OTA Sign Aggregation", "Resilient Async FL", "Clustered Personalization", "Private Hardware AirComp", "Energy-Aware Split", "Layered Model Multicast", "Differential Model Broadcast", "Progressive Split Inference", "AirComp Selection Bias", "EH AirComp FL", "Importance-Aware Multicast", "Adaptive FL Downlink", "Carbon-Aware FL", "Edge Model Caching", "Queued Progressive Split", "Multicast Repair", "Selective Downlink Repair", "Version-Aware Model Cache", "Fair Carbon Orchestration", "Split Admission Control", "Digital Twin Sync", "Task-Aware Model Repair", "Congested Model Refresh", "Battery-Carbon Fair FL", "Twin-Guided Prefetch", "Networked Control", "Risk-Sensitive Control", "Variable-Rate Control", "Failure-Aware Edge", "Joint Cache-Offload", "Cooperative Control", "Safety-Aware Control", "Adaptive-Depth Inference", "Failure Recovery", "Risk-Aware Model Replication", "Component-Selective Control", "Semantic HARQ", "Mixed Control-Inference", "Failure-Domain Replication", "Checkpoint Service Migration", "Safety Bit Allocation", "Predictive Failure Migration", "Chance-Constrained Inference", "Control UEP", "Multi-Connectivity Reliability", "Multi-Connectivity Safety Control", "Unified Resilience Budget", "Adaptive Risk Control", "Observable Resilience", "Offline Resilience Evaluation", "Propensity-Robust OPE", "eMBB-URLLC Slicing", "Energy-Harvesting AoI", "Water-Filling"])

GROUPS = (
    "Waveform & receiver",
    "MIMO, RIS & sensing",
    "Access & scheduling",
    "AirComp & federated learning",
    "Edge intelligence & control",
    "Resilience & evaluation",
)

GROUP_LABELS = dict(zip(GROUPS, (
    "波形与接收机", "MIMO、RIS 与感知", "接入与调度",
    "空中计算与联邦学习", "边缘智能与控制", "韧性与评估",
)))

def group_for(name: str) -> str:
    value = name.casefold()
    if any(word in value for word in ("resilience", "reliability", "risk", "failure", "counterfactual", "propensity", "observable", "offline", "budget", "drift", "recovery", "replication", "migration", "checkpoint", "multi-connectivity", "control uep")):
        return GROUPS[5]
    if any(word in value for word in ("aircomp", "federated", "fl ", " fl", "multicast", "distillation", "aggregation", "byzantine", "private", "personalized")):
        return GROUPS[3]
    if any(word in value for word in ("edge", "split", "cache", "carbon", "digital twin", "model refresh", "inference", "prefetch", "networked control", "task-aware", "semantic", "energy-aware")):
        return GROUPS[4]
    if any(word in value for word in ("mimo", "ris", "isac", "sensing", "beam", "cell-free", "angle", "music", "doppler")):
        return GROUPS[1]
    if any(word in value for word in ("access", "scheduling", "scheduler", "harq", "noma", "ofa", "queue", "aoi", "slicing", "water-filling", "adaptation", "blocklength", "grant-free")):
        return GROUPS[2]
    return GROUPS[0]

def find_labs(query: str = "", group: str = "All", names: Iterable[str] = ALL_LABS) -> tuple[str, ...]:
    terms = query.casefold().strip().split()
    return tuple(name for name in names if (group == "All" or group_for(name) == group) and all(term in name.casefold() or term in group_for(name).casefold() or term in GROUP_LABELS[group_for(name)].casefold() for term in terms))

def recent_labs(history: Iterable[str], *, limit: int = 6) -> tuple[str, ...]:
    seen: set[str] = set()
    result: list[str] = []
    for name in history:
        if name in ALL_LABS and name not in seen:
            seen.add(name)
            result.append(name)
        if len(result) == limit:
            break
    return tuple(result)
