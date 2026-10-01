"""Convenience facade functions for principle_viz."""

from __future__ import annotations

from principle_viz.core.controls import (
    PriceControlScenario,
    PriceControlType,
    evaluate_price_control,
)
from principle_viz.core.discrete import (
    DiscreteDemand,
    DiscreteSupply,
    EquilibriumPriceRule,
    solve_discrete_equilibrium,
)
from principle_viz.core.elasticity import arc_price_elasticity, point_price_elasticity
from principle_viz.core.equilibrium import solve_equilibrium
from principle_viz.core.line import Line
from principle_viz.core.public_goods import analyze_public_good
from principle_viz.core.revenue import elasticity_revenue_schedule
from principle_viz.core.shifts import ShiftScenario, ShiftSpec, comparative_statics
from principle_viz.policy.common_resources import analyze_common_resource
from principle_viz.policy.externality import ExternalityScenario, analyze_externality
from principle_viz.policy.subsidy import (
    SubsidyScenario,
    compare_subsidy_scenario,
    solve_subsidy_equilibrium,
)
from principle_viz.policy.tax import (
    TaxScenario,
    build_tax_visual_guide,
    compare_tax_scenario,
    solve_tax_equilibrium,
)
from principle_viz.policy.trade import TradeScenario, analyze_trade
from principle_viz.welfare.report import build_dwl_report
from principle_viz.welfare.surplus import MarketOutcome
from principle_viz.welfare.surplus import compute_surplus as _compute_surplus


def line_from_inverse(intercept: float, slope: float) -> Line:
    """Create line from inverse form P = a + bQ."""
    return Line.from_inverse(intercept, slope)


def line_from_standard(a: float, b: float, c: float) -> Line:
    """Create line from standard form A*P + B*Q + C = 0."""
    return Line.from_standard(a, b, c)


def compute_point_elasticity(line: Line, quantity: float) -> float:
    """Compute point elasticity at quantity."""
    return point_price_elasticity(line, quantity)


def compute_arc_elasticity(q0: float, p0: float, q1: float, p1: float) -> float:
    """Compute arc elasticity between two points."""
    return arc_price_elasticity(q0, p0, q1, p1)


def solve_discrete_market(
    demand_values: tuple[float, ...],
    supply_values: tuple[float, ...],
    *,
    price_rule: EquilibriumPriceRule | str = EquilibriumPriceRule.MIDPOINT,
):
    """Construct discrete schedules and solve their competitive equilibrium."""
    return solve_discrete_equilibrium(
        DiscreteDemand(demand_values),
        DiscreteSupply(supply_values),
        price_rule=price_rule,
    )


def compute_surplus_from_prices(
    demand: Line,
    supply: Line,
    quantity: float,
    consumer_price: float,
    producer_price: float,
    baseline_quantity: float | None = None,
    baseline_consumer_price: float | None = None,
    baseline_producer_price: float | None = None,
):
    """Compatibility helper for direct price-quantity surplus calculations."""
    baseline = None
    if (
        baseline_quantity is not None
        and baseline_consumer_price is not None
        and baseline_producer_price is not None
    ):
        baseline = MarketOutcome(
            quantity=float(baseline_quantity),
            consumer_price=float(baseline_consumer_price),
            producer_price=float(baseline_producer_price),
            label="baseline",
        )

    outcome = MarketOutcome(
        quantity=float(quantity),
        consumer_price=float(consumer_price),
        producer_price=float(producer_price),
        label="policy",
    )
    return _compute_surplus(demand, supply, outcome, baseline_outcome=baseline)


def compute_surplus(
    demand: Line,
    supply: Line,
    outcome: MarketOutcome,
    baseline_outcome: MarketOutcome | None = None,
):
    """Expose surplus compute function through API facade."""
    return _compute_surplus(demand, supply, outcome, baseline_outcome=baseline_outcome)


__all__ = [
    "ExternalityScenario",
    "PriceControlScenario",
    "PriceControlType",
    "ShiftScenario",
    "ShiftSpec",
    "SubsidyScenario",
    "TaxScenario",
    "TradeScenario",
    "analyze_common_resource",
    "analyze_externality",
    "analyze_public_good",
    "analyze_trade",
    "build_dwl_report",
    "build_tax_visual_guide",
    "comparative_statics",
    "compare_subsidy_scenario",
    "compare_tax_scenario",
    "compute_arc_elasticity",
    "compute_point_elasticity",
    "compute_surplus",
    "compute_surplus_from_prices",
    "elasticity_revenue_schedule",
    "evaluate_price_control",
    "line_from_inverse",
    "line_from_standard",
    "solve_discrete_market",
    "solve_equilibrium",
    "solve_subsidy_equilibrium",
    "solve_tax_equilibrium",
]
