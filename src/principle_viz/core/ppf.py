"""Production-possibilities frontiers and comparative advantage."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum

from principle_viz.core.line import EPSILON
from principle_viz.exceptions import PrincipleVizError


class PPFError(PrincipleVizError):
    """Raised for invalid production-possibilities inputs."""


class PointStatus(str, Enum):
    EFFICIENT = "efficient"
    INEFFICIENT = "inefficient"
    UNATTAINABLE = "unattainable"


@dataclass(frozen=True, slots=True)
class ProductionPossibilitiesFrontier:
    x_intercept: float
    y_intercept: float
    curvature: float = 1.0
    x_good: str = "Good X"
    y_good: str = "Good Y"

    def __post_init__(self) -> None:
        values = (self.x_intercept, self.y_intercept, self.curvature)
        if not all(math.isfinite(value) and value > 0 for value in values):
            raise PPFError("PPF intercepts and curvature must be finite and positive.")
        if self.curvature < 1:
            raise PPFError("PPF curvature must be at least 1.")

    def y_at(self, x: float) -> float:
        quantity = float(x)
        if quantity < 0 or quantity > self.x_intercept:
            raise PPFError("X quantity must lie on the PPF domain.")
        share = quantity / self.x_intercept
        return self.y_intercept * (1.0 - share**self.curvature)

    def opportunity_cost_x(self, x: float) -> float:
        """Return marginal units of Y forgone for one more unit of X."""
        quantity = float(x)
        if quantity < 0 or quantity > self.x_intercept:
            raise PPFError("X quantity must lie on the PPF domain.")
        share = quantity / self.x_intercept
        return (
            self.y_intercept
            * self.curvature
            / self.x_intercept
            * share ** (self.curvature - 1.0)
        )

    def assess(self, x: float, y: float, *, tolerance: float = EPSILON) -> PointStatus:
        x_value, y_value = float(x), float(y)
        if x_value < 0 or y_value < 0:
            raise PPFError("Production quantities must be nonnegative.")
        if x_value > self.x_intercept + tolerance:
            return PointStatus.UNATTAINABLE
        frontier_y = self.y_at(min(x_value, self.x_intercept))
        if abs(y_value - frontier_y) <= tolerance:
            return PointStatus.EFFICIENT
        if y_value < frontier_y:
            return PointStatus.INEFFICIENT
        return PointStatus.UNATTAINABLE


@dataclass(frozen=True, slots=True)
class PPFPoint:
    x: float
    y: float
    label: str
    status: PointStatus


@dataclass(frozen=True, slots=True)
class PPFAnalysisResult:
    frontier: ProductionPossibilitiesFrontier
    frontier_points: tuple[tuple[float, float], ...]
    assessed_points: tuple[PPFPoint, ...]


def analyze_ppf(
    frontier: ProductionPossibilitiesFrontier,
    points: tuple[tuple[float, float, str], ...] = (),
    *,
    samples: int = 101,
) -> PPFAnalysisResult:
    if samples < 2:
        raise ValueError("samples must be at least 2.")
    frontier_points = tuple(
        (x, frontier.y_at(x))
        for x in (
            frontier.x_intercept * index / (samples - 1) for index in range(samples)
        )
    )
    assessed = tuple(
        PPFPoint(x, y, label, frontier.assess(x, y)) for x, y, label in points
    )
    return PPFAnalysisResult(frontier, frontier_points, assessed)


@dataclass(frozen=True, slots=True)
class PPFGrowthScenario:
    x_growth_rate: float = 0.0
    y_growth_rate: float = 0.0

    def __post_init__(self) -> None:
        values = (self.x_growth_rate, self.y_growth_rate)
        if not all(math.isfinite(value) and value > -1 for value in values):
            raise PPFError("PPF growth rates must be finite and greater than -1.")


@dataclass(frozen=True, slots=True)
class PPFGrowthResult:
    baseline: ProductionPossibilitiesFrontier
    shifted: ProductionPossibilitiesFrontier
    baseline_points: tuple[tuple[float, float], ...]
    shifted_points: tuple[tuple[float, float], ...]


def analyze_ppf_growth(
    frontier: ProductionPossibilitiesFrontier,
    scenario: PPFGrowthScenario,
    *,
    samples: int = 101,
) -> PPFGrowthResult:
    shifted = ProductionPossibilitiesFrontier(
        x_intercept=frontier.x_intercept * (1 + scenario.x_growth_rate),
        y_intercept=frontier.y_intercept * (1 + scenario.y_growth_rate),
        curvature=frontier.curvature,
        x_good=frontier.x_good,
        y_good=frontier.y_good,
    )
    baseline_points = analyze_ppf(frontier, samples=samples).frontier_points
    shifted_points = analyze_ppf(shifted, samples=samples).frontier_points
    return PPFGrowthResult(frontier, shifted, baseline_points, shifted_points)


@dataclass(frozen=True, slots=True)
class ComparativeAdvantageResult:
    producer_a: str
    producer_b: str
    opportunity_cost_x_a: float
    opportunity_cost_x_b: float
    comparative_advantage_x: str
    comparative_advantage_y: str


def compare_linear_ppfs(
    producer_a: str,
    frontier_a: ProductionPossibilitiesFrontier,
    producer_b: str,
    frontier_b: ProductionPossibilitiesFrontier,
) -> ComparativeAdvantageResult:
    if (
        abs(frontier_a.curvature - 1) > EPSILON
        or abs(frontier_b.curvature - 1) > EPSILON
    ):
        raise PPFError("Comparative advantage requires linear PPFs.")
    cost_a = frontier_a.y_intercept / frontier_a.x_intercept
    cost_b = frontier_b.y_intercept / frontier_b.x_intercept
    if abs(cost_a - cost_b) <= EPSILON:
        advantage_x = advantage_y = "tie"
    elif cost_a < cost_b:
        advantage_x, advantage_y = producer_a, producer_b
    else:
        advantage_x, advantage_y = producer_b, producer_a
    return ComparativeAdvantageResult(
        producer_a=producer_a,
        producer_b=producer_b,
        opportunity_cost_x_a=cost_a,
        opportunity_cost_x_b=cost_b,
        comparative_advantage_x=advantage_x,
        comparative_advantage_y=advantage_y,
    )


__all__ = [
    "ComparativeAdvantageResult",
    "PPFAnalysisResult",
    "PPFError",
    "PPFGrowthResult",
    "PPFGrowthScenario",
    "PPFPoint",
    "PointStatus",
    "ProductionPossibilitiesFrontier",
    "analyze_ppf",
    "analyze_ppf_growth",
    "compare_linear_ppfs",
]
