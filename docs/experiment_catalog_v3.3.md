# Experiment Catalog — v3.3

## New v3.3 experiment family

1. `experiments/v33_resilience_budget.py`
   - sweeps normalized resilience budget;
   - compares reactive, radio-first, edge-first, risk-budget, and uncertainty-gated policies;
   - outputs reliability, tail latency, radio, replica, migration, and credit metrics.

2. `experiments/v33_risk_regimes.py`
   - creates radio-limited, mixed, and edge-limited operating regions;
   - tests whether the unified policy reallocates budget between duplication and edge resilience.

3. `experiments/v33_forecast_uncertainty.py`
   - sweeps edge forecast noise;
   - compares point-estimate risk orchestration with uncertainty gating;
   - preserves the low-noise cost of over-conservative gating.

4. `experiments/v33_correlation_reallocation.py`
   - sweeps radio-path correlation;
   - measures whether the runtime redirects credits from radio duplication toward failure-domain replicas.

5. `experiments/v33_budget_saturation.py`
   - extends the budget into an excess-resource region;
   - exposes saturation, speculative migration traffic, and credits intentionally left unused by uncertainty gating.

6. `experiments/v33_task_weighting.py`
   - compares task-criticality weighting against an unweighted myopic risk proxy;
   - retains the negative result that simple criticality weighting does not dominate across all budgets.

## New result files

- `results/data/v33_resilience_budget.csv`
- `results/data/v33_risk_regimes.csv`
- `results/data/v33_forecast_uncertainty.csv`
- `results/data/v33_correlation_reallocation.csv`
- `results/data/v33_budget_saturation.csv`
- `results/data/v33_task_weighting.csv`

The corresponding `v33_*.png` figures live in `results/figures/`.

## Preserved history

All v3.2 and earlier datasets/figures remain part of the tree and are included in the release manifest. v3.3 adds a coupled orchestration layer; it does not replace the component-level experiments that motivate it.
