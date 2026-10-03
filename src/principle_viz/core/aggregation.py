"""Horizontal summation of individual linear demand and supply curves."""

from __future__ import annotations

import math
from collections.abc import Iterable
from itertools import pairwise

from principle_viz.core.equilibrium import EquilibriumResult
from principle_viz.core.line import EPSILON, Line
from principle_viz.core.piecewise import PiecewiseLinear
from principle_viz.exceptions import EquilibriumError, PrincipleVizError


class AggregationError(PrincipleVizError):
    """Raised for individual curves that cannot be summed into a market curve."""


def _individuals(lines: Iterable[Line]) -> tuple[Line, ...]:
    lines = tuple(lines)
    if not lines:
        raise AggregationError("Aggregation needs at least one individual curve.")
    return lines


def _slope(line: Line, *, downward: bool) -> float:
    direction = "downward" if downward else "upward"
    if abs(line.p_coef) < EPSILON or abs(line.q_coef) < EPSILON:
        raise AggregationError(f"Individual curves must slope {direction}.")
    slope = line.slope()
    if (slope >= 0) if downward else (slope <= 0):
        raise AggregationError(f"Individual curves must slope {direction}.")
    return slope


def _sum_at(lines: tuple[Line, ...], price: float) -> float:
    return sum(max(0.0, line.q_at(price)) for line in lines)


def _distinct(prices: Iterable[float]) -> list[float]:
    distinct: list[float] = []
    for price in sorted(prices):
        if not distinct or not math.isclose(price, distinct[-1], abs_tol=EPSILON):
            distinct.append(price)
    return distinct


def market_demand(individuals: Iterable[Line]) -> PiecewiseLinear:
    """Sum downward-sloping individual demands horizontally.

    Each individual buys nothing above their choke price, so the market curve
    kinks at every choke price below the highest one and ends on the Q axis.
    """
    lines = _individuals(individuals)
    for line in lines:
        _slope(line, downward=True)
        if line.p_intercept() <= 0:
            raise AggregationError("Each demand needs a positive choke price.")
    prices = _distinct([0.0, *(line.p_intercept() for line in lines)])
    return PiecewiseLinear(
        tuple((_sum_at(lines, price), price) for price in reversed(prices))
    )


def market_supply(individuals: Iterable[Line], *, p_max: float) -> PiecewiseLinear:
    """Sum upward-sloping individual supplies horizontally up to ``p_max``.

    Each individual sells nothing below their minimum price, so the market curve
    starts at the lowest minimum price and kinks at every other one.
    """
    lines = _individuals(individuals)
    for line in lines:
        _slope(line, downward=False)
        if line.p_intercept() < 0:
            raise AggregationError("Each supply needs a nonnegative minimum price.")
    minimums = [line.p_intercept() for line in lines]
    if not math.isfinite(p_max) or p_max <= max(minimums):
        raise AggregationError(
            f"p_max must exceed every individual's minimum price ({max(minimums):g})."
        )
    prices = _distinct([*minimums, float(p_max)])
    return PiecewiseLinear(tuple((_sum_at(lines, price), price) for price in prices))


def solve_piecewise_equilibrium(
    demand: PiecewiseLinear, supply: PiecewiseLinear
) -> EquilibriumResult:
    """Price where market demand meets market supply, exact on each segment."""
    if not demand.is_downward_sloping or supply.is_downward_sloping:
        raise EquilibriumError("Need a downward-sloping demand and an upward supply.")
    top = demand.price_range[1]
    if demand.points[0][0] == 0.0 and top <= supply.price_range[0]:
        raise EquilibriumError(
            "no trade: the highest choke price is at or below the lowest minimum price."
        )
    low = max(demand.price_range[0], 0.0)
    high = supply.price_range[1]

    def excess(price: float) -> float:
        return demand.q_at(price) - supply.q_at(price)

    if excess(high) > 0:
        raise EquilibriumError(
            "Demand exceeds supply at the supply curve's p_max; raise p_max."
        )
    cuts = sorted(
        {
            low,
            high,
            *(p for p in demand.breakpoints() + supply.breakpoints() if low < p < high),
        }
    )
    for left, right in pairwise(cuts):
        left_gap, right_gap = excess(left), excess(right)
        if left_gap >= 0 >= right_gap:
            price = (
                left
                if left_gap == right_gap
                else left + (right - left) * left_gap / (left_gap - right_gap)
            )
            return EquilibriumResult(
                q_star=supply.q_at(price), p_star=price, is_valid_market=True
            )
    raise EquilibriumError(  # pragma: no cover - excess demand is monotone
        "Market demand and supply do not cross."
    )


def piecewise_surplus(
    demand: PiecewiseLinear,
    supply: PiecewiseLinear,
    equilibrium: EquilibriumResult,
) -> tuple[float, float]:
    """Consumer and producer surplus at ``equilibrium``, integrated along price."""
    price = equilibrium.p_star
    consumer = demand.integrate_q(price, max(price, demand.price_range[1]))
    producer = supply.integrate_q(min(price, supply.price_range[0]), price)
    return consumer, producer


__all__ = [
    "AggregationError",
    "market_demand",
    "market_supply",
    "piecewise_surplus",
    "solve_piecewise_equilibrium",
]
