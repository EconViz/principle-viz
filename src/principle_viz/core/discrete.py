"""Discrete unit demand and supply schedules."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from itertools import pairwise

from principle_viz.exceptions import EquilibriumError, PrincipleEconError


class DiscreteMarketError(PrincipleEconError):
    """Raised for invalid discrete schedules."""


class EquilibriumPriceRule(str, Enum):
    MIDPOINT = "midpoint"
    LOWER = "lower"
    UPPER = "upper"


def _values(raw: tuple[float, ...]) -> tuple[float, ...]:
    values = tuple(float(value) for value in raw)
    if not values:
        raise DiscreteMarketError("A discrete schedule requires at least one unit.")
    if any(not math.isfinite(value) or value < 0 for value in values):
        raise DiscreteMarketError("Schedule values must be finite and nonnegative.")
    return values


@dataclass(frozen=True, slots=True)
class DiscreteDemand:
    """Marginal willingness-to-pay values ordered from first to last unit."""

    values: tuple[float, ...]

    def __post_init__(self) -> None:
        values = _values(self.values)
        if any(left < right for left, right in pairwise(values)):
            raise DiscreteMarketError("Demand values must be weakly decreasing.")
        object.__setattr__(self, "values", values)

    @property
    def unit_count(self) -> int:
        return len(self.values)


@dataclass(frozen=True, slots=True)
class DiscreteSupply:
    """Marginal cost values ordered from first to last unit."""

    values: tuple[float, ...]

    def __post_init__(self) -> None:
        values = _values(self.values)
        if any(left > right for left, right in pairwise(values)):
            raise DiscreteMarketError("Supply values must be weakly increasing.")
        object.__setattr__(self, "values", values)

    @property
    def unit_count(self) -> int:
        return len(self.values)


@dataclass(frozen=True, slots=True)
class DiscreteEquilibriumResult:
    q_star: int
    price_low: float
    price_high: float
    price: float
    traded_values: tuple[float, ...]
    traded_costs: tuple[float, ...]
    gains_from_trade: tuple[float, ...]
    price_rule: EquilibriumPriceRule
    notes: tuple[str, ...] = ()

    @property
    def is_unique_price(self) -> bool:
        return math.isclose(self.price_low, self.price_high)


def solve_discrete_equilibrium(
    demand: DiscreteDemand,
    supply: DiscreteSupply,
    *,
    price_rule: EquilibriumPriceRule | str = EquilibriumPriceRule.MIDPOINT,
    tolerance: float = 1e-9,
) -> DiscreteEquilibriumResult:
    """Find efficient trades and the competitive supporting-price interval."""
    if not math.isfinite(tolerance) or tolerance < 0:
        raise DiscreteMarketError("tolerance must be finite and nonnegative.")
    rule = EquilibriumPriceRule(price_rule)
    limit = min(demand.unit_count, supply.unit_count)
    quantity = 0
    for value, cost in zip(demand.values[:limit], supply.values[:limit]):
        if value + tolerance < cost:
            break
        quantity += 1

    last_value = demand.values[quantity - 1] if quantity else math.inf
    last_cost = supply.values[quantity - 1] if quantity else 0.0
    next_value = demand.values[quantity] if quantity < demand.unit_count else 0.0
    next_cost = supply.values[quantity] if quantity < supply.unit_count else math.inf
    price_low = max(0.0, last_cost, next_value)
    price_high = min(last_value, next_cost)
    if price_low > price_high + tolerance:
        raise EquilibriumError("Discrete market has no supporting competitive price.")
    if math.isclose(price_low, price_high, abs_tol=tolerance):
        price_low = price_high = 0.5 * (price_low + price_high)

    price = {
        EquilibriumPriceRule.LOWER: price_low,
        EquilibriumPriceRule.UPPER: price_high,
        EquilibriumPriceRule.MIDPOINT: 0.5 * (price_low + price_high),
    }[rule]
    traded_values = demand.values[:quantity]
    traded_costs = supply.values[:quantity]
    notes = () if price_low == price_high else ("Equilibrium price is an interval.",)
    return DiscreteEquilibriumResult(
        q_star=quantity,
        price_low=price_low,
        price_high=price_high,
        price=price,
        traded_values=traded_values,
        traded_costs=traded_costs,
        gains_from_trade=tuple(
            value - cost for value, cost in zip(traded_values, traded_costs)
        ),
        price_rule=rule,
        notes=notes,
    )
