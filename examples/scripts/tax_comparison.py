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

    fig = MarketFigure(x_max=11, y_max=11, title=name, palette=EXAMPLE_PALETTE)
    fig.add_curves(demand, supply, q_max=10)
    fig.add_tax_transform(demand, supply, scenario, q_max=10)
    fig.finalize()
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
