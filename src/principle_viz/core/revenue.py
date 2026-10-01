"""Price elasticity and total-revenue schedules for linear demand."""

from __future__ import annotations

from dataclasses import dataclass

from principle_viz.core.elasticity import point_price_elasticity
from principle_viz.core.line import EPSILON, Line
from principle_viz.exceptions import LineError


@dataclass(frozen=True, slots=True)
class RevenuePoint:
    quantity: float
    price: float
    total_revenue: float
    elasticity: float
    classification: str


@dataclass(frozen=True, slots=True)
class ElasticityRevenueResult:
    points: tuple[RevenuePoint, ...]
    unit_elastic_quantity: float
    unit_elastic_price: float
    maximum_revenue: float
    choke_quantity: float
    choke_price: float


def elasticity_revenue_schedule(
    demand: Line, *, samples: int = 101
) -> ElasticityRevenueResult:
    intercept, slope = demand.to_inverse()
    if intercept <= 0 or slope >= -EPSILON:
        raise LineError("Elasticity-revenue diagrams require downward-sloping demand.")
    if samples < 3:
        raise ValueError("samples must be at least 3.")
    choke_quantity = -intercept / slope
    unit_quantity = choke_quantity / 2.0
    unit_price = intercept / 2.0
    points: list[RevenuePoint] = []
    for index in range(1, samples + 1):
        quantity = choke_quantity * index / (samples + 1)
        price = demand.p_at(quantity)
        elasticity = point_price_elasticity(demand, quantity)
        magnitude = abs(elasticity)
        classification = (
            "unit_elastic"
            if abs(magnitude - 1.0) <= 1e-9
            else "elastic"
            if magnitude > 1.0
            else "inelastic"
        )
        points.append(
            RevenuePoint(quantity, price, price * quantity, elasticity, classification)
        )
    return ElasticityRevenueResult(
        points=tuple(points),
        unit_elastic_quantity=unit_quantity,
        unit_elastic_price=unit_price,
        maximum_revenue=unit_quantity * unit_price,
        choke_quantity=choke_quantity,
        choke_price=intercept,
    )
