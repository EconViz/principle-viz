from __future__ import annotations

import pytest
from mosaickit import FillLayer, LegendLayer, PathLayer, RegionLabelLayer, TextLayer

from principle_viz.core.equilibrium import solve_equilibrium
from principle_viz.core.factor_markets import (
    LoanableFundsScenario,
    analyze_loanable_funds,
)
from principle_viz.core.line import Line
from principle_viz.core.ppf import (
    PPFGrowthScenario,
    ProductionPossibilitiesFrontier,
    analyze_ppf,
    analyze_ppf_growth,
)
from principle_viz.core.shifts import ShiftScenario, ShiftSpec, comparative_statics
from principle_viz.plot.figure import MarketFigure
from principle_viz.policy.externality import ExternalityScenario, analyze_externality
from principle_viz.policy.subsidy import (
    SubsidyScenario,
    SubsidyTo,
    compare_subsidy_scenario,
)
from principle_viz.policy.tax import TaxOn, TaxScenario, TaxType, solve_tax_equilibrium
from principle_viz.policy.trade import TradeScenario, analyze_trade
from principle_viz.visuals import curve_label_layer, curve_layer
from principle_viz.visuals.ppf import ppf_canvas, ppf_growth_canvas
from principle_viz.visuals.theme import PlotTheme
from principle_viz.welfare.surplus import (
    compute_surplus,
    outcome_from_equilibrium,
    outcome_from_tax,
)

DEMAND = Line.from_inverse(10.0, -1.0)
SUPPLY = Line.from_inverse(2.0, 1.0)


def _layers(figure: MarketFigure) -> dict[str, object]:
    return {layer.id: layer for layer in figure.scene.layers}


def _label(figure: MarketFigure, curve_id: str) -> TextLayer:
    label = _layers(figure)[f"{curve_id}.label"]
    assert isinstance(label, TextLayer)
    return label


def test_add_curves_names_each_curve_from_its_legend_label() -> None:
    figure = MarketFigure(x_max=12, y_max=12).add_curves(
        DEMAND,
        SUPPLY,
        q_max=10,
        demand_label="Labor demand",
        supply_label="Labor supply",
    )
    layers = _layers(figure)
    for curve_id, text in (
        ("market.demand", "Labor demand"),
        ("market.supply", "Labor supply"),
    ):
        label = _label(figure, curve_id)
        assert label.text == text == layers[curve_id].legend
        assert label.role == layers[curve_id].role


def test_curve_label_sits_beside_the_visible_end() -> None:
    figure = MarketFigure(x_max=12, y_max=12).add_curves(DEMAND, SUPPLY, q_max=11)
    demand = _label(figure, "market.demand")
    supply = _label(figure, "market.supply")
    # Demand meets the quantity axis at Q=10: text goes up and right, off the line.
    assert demand.position == pytest.approx((10.0, 0.0))
    assert demand.anchor == "bottom-left"
    # Supply leaves through the top (p=12 at Q=10): named just past its exit point.
    assert supply.position == pytest.approx((10.0, 12.0))
    assert supply.anchor == "bottom-left"
    assert demand.offset[0] > 0 and demand.offset[1] > 0


def test_curve_label_ending_at_right_edge_extends_left() -> None:
    path = curve_layer(
        Line.from_inverse(1.0, 0.5),
        q_min=0,
        q_max=10,
        layer_id="test.curve",
        role="principle.market.supply",
        label="S",
    )
    label = curve_label_layer(path, x_range=(0, 10), y_range=(0, 12))
    assert label.position == pytest.approx((10.0, 6.0))
    assert label.anchor == "bottom-right"


def test_curve_label_below_a_rising_curve_goes_under_it() -> None:
    path = curve_layer(
        Line.from_inverse(9.0, -0.5),
        q_min=0,
        q_max=10,
        layer_id="test.curve",
        role="principle.market.demand",
        label="D",
    )
    label = curve_label_layer(path, x_range=(0, 10), y_range=(0, 12))
    # Ends at the right edge and rises leftwards: the text goes left and below.
    assert label.position == pytest.approx((10.0, 4.0))
    assert label.anchor == "top-right"
    assert label.offset == (-4.0, -4.0)


def test_curve_resting_on_the_axis_is_named_where_it_lifts_off() -> None:
    path = PathLayer(
        ((0, 6), (6, 0), (10, 0)), id="mb", role="principle.market.demand", legend="MB"
    )
    label = curve_label_layer(path, x_range=(0, 10), y_range=(0, 8))
    assert label.position == pytest.approx((6.0, 0.0))
    assert label.anchor == "bottom-left"


