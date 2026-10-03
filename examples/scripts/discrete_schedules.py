"""Discrete demand alone and discrete supply alone."""

from __future__ import annotations

from common import EXAMPLE_PALETTE, ensure_output_dir, themed_output_path

from principle_viz.core.discrete import DiscreteDemand, DiscreteSupply
from principle_viz.plot import MarketFigure

THEME = "discrete"


def main() -> None:
    for name, title, schedule in (
        ("demand", "Discrete Demand", {"demand": DiscreteDemand((11, 9, 7, 5, 3))}),
        ("supply", "Discrete Supply", {"supply": DiscreteSupply((1, 3, 5, 8, 10))}),
    ):
        figure = MarketFigure(x_max=5.5, y_max=12, title=title, palette=EXAMPLE_PALETTE)
        figure.add_discrete_curves(**schedule)
        figure.finalize()
        figure.save(themed_output_path(THEME, f"discrete_{name}.png"))


if __name__ == "__main__":
    ensure_output_dir(THEME)
    main()
