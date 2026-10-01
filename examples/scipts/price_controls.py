"""Price control example (image-only output)."""

from __future__ import annotations

from common import EXAMPLE_PALETTE, ensure_output_dir, themed_output_path

from principle_viz.core.controls import (
    PriceControlScenario,
    PriceControlType,
    evaluate_price_control,
)
from principle_viz.core.line import Line
from principle_viz.plot.figure import MarketFigure

THEME = "price_controls"


def main() -> None:
    demand = Line.from_inverse(10.0, -1.0)
    supply = Line.from_inverse(2.0, 1.0)

    result = evaluate_price_control(
        demand,
        supply,
        PriceControlScenario(control_type=PriceControlType.CEILING, control_price=4.0),
    )

    fig = MarketFigure(
        x_max=12, y_max=12, title="Binding Price Ceiling", palette=EXAMPLE_PALETTE
    )
    fig.add_curves(demand, supply, q_max=10)
    fig.add_price_control(result)
    fig.add_metrics(
        {
            "binding": result.is_binding,
            "Q traded": result.traded_quantity,
            "shortage": result.shortage,
            "surplus": result.surplus,
        },
        title="Control Outcome",
        location="upper right",
    )
    fig.finalize()
    fig.save(str(themed_output_path(THEME, "price_controls.png")))
    fig.close()


if __name__ == "__main__":
    ensure_output_dir(THEME)
    main()
