"""Externality, social-optimum, and corrective-policy analysis."""

from __future__ import annotations

import math
from dataclasses import dataclass

from principle_viz.core.equilibrium import EquilibriumResult, solve_equilibrium
from principle_viz.core.line import Line
from principle_viz.exceptions import PolicyError


@dataclass(frozen=True, slots=True)
class ExternalityScenario:
    marginal_external_cost: float = 0.0
    marginal_external_benefit: float = 0.0

    def __post_init__(self) -> None:
        values = (self.marginal_external_cost, self.marginal_external_benefit)
        if not all(math.isfinite(value) and value >= 0 for value in values):
            raise PolicyError(
                "Marginal external effects must be finite and nonnegative."
            )


@dataclass(frozen=True, slots=True)
class ExternalityResult:
    private_equilibrium: EquilibriumResult
    social_equilibrium: EquilibriumResult
    social_demand: Line
    social_supply: Line
    corrective_tax: float
    corrective_subsidy: float
    quantity_distortion: float
    deadweight_loss: float


def analyze_externality(
    demand: Line,
    supply: Line,
    scenario: ExternalityScenario,
) -> ExternalityResult:
    """Compare the private market outcome with the social optimum."""
    private = solve_equilibrium(demand, supply)
    social_demand = demand.shifted(delta_intercept=scenario.marginal_external_benefit)
    social_supply = supply.shifted(delta_intercept=scenario.marginal_external_cost)
    social = solve_equilibrium(social_demand, social_supply)
    net_external_cost = (
        scenario.marginal_external_cost - scenario.marginal_external_benefit
    )
    quantity_distortion = private.q_star - social.q_star
    return ExternalityResult(
        private_equilibrium=private,
        social_equilibrium=social,
        social_demand=social_demand,
        social_supply=social_supply,
        corrective_tax=max(0.0, net_external_cost),
        corrective_subsidy=max(0.0, -net_external_cost),
        quantity_distortion=quantity_distortion,
        deadweight_loss=0.5 * abs(quantity_distortion) * abs(net_external_cost),
    )


__all__ = ["ExternalityResult", "ExternalityScenario", "analyze_externality"]
