"""Centered elasticity-type example: exactly two output figures.

Outputs:
- examples/output/elasticity_five_types_centered/demand_elasticity_five_types.png
- examples/output/elasticity_five_types_centered/supply_elasticity_five_types.png
"""

from __future__ import annotations

import numpy as np
from common import EXAMPLE_PALETTE, ensure_output_dir, themed_output_path

from principle_viz.plot import MarketFigure
from principle_viz.plot.primitives import annotate_text, plot_point

Q0 = 5.0
P0 = 5.0
Q_MIN = 0.0
Q_MAX = 10.0
Y_MIN = 0.0
Y_MAX = 10.0
THEME = "elasticity"
DEMAND_FILENAME = "demand_elasticity_five_types.png"
SUPPLY_FILENAME = "supply_elasticity_five_types.png"



def _line_through_center(slope: float, q_values: np.ndarray) -> np.ndarray:
    intercept = P0 - slope * Q0
    return intercept + slope * q_values



def _add_center_point(fig: MarketFigure) -> None:
    plot_point(
        fig.ax,
        x=Q0,
        y=P0,
        color=fig.theme.baseline_color,
        marker_size=7.0,
    )
    annotate_text(
        fig.ax,
        x=Q0,
        y=P0,
        text=r"$e^{*}$",
        color=fig.theme.baseline_color,
        offset=(14, 14),
        curved_arrow=True,
        curvature=0.22,
    )



def _plot_demand_types() -> None:
    fig = MarketFigure(
        x_max=Q_MAX,
        y_max=Y_MAX,
        x_label="Q",
        y_label="P",
        title="Demand: Five Elasticity Types (Centered)",
        palette=EXAMPLE_PALETTE,
    )

    q = np.linspace(Q_MIN, Q_MAX, 300)

    # Perfectly elastic: horizontal line through center price.
    fig.ax.hlines(P0, Q_MIN, Q_MAX, colors="#111111", linewidth=2.2, linestyles="-", label="Perfectly Elastic")

    # Elastic / unit / inelastic are linear and all pass through the center.
    demand_specs = [
        ("Elastic", -0.5, "#111111", "--"),
        ("Unit Elastic", -1.0, "#111111", "-."),
        ("Inelastic", -2.0, "#111111", ":"),
    ]
    for label, slope, color, linestyle in demand_specs:
        p_vals = _line_through_center(slope, q)
        fig.ax.plot(q, p_vals, color=color, linewidth=2.0, linestyle=linestyle, label=label)

    # Perfectly inelastic: vertical line through center quantity.
    fig.ax.vlines(
        Q0,
        Y_MIN,
        Y_MAX,
        colors="#111111",
        linewidth=2.2,
        linestyles=(0, (4, 1, 1, 1)),
        label="Perfectly Inelastic",
    )

    _add_center_point(fig)
    fig.finalize(legend=True)
    fig.save(str(themed_output_path(THEME, DEMAND_FILENAME)))
    fig.close()



def _plot_supply_types() -> None:
    fig = MarketFigure(
        x_max=Q_MAX,
        y_max=Y_MAX,
        x_label="Q",
        y_label="P",
        title="Supply: Five Elasticity Types (Centered)",
        palette=EXAMPLE_PALETTE,
    )

    q = np.linspace(Q_MIN, Q_MAX, 300)

    # Perfectly elastic: horizontal line through center price.
    fig.ax.hlines(P0, Q_MIN, Q_MAX, colors="#111111", linewidth=2.2, linestyles="-", label="Perfectly Elastic")

    supply_specs = [
        ("Elastic", 0.5, "#111111", "--"),
        ("Unit Elastic", 1.0, "#111111", "-."),
        ("Inelastic", 2.0, "#111111", ":"),
    ]
    for label, slope, color, linestyle in supply_specs:
        p_vals = _line_through_center(slope, q)
        fig.ax.plot(q, p_vals, color=color, linewidth=2.0, linestyle=linestyle, label=label)

    # Perfectly inelastic: vertical line through center quantity.
    fig.ax.vlines(
        Q0,
        Y_MIN,
        Y_MAX,
        colors="#111111",
        linewidth=2.2,
        linestyles=(0, (4, 1, 1, 1)),
        label="Perfectly Inelastic",
    )

    _add_center_point(fig)
    fig.finalize(legend=True)
    fig.save(str(themed_output_path(THEME, SUPPLY_FILENAME)))
    fig.close()



def main() -> None:
    ensure_output_dir(THEME)
    _plot_demand_types()
    _plot_supply_types()


if __name__ == "__main__":
    main()
