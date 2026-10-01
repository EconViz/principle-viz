"""Welfare accounting for discrete unit markets."""

from __future__ import annotations

from dataclasses import dataclass

from principle_viz.core.discrete import DiscreteEquilibriumResult


@dataclass(frozen=True, slots=True)
class DiscreteSurplusResult:
    quantity: int
    price: float
    consumer_surplus: float
    producer_surplus: float
    total_surplus: float
    consumer_surplus_by_unit: tuple[float, ...]
    producer_surplus_by_unit: tuple[float, ...]


def compute_discrete_surplus(
    equilibrium: DiscreteEquilibriumResult,
) -> DiscreteSurplusResult:
    consumer = tuple(value - equilibrium.price for value in equilibrium.traded_values)
    producer = tuple(equilibrium.price - cost for cost in equilibrium.traded_costs)
    return DiscreteSurplusResult(
        quantity=equilibrium.q_star,
        price=equilibrium.price,
        consumer_surplus=sum(consumer),
        producer_surplus=sum(producer),
        total_surplus=sum(equilibrium.gains_from_trade),
        consumer_surplus_by_unit=consumer,
        producer_surplus_by_unit=producer,
    )
