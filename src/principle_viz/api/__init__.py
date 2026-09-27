"""Public API facade."""

from principle_viz.api.facade import (
    build_dwl_report,
    build_tax_visual_guide,
    comparative_statics,
    compare_tax_scenario,
    compute_arc_elasticity,
    compute_point_elasticity,
    compute_surplus,
    evaluate_price_control,
    line_from_inverse,
    line_from_standard,
    solve_equilibrium,
    solve_tax_equilibrium,
)

__all__ = [
    "build_dwl_report",
    "build_tax_visual_guide",
    "comparative_statics",
    "compare_tax_scenario",
    "compute_arc_elasticity",
    "compute_point_elasticity",
    "compute_surplus",
    "evaluate_price_control",
    "line_from_inverse",
    "line_from_standard",
    "solve_equilibrium",
    "solve_tax_equilibrium",
]
