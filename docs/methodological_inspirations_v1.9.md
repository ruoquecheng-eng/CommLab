# Methodological Inspirations — v1.9

v1.9 uses published communication-system structures only as methodological inspiration. Implementations in CommLab are independent and deliberately simplified.

- **IRSA / coded random access:** iterative singleton decoding and replica cancellation are based on the graph-peeling view of repetition slotted ALOHA. CommLab does not reproduce a standards random-access PHY or density-evolution implementation.
- **AirComp:** analog channel superposition is used as a one-shot arithmetic-mean primitive. The implementation focuses on channel inversion, truncation and aggregation MSE rather than a complete wireless federated-learning stack.
- **eMBB/URLLC coexistence:** mini-slot preemption/reservation is used to study throughput-versus-deadline reliability, not to reproduce NR MAC/RLC procedures.
- **Energy/AoI:** stochastic energy availability is combined with generate-at-will status updating to study freshness under battery constraints.

The consistent design rule remains: expose assumptions, compare interpretable baselines, retain failure regions, and avoid claiming standards or hardware validation that the repository does not provide.
