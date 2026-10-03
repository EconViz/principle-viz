"""Reservation prices of two buyers combined into a market demand schedule."""

from __future__ import annotations

from common import EXAMPLE_PALETTE, ensure_output_dir, themed_output_path

from principle_viz import DiscreteDemand, discrete_demand_aggregation_figure

THEME = "aggregation"


def main() -> None:
    figure = discrete_demand_aggregation_figure(
        {
            "A": DiscreteDemand((10, 7, 4)),
            "B": DiscreteDemand((8, 5, 2)),
        },
        price=6.0,
        palette=EXAMPLE_PALETTE,
    )
    figure.save(themed_output_path(THEME, "discrete_market_demand.png"))


if __name__ == "__main__":
    ensure_output_dir(THEME)
    main()
