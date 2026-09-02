# Methodological Inspirations — v1.8

CommLab v1.8 borrows **problem structures**, not code, from several established research directions.

## Cell-Free fronthaul / channel acquisition

The Cell-Free literature repeatedly identifies fronthaul limitation, scalable resource allocation, synchronization and channel acquisition as core deployment constraints. v1.8 therefore combines AP refresh scheduling, temporal prediction and finite CSI precision under one hard bit budget rather than assuming independent unlimited updates.

Reference context: H. Q. Ngo et al., *Ultra-Dense Cell-Free Massive MIMO for 6G: Technical Overview and Open Questions*, arXiv:2401.03898.

## Age of Information

AoI treats successful throughput and information freshness as different objectives. v1.8 uses a simple age×reliability index rather than reproducing an optimal MDP/Whittle-index solution.

Reference context: M. Zanni, M. Assaad, T. Soleymani, *Age of Information Optimization for Status Updates in Integrated Sensing and Communication Systems*, arXiv:2605.24714; and A. Li et al., *Age of Information with Hybrid-ARQ: A Unified Explicit Result*, arXiv:2204.01257.

## Grant-free NOMA

Grant-free access is motivated by reducing request/grant signalling for sparse massive-device activity. v1.8 implements only slotted random resource selection and ideal power-domain SIC; it does not implement preamble detection, compressed sensing activity detection or residual cancellation error.

Reference context: M. B. Shahab et al., *Grant-free Non-orthogonal Multiple Access for IoT: A Survey*, arXiv:1910.06529.

## RIS control timing

Prior RIS-assisted Cell-Free work has motivated separating slower passive-surface control from faster active beamforming. v1.8 extends the project with a simple utility-drop event trigger; the trigger itself is a CommLab heuristic rather than a reproduced published algorithm.

Reference context: M. Eskandari et al., *Two-Timescale Design for RIS-aided Cell-free Massive MIMO Systems with Imperfect CSI*, arXiv:2304.02606.
