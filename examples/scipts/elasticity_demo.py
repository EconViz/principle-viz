"""Single-line elasticity classification with five marked points."""

from __future__ import annotations

from common import EXAMPLE_PALETTE, ensure_output_dir, themed_output_path

from principle_viz.core.elasticity import point_price_elasticity
from principle_viz.core.line import Line
from principle_viz.plot.figure import MarketFigure
from principle_viz.plot.primitives import annotate_text, plot_point
from principle_viz.plot.renderers import render_curve

THEME = "elasticity"


def _format_elasticity_label(abs_epsilon: float) -> str:
    if abs_epsilon >= 20.0:
        return "Perfectly Elastic (limit)"
    if abs(abs_epsilon - 1.0) <= 1e-9:
        return "Unit Elastic"
    if abs_epsilon > 1.0:
        return "Elastic"
    if abs_epsilon <= 0.05:
        return "Perfectly Inelastic (limit)"
    return "Inelastic"


def main() -> None:
    demand = Line.from_inverse(10.0, -1.0)
    fig = MarketFigure(
        x_max=10.2,
        y_max=10.2,
        title="One Demand Line: Five Elasticity Categories",
        palette=EXAMPLE_PALETTE,
    )
    render_curve(fig.ax, demand, q_min=0.05, q_max=9.95, label="Demand", color=fig.theme.demand_color)

    sample_points = (
        (0.2, "s", (12, 10)),
        (2.0, "o", (12, 8)),
        (5.0, "^", (12, 10)),
        (8.0, "D", (12, -10)),
        (9.8, "v", (12, -12)),
    )

    for q, marker, text_offset in sample_points:
        p = demand.p_at(q)
        epsilon = point_price_elasticity(demand, q=q)
        abs_epsilon = abs(epsilon)
        category = _format_elasticity_label(abs_epsilon)

        plot_point(
            fig.ax,
            x=q,
            y=p,
            color=fig.theme.baseline_color,
            marker_size=6.5,
            marker=marker,
        )
        annotate_text(
            fig.ax,
            x=q,
            y=p,
            text=f"{category}\n|ε|≈{abs_epsilon:.2f}",
            color=fig.theme.baseline_color,
            offset=text_offset,
            curved_arrow=True,
            curvature=0.2,
        )

    fig.add_metrics(
        {
            "point count": 5,
            "curve": "single demand line",
            "mapping": "top->bottom: PE, E, U, I, PI",
        },
        title="Classification Points",
        location="upper right",
    )
    fig.finalize(legend=True)
    fig.save(str(themed_output_path(THEME, "elasticity_demo.png")))
    fig.close()


if __name__ == "__main__":
    ensure_output_dir(THEME)
    main()
