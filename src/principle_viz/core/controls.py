"""Price control models for ceilings and floors."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from principle_viz.core.equilibrium import EquilibriumResult, solve_equilibrium
from principle_viz.core.line import EPSILON, Line


class PriceControlType(str, Enum):
    """Supported price control types."""

    CEILING = "ceiling"
    FLOOR = "floor"


@dataclass(frozen=True)
class PriceControlScenario:
    """Price control scenario definition."""

    control_type: PriceControlType
    control_price: float


@dataclass(frozen=True)
class PriceControlResult:
    """Price control output with quantity rationing metadata."""

    control_type: PriceControlType
    control_price: float
    is_binding: bool
    traded_quantity: float
    consumer_price: float
    producer_price: float
    shortage: float
    surplus: float
    baseline_equilibrium: EquilibriumResult


def evaluate_price_control(
    demand: Line,
    supply: Line,
    scenario: PriceControlScenario,
    tol: float = EPSILON,
) -> PriceControlResult:
    """Evaluate binding/non-binding control outcomes."""
    baseline_eq = solve_equilibrium(demand, supply)
    control_price = float(scenario.control_price)

    qd = demand.q_at(control_price)
    qs = supply.q_at(control_price)

    if scenario.control_type == PriceControlType.CEILING:
        is_binding = control_price < baseline_eq.p_star - tol
        if is_binding:
            traded_quantity = min(qd, qs)
            shortage = max(0.0, qd - qs)
            surplus = 0.0
        else:
            traded_quantity = baseline_eq.q_star
            shortage = 0.0
            surplus = 0.0
    else:
        is_binding = control_price > baseline_eq.p_star + tol
        if is_binding:
            traded_quantity = min(qd, qs)
            shortage = 0.0
            surplus = max(0.0, qs - qd)
        else:
            traded_quantity = baseline_eq.q_star
            shortage = 0.0
            surplus = 0.0

    if not is_binding:
        consumer_price = baseline_eq.p_star
        producer_price = baseline_eq.p_star
    else:
        consumer_price = control_price
        producer_price = control_price

    return PriceControlResult(
        control_type=scenario.control_type,
        control_price=control_price,
        is_binding=is_binding,
        traded_quantity=max(0.0, traded_quantity),
        consumer_price=consumer_price,
        producer_price=producer_price,
        shortage=shortage,
        surplus=surplus,
        baseline_equilibrium=baseline_eq,
    )
