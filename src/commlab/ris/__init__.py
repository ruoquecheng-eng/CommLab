from .surface import (
    optimal_ris_phases, quantize_phases, ris_effective_channel,
    ris_spectral_efficiency,
)
__all__=["optimal_ris_phases","quantize_phases","ris_effective_channel","ris_spectral_efficiency"]
from .multiuser import effective_multiuser_channel, ris_mu_sum_rate, coordinate_optimize_ris
__all__ += ["effective_multiuser_channel","ris_mu_sum_rate","coordinate_optimize_ris"]

from .cellfree import effective_cellfree_ris_channel, coordinate_optimize_cellfree_ris
from .cellfree_imperfect import (
    age_complex_channel, quantize_ris_cellfree_csi, predicted_channel_samples,
    design_and_evaluate_aged_cellfree_ris,
)
__all__ += ["age_complex_channel","quantize_ris_cellfree_csi","predicted_channel_samples","design_and_evaluate_aged_cellfree_ris"]

from .event_triggered import simulate_event_triggered_cellfree_ris
