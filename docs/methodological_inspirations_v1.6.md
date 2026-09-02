# Methodological inspirations — v1.6

The implementation is original to CommLab; the following public work informed **which system couplings were worth testing**, not the source code.

- **Joint pilot allocation and AP selection for massive access in Cell-Free massive MIMO** (Computer Networks, 2026): motivates treating pilot/CSI acquisition and AP service decisions as coupled rather than independent controls.
- **Cell-free ISAC massive MIMO systems with capacity-constrained fronthaul links**: motivates explicitly accounting for fronthaul limits/cost when optimizing distributed communication/sensing resources.
- **Deep Reinforcement Learning-Based Dynamic Resource Allocation in Cell-Free Massive MIMO** (2026): its antenna-activation/energy-efficiency framing motivated our transparent non-DRL AP/fronthaul energy baseline.
- **A Predictive Closed-Loop Resource Allocation Framework for OFDM-ISAC** (ICCCS 2026): motivates uncertainty-driven sensing-on-demand. CommLab deliberately uses a two-step interpretable controller instead of DRL.
- 2026 URLLC surveys emphasizing finite blocklength and cross-layer scheduling motivated connecting FBL reliability to packet queues/HARQ rather than leaving it as a standalone information-theory curve.
