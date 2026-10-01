"""Tax visualization helpers for anchored shifts/rotations."""

from __future__ import annotations

from dataclasses import dataclass

from principle_viz.core.equilibrium import EquilibriumResult, solve_equilibrium
from principle_viz.core.line import Line
from principle_viz.exceptions import PolicyError
from principle_viz.policy.models import AnchorMode, TaxOn, TaxScenario, TaxType


@dataclass(frozen=True)
class TaxVisualGuide:
    """Geometry guide for drawing taxed curves against a baseline market."""

    baseline_equilibrium: EquilibriumResult
    base_curve: Line
    taxed_curve: Line
    curve_role: str
    transform_kind: str


def _anchored_rotation(
    line: Line, *, anchor_q: float, anchor_p: float, slope_scale: float
) -> Line:
    intercept, slope = line.to_inverse()
    _ = intercept  # keep explicit to document that intercept is intentionally recomputed
    rotated_slope = slope * slope_scale
    rotated_intercept = anchor_p - rotated_slope * anchor_q
    return Line.from_inverse(rotated_intercept, rotated_slope)


def _origin_rotation(line: Line, *, slope_scale: float) -> Line:
    intercept, slope = line.to_inverse()
    return Line.from_inverse(intercept * slope_scale, slope * slope_scale)


def build_tax_visual_guide(
    demand: Line, supply: Line, scenario: TaxScenario
) -> TaxVisualGuide:
    """Build a baseline-vs-taxed curve guide for rendering classroom diagrams."""
    baseline = solve_equilibrium(demand, supply)

    if scenario.tax_type in {TaxType.FIXED_TAX, TaxType.PER_UNIT_TAX}:
        amount = float(scenario.amount)
        if scenario.tax_on == TaxOn.PRODUCER:
            return TaxVisualGuide(
                baseline_equilibrium=baseline,
                base_curve=supply,
                taxed_curve=supply.shifted(delta_intercept=amount),
                curve_role="supply",
                transform_kind="shift",
            )
        return TaxVisualGuide(
            baseline_equilibrium=baseline,
            base_curve=demand,
            taxed_curve=demand.shifted(delta_intercept=-amount),
            curve_role="demand",
            transform_kind="shift",
        )

    if scenario.tax_type != TaxType.AD_VALOREM_TAX:
        raise PolicyError(
            f"Unsupported tax type for visualization: {scenario.tax_type}"
        )

    rate = float(scenario.amount)
    if rate <= -1.0:
        raise PolicyError("Ad valorem rate must be greater than -1.")

    if scenario.tax_on == TaxOn.PRODUCER:
        base_curve = supply
        slope_scale = 1.0 + rate
        curve_role = "supply"
    else:
        base_curve = demand
        slope_scale = 1.0 / (1.0 + rate)
        curve_role = "demand"

    if scenario.anchor_mode == AnchorMode.BASELINE_EQUILIBRIUM:
        taxed_curve = _anchored_rotation(
            base_curve,
            anchor_q=baseline.q_star,
            anchor_p=baseline.p_star,
            slope_scale=slope_scale,
        )
    else:
        taxed_curve = _origin_rotation(base_curve, slope_scale=slope_scale)

    return TaxVisualGuide(
        baseline_equilibrium=baseline,
        base_curve=base_curve,
        taxed_curve=taxed_curve,
        curve_role=curve_role,
        transform_kind="rotation",
    )


__all__ = ["TaxVisualGuide", "build_tax_visual_guide"]
