# CommLab v3.4 Portfolio Summary

CommLab is a pure-software wireless/edge-intelligence research platform spanning PHY links, MIMO, coding/HARQ, RF impairments, mobility, MAC/scheduling, ISAC, federated and semantic communication, edge inference, Digital Twins, networked control, and reliability orchestration.

v3.4 adds **closed-loop adaptive risk control** to the unified v3.3 resilience budget. It compares stale point decisions, fixed conservatism, global feedback, per-criticality localized feedback, and a hidden-probability reference under distribution drift and delayed outcomes.

The release emphasizes engineering and scientific honesty:

- current outcomes cannot influence current decisions;
- global and class-specific miss, tail latency, calibration, spend, and switching are reported together;
- infeasible targets, noisy feedback, scarce-budget reversals, and correlation failures are kept;
- the implementation is transparent NumPy rather than black-box RL;
- no conformal theorem, production SLO, 3GPP conformance, real MEC trace, or safety certification is claimed.
