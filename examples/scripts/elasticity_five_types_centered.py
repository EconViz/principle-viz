"""Centered demand and supply elasticity-type diagrams."""

from __future__ import annotations

from common import EXAMPLE_PALETTE, ensure_output_dir, themed_output_path
from mosaickit import DashStyle, PathLayer, Stroke

from principle_viz.core.equilibrium import EquilibriumResult
from principle_viz.plot import MarketFigure
from principle_viz.visuals import curve_label_layer

Q0 = 5.0
P0 = 5.0
Q_MIN = 0.0
Q_MAX = 10.0
Y_MIN = 0.0
Y_MAX = 10.0
# The axes run past the lines so each line is named beside its end.
AXIS_MAX = 12.0
THEME = "elasticity"


def _line_points(slope: float) -> tuple[tuple[float, float], tuple[float, float]]:
    """The line through (Q0, P0), kept inside the [0, 10] x [0, 10] box."""
    intercept = P0 - slope * Q0
    q_at_bottom = (Y_MIN - intercept) / slope
    q_at_top = (Y_MAX - intercept) / slope
    q_lo = max(Q_MIN, min(q_at_bottom, q_at_top))
    q_hi = min(Q_MAX, max(q_at_bottom, q_at_top))
    return ((q_lo, intercept + slope * q_lo), (q_hi, intercept + slope * q_hi))


def _plot_types(kind: str, slopes: tuple[float, float, float], filename: str) -> None:
    fig = MarketFigure(
        x_max=AXIS_MAX,
        y_max=AXIS_MAX,
        title=f"{kind} Elasticity Types",
        palette=EXAMPLE_PALETTE,
    )
    specs = (
        ("Perfectly Elastic", ((Q_MIN, P0), (Q_MAX, P0)), DashStyle.SOLID),
        ("Elastic", _line_points(slopes[0]), DashStyle.DASHED),
        ("Unit Elastic", _line_points(slopes[1]), DashStyle.DASHDOT),
        ("Inelastic", _line_points(slopes[2]), DashStyle.DOTTED),
        ("Perfectly Inelastic", ((Q0, Y_MIN), (Q0, Y_MAX + 1)), DashStyle.SOLID),
    )
    curves = tuple(
        PathLayer(
            points,
            id=f"elasticity.type.{index}",
            role="principle.annotation",
            legend=label,
            stroke=Stroke(color="#111111", width=2.0, dash=dash),
            z_index=2,
        )
        for index, (label, points, dash) in enumerate(specs)
    )
    fig.add_layers(curves)
    fig.add_layers(
        curve_label_layer(curve, x_range=(0, AXIS_MAX), y_range=(0, AXIS_MAX))
        for curve in curves
    )
    fig.add_equilibrium(EquilibriumResult(Q0, P0, is_valid_market=True))
    fig.finalize()
    fig.save(themed_output_path(THEME, filename))


def main() -> None:
    ensure_output_dir(THEME)
    _plot_types("Demand", (-0.5, -1.0, -2.0), "demand_elasticity_five_types.png")
    _plot_types("Supply", (0.5, 1.0, 2.0), "supply_elasticity_five_types.png")


if __name__ == "__main__":
    main()
