"""DWL summary visualization rendered through MosaicKit."""

from __future__ import annotations

from common import EXAMPLE_PALETTE, ensure_output_dir, themed_output_path
from mosaickit import Canvas, CanvasSpec, Fill, FillLayer, TextLayer, quadrant_axes

from principle_viz.core.equilibrium import solve_equilibrium
from principle_viz.core.line import Line
from principle_viz.policy.tax import TaxOn, TaxScenario, TaxType, solve_tax_equilibrium
from principle_viz.visuals.theme import PlotTheme
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
    values = (baseline.total_surplus, policy.total_surplus, policy.deadweight_loss)
    labels = ("Baseline TS", "Policy TS", "DWL")
    colors = ("#1A1A1A", "#777777", "#B5B5B5")
    y_max = max(values) * 1.2
    canvas = Canvas(
        CanvasSpec(
            x_range=(0.0, 4.0),
            y_range=(0.0, y_max),
            width=7.2,
            height=4.8,
            dpi=150,
            x_label="",
            y_label="Value",
            title="Deadweight Loss Summary",
        ),
        theme=PlotTheme.from_palette(EXAMPLE_PALETTE).to_mosaickit(),
    ).extend(quadrant_axes(4.0, y_max))
    for index, (label, value, color) in enumerate(zip(labels, values, colors), start=1):
        canvas.add(
            FillLayer(
                (
                    (index - 0.3, 0.0),
                    (index + 0.3, 0.0),
                    (index + 0.3, value),
                    (index - 0.3, value),
                ),
                id=f"dwl.bar.{index}",
                role="region",
                fill=Fill(color=color, opacity=1),
            )
        )
        canvas.add(
            TextLayer(
                (float(index), 0.0),
                label,
                id=f"dwl.label.{index}",
                offset=(0, -12),
                anchor="bottom",
            )
        )
        canvas.add(
            TextLayer(
                (float(index), value),
                f"{value:.3f}",
                id=f"dwl.value.{index}",
                offset=(0, 8),
                anchor="top",
            )
        )
    canvas.save(themed_output_path(THEME, "dwl_report.png"))


if __name__ == "__main__":
    ensure_output_dir(THEME)
    main()
