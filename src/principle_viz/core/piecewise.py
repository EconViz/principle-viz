"""Monotone piecewise-linear curves in (Q, p) space."""

from __future__ import annotations

import math
from bisect import bisect_right
from dataclasses import dataclass
from itertools import pairwise

from principle_viz.exceptions import PrincipleVizError

Point = tuple[float, float]


class PiecewiseLinearError(PrincipleVizError):
    """Raised for invalid piecewise curves or points outside their domain."""


def _interpolate(x: float, x0: float, y0: float, x1: float, y1: float) -> float:
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)


@dataclass(frozen=True, slots=True)
class PiecewiseLinear:
    """A demand or supply curve through ``points`` ``(Q, p)``, ordered by quantity.

    Quantity strictly increases along the points and price strictly decreases
    (demand) or strictly increases (supply). If the first point has ``Q = 0``,
    the quantity is zero at prices beyond it: above it for demand (no one buys
    past the highest choke price), below it for supply.
    """

    points: tuple[Point, ...]

    def __post_init__(self) -> None:
        points = tuple((float(q), float(p)) for q, p in self.points)
        if len(points) < 2:
            raise PiecewiseLinearError("A piecewise curve needs at least two points.")
        if not all(math.isfinite(v) for point in points for v in point):
            raise PiecewiseLinearError("Piecewise curve points must be finite.")
        if any(right[0] <= left[0] for left, right in pairwise(points)):
            raise PiecewiseLinearError("Quantities must strictly increase.")
        steps = [right[1] - left[1] for left, right in pairwise(points)]
        if not (all(step < 0 for step in steps) or all(step > 0 for step in steps)):
            raise PiecewiseLinearError(
                "Prices must be strictly monotone (all falling or all rising)."
            )
        object.__setattr__(self, "points", points)

    @property
    def is_downward_sloping(self) -> bool:
        return self.points[1][1] < self.points[0][1]

    @property
    def kinks(self) -> tuple[Point, ...]:
        """Interior points where the slope changes."""
        return self.points[1:-1]

    @property
    def domain(self) -> tuple[float, float]:
        """Quantity range ``(Q_min, Q_max)``."""
        return self.points[0][0], self.points[-1][0]

    @property
    def price_range(self) -> tuple[float, float]:
        prices = (self.points[0][1], self.points[-1][1])
        return min(prices), max(prices)

    def p_at(self, q: float) -> float:
        """Price at quantity ``q`` within the domain."""
        q = float(q)
        low, high = self.domain
        if not low <= q <= high:
            raise PiecewiseLinearError(
                f"quantity {q:g} is outside the curve's domain [{low:g}, {high:g}]."
            )
        quantities = [point[0] for point in self.points]
        index = min(max(bisect_right(quantities, q), 1), len(self.points) - 1)
        (q0, p0), (q1, p1) = self.points[index - 1], self.points[index]
        return _interpolate(q, q0, p0, q1, p1)

    def q_at(self, p: float) -> float:
        """Quantity at price ``p``; zero past a ``Q = 0`` end."""
        p = float(p)
        low, high = self.price_range
        start_q, start_p = self.points[0]
        if start_q == 0.0 and (
            (self.is_downward_sloping and p >= start_p)
            or (not self.is_downward_sloping and p <= start_p)
        ):
            return 0.0
        if not low <= p <= high:
            raise PiecewiseLinearError(
                f"price {p:g} is outside the curve's range [{low:g}, {high:g}]."
            )
        for (q0, p0), (q1, p1) in pairwise(self.points):
            if min(p0, p1) <= p <= max(p0, p1):
                return _interpolate(p, p0, q0, p1, q1)
        raise AssertionError("unreachable: price inside range")  # pragma: no cover

    def breakpoints(self) -> tuple[float, ...]:
        """Vertex prices in ascending order."""
        return tuple(sorted(p for _, p in self.points))

    def integrate_q(self, p_low: float, p_high: float) -> float:
        """Area under Q(p) between two prices (surplus measured along p)."""
        if p_high < p_low:
            raise PiecewiseLinearError("p_low must not exceed p_high.")
        cuts = sorted(
            {p_low, p_high, *(p for p in self.breakpoints() if p_low < p < p_high)}
        )
        return sum(
            0.5 * (self.q_at(left) + self.q_at(right)) * (right - left)
            for left, right in pairwise(cuts)
        )


__all__ = ["PiecewiseLinear", "PiecewiseLinearError"]
