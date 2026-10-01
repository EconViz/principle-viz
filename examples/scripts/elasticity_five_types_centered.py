"""Centered demand and supply elasticity-type diagrams."""

from __future__ import annotations

from common import EXAMPLE_PALETTE, ensure_output_dir, themed_output_path
from mosaickit import DashStyle, Marker, MarkerLayer, PathLayer, Stroke, TextLayer

from principle_viz.plot import MarketFigure

Q0 = 5.0
P0 = 5.0
Q_MIN = 0.0
Q_MAX = 10.0
Y_MIN = 0.0
Y_MAX = 10.0
THEME = "elasticity"


def _line_points(slope: float) -> tuple[tuple[float, float], tuple[float, float]]:
    intercept = P0 - slope * Q0
    return ((Q_MIN, intercept + slope * Q_MIN), (Q_MAX, intercept + slope * Q_MAX))


def _add_center_point(fig: MarketFigure) -> None:
    fig.add_layers(
        (
            MarkerLayer(
                ((Q0, P0),),
                id="elasticity.center",
                role="principle.market.equilibrium",
                marker=Marker(
                    color=fig.theme.baseline_color,
                    edge_color=fig.theme.baseline_color,
                    edge_width=0,
                    size=48,
                ),
                z_index=6,
            ),
            TextLayer(
                (Q0, P0),
                r"$e^{*}$",
                id="elasticity.center.label",
                role="principle.market.equilibrium",
                offset=(14, 14),
                anchor="left",
                z_index=7,
            ),
        )
    )


def _plot_types(kind: str, slopes: tuple[float, float, float], filename: str) -> None:
    fig = MarketFigure(
        x_max=Q_MAX,
        y_max=Y_MAX,
        x_label="Q",
        y_label="P",
        title=f"{kind}: Five Elasticity Types (Centered)",
        palette=EXAMPLE_PALETTE,
    )
    specs = (
        ("Perfectly Elastic", ((Q_MIN, P0), (Q_MAX, P0)), DashStyle.SOLID),
        ("Elastic", _line_points(slopes[0]), DashStyle.DASHED),
        ("Unit Elastic", _line_points(slopes[1]), DashStyle.DASHDOT),
        ("Inelastic", _line_points(slopes[2]), DashStyle.DOTTED),
        ("Perfectly Inelastic", ((Q0, Y_MIN), (Q0, Y_MAX)), DashStyle.SOLID),
    )
    for index, (label, points, dash) in enumerate(specs):
        fig.add_layer(
            PathLayer(
                points,
                id=f"elasticity.type.{index}",
                role="principle.market.demand",
                legend=label,
                stroke=Stroke(color="#111111", width=2.0, dash=dash),
                z_index=2,
            )
        )
    _add_center_point(fig)
    fig.finalize(legend=True)
    fig.save(themed_output_path(THEME, filename))


def main() -> None:
    ensure_output_dir(THEME)
    _plot_types("Demand", (-0.5, -1.0, -2.0), "demand_elasticity_five_types.png")
    _plot_types("Supply", (0.5, 1.0, 2.0), "supply_elasticity_five_types.png")


if __name__ == "__main__":
    main()
