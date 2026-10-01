"""Production-possibilities frontier examples."""

from __future__ import annotations

from common import EXAMPLE_PALETTE, ensure_output_dir, themed_output_path

from principle_viz.core.ppf import (
    PPFGrowthScenario,
    ProductionPossibilitiesFrontier,
    analyze_ppf,
    analyze_ppf_growth,
)
from principle_viz.visuals.ppf import ppf_canvas, ppf_growth_canvas
from principle_viz.visuals.theme import PlotTheme

THEME = "ppf"


def main() -> None:
    theme = PlotTheme.from_palette(EXAMPLE_PALETTE)
    frontier = ProductionPossibilitiesFrontier(
        x_intercept=10,
        y_intercept=8,
        curvature=2,
        x_good="Consumer",
        y_good="Capital",
    )
    analysis = analyze_ppf(
        frontier,
        points=(
            (6, frontier.y_at(6), "A: efficient"),
            (4, 3, "B: inefficient"),
            (7, 6, "C: unattainable"),
        ),
    )
    ppf_canvas(analysis, theme=theme).save(themed_output_path(THEME, "ppf_points.png"))

    growth = analyze_ppf_growth(
        frontier,
        PPFGrowthScenario(x_growth_rate=0.2, y_growth_rate=0.1),
    )
    ppf_growth_canvas(growth, theme=theme).save(
        themed_output_path(THEME, "ppf_economic_growth.png")
    )


if __name__ == "__main__":
    ensure_output_dir(THEME)
    main()