def test_curve_label_needs_a_legend_and_a_visible_segment() -> None:
    unnamed = PathLayer(((0, 0), (1, 1)), id="x")
    assert curve_label_layer(unnamed, x_range=(0, 1), y_range=(0, 1)) is None
    outside = PathLayer(((5, 5), (6, 6)), id="y", legend="Y")
    assert curve_label_layer(outside, x_range=(0, 1), y_range=(0, 1)) is None


def test_shifted_curves_use_short_symbols() -> None:
    result = comparative_statics(
        DEMAND,
        SUPPLY,
        ShiftScenario(
            demand_shift=ShiftSpec(delta_intercept=1.5),
            supply_shift=ShiftSpec(delta_intercept=0.5),
        ),
    )
    figure = (
        MarketFigure(x_max=12, y_max=12)
        .add_curves(DEMAND, SUPPLY, q_max=10, demand_label="D₀", supply_label="S₀")
        .add_comparative_statics(result, q_max=10)
    )
    assert _label(figure, "market.demand").text == "D₀"
    assert _label(figure, "market.demand.shifted").text == "D₁"
    assert _label(figure, "market.supply.shifted").text == "S₁"


def test_unshifted_curve_is_not_labelled_twice() -> None:
    result = comparative_statics(
        DEMAND, SUPPLY, ShiftScenario(demand_shift=ShiftSpec(delta_intercept=1.5))
    )
    figure = MarketFigure(x_max=12, y_max=12).add_comparative_statics(result, q_max=10)
    assert "market.supply.shifted.label" not in _layers(figure)


@pytest.mark.parametrize("tax_type", [TaxType.PER_UNIT_TAX, TaxType.AD_VALOREM_TAX])
def test_taxed_curve_is_named(tax_type: TaxType) -> None:
    scenario = TaxScenario(tax_type=tax_type, amount=0.2, tax_on=TaxOn.PRODUCER)
    figure = MarketFigure(x_max=12, y_max=12).add_tax_transform(
        DEMAND, SUPPLY, scenario, q_max=10
    )
    label = _label(figure, "market.supply.taxed")
    assert label.text == _layers(figure)["market.supply.taxed"].legend


def test_policy_builders_name_their_curves() -> None:
    figure = MarketFigure(x_max=12, y_max=14)
    figure.add_externality(
        analyze_externality(
            DEMAND, SUPPLY, ExternalityScenario(marginal_external_cost=2)
        )
    )
    figure.add_trade(
        analyze_trade(DEMAND, SUPPLY, TradeScenario(world_price=3, tariff=1))
    )
    figure.add_loanable_funds(
        analyze_loanable_funds(
            SUPPLY, DEMAND, LoanableFundsScenario(government_borrowing=2)
        )
    )
    for curve_id in (
        "market.externality.social_cost",
        "market.trade.world_price",
        "market.trade.policy_price",
        "loanable.investment.shifted",
    ):
        assert _label(figure, curve_id).text == _layers(figure)[curve_id].legend


def test_ppf_canvases_name_frontiers_without_legends() -> None:
    frontier = ProductionPossibilitiesFrontier(10, 8, 2, "X", "Y")
    analysis = analyze_ppf(frontier, points=((6, frontier.y_at(6), "A"),))
    growth = analyze_ppf_growth(frontier, PPFGrowthScenario(x_growth_rate=0.2))
    theme = PlotTheme()
    for canvas, curve_ids in (
        (ppf_canvas(analysis, theme=theme), ("ppf.frontier",)),
        (
            ppf_growth_canvas(growth, theme=theme),
            ("ppf.growth.baseline", "ppf.growth.shifted"),
        ),
    ):
        layers = {layer.id: layer for layer in canvas.snapshot().layers}
        assert not any(isinstance(layer, LegendLayer) for layer in layers.values())
        for curve_id in curve_ids:
            assert layers[f"{curve_id}.label"].text == layers[curve_id].legend


def _tax_surplus():
    baseline = outcome_from_equilibrium(solve_equilibrium(DEMAND, SUPPLY))
    policy = outcome_from_tax(
        solve_tax_equilibrium(
            DEMAND,
            SUPPLY,
            TaxScenario(
                tax_type=TaxType.PER_UNIT_TAX, amount=1.0, tax_on=TaxOn.PRODUCER
            ),
        )
    )
    return (
        baseline,
        policy,
        compute_surplus(DEMAND, SUPPLY, policy, baseline_outcome=baseline),
    )


