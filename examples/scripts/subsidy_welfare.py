"""Per-unit subsidy incidence and welfare example."""

from __future__ import annotations

from common import EXAMPLE_PALETTE, ensure_output_dir, themed_output_path

from principle_viz.core.equilibrium import solve_equilibrium
from principle_viz.core.line import Line
from principle_viz.plot.figure import MarketFigure
from principle_viz.policy.subsidy import (
    SubsidyScenario,
    SubsidyTo,
    compare_subsidy_scenario,
)
from principle_viz.welfare.surplus import (
    compare_surplus,
    outcome_from_equilibrium,
    outcome_from_subsidy,
)

THEME = "subsidy"


def main() -> None:
    demand = Line.from_inverse(12.0, -1.0)
    supply = Line.from_inverse(2.0, 1.0)
    comparison = compare_subsidy_scenario(
        demand,
        supply,
        SubsidyScenario(amount=3.0, subsidy_to=SubsidyTo.PRODUCER),
    )
    baseline = outcome_from_equilibrium(solve_equilibrium(demand, supply))
    subsidized = outcome_from_subsidy(comparison.post_subsidy)
    welfare = compare_surplus(demand, supply, baseline, subsidized)

    figure = MarketFigure(
        x_max=12,
        y_max=13,
        title="Per-Unit Subsidy",
        palette=EXAMPLE_PALETTE,
        visibility={
            "market.subsidy.expenditure.label": False,
            "market.subsidy.wedge.label": False,
            "market.subsidy.wedge.mark.p_0": False,
            "market.subsidy.wedge.brace": False,
        },
    )
    figure.add_curves(demand, supply, q_max=11)
    # The subsidy cost overlaps the surplus areas, so only the loss is shaded.
    figure.add_welfare(welfare.policy, regions=("dwl",))
    figure.add_subsidy_comparison(comparison)
    figure.finalize()
    figure.save(str(themed_output_path(THEME, "subsidy_welfare.png")))
    figure.close()


if __name__ == "__main__":
    ensure_output_dir(THEME)
    main()
