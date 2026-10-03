"""Welfare decomposition under tax (image-only output)."""

from __future__ import annotations

from common import EXAMPLE_PALETTE, ensure_output_dir, themed_output_path

from principle_viz.core.equilibrium import solve_equilibrium
from principle_viz.core.line import Line
from principle_viz.plot.figure import MarketFigure
from principle_viz.policy.tax import (
    TaxOn,
    TaxScenario,
    TaxType,
    compare_tax_scenario,
    solve_tax_equilibrium,
)
from principle_viz.welfare.surplus import (
    compare_surplus,
    outcome_from_equilibrium,
    outcome_from_tax,
)

THEME = "welfare"


def main() -> None:
    demand = Line.from_inverse(10.0, -1.0)
    supply = Line.from_inverse(2.0, 1.0)

    baseline_eq = solve_equilibrium(demand, supply)
    tax_eq = solve_tax_equilibrium(
        demand,
        supply,
        TaxScenario(tax_type=TaxType.PER_UNIT_TAX, amount=3.0, tax_on=TaxOn.PRODUCER),
    )

    baseline_outcome = outcome_from_equilibrium(baseline_eq)
    policy_outcome = outcome_from_tax(tax_eq)
    delta = compare_surplus(demand, supply, baseline_outcome, policy_outcome)
    tax_comparison = compare_tax_scenario(
        demand,
        supply,
        TaxScenario(tax_type=TaxType.PER_UNIT_TAX, amount=3.0, tax_on=TaxOn.PRODUCER),
    )

    # Welfare regions, each named inside or by callout.
    fig_raw = MarketFigure(
        x_max=12,
        y_max=12,
        title="Welfare Under a Tax",
        palette=EXAMPLE_PALETTE,
    )
    fig_raw.add_curves(demand, supply, q_max=10)
    fig_raw.add_welfare(delta.policy)
    fig_raw.add_tax_comparison(tax_comparison)
    fig_raw.finalize()
    fig_raw.save(str(themed_output_path(THEME, "welfare_tax_raw.png")))
    fig_raw.close()

    # The same regions with baseline/policy reference guides.
    fig = MarketFigure(
        x_max=12,
        y_max=12,
        title="Welfare Change from a Tax",
        palette=EXAMPLE_PALETTE,
    )
    fig.add_curves(demand, supply, q_max=10)
    fig.add_welfare_transition(
        baseline_outcome=baseline_outcome,
        policy_outcome=policy_outcome,
        surplus=delta.policy,
    )
    fig.add_tax_comparison(tax_comparison)
    fig.finalize()
    fig.save(str(themed_output_path(THEME, "welfare_tax.png")))
    fig.close()


if __name__ == "__main__":
    ensure_output_dir(THEME)
    main()
