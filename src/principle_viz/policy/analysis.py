"""Tax scenario comparative analysis."""

from __future__ import annotations

from principle_viz.core.equilibrium import solve_equilibrium
from principle_viz.core.line import EPSILON, Line
from principle_viz.policy.models import TaxComparisonResult, TaxScenario
from principle_viz.policy.solver import solve_tax_equilibrium


def _direction(
    delta: float, positive_label: str, negative_label: str, tol: float = EPSILON
) -> str:
    if delta > tol:
        return positive_label
    if delta < -tol:
        return negative_label
    return "none"


def compare_tax_scenario(
    demand: Line, supply: Line, scenario: TaxScenario
) -> TaxComparisonResult:
    """Compute baseline and post-tax comparison, with movement directions."""
    baseline = solve_equilibrium(demand, supply)
    post_tax = solve_tax_equilibrium(demand, supply, scenario)

    delta_q = post_tax.q_star - baseline.q_star
    delta_p_consumer = post_tax.consumer_price - baseline.p_star
    delta_p_producer = post_tax.producer_price - baseline.p_star

    return TaxComparisonResult(
        baseline_equilibrium=baseline,
        post_tax=post_tax,
        delta_q=delta_q,
        delta_p_consumer=delta_p_consumer,
        delta_p_producer=delta_p_producer,
        direction_q=_direction(delta_q, positive_label="right", negative_label="left"),
        direction_p_consumer=_direction(
            delta_p_consumer, positive_label="up", negative_label="down"
        ),
        direction_p_producer=_direction(
            delta_p_producer, positive_label="up", negative_label="down"
        ),
    )
