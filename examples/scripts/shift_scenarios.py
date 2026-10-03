"""Comparative statics example (image-only output)."""

from __future__ import annotations

from common import EXAMPLE_PALETTE, ensure_output_dir, themed_output_path

from principle_viz.core.line import Line
from principle_viz.core.shifts import ShiftScenario, ShiftSpec, comparative_statics
from principle_viz.plot.figure import MarketFigure

THEME = "equilibrium"


def main() -> None:
    demand = Line.from_inverse(10.0, -1.0)
    supply = Line.from_inverse(2.0, 1.0)

    scenario = ShiftScenario(
        demand_shift=ShiftSpec(delta_intercept=1.5),
        supply_shift=ShiftSpec(delta_intercept=0.5),
    )
    result = comparative_statics(demand, supply, scenario)

    fig = MarketFigure(
        x_max=12, y_max=12, title="Comparative Statics", palette=EXAMPLE_PALETTE
    )
    fig.add_curves(demand, supply, q_max=10)
    fig.add_comparative_statics(result, q_max=10)
    fig.finalize()
    fig.save(str(themed_output_path(THEME, "comparative_statics.png")))
    fig.close()


if __name__ == "__main__":
    ensure_output_dir(THEME)
    main()
