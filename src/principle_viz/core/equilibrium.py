"""Linear market equilibrium solver."""

from __future__ import annotations

from dataclasses import dataclass

from principle_viz.core.line import EPSILON, Line
from principle_viz.exceptions import CoincidentLinesError, ParallelLinesError


@dataclass(frozen=True)
class EquilibriumResult:
    """Solved market equilibrium for demand/supply intersection."""

    q_star: float
    p_star: float
    is_valid_market: bool
    notes: tuple[str, ...] = ()



def solve_equilibrium(demand: Line, supply: Line, tol: float = EPSILON) -> EquilibriumResult:
    """Solve equilibrium from two linear equations."""
    a1, b1, c1 = demand.as_tuple()
    a2, b2, c2 = supply.as_tuple()

    det = a1 * b2 - a2 * b1
    if abs(det) <= tol:
        if demand.is_coincident(supply, tol=tol):
            raise CoincidentLinesError("Demand and supply are coincident; equilibrium is non-unique.")
        raise ParallelLinesError("Demand and supply are parallel; no equilibrium intersection exists.")

    p_star = ((-c1) * b2 - (-c2) * b1) / det
    q_star = (a1 * (-c2) - a2 * (-c1)) / det

    notes: list[str] = []
    is_valid_market = True
    if q_star < -tol:
        is_valid_market = False
        notes.append("Negative equilibrium quantity.")
    if p_star < -tol:
        notes.append("Negative equilibrium price.")

    return EquilibriumResult(
        q_star=float(q_star),
        p_star=float(p_star),
        is_valid_market=is_valid_market,
        notes=tuple(notes),
    )
