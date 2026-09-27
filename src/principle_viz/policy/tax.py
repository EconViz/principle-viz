"""Compatibility facade for tax policy API."""

from principle_viz.policy.analysis import compare_tax_scenario
from principle_viz.policy.models import (
    AnchorMode,
    TaxComparisonResult,
    TaxEquilibriumResult,
    TaxOn,
    TaxScenario,
    TaxType,
)
from principle_viz.policy.solver import solve_tax_equilibrium
from principle_viz.policy.visual import TaxVisualGuide, build_tax_visual_guide

__all__ = [
    "AnchorMode",
    "TaxComparisonResult",
    "TaxEquilibriumResult",
    "TaxOn",
    "TaxScenario",
    "TaxType",
    "TaxVisualGuide",
    "build_tax_visual_guide",
    "compare_tax_scenario",
    "solve_tax_equilibrium",
]
