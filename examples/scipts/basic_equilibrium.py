"""Basic equilibrium example (image-only output)."""

from __future__ import annotations

from common import EXAMPLE_PALETTE, ensure_output_dir, themed_output_path

from principle_viz.core.equilibrium import solve_equilibrium
from principle_viz.core.line import Line
from principle_viz.plot.figure import MarketFigure

THEME = "equilibrium"


def main() -> None:
    demand = Line.from_inverse(12.0, -1.2)
    supply = Line.from_inverse(2.0, 0.8)
    eq = solve_equilibrium(demand, supply)

    fig = MarketFigure(
        x_max=14, y_max=14, title="Basic Equilibrium", palette=EXAMPLE_PALETTE
    )
    fig.add_curves(demand, supply, q_max=12)
    fig.add_equilibrium(eq)
    fig.add_metrics(
        {
            "q*": eq.q_star,
            "p*": eq.p_star,
            "valid": eq.is_valid_market,
        },
        title="Equilibrium",
        location="upper right",
    )
    fig.finalize()
    fig.save(str(themed_output_path(THEME, "basic_equilibrium.png")))
    fig.close()


if __name__ == "__main__":
    ensure_output_dir(THEME)
    main()
