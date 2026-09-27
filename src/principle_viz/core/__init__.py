"""Core domain and solvers for linear market analysis."""

from principle_viz.core.controls import (
    PriceControlResult,
    PriceControlScenario,
    PriceControlType,
    evaluate_price_control,
)
from principle_viz.core.elasticity import (
    arc_price_elasticity,
    classify_elasticity,
    point_price_elasticity,
)
from principle_viz.core.equilibrium import EquilibriumResult, solve_equilibrium
from principle_viz.core.line import Line
from principle_viz.core.shifts import (
    ComparativeStaticsResult,
    ShiftedMarket,
    ShiftScenario,
    ShiftSpec,
    apply_shifts,
    comparative_statics,
)

__all__ = [
    "ComparativeStaticsResult",
    "EquilibriumResult",
    "Line",
    "PriceControlResult",
    "PriceControlScenario",
    "PriceControlType",
    "ShiftScenario",
    "ShiftSpec",
    "ShiftedMarket",
    "apply_shifts",
    "arc_price_elasticity",
    "classify_elasticity",
    "comparative_statics",
    "evaluate_price_control",
    "point_price_elasticity",
    "solve_equilibrium",
]
