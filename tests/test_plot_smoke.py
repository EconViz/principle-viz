from __future__ import annotations

from mosaickit import AxisMarkLayer, PointLabelLayer, RegionLabelLayer, TextLayer

from principle_viz.core.equilibrium import solve_equilibrium
from principle_viz.core.line import Line
from principle_viz.core.shifts import ShiftScenario, ShiftSpec, comparative_statics
from principle_viz.plot.figure import MarketFigure
from principle_viz.policy.tax import TaxOn, TaxScenario, TaxType, solve_tax_equilibrium
from principle_viz.visuals.theme import PlotTheme
from principle_viz.welfare.surplus import (
    compute_surplus,
    outcome_from_equilibrium,
    outcome_from_tax,
)


def _texts(figure: MarketFigure) -> list[str]:
    """Every piece of text a figure draws: plain text, point labels, axis marks."""
    texts = []
    for layer in figure.scene.layers:
        if isinstance(layer, (TextLayer, PointLabelLayer)):
            texts.append(str(layer.text))
        elif isinstance(layer, AxisMarkLayer):
            texts.append(f"${layer.label}$" if layer.math else str(layer.label))
    return texts


def test_market_figure_smoke_save_all_static_formats(tmp_path) -> None:
    demand = Line.from_inverse(10.0, -1.0)
    supply = Line.from_inverse(2.0, 1.0)
    eq = solve_equilibrium(demand, supply)
    figure = MarketFigure(x_max=12, y_max=12, title="Smoke")
    figure.add_curves(demand, supply, q_max=10).add_equilibrium(eq).finalize()

    assert "$e^*$" in _texts(figure)
    layer_ids = {layer.id for layer in figure.scene.layers}
    assert layer_ids.issuperset(
        {"market.demand", "market.supply", "market.equilibrium"}
    )
    assert "market.legend" not in layer_ids
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
    assert any(label.startswith("$t = ") for label in _texts(figure))
    assert "$e^*$" in _texts(figure)
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
    assert any(
        label.startswith("$t = ") and label.endswith("\\%$") for label in _texts(figure)
    )
    assert "$e^*$" in _texts(figure)
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
    region_names = {
        layer.text
        for layer in figure.scene.layers
        if isinstance(layer, RegionLabelLayer)
    }
    assert {"Consumer surplus", "Producer surplus"} <= region_names
    output = tmp_path / "smoke_welfare_transition.png"
    figure.save(output)
    assert output.exists()


def test_market_figure_accepts_multiple_metrics_boxes() -> None:
    figure = MarketFigure()
    figure.add_metrics({"first": 1}, location="upper right")
    figure.add_metrics({"second": 2}, location="upper left")

    ids = {layer.id for layer in figure.scene.layers}
    assert {"market.metrics.0", "market.metrics.1"}.issubset(ids)


def test_comparative_statics_redraws_only_the_curve_that_moved() -> None:
    demand, supply = Line.from_inverse(10.0, -1.0), Line.from_inverse(2.0, 1.0)
    result = comparative_statics(
        demand, supply, ShiftScenario(demand_shift=ShiftSpec(delta_intercept=3.0))
    )
    figure = MarketFigure(x_max=12, y_max=14)
    figure.add_curves(demand, supply, q_max=10).add_comparative_statics(result, 10)
    ids = {layer.id for layer in figure.scene.layers}
    assert "market.demand.shifted" in ids
    assert "market.supply.shifted" not in ids


def test_movement_arrows_are_thin_black_and_dashed() -> None:
    from mosaickit import DashStyle

    from principle_viz.visuals.policy import MOVEMENT_ROLE, tax_shift_layers

    theme = PlotTheme()
    stroke = theme.to_mosaickit().roles[MOVEMENT_ROLE].stroke
    assert stroke.dash == DashStyle.DASHED
    assert stroke.width == theme.arrow_linewidth < theme.demand_linewidth
    assert stroke.color == theme.arrow_color
    arrow, label = tax_shift_layers(
        quantity=4, base_price=6, taxed_price=8, label="$t = 2$", layer_id="tax"
    )
    assert arrow.role == label.role == MOVEMENT_ROLE


def test_every_dashed_semantic_role_uses_the_thin_width() -> None:
    from mosaickit import DashStyle

    theme = PlotTheme()
    roles = theme.to_mosaickit().roles
    dashed_roles = {
        "principle.market.demand.shifted": theme.shifted_linewidth,
        "principle.market.supply.shifted": theme.shifted_linewidth,
        "principle.market.movement": theme.arrow_linewidth,
        "principle.policy.control": theme.dashed_linewidth,
        "principle.policy.tax": theme.tax_linewidth,
        "principle.policy.subsidy": theme.tax_linewidth,
        "principle.trade.world": theme.dashed_linewidth,
        "principle.trade.policy": theme.dashed_linewidth,
        "principle.ppf.shifted": theme.dashed_linewidth,
    }

    for role, expected_width in dashed_roles.items():
        assert roles[role].stroke.dash == DashStyle.DASHED
        assert roles[role].stroke.width == expected_width == 1.0
