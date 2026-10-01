from __future__ import annotations

from mosaickit import TextLayer

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


def _texts(figure: MarketFigure) -> list[str]:
    return [
        str(layer.text) for layer in figure.scene.layers if isinstance(layer, TextLayer)
    ]


def test_market_figure_smoke_save_all_static_formats(tmp_path) -> None:
    demand = Line.from_inverse(10.0, -1.0)
    supply = Line.from_inverse(2.0, 1.0)
    eq = solve_equilibrium(demand, supply)
    figure = MarketFigure(x_max=12, y_max=12, title="Smoke")
    figure.add_curves(demand, supply, q_max=10).add_equilibrium(eq).finalize()

    assert r"$e^{*}$" in _texts(figure)
    assert {layer.id for layer in figure.scene.layers}.issuperset(
        {"market.demand", "market.supply", "market.equilibrium", "market.legend"}
    )
    for suffix in ("png", "svg", "pdf"):
        output = tmp_path / f"smoke_basic.{suffix}"
        figure.save(output)
        assert output.exists() and output.stat().st_size > 0


def test_market_figure_comparative_smoke(tmp_path) -> None:
    demand = Line.from_inverse(10.0, -1.0)
    supply = Line.from_inverse(2.0, 1.0)
    comparison = comparative_statics(
        demand, supply, ShiftScenario(demand_shift=ShiftSpec(delta_intercept=1.5))
    )
    figure = MarketFigure(x_max=12, y_max=12, title="Comparative")
    figure.add_curves(demand, supply, q_max=10).add_comparative_statics(
        comparison, q_max=10
    ).finalize()
    output = tmp_path / "smoke_comparative.png"
    figure.save(output)
    assert output.exists()
    assert "market.comparison.movement.quantity" in {
        layer.id for layer in figure.scene.layers
    }


def test_market_figure_tax_shift_transform_smoke(tmp_path) -> None:
    demand = Line.from_inverse(12.0, -1.0)
    supply = Line.from_inverse(2.0, 1.0)
    scenario = TaxScenario(
        tax_type=TaxType.PER_UNIT_TAX, amount=1.2, tax_on=TaxOn.PRODUCER
    )
    figure = MarketFigure(x_max=12, y_max=12, title="Tax Shift", palette="monochrome")
    figure.add_curves(demand, supply, q_max=10).add_tax_transform(
        demand, supply, scenario, q_max=10
    ).finalize()
    assert any(label.startswith("Tax = ") for label in _texts(figure))
    assert r"$e^{*}$" in _texts(figure)
    output = tmp_path / "smoke_tax_shift.png"
    figure.save(output)
    assert output.exists()


def test_market_figure_tax_rotation_transform_smoke(tmp_path) -> None:
    demand = Line.from_inverse(12.0, -1.0)
    supply = Line.from_inverse(2.0, 1.0)
    scenario = TaxScenario(
        tax_type=TaxType.AD_VALOREM_TAX, amount=0.2, tax_on=TaxOn.CONSUMER
    )
    figure = MarketFigure(
        x_max=12, y_max=12, title="Tax Rotation", palette="monochrome"
    )
    figure.add_curves(demand, supply, q_max=10).add_tax_transform(
        demand, supply, scenario, q_max=10
    ).finalize()
    assert any(label.startswith("Tax rate = ") for label in _texts(figure))
    assert r"$e^{*}$" in _texts(figure)
    output = tmp_path / "smoke_tax_rotation.png"
    figure.save(output)
    assert output.exists()


def test_market_figure_welfare_transition_smoke(tmp_path) -> None:
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
    figure = MarketFigure(
        x_max=12, y_max=12, title="Welfare Transition", palette="monochrome"
    )
    figure.add_curves(demand, supply, q_max=10).add_welfare_transition(
        baseline_outcome=baseline_outcome,
        policy_outcome=policy_outcome,
        surplus=policy_surplus,
    ).finalize()
    labels = _texts(figure)
    assert r"$Q_0$" in labels
    assert r"$Q_1$" in labels
    assert any(letter in labels for letter in ("A", "B", "C"))
    output = tmp_path / "smoke_welfare_transition.png"
    figure.save(output)
    assert output.exists()


def test_market_figure_accepts_multiple_metrics_boxes() -> None:
    figure = MarketFigure()
    figure.add_metrics({"first": 1}, location="upper right")
    figure.add_metrics({"second": 2}, location="upper left")

    ids = {layer.id for layer in figure.scene.layers}
    assert {"market.metrics.0", "market.metrics.1"}.issubset(ids)
