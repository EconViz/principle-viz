"""Linked demand-elasticity and total-revenue diagrams."""

from __future__ import annotations

from common import EXAMPLE_PALETTE, ensure_output_dir, themed_output_path
from mosaickit import CanvasGrid

from principle_viz.core.line import Line
from principle_viz.core.revenue import elasticity_revenue_schedule
from principle_viz.visuals.revenue import elasticity_revenue_canvases
from principle_viz.visuals.theme import PlotTheme

THEME = "elasticity"


def main() -> None:
    demand = Line.from_inverse(12.0, -1.0)
    schedule = elasticity_revenue_schedule(demand)
    canvases = elasticity_revenue_canvases(
        demand,
        schedule,
        theme=PlotTheme.from_palette(EXAMPLE_PALETTE),
    )
    CanvasGrid(canvases, rows=1).save(
        themed_output_path(THEME, "elasticity_total_revenue.png")
    )


if __name__ == "__main__":
    ensure_output_dir(THEME)
    main()
