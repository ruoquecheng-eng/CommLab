# CommLab v3.2 Portfolio Summary

**CommLab — Wireless Communication Systems Laboratory** is a pure-software research platform that has grown from an OFDM simulator into a cross-layer wireless/edge-intelligence laboratory spanning PHY, coding/HARQ, MIMO, RF impairments, high mobility, scheduling, ISAC, AirComp/FL, semantic communication, split inference, model caching, Digital Twin synchronization, and networked control.

## v3.2 focus

v3.2 studies **predictive resilience and reliability orchestration** rather than adding isolated algorithms. The main research question is how imperfect state information changes reliability decisions across edge execution, model placement, deadline-constrained inference, control-state protection, and multi-connectivity.

Key additions:
- predictive edge-failure migration with an explicit forecast-noise/churn crossover;
- model replication across correlated failure domains rather than independent-node assumptions;
- chance-constrained inference admission based on `P(latency <= deadline)`;
- unequal error protection for control-state components under a fixed radio budget;
- correlation-aware full/adaptive dual-link packet duplication plus an explicit reliability-resource threshold frontier;
- a direct coupling from multi-connectivity into safety-aware networked control.

The earlier v3.2 semantic HARQ, mixed control/inference scheduling, checkpoint migration, failure-domain storage sweep, and safety bit-allocation experiments are preserved as complementary extensions.

## Engineering discipline

Every v3.2 direction has module code, independent tests, deterministic Monte Carlo scripts, CSV data, PNG figures, Dashboard Labs, release documentation, reproducibility instructions, a trade-off matrix, and SHA-256 artifact verification. Release acceptance also checks editable installation, import-path/version consistency without manual `PYTHONPATH`, `compileall`, ZIP CRC, and ZIP SHA-256.

## Research stance

The project intentionally retains negative results. Predictive migration can become worse than reactive migration when forecasts are noisy; critical UEP loses relevance at high SNR; full duplication loses diversity as links become correlated; and chance constraints reduce deadline misses by rejecting more tasks. The platform therefore emphasizes operating regions and system-level trade-offs rather than universal algorithm dominance.
