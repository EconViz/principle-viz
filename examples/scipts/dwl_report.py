"""DWL summary visualization (image-only output)."""

from __future__ import annotations

import matplotlib.pyplot as plt
from common import ensure_output_dir, themed_output_path

from principle_viz.core.equilibrium import solve_equilibrium
from principle_viz.core.line import Line
from principle_viz.policy.tax import TaxOn, TaxScenario, TaxType, solve_tax_equilibrium
from principle_viz.welfare.surplus import (
    compute_surplus,
    outcome_from_equilibrium,
    outcome_from_tax,
)

THEME = "welfare"



def main() -> None:
    demand = Line.from_inverse(10.0, -1.0)
    supply = Line.from_inverse(2.0, 1.0)

    baseline_eq = solve_equilibrium(demand, supply)
    baseline = compute_surplus(demand, supply, outcome_from_equilibrium(baseline_eq))

    tax_eq = solve_tax_equilibrium(
        demand,
        supply,
        TaxScenario(tax_type=TaxType.PER_UNIT_TAX, amount=1.0, tax_on=TaxOn.CONSUMER),
    )
    policy = compute_surplus(
        demand,
        supply,
        outcome_from_tax(tax_eq),
        baseline_outcome=outcome_from_equilibrium(baseline_eq),
    )

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    labels = ["Baseline TS", "Policy TS", "DWL"]
    values = [baseline.total_surplus, policy.total_surplus, policy.deadweight_loss]
    colors = ["#1A1A1A", "#777777", "#B5B5B5"]

    bars = ax.bar(labels, values, color=colors)
    ax.set_title("Deadweight Loss Summary")
    ax.set_ylabel("Value")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(False)

    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2.0, bar.get_height(), f"{value:.3f}", ha="center", va="bottom")

    fig.tight_layout()
    fig.savefig(themed_output_path(THEME, "dwl_report.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    ensure_output_dir(THEME)
    main()
