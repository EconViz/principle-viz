"""Externalities, public goods, and common-resource examples."""

from __future__ import annotations

from common import EXAMPLE_PALETTE, ensure_output_dir, themed_output_path

from principle_viz.core.line import Line
from principle_viz.core.public_goods import IndividualBenefit, analyze_public_good
from principle_viz.plot.figure import MarketFigure
from principle_viz.policy.common_resources import analyze_common_resource
from principle_viz.policy.externality import ExternalityScenario, analyze_externality
from principle_viz.visuals.market_failures import public_good_canvas
from principle_viz.visuals.theme import PlotTheme

THEME = "market_failures"


def _externality(name: str, filename: str, scenario: ExternalityScenario) -> None:
    demand = Line.from_inverse(12, -1)
    supply = Line.from_inverse(2, 1)
    result = analyze_externality(demand, supply, scenario)
    figure = MarketFigure(x_max=11, y_max=14, title=name, palette=EXAMPLE_PALETTE)
    figure.add_curves(demand, supply, q_max=10)
    figure.add_externality(result)
    figure.finalize()
    figure.save(str(themed_output_path(THEME, filename)))
    figure.close()


def main() -> None:
    _externality(
        "Negative Production Externality",
        "negative_externality.png",
        ExternalityScenario(marginal_external_cost=2),
    )
    _externality(
        "Positive Consumption Externality",
        "positive_externality.png",
        ExternalityScenario(marginal_external_benefit=2),
    )

    public_good = analyze_public_good(
        (
            IndividualBenefit("Person A", Line.from_inverse(8, -1)),
            IndividualBenefit("Person B", Line.from_inverse(6, -1)),
        ),
        Line.from_inverse(5, 0),
    )
    public_good_canvas(
        public_good,
        theme=PlotTheme.from_palette(EXAMPLE_PALETTE),
    ).save(themed_output_path(THEME, "public_good_vertical_sum.png"))

    benefit = Line.from_inverse(12, -1)
    private_cost = Line.from_inverse(2, 1)
    common = analyze_common_resource(
        benefit,
        private_cost,
        marginal_congestion_cost=3,
    )
    figure = MarketFigure(
        x_max=11,
        y_max=14,
        title="Common Resource Overuse",
        palette=EXAMPLE_PALETTE,
    )
    figure.add_curves(
        benefit,
        private_cost,
        q_max=10,
        demand_label="Marginal benefit",
        supply_label="Private marginal cost",
    )
    figure.add_common_resource(common)
    figure.finalize()
    figure.save(str(themed_output_path(THEME, "common_resource.png")))
    figure.close()


if __name__ == "__main__":
    ensure_output_dir(THEME)
    main()
