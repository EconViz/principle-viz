"""Tax transformation examples in monochrome style.

Includes both legal incidence sides (consumer/producer) for:
- fixed tax
- per-unit tax
- ad valorem tax
"""

from __future__ import annotations

from common import EXAMPLE_PALETTE, ensure_output_dir, themed_output_path

from principle_viz.core.line import Line
from principle_viz.plot.figure import MarketFigure
from principle_viz.policy.tax import TaxOn, TaxScenario, TaxType, compare_tax_scenario

THEME = "taxation"



def _plot_tax_case(name: str, scenario: TaxScenario, filename: str) -> None:
    demand = Line.from_inverse(10.0, -1.0)
    supply = Line.from_inverse(0.0, 1.0)
    result = compare_tax_scenario(demand, supply, scenario)

    fig = MarketFigure(x_max=11, y_max=11, title=name, palette=EXAMPLE_PALETTE)
    fig.add_curves(demand, supply, q_max=10)
    fig.add_tax_transform(demand, supply, scenario, q_max=10)
    fig.add_metrics(
        {
            "tax on": scenario.tax_on.value,
            "tax type": scenario.tax_type.value,
            "baseline q*": result.baseline_equilibrium.q_star,
            "Pc": result.post_tax.consumer_price,
            "Pp": result.post_tax.producer_price,
            "wedge": result.post_tax.tax_wedge,
            "tax rev": result.post_tax.tax_revenue,
        },
        title="Tax Outcome",
        location="upper right",
    )
    fig.finalize(legend=True)
    fig.save(str(themed_output_path(THEME, filename)))
    fig.close()



def main() -> None:
    tax_cases = (
        (TaxType.FIXED_TAX, 1.2, "fixed"),
        (TaxType.PER_UNIT_TAX, 1.5, "per_unit"),
        (TaxType.AD_VALOREM_TAX, 0.2, "ad_valorem"),
    )
    incidences = (
        (TaxOn.CONSUMER, "consumer"),
        (TaxOn.PRODUCER, "producer"),
    )

    for tax_type, amount, slug in tax_cases:
        for tax_on, incidence_slug in incidences:
            if tax_type == TaxType.AD_VALOREM_TAX:
                title_suffix = "Proportional Rotation"
            else:
                title_suffix = "Anchored Tax Shift Arrow"
            _plot_tax_case(
                name=f"{tax_type.value.replace('_', ' ').title()} Tax ({tax_on.value.title()}) - {title_suffix}",
                scenario=TaxScenario(tax_type=tax_type, amount=amount, tax_on=tax_on),
                filename=f"tax_{slug}_{incidence_slug}.png",
            )


if __name__ == "__main__":
    ensure_output_dir(THEME)
    main()
