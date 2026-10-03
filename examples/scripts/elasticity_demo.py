"""Single-line elasticity classification with five marked points."""

from __future__ import annotations

from common import EXAMPLE_PALETTE, ensure_output_dir, themed_output_path
from mosaickit import Marker, MarkerLayer, PointLabelLayer, TextStyle

from principle_viz.core.elasticity import point_price_elasticity
from principle_viz.core.line import Line
from principle_viz.plot.figure import MarketFigure
from principle_viz.visuals import curve_layer

THEME = "elasticity"


def _elasticity_name(abs_epsilon: float) -> str:
    if abs_epsilon == float("inf"):
        return "Perfectly elastic"
    if abs_epsilon == 0.0:
        # Two lines: the point sits at the end of the quantity axis.
        return "Perfectly\ninelastic"
    if abs(abs_epsilon - 1.0) <= 1e-9:
        return "Unit elastic"
    return "Elastic" if abs_epsilon > 1.0 else "Inelastic"


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
            q_min=0.0,
            q_max=10.0,
            layer_id="market.demand",
            role="principle.market.demand",
            # One curve, named by the title: no direct label needed.
            label=None,
        )
    )

    # The ends sit on the axes: |e| is infinite where Q = 0 and zero where p = 0.
    choke = demand.q_intercept()
    for index, q in enumerate((0.0, 0.2 * choke, 0.5 * choke, 0.8 * choke, choke)):
        p = demand.p_at(q)
        abs_epsilon = (
            float("inf")
            if q == 0.0
            else 0.0
            if p == 0.0
            else abs(point_price_elasticity(demand, q=q))
        )
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
                        shape="o",
                    ),
                    z_index=6,
                ),
                PointLabelLayer(
                    (q, p),
                    _elasticity_name(abs_epsilon),
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
