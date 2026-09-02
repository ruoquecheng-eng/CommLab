# CommLab v1.3 Release Notes

v1.3 extends CommLab from single-cell/link abstractions toward distributed access, programmable propagation, and sensing-assisted beam management while keeping every new branch intentionally transparent and testable.

## New capability groups

### Cell-Free / User-Centric Massive MIMO
- Geometry-based AP/user placement and large-scale fading.
- Per-user strongest-AP clustering.
- Distributed masked MRT directions.
- AP-user service-link accounting as a simple coordination/fronthaul proxy.
- Per-user rate and Jain-fairness evaluation.
- Fixed-direction max-min SINR power allocation by bisection over the standard interference-coupled feasibility equations.

### Multi-user RIS optimization
- K-user MISO effective channel through a phase-only RIS.
- ZF or MRT digital precoding after each passive phase update.
- Finite-bit discrete coordinate ascent over RIS elements.
- Convergence history and random-phase baselines.

### Predictive ISAC beam management
- ULA pointing-gain model.
- Constant-velocity and constant-acceleration Kalman angle trackers.
- Sparse/missed sensing updates.
- Reactive-hold versus model-based predictive beam selection.
- Explicit model-mismatch counterexample: a CV tracker can underperform a reactive baseline on an accelerating target.

### Uncertainty-aware beamwidth/aperture
- Expected-rate evaluation under Gaussian angle uncertainty.
- Candidate active-aperture selection across 8/16/32/64 elements.
- Quantifies narrow-beam array gain versus pointing-error robustness.

## New experiments
- `cell_free_user_centric.py`
- `cell_free_power_control.py`
- `ris_multiuser_coordinate.py`
- `isac_predictive_beam_tracking.py`
- `isac_uncertainty_aware_beamwidth.py`

## Validation
- 101/101 automated tests passing.
- v1.3 suite re-runs all five new experiment families.
- Results are included in the v1.3 SHA-256 artifact manifest.

## Scope boundaries
- Cell-Free is a normalized distributed-MRT abstraction, not a 3GPP/O-RAN implementation and not a fronthaul network simulator.
- The max-min power controller assumes fixed beam directions and perfect instantaneous channel knowledge.
- RIS coordinate ascent is a local finite-grid search; no global optimality is claimed.
- Predictive beam tracking uses synthetic angle measurements and idealized ULA patterns; no calibrated antenna/RF hardware is modeled.
