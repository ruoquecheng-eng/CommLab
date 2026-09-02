# Methodological Inspirations — v1.7

v1.7 borrows **problem structure**, not source code, from several current wireless-system themes:

1. **Cell-Free / user-centric scalability:** recent work continues to emphasize fronthaul cost, AP selection, CSI acquisition, and heterogeneous participation instead of assuming unlimited central coordination.
2. **Two-timescale RIS control:** RIS-assisted Cell-Free studies often separate slowly updated passive phases/statistical CSI from faster instantaneous AP-side processing to reduce feedback and control burden.
3. **Finite-blocklength retransmission:** short-packet reliability is fundamentally coupled to accumulated blocklength, SNR, retransmission count, and latency; v1.7 uses a transparent normal-approximation abstraction rather than a standards decoder.
4. **Predictive sensing/resource control:** ISAC research increasingly treats sensing as a resource-consuming action whose information value affects future beam alignment and scheduling.
5. **Temporal CSI compression:** highly correlated channel states are treated as a time series; innovation coding is a basic interpretable reference before learned CSI-compression models.

The release intentionally avoids presenting these baselines as globally optimal solvers, standards implementations, or learned end-to-end systems.
