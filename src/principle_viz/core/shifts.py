"""Shift scenarios and comparative statics helpers."""

from __future__ import annotations

from dataclasses import dataclass

from principle_viz.core.equilibrium import EquilibriumResult, solve_equilibrium
from principle_viz.core.line import EPSILON, Line


@dataclass(frozen=True)
class ShiftSpec:
    """Shift/rotation parameters in inverse form P = a + bQ."""

    delta_intercept: float = 0.0
    delta_slope: float = 0.0

    def apply(self, line: Line) -> Line:
        """Apply shift to line."""
        return line.shifted(
            delta_intercept=float(self.delta_intercept),
            delta_slope=float(self.delta_slope),
        )


@dataclass(frozen=True)
class ShiftScenario:
    """Demand/supply shift setup."""

    demand_shift: ShiftSpec | None = None
    supply_shift: ShiftSpec | None = None


@dataclass(frozen=True)
class ShiftedMarket:
    """Baseline and shifted line pair."""

    baseline_demand: Line
    baseline_supply: Line
    shifted_demand: Line
    shifted_supply: Line


@dataclass(frozen=True)
class ComparativeStaticsResult:
    """Comparative statics between baseline and shifted equilibria."""

    baseline_equilibrium: EquilibriumResult
    shifted_equilibrium: EquilibriumResult
    shifted_market: ShiftedMarket
    delta_q: float
    delta_p: float
    direction_q: str
    direction_p: str


def _direction(
    delta: float, positive_label: str, negative_label: str, tol: float = EPSILON
) -> str:
    if delta > tol:
        return positive_label
    if delta < -tol:
        return negative_label
    return "none"


def apply_shifts(demand: Line, supply: Line, scenario: ShiftScenario) -> ShiftedMarket:
    """Apply demand/supply shifts to baseline lines."""
    demand_shift = scenario.demand_shift or ShiftSpec()
    supply_shift = scenario.supply_shift or ShiftSpec()

    shifted_demand = demand_shift.apply(demand)
    shifted_supply = supply_shift.apply(supply)

    return ShiftedMarket(
        baseline_demand=demand,
        baseline_supply=supply,
        shifted_demand=shifted_demand,
        shifted_supply=shifted_supply,
    )


def comparative_statics(
    demand: Line, supply: Line, scenario: ShiftScenario
) -> ComparativeStaticsResult:
    """Solve baseline and shifted equilibria with movement metadata."""
    shifted = apply_shifts(demand, supply, scenario)

    baseline_eq = solve_equilibrium(shifted.baseline_demand, shifted.baseline_supply)
    shifted_eq = solve_equilibrium(shifted.shifted_demand, shifted.shifted_supply)

    delta_q = shifted_eq.q_star - baseline_eq.q_star
    delta_p = shifted_eq.p_star - baseline_eq.p_star

    return ComparativeStaticsResult(
        baseline_equilibrium=baseline_eq,
        shifted_equilibrium=shifted_eq,
        shifted_market=shifted,
        delta_q=delta_q,
        delta_p=delta_p,
        direction_q=_direction(delta_q, positive_label="right", negative_label="left"),
        direction_p=_direction(delta_p, positive_label="up", negative_label="down"),
    )
