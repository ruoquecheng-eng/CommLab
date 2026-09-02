# CommLab v2.8 — Portfolio Summary

**Recommended title:** CommLab — Wireless Communication & Edge Intelligence Systems Laboratory

**One-line description:** A reproducible Python research simulator spanning PHY/MIMO/RIS/ISAC through cross-layer scheduling and wireless edge intelligence, with v2.8 focusing on state-aware runtime control and failure recovery.

## Strongest v2.8 evidence

1. **Selective model repair has an operating region, not universal superiority.** At low SNR broad desynchronization favors global keyframes; at high SNR sparse failures make targeted repair more efficient at essentially the same downlink budget.
2. **A cache hit can still be wrong for the task.** v2.8 tracks model versions and shows a direct tradeoff between hit rate, served model staleness, task utility, and model-refresh backhaul.
3. **Fairness is persistent state.** Virtual participation debt avoids the weakness of one-slot age bonuses and makes the carbon price of long-run participation explicit.
4. **Admission is part of inference control.** Under overload, rejecting some wireless refinements and finishing locally can increase on-time application utility.
5. **Digital-twin synchronization is modeled as a communication-control loop.** The twin predicts between updates and semantic innovation packets are triggered by state error rather than a fixed clock.

## Suggested portfolio figures
- `results/figures/v28_selective_repair_age.png`
- `results/figures/v28_versioned_cache_utility_backhaul.png`
- `results/figures/v28_fair_carbon_pareto.png`
- `results/figures/v28_split_admission_utility.png`
- `results/figures/v28_digital_twin_rmse_load.png`

## Safe CV bullets
- Developed a modular Python wireless/edge-intelligence simulator with automated regression tests and reproducible experiment artifacts across PHY, MIMO/RIS/ISAC, MAC/cross-layer control, and distributed edge learning.
- Implemented state-aware runtime controllers for differential model repair, model-version caching, long-horizon client fairness, progressive-inference admission, and digital-twin synchronization.
- Designed Monte Carlo experiments that preserve negative operating regions rather than claiming universal gains, including SNR-dependent repair crossover and overload regimes where simple gating beats value-based backpressure.

## Claims to avoid
- Do not call the digital-twin module a production twin or calibrated cyber-physical system.
- Do not call carbon proxies lifecycle emissions.
- Do not claim version-aware caching or selective repair are globally optimal.
- Do not claim semantic-delta synchronization is a standardized semantic-communication codec.
