"""Individual supplies summed horizontally into a kinked market supply."""

from __future__ import annotations

from common import EXAMPLE_PALETTE, ensure_output_dir, themed_output_path

from principle_viz import supply_aggregation_figure
from principle_viz.core.line import Line

THEME = "aggregation"


def main() -> None:
    figure = supply_aggregation_figure(
        {
            "A": Line.from_inverse(2.0, 1.0),
            "B": Line.from_inverse(5.0, 0.5),
        },
        price=8.0,
        p_max=10.0,
        palette=EXAMPLE_PALETTE,
    )
    figure.save(themed_output_path(THEME, "market_supply.png"))


if __name__ == "__main__":
    ensure_output_dir(THEME)
    main()
