"""Single-line elasticity classification with five marked points."""

from __future__ import annotations

from common import EXAMPLE_PALETTE, ensure_output_dir, themed_output_path
from mosaickit import Marker, MarkerLayer, PointLabelLayer, TextStyle

from principle_viz.core.elasticity import point_price_elasticity
from principle_viz.core.line import Line
from principle_viz.plot.figure import MarketFigure
from principle_viz.visuals import curve_layer

THEME = "elasticity"


def _format_elasticity_label(abs_epsilon: float) -> str:
    if abs_epsilon >= 20.0:
        return "Perfectly Elastic\n(limit)"
    if abs(abs_epsilon - 1.0) <= 1e-9:
        return "Unit Elastic"
    if abs_epsilon > 1.0:
        return "Elastic"
    if abs_epsilon <= 0.05:
        return "Perfectly Inelastic\n(limit)"
    return "Inelastic"


def main() -> None:
    demand = Line.from_inverse(10.0, -1.0)
    fig = MarketFigure(
        x_max=12,
        y_max=11.5,
        title="Elasticity Along Demand",
        palette=EXAMPLE_PALETTE,
    )
    fig.add_layer(
        curve_layer(
            demand,
            q_min=0.05,
            q_max=9.95,
            layer_id="market.demand",
            role="principle.market.demand",
            label="Demand",
        )
    )

    sample_points = ((0.2, "s"), (2.0, "o"), (5.0, "^"), (8.0, "D"), (9.8, "v"))
    for index, (q, shape) in enumerate(sample_points):
        p = demand.p_at(q)
        abs_epsilon = abs(point_price_elasticity(demand, q=q))
        fig.add_layers(
            (
                MarkerLayer(
                    ((q, p),),
                    id=f"elasticity.point.{index}",
                    role="principle.market.equilibrium",
                    marker=Marker(
                        color=fig.theme.baseline_color,
                        edge_color=fig.theme.baseline_color,
                        edge_width=0,
                        size=42,
                        shape=shape,
                    ),
                    z_index=6,
                ),
                PointLabelLayer(
                    (q, p),
                    f"{_format_elasticity_label(abs_epsilon)}\n"
                    rf"$|\varepsilon| \approx {abs_epsilon:.2f}$",
                    id=f"elasticity.point.{index}.label",
                    role="principle.annotation",
                    style=TextStyle(color=fig.theme.baseline_color),
                    z_index=7,
                ),
            )
        )

    fig.finalize()
    fig.save(themed_output_path(THEME, "elasticity_demo.png"))


if __name__ == "__main__":
    ensure_output_dir(THEME)
    main()
