"""Discrete demand and supply with closed/open step endpoints."""

from __future__ import annotations

from common import EXAMPLE_PALETTE, ensure_output_dir, themed_output_path

from principle_viz.core.discrete import (
    DiscreteDemand,
    DiscreteSupply,
    solve_discrete_equilibrium,
)
from principle_viz.plot import MarketFigure

THEME = "discrete"


def main() -> None:
    demand = DiscreteDemand((11, 9, 7, 5, 3))
    supply = DiscreteSupply((1, 3, 5, 8, 10))
    equilibrium = solve_discrete_equilibrium(demand, supply)

    figure = MarketFigure(
        x_max=5.5,
        y_max=12,
        title="Discrete Demand and Supply",
        palette=EXAMPLE_PALETTE,
    )
    figure.add_discrete_curves(demand, supply)
    figure.add_discrete_equilibrium(equilibrium)
    figure.finalize()
    figure.save(themed_output_path(THEME, "discrete_market.png"))


if __name__ == "__main__":
    ensure_output_dir(THEME)
    main()
