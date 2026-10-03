"""Price control welfare examples with labelled surplus and deadweight-loss regions."""

from __future__ import annotations

from common import EXAMPLE_PALETTE, ensure_output_dir, themed_output_path

from principle_viz.core.controls import (
    PriceControlScenario,
    PriceControlType,
    evaluate_price_control,
)
from principle_viz.core.equilibrium import solve_equilibrium
from principle_viz.core.line import Line
from principle_viz.plot.figure import MarketFigure
from principle_viz.welfare.surplus import (
    compare_surplus,
    outcome_from_control,
    outcome_from_equilibrium,
)

THEME = "price_controls"


def main() -> None:
    demand = Line.from_inverse(10.0, -1.0)
    supply = Line.from_inverse(2.0, 1.0)

    baseline_eq = solve_equilibrium(demand, supply)
    baseline_outcome = outcome_from_equilibrium(baseline_eq)

    control_result = evaluate_price_control(
        demand,
        supply,
        PriceControlScenario(control_type=PriceControlType.CEILING, control_price=3.5),
    )
    control_outcome = outcome_from_control(control_result)

    delta = compare_surplus(demand, supply, baseline_outcome, control_outcome)

    # Welfare regions, each named inside or by callout.
    fig_raw = MarketFigure(
        x_max=12,
        y_max=12,
        title="Price Ceiling Welfare",
        palette=EXAMPLE_PALETTE,
    )
    fig_raw.add_curves(demand, supply, q_max=10)
    fig_raw.add_price_control(control_result)
    fig_raw.add_welfare(delta.policy)
    fig_raw.finalize()
    fig_raw.save(str(themed_output_path(THEME, "price_controls_welfare_raw.png")))
    fig_raw.close()

    # The same regions with baseline/policy reference guides.
    fig = MarketFigure(
        x_max=12,
        y_max=12,
        title="Welfare Change from a Ceiling",
        palette=EXAMPLE_PALETTE,
    )
    fig.add_curves(demand, supply, q_max=10)
    fig.add_price_control(control_result)
    fig.add_welfare_transition(
        baseline_outcome=baseline_outcome,
        policy_outcome=control_outcome,
        surplus=delta.policy,
    )
    fig.finalize()
    fig.save(str(themed_output_path(THEME, "price_controls_welfare.png")))
    fig.close()


if __name__ == "__main__":
    ensure_output_dir(THEME)
    main()