def test_welfare_regions_are_named_not_lettered() -> None:
    baseline, policy, surplus = _tax_surplus()
    figure = MarketFigure(x_max=12, y_max=12).add_welfare_transition(
        baseline_outcome=baseline, policy_outcome=policy, surplus=surplus
    )
    layers = figure.scene.layers
    labels = {
        layer.text: layer for layer in layers if isinstance(layer, RegionLabelLayer)
    }
    assert set(labels) == {
        "Consumer surplus",
        "Producer surplus",
        "Tax revenue",
        "Deadweight loss",
    }
    assert labels["Consumer surplus"].short_text == "CS"
    assert labels["Producer surplus"].short_text == "PS"
    assert labels["Tax revenue"].short_text == "Tax"
    assert labels["Deadweight loss"].short_text == "DWL"
    assert all(label.placement == "auto" for label in labels.values())
    fill_ids = {layer.id for layer in layers if isinstance(layer, FillLayer)}
    for text in ("Consumer surplus", "Producer surplus", "Deadweight loss"):
        assert labels[text].region in fill_ids
    texts = [str(layer.text) for layer in layers if isinstance(layer, TextLayer)]
    assert not any(text in {"A", "B", "C", "D"} for text in texts)


def test_policy_regions_are_named() -> None:
    figure = MarketFigure(x_max=12, y_max=14)
    figure.add_subsidy_comparison(
        compare_subsidy_scenario(
            DEMAND, SUPPLY, SubsidyScenario(amount=2.0, subsidy_to=SubsidyTo.PRODUCER)
        )
    )
    figure.add_trade(
        analyze_trade(DEMAND, SUPPLY, TradeScenario(world_price=3, tariff=1))
    )
    figure.add_externality(
        analyze_externality(
            DEMAND, SUPPLY, ExternalityScenario(marginal_external_cost=2)
        )
    )
    regions = {
        layer.region: layer.text
        for layer in figure.scene.layers
        if isinstance(layer, RegionLabelLayer)
    }
    assert regions == {
        "market.subsidy.expenditure": "Subsidy cost",
        "market.trade.policy_rent": "Tariff revenue",
        "market.externality.dwl": "Deadweight loss",
    }


def test_axis_titles_default_to_p_and_q_past_the_arrow_tips() -> None:
    layers = _layers(MarketFigure(x_max=12, y_max=10))
    y_title = layers["axes.y.label"]
    x_title = layers["axes.x.label"]
    assert (y_title.text, y_title.math, y_title.anchor) == ("p", True, "bottom")
    assert y_title.position == (0.0, 10.0) and y_title.offset[1] > 0
    assert (x_title.text, x_title.math, x_title.anchor) == ("Q", True, "left")
    assert x_title.position == (12.0, 0.0) and x_title.offset[0] > 0


def test_worded_axis_titles_are_not_math() -> None:
    layers = _layers(MarketFigure(x_label="Labor", y_label="w"))
    assert layers["axes.x.label"].math is False
    assert layers["axes.x.label"].anchor == "top-right"
    assert layers["axes.y.label"].math is True


def test_sum_curve_can_be_named_at_its_start() -> None:
    path = PathLayer(
        ((0, 9), (5, 4), (9, 0)), id="s", role="principle.market.demand", legend="ΣMB"
    )
    label = curve_label_layer(path, x_range=(0, 10), y_range=(0, 10), at="start")
    assert label.position == pytest.approx((0.0, 9.0))
    assert label.anchor == "bottom-left"


def test_titles_use_normal_weight() -> None:
    theme = PlotTheme().to_mosaickit()
    assert theme.roles["title"].text.weight == "normal"


def test_curves_ending_at_the_same_point_are_stacked() -> None:
    scenario = TaxScenario(
        tax_type=TaxType.AD_VALOREM_TAX, amount=0.2, tax_on=TaxOn.CONSUMER
    )
    figure = (
        MarketFigure(x_max=11, y_max=11)
        .add_curves(DEMAND, SUPPLY, q_max=10)
        .add_tax_transform(DEMAND, SUPPLY, scenario, q_max=10)
    )
    base = _label(figure, "market.demand")
    taxed = _label(figure, "market.demand.taxed")
    assert taxed.text == "D − t"
    assert taxed.position == pytest.approx(base.position)
    assert taxed.offset[1] > base.offset[1]
