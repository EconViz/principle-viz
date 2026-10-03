"""Individual demands summed horizontally into a kinked market demand."""

from __future__ import annotations

from common import EXAMPLE_PALETTE, ensure_output_dir, themed_output_path

from principle_viz import demand_aggregation_figure
from principle_viz.core.line import Line

THEME = "aggregation"


def main() -> None:
    figure = demand_aggregation_figure(
        {
            "A": Line.from_inverse(10.0, -2.0),
            "B": Line.from_inverse(6.0, -0.5),
        },
        price=4.0,
        palette=EXAMPLE_PALETTE,
    )
    figure.save(themed_output_path(THEME, "market_demand.png"))


if __name__ == "__main__":
    ensure_output_dir(THEME)
    main()
