"""World-price, tariff, and import-quota examples."""

from __future__ import annotations

from common import EXAMPLE_PALETTE, ensure_output_dir, themed_output_path

from principle_viz.core.line import Line
from principle_viz.plot.figure import MarketFigure
from principle_viz.policy.trade import TradeScenario, analyze_trade

THEME = "trade"


def _draw(name: str, filename: str, scenario: TradeScenario) -> None:
    demand = Line.from_inverse(12.0, -1.0)
    supply = Line.from_inverse(2.0, 1.0)
    result = analyze_trade(demand, supply, scenario)

    figure = MarketFigure(x_max=12, y_max=13, title=name, palette=EXAMPLE_PALETTE)
    figure.add_curves(demand, supply, q_max=11)
    figure.add_trade(result)
    figure.finalize()
    figure.save(str(themed_output_path(THEME, filename)))
    figure.close()


def main() -> None:
    _draw("Free Trade: Imports", "free_trade_import.png", TradeScenario(4))
    _draw("Free Trade: Exports", "free_trade_export.png", TradeScenario(9))
    _draw(
        "Import Tariff",
        "import_tariff.png",
        TradeScenario(world_price=4, tariff=2),
    )
    _draw(
        "Binding Import Quota",
        "import_quota.png",
        TradeScenario(world_price=4, import_quota=2),
    )


if __name__ == "__main__":
    ensure_output_dir(THEME)
    main()
