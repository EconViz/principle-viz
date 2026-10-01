"""Public-good demand aggregation and efficient provision."""

from __future__ import annotations

from dataclasses import dataclass

from principle_viz.core.equilibrium import solve_equilibrium
from principle_viz.core.line import EPSILON, Line
from principle_viz.exceptions import LineError


@dataclass(frozen=True, slots=True)
class IndividualBenefit:
    name: str
    marginal_benefit: Line


@dataclass(frozen=True, slots=True)
class PublicGoodPoint:
    quantity: float
    individual_benefits: tuple[float, ...]
    social_marginal_benefit: float
    marginal_cost: float


@dataclass(frozen=True, slots=True)
class PublicGoodResult:
    individuals: tuple[IndividualBenefit, ...]
    marginal_cost: Line
    points: tuple[PublicGoodPoint, ...]
    efficient_quantity: float
    efficient_marginal_value: float
    private_provision_quantity: float
    free_rider_gap: float


def _benefits_at(
    individuals: tuple[IndividualBenefit, ...], quantity: float
) -> tuple[float, ...]:
    return tuple(
        max(0.0, individual.marginal_benefit.p_at(quantity))
        for individual in individuals
    )


def analyze_public_good(
    individuals: tuple[IndividualBenefit, ...],
    marginal_cost: Line,
    *,
    samples: int = 101,
) -> PublicGoodResult:
    """Vertically sum individual marginal benefits and solve Samuelson provision."""
    if not individuals:
        raise ValueError("At least one individual benefit curve is required.")
    if samples < 3:
        raise ValueError("samples must be at least 3.")
    for individual in individuals:
        intercept, slope = individual.marginal_benefit.to_inverse()
        if intercept <= 0 or slope >= -EPSILON:
            raise LineError("Individual marginal benefits must slope downward.")
    _, cost_slope = marginal_cost.to_inverse()
    if cost_slope < -EPSILON:
        raise LineError("Public-good marginal cost must be flat or upward sloping.")

    q_max = max(individual.marginal_benefit.q_intercept() for individual in individuals)

    def gap(quantity: float) -> float:
        return sum(_benefits_at(individuals, quantity)) - marginal_cost.p_at(quantity)

    if gap(0.0) <= 0:
        efficient_quantity = 0.0
    else:
        low, high = 0.0, q_max
        for _ in range(100):
            midpoint = 0.5 * (low + high)
            if gap(midpoint) > 0:
                low = midpoint
            else:
                high = midpoint
        efficient_quantity = 0.5 * (low + high)

    private_quantities: list[float] = []
    for individual in individuals:
        equilibrium = solve_equilibrium(individual.marginal_benefit, marginal_cost)
        if equilibrium.is_valid_market:
            private_quantities.append(max(0.0, equilibrium.q_star))
    private_quantity = max(private_quantities, default=0.0)

    points = tuple(
        PublicGoodPoint(
            quantity=quantity,
            individual_benefits=_benefits_at(individuals, quantity),
            social_marginal_benefit=sum(_benefits_at(individuals, quantity)),
            marginal_cost=marginal_cost.p_at(quantity),
        )
        for quantity in (q_max * index / (samples - 1) for index in range(samples))
    )
    return PublicGoodResult(
        individuals=individuals,
        marginal_cost=marginal_cost,
        points=points,
        efficient_quantity=efficient_quantity,
        efficient_marginal_value=marginal_cost.p_at(efficient_quantity),
        private_provision_quantity=private_quantity,
        free_rider_gap=max(0.0, efficient_quantity - private_quantity),
    )


__all__ = [
    "IndividualBenefit",
    "PublicGoodPoint",
    "PublicGoodResult",
    "analyze_public_good",
]
