from __future__ import annotations

import pytest

from principle_viz.core.factor_markets import (
    LoanableFundsScenario,
    analyze_loanable_funds,
    analyze_minimum_wage,
)
from principle_viz.core.line import Line
from principle_viz.plot.figure import MarketFigure


def test_binding_minimum_wage_creates_unemployment() -> None:
    demand = Line.from_inverse(12, -1)
    supply = Line.from_inverse(2, 1)
    result = analyze_minimum_wage(demand, supply, minimum_wage=9)

    assert result.is_binding
    assert result.labor_demanded == pytest.approx(3)
    assert result.labor_supplied == pytest.approx(7)
    assert result.employment == pytest.approx(3)
    assert result.unemployment == pytest.approx(4)
    assert result.wage_bill == pytest.approx(27)


def test_nonbinding_minimum_wage_preserves_equilibrium() -> None:
    result = analyze_minimum_wage(
        Line.from_inverse(12, -1), Line.from_inverse(2, 1), minimum_wage=5
    )

    assert not result.is_binding
    assert result.employment == pytest.approx(5)
    assert result.unemployment == pytest.approx(0)


def test_government_borrowing_raises_interest_and_crowds_out_investment() -> None:
    savings = Line.from_inverse(2, 0.5)
    investment = Line.from_inverse(12, -0.5)
    result = analyze_loanable_funds(
        savings,
        investment,
        LoanableFundsScenario(government_borrowing=4),
    )

    assert result.baseline_equilibrium.q_star == pytest.approx(10)
    assert result.baseline_equilibrium.p_star == pytest.approx(7)
    assert result.shifted_equilibrium.q_star == pytest.approx(12)
    assert result.shifted_equilibrium.p_star == pytest.approx(8)
    assert result.private_investment_after == pytest.approx(8)
    assert result.crowding_out == pytest.approx(2)


def test_factor_market_visual_layers() -> None:
    labor_demand = Line.from_inverse(12, -1)
    labor_supply = Line.from_inverse(2, 1)
    labor = analyze_minimum_wage(labor_demand, labor_supply, minimum_wage=9)
    labor_figure = MarketFigure(x_max=11, y_max=14)
    labor_figure.add_curves(labor_demand, labor_supply, q_max=10)
    labor_figure.add_minimum_wage(labor)
    labor_ids = {layer.id for layer in labor_figure.scene.layers}
    assert "labor.minimum_wage" in labor_ids
    assert "labor.unemployment" in labor_ids

    savings = Line.from_inverse(2, 0.5)
    investment = Line.from_inverse(12, -0.5)
    funds = analyze_loanable_funds(
        savings,
        investment,
        LoanableFundsScenario(government_borrowing=4),
    )
    funds_figure = MarketFigure(x_max=18, y_max=14)
    funds_figure.add_curves(investment, savings, q_max=17)
    funds_figure.add_loanable_funds(funds)
    fund_ids = {layer.id for layer in funds_figure.scene.layers}
    assert "loanable.investment.shifted" in fund_ids
    assert "loanable.equilibrium.shifted" in fund_ids


def test_binding_minimum_wage_braces_unemployment_on_the_wage_line() -> None:
    from mosaickit import AxisMarkLayer, PointLabelLayer, SpanBraceLayer

    demand, supply = Line.from_inverse(12, -1), Line.from_inverse(2, 1)
    result = analyze_minimum_wage(demand, supply, minimum_wage=9)
    figure = MarketFigure(x_max=12, y_max=14, x_label="L", y_label="w")
    figure.add_minimum_wage(result)
    layers = {layer.id: layer for layer in figure.scene.layers}
    label = layers["labor.minimum_wage.label"]
    assert isinstance(label, PointLabelLayer) and label.text == r"$w_{\min}$"
    marks = {
        (layer.axis, layer.label): layer.value
        for layer in figure.scene.layers
        if isinstance(layer, AxisMarkLayer)
    }
    assert marks[("y", r"w_{\min}")] == pytest.approx(9)
    assert marks[("x", "L_d")] == pytest.approx(result.labor_demanded)
    assert marks[("x", "L_s")] == pytest.approx(result.labor_supplied)
    brace = layers["labor.unemployment"]
    assert isinstance(brace, SpanBraceLayer)
    assert (brace.label, brace.side, brace.role) == ("Unemployment", "above", "axes")
    assert brace.start == pytest.approx((result.labor_demanded, 9))
    assert brace.end == pytest.approx((result.labor_supplied, 9))
