"""Unit costs of two sellers combined into a market supply schedule."""

from __future__ import annotations

from common import EXAMPLE_PALETTE, ensure_output_dir, themed_output_path

from principle_viz import DiscreteSupply, discrete_supply_aggregation_figure

THEME = "aggregation"


def main() -> None:
    figure = discrete_supply_aggregation_figure(
        {
            "A": DiscreteSupply((2, 5, 8)),
            "B": DiscreteSupply((3, 4, 9)),
        },
        price=6.0,
        palette=EXAMPLE_PALETTE,
    )
    figure.save(themed_output_path(THEME, "discrete_market_supply.png"))


if __name__ == "__main__":
    ensure_output_dir(THEME)
    main()
