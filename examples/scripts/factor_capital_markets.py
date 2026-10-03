"""Labor-market and loanable-funds examples."""

from __future__ import annotations

from common import EXAMPLE_PALETTE, ensure_output_dir, themed_output_path

from principle_viz.core.factor_markets import (
    LoanableFundsScenario,
    analyze_loanable_funds,
    analyze_minimum_wage,
)
from principle_viz.core.line import Line
from principle_viz.plot.figure import MarketFigure

THEME = "factor_capital_markets"


def main() -> None:
    labor_demand = Line.from_inverse(12, -1)
    labor_supply = Line.from_inverse(2, 1)
    labor = analyze_minimum_wage(labor_demand, labor_supply, minimum_wage=9)
    figure = MarketFigure(
        x_max=11,
        y_max=14,
        x_label="L",
        y_label="w",
        title="Binding Minimum Wage",
        palette=EXAMPLE_PALETTE,
    )
    figure.add_curves(
        labor_demand,
        labor_supply,
        q_max=10,
        demand_label="Labor demand",
        supply_label="Labor supply",
    )
    figure.add_minimum_wage(labor)
    figure.finalize()
    figure.save(str(themed_output_path(THEME, "minimum_wage.png")))
    figure.close()

    savings = Line.from_inverse(2, 0.5)
    investment = Line.from_inverse(12, -0.5)
    funds = analyze_loanable_funds(
        savings,
        investment,
        LoanableFundsScenario(government_borrowing=4),
    )
    figure = MarketFigure(
        x_max=18,
        y_max=14,
        y_label="r",
        title="Government Borrowing",
        palette=EXAMPLE_PALETTE,
    )
    figure.add_curves(
        investment,
        savings,
        q_max=17,
        demand_label="$D_0$",
        supply_label="$S_0$",
    )
    figure.add_loanable_funds(funds)
    figure.finalize()
    figure.save(str(themed_output_path(THEME, "loanable_funds_crowding_out.png")))
    figure.close()


if __name__ == "__main__":
    ensure_output_dir(THEME)
    main()
