# Methodological Inspirations — v3.2

v3.2 uses public work only to identify useful *problem structures*. Implementations are independent NumPy baselines.

- **Predictive mobility-aware migration:** 2026 work on predictive service-function-chain migration highlights the latency benefit and prediction/migration trade-off in mobile edge systems. CommLab uses a short-horizon kinematic/risk heuristic rather than hierarchical RL.  
  https://www.sciencedirect.com/science/article/pii/S1389128626000836

- **Latency/energy-aware service migration:** recent MEC work continues to frame migration as a latency/resource decision under mobility. CommLab additionally makes forecast error and migration churn explicit.  
  https://www.nature.com/articles/s41598-026-36711-y

- **Goal-oriented communication:** a 2026 review argues for task/control metrics rather than treating all packets as equal. This motivates chance-constrained task admission and unequal protection of control-relevant state.  
  https://www.nature.com/articles/s44287-026-00303-9

- **Component-based networked control:** 2026 work studies component-wise event-triggered state transmission. CommLab's UEP experiment is a simpler fixed-bit-budget packet abstraction focused on unequal downstream control value.  
  https://www.sciencedirect.com/science/article/abs/pii/S0016003226003741

- **Multi-connectivity and partial duplication:** 2026 field evaluation of dual commercial 5G paths reports that packet duplication reliability depends on path correlation and that conditional/partial duplication can approach full-duplication performance at lower overhead. CommLab models the same qualitative reliability-overhead question with synthetic correlated links rather than field traces.  
  https://doi.org/10.1109/OJCOMS.2026.3695929

- **Forecast-driven edge offloading:** 2026 work closes a forecast/decision loop for adaptive MEC offloading under time-varying reliability and workload. CommLab keeps the predictor deliberately simple and instead stress-tests forecast error, tail constraints, and decision churn so that the failure mode remains interpretable.  
  https://www.sciencedirect.com/science/article/pii/S108480452600069X

- **Dynamic/partial packet duplication:** recent multi-connectivity measurements motivate treating redundancy activation as a resource-allocation decision rather than a binary always-on feature. CommLab therefore exposes the adaptive duplication threshold and its outage-versus-transmission Pareto frontier under synthetic path correlation.  
  https://doi.org/10.1109/OJCOMS.2026.3695929
