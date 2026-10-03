from __future__ import annotations

from principle_viz.core.equilibrium import solve_equilibrium
from principle_viz.core.line import Line
from principle_viz.policy.tax import TaxOn, TaxScenario, TaxType, solve_tax_equilibrium
from principle_viz.welfare.layout import build_welfare_annotation_layout
from principle_viz.welfare.report import build_dwl_report
from principle_viz.welfare.surplus import (
    compare_surplus,
    compute_surplus,
    outcome_from_equilibrium,
    outcome_from_tax,
)


def test_baseline_surplus_positive() -> None:
    demand = Line.from_inverse(10.0, -1.0)
    supply = Line.from_inverse(2.0, 1.0)
    eq = solve_equilibrium(demand, supply)
    baseline = compute_surplus(demand, supply, outcome_from_equilibrium(eq))

    assert baseline.consumer_surplus > 0.0
    assert baseline.producer_surplus > 0.0
    assert baseline.total_surplus > 0.0


def test_tax_generates_dwl() -> None:
    demand = Line.from_inverse(10.0, -1.0)
    supply = Line.from_inverse(2.0, 1.0)

    baseline_eq = solve_equilibrium(demand, supply)
    tax_eq = solve_tax_equilibrium(
        demand,
        supply,
        TaxScenario(tax_type=TaxType.PER_UNIT_TAX, amount=1.0, tax_on=TaxOn.PRODUCER),
    )

    delta = compare_surplus(
        demand,
        supply,
        outcome_from_equilibrium(baseline_eq),
        outcome_from_tax(tax_eq),
    )
    assert delta.deadweight_loss >= 0.0


def test_dwl_report_has_expected_columns() -> None:
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

    report = build_dwl_report([("tax", baseline, policy)])
    assert len(report) == 1
    assert report[0].scenario == "tax"


def test_welfare_annotation_layout_builds_reference_and_named_regions() -> None:
    demand = Line.from_inverse(10.0, -1.0)
    supply = Line.from_inverse(2.0, 1.0)
    baseline_eq = solve_equilibrium(demand, supply)
    baseline_outcome = outcome_from_equilibrium(baseline_eq)

    tax_eq = solve_tax_equilibrium(
        demand,
        supply,
        TaxScenario(tax_type=TaxType.PER_UNIT_TAX, amount=1.0, tax_on=TaxOn.PRODUCER),
    )
    policy_outcome = outcome_from_tax(tax_eq)
    policy_surplus = compute_surplus(
        demand, supply, policy_outcome, baseline_outcome=baseline_outcome
    )

    layout = build_welfare_annotation_layout(
        baseline_outcome=baseline_outcome,
        policy_outcome=policy_outcome,
        surplus=policy_surplus,
    )

    assert layout.reference.baseline_quantity == baseline_outcome.quantity
    assert layout.reference.policy_quantity == policy_outcome.quantity
    assert len(layout.regions) >= 3
    assert [(r.key, r.label, r.short_label) for r in layout.regions] == [
        ("cs", "Consumer surplus", "CS"),
        ("ps", "Producer surplus", "PS"),
        ("tax_revenue", "Tax revenue", "Tax"),
        ("dwl", "Deadweight loss", "DWL"),
    ]
