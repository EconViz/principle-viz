"""Tax transformation examples.

Includes both legal incidence sides (consumer/producer) for:
- fixed tax
- per-unit tax
- ad valorem tax
"""

from __future__ import annotations

from common import EXAMPLE_PALETTE, ensure_output_dir, themed_output_path

from principle_viz.core.line import Line
from principle_viz.plot.figure import MarketFigure
from principle_viz.policy.tax import TaxOn, TaxScenario, TaxType

THEME = "taxation"


def _plot_tax_case(name: str, scenario: TaxScenario, filename: str) -> None:
    demand = Line.from_inverse(10.0, -1.0)
    supply = Line.from_inverse(0.0, 1.0)

    fig = MarketFigure(x_max=12, y_max=13, title=name, palette=EXAMPLE_PALETTE)
    fig.add_curves(demand, supply, q_max=10)
    fig.add_tax_transform(demand, supply, scenario, q_max=10)
    fig.finalize()
    fig.save(str(themed_output_path(THEME, filename)))
    fig.close()


def main() -> None:
    tax_cases = (
        (TaxType.FIXED_TAX, 2.0, "fixed"),
        (TaxType.PER_UNIT_TAX, 2.5, "per_unit"),
        (TaxType.AD_VALOREM_TAX, 0.2, "ad_valorem"),
    )
    incidences = (
        (TaxOn.CONSUMER, "consumer"),
        (TaxOn.PRODUCER, "producer"),
    )

    names = {
        TaxType.FIXED_TAX: "Fixed Tax",
        TaxType.PER_UNIT_TAX: "Per-Unit Tax",
        TaxType.AD_VALOREM_TAX: "Ad Valorem Tax",
    }
    for tax_type, amount, slug in tax_cases:
        for tax_on, incidence_slug in incidences:
            _plot_tax_case(
                name=f"{names[tax_type]} on {tax_on.value.title()}s",
                scenario=TaxScenario(tax_type=tax_type, amount=amount, tax_on=tax_on),
                filename=f"tax_{slug}_{incidence_slug}.png",
            )


if __name__ == "__main__":
    ensure_output_dir(THEME)
    main()
