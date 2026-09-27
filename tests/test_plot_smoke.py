from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

from principle_viz.core.equilibrium import solve_equilibrium
from principle_viz.core.line import Line
from principle_viz.core.shifts import ShiftScenario, ShiftSpec, comparative_statics
from principle_viz.plot.figure import MarketFigure
from principle_viz.policy.tax import TaxOn, TaxScenario, TaxType, solve_tax_equilibrium
from principle_viz.welfare.surplus import (
    compute_surplus,
    outcome_from_equilibrium,
    outcome_from_tax,
)


def test_market_figure_smoke_save(tmp_path) -> None:
    demand = Line.from_inverse(10.0, -1.0)
    supply = Line.from_inverse(2.0, 1.0)
    eq = solve_equilibrium(demand, supply)

    fig = MarketFigure(x_max=12, y_max=12, title="Smoke")
    fig.add_curves(demand, supply, q_max=10).add_equilibrium(eq).finalize()

    eq_annotations = [text for text in fig.ax.texts if text.get_text() == r"$e^{*}$"]
    assert len(eq_annotations) == 1
    assert eq_annotations[0].arrow_patch is not None
    assert type(eq_annotations[0].arrow_patch.get_connectionstyle()).__name__ == "Arc3"

    output = tmp_path / "smoke_basic.png"
    fig.save(str(output))
    fig.close()

    assert output.exists()


def test_market_figure_comparative_smoke(tmp_path) -> None:
    demand = Line.from_inverse(10.0, -1.0)
    supply = Line.from_inverse(2.0, 1.0)
    comp = comparative_statics(demand, supply, ShiftScenario(demand_shift=ShiftSpec(delta_intercept=1.5)))

    fig = MarketFigure(x_max=12, y_max=12, title="Comparative")
    fig.add_curves(demand, supply, q_max=10).add_comparative_statics(comp, q_max=10).finalize()
    output = tmp_path / "smoke_comparative.png"
    fig.save(str(output))
    fig.close()

    assert output.exists()


def test_market_figure_tax_shift_transform_smoke(tmp_path) -> None:
    demand = Line.from_inverse(12.0, -1.0)
    supply = Line.from_inverse(2.0, 1.0)
    scenario = TaxScenario(tax_type=TaxType.PER_UNIT_TAX, amount=1.2, tax_on=TaxOn.PRODUCER)

    fig = MarketFigure(x_max=12, y_max=12, title="Tax Shift", palette="monochrome")
    fig.add_curves(demand, supply, q_max=10).add_tax_transform(demand, supply, scenario, q_max=10).finalize()

    labels = [text.get_text() for text in fig.ax.texts]
    assert any(label.startswith("Tax = ") for label in labels)
    assert r"$e^{*}$" in labels

    output = tmp_path / "smoke_tax_shift.png"
    fig.save(str(output))
    fig.close()
    assert output.exists()


def test_market_figure_tax_rotation_transform_smoke(tmp_path) -> None:
    demand = Line.from_inverse(12.0, -1.0)
    supply = Line.from_inverse(2.0, 1.0)
    scenario = TaxScenario(tax_type=TaxType.AD_VALOREM_TAX, amount=0.2, tax_on=TaxOn.CONSUMER)

    fig = MarketFigure(x_max=12, y_max=12, title="Tax Rotation", palette="monochrome")
    fig.add_curves(demand, supply, q_max=10).add_tax_transform(demand, supply, scenario, q_max=10).finalize()

    labels = [text.get_text() for text in fig.ax.texts]
    assert any(label.startswith("Tax rate = ") for label in labels)
    assert r"$e^{*}$" in labels

    output = tmp_path / "smoke_tax_rotation.png"
    fig.save(str(output))
    fig.close()
    assert output.exists()


def test_market_figure_welfare_transition_smoke(tmp_path) -> None:
    demand = Line.from_inverse(10.0, -1.0)
    supply = Line.from_inverse(2.0, 1.0)
    baseline_eq = solve_equilibrium(demand, supply)
    baseline_outcome = outcome_from_equilibrium(baseline_eq)

    scenario = TaxScenario(tax_type=TaxType.PER_UNIT_TAX, amount=1.0, tax_on=TaxOn.PRODUCER)

    tax_eq = solve_tax_equilibrium(demand, supply, scenario)
    policy_outcome = outcome_from_tax(tax_eq)
    policy_surplus = compute_surplus(demand, supply, policy_outcome, baseline_outcome=baseline_outcome)

    fig = MarketFigure(x_max=12, y_max=12, title="Welfare Transition", palette="monochrome")
    fig.add_curves(demand, supply, q_max=10).add_welfare_transition(
        baseline_outcome=baseline_outcome,
        policy_outcome=policy_outcome,
        surplus=policy_surplus,
    ).finalize()

    labels = [text.get_text() for text in fig.ax.texts]
    assert r"$Q_0$" in labels
    assert r"$Q_1$" in labels
    assert any(letter in labels for letter in ("A", "B", "C"))

    output = tmp_path / "smoke_welfare_transition.png"
    fig.save(str(output))
    fig.close()
    assert output.exists()
