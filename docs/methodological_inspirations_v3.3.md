# Methodological Inspirations — v3.3

v3.3 borrows **problem structures**, not implementations. The code remains an independent transparent NumPy baseline.

- **Adaptive / predictive service migration:** recent MEC work continues to formulate migration as a joint latency/resource decision and shows why proactive migration has value under mobility or predicted state. CommLab deliberately replaces learned migration controllers with a short-horizon explicit risk heuristic so forecast error and migration churn remain inspectable.  
  https://www.nature.com/articles/s41598-026-36711-y

- **Predictive mobility-aware migration:** recent work on predictive service-function-chain migration motivates treating prediction as an input to orchestration rather than a free oracle. CommLab focuses on prediction error and action cost instead of reproducing hierarchical RL.  
  https://www.sciencedirect.com/science/article/pii/S1389128626000836

- **Conditional / partial multi-connectivity:** 2026 field evaluation of two commercial 5G paths reports that conditional/partial duplication can approach full-duplication reliability with less overhead, and that impairments can be partially correlated. CommLab uses this qualitative structure in a synthetic correlated-link model and makes the redundancy budget compete directly with edge actions.  
  https://doi.org/10.1109/OJCOMS.2026.3695929

- **Joint migration and resource allocation:** MEC literature has long emphasized that migration should be coupled to communication/computation resource allocation rather than treated independently. v3.3 applies that principle to a broader reliability budget covering migration, replicas, and radio duplication.  
  https://ieeexplore.ieee.org/document/9400771/

These sources do not make CommLab standards-compliant or empirically validated against their datasets. They motivate questions and baselines only.
