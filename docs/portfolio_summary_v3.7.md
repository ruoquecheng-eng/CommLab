# CommLab v3.7 Portfolio Summary

CommLab v3.7 extends the platform's safe offline evaluation line from known propensities to uncertain logging mechanisms. It supports propensity drift, stale recorded metadata, logistic nuisance estimation, fold-separated prediction, deliberate model misspecification, hidden time-correlated confounding, empirical odds-envelope sensitivity diagnostics, and baseline-aware fallback selection.

The engineering contribution is a deterministic NumPy implementation with focused unit tests, six reproducible experiments, twelve plots, an interactive Dashboard Lab, complete retained historical results, and hash-verified release tooling.

The scientific contribution is mostly negative and diagnostic: a well-calibrated observed propensity model cannot reconstruct an omitted common cause; cross-fitting can raise finite-sample variance; an envelope can cover an aggregate oracle while failing row-wise protection; and a conservative selector can replace unsafe optimism with permanent inaction.

The intended use is research prototyping, teaching, and estimator stress testing. It is not a deployment safety case, a causal-identification library, or a substitute for randomized logging, valid instruments, richer telemetry, and domain-specific assumptions.
