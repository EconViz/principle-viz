"""Open-access common-resource overuse analysis."""

from __future__ import annotations

from dataclasses import dataclass

from principle_viz.core.equilibrium import EquilibriumResult
from principle_viz.core.line import Line
from principle_viz.policy.externality import ExternalityScenario, analyze_externality


@dataclass(frozen=True, slots=True)
class CommonResourceResult:
    private_benefit: Line
    private_cost: Line
    open_access_equilibrium: EquilibriumResult
    efficient_equilibrium: EquilibriumResult
    social_cost: Line
    overuse: float
    corrective_fee: float
    deadweight_loss: float


def analyze_common_resource(
    private_benefit: Line,
    private_cost: Line,
    *,
    marginal_congestion_cost: float,
) -> CommonResourceResult:
    """Treat congestion/depletion damage as a marginal external cost."""
    externality = analyze_externality(
        private_benefit,
        private_cost,
        ExternalityScenario(marginal_external_cost=marginal_congestion_cost),
    )
    return CommonResourceResult(
        private_benefit=private_benefit,
        private_cost=private_cost,
        open_access_equilibrium=externality.private_equilibrium,
        efficient_equilibrium=externality.social_equilibrium,
        social_cost=externality.social_supply,
        overuse=max(0.0, externality.quantity_distortion),
        corrective_fee=externality.corrective_tax,
        deadweight_loss=externality.deadweight_loss,
    )


__all__ = ["CommonResourceResult", "analyze_common_resource"]
