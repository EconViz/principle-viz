"""Automatic point labels, axis marks, the tax brace, and palette-named colours."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
from mosaickit import (
    DEFAULT_PALETTE,
    AxisMarkLayer,
    AxisNoteLayer,
    BraceLayer,
    Config,
    Palette,
    PointLabelLayer,
    SpanBraceLayer,
    TextLayer,
    use_config,
)

from principle_viz.core.controls import (
    PriceControlScenario,
    PriceControlType,
    evaluate_price_control,
)
from principle_viz.core.equilibrium import solve_equilibrium
from principle_viz.core.factor_markets import (
    LoanableFundsScenario,
    analyze_loanable_funds,
)
from principle_viz.core.line import Line
from principle_viz.core.shifts import ShiftScenario, ShiftSpec, comparative_statics
from principle_viz.plot import get_color_model
from principle_viz.plot.figure import MarketFigure
from principle_viz.policy.common_resources import analyze_common_resource
from principle_viz.policy.externality import ExternalityScenario, analyze_externality
from principle_viz.policy.subsidy import (
    SubsidyScenario,
    SubsidyTo,
    compare_subsidy_scenario,
)
from principle_viz.policy.tax import (
    TaxOn,
    TaxScenario,
    TaxType,
    compare_tax_scenario,
    solve_tax_equilibrium,
)
from principle_viz.policy.trade import TradeScenario, analyze_trade
from principle_viz.visuals.theme import PlotTheme
from principle_viz.welfare.surplus import (
    compute_surplus,
    outcome_from_equilibrium,
    outcome_from_tax,
)

ROOT = Path(__file__).parents[1]
DEMAND = Line.from_inverse(10.0, -1.0)
SUPPLY = Line.from_inverse(2.0, 1.0)
TAX = TaxScenario(tax_type=TaxType.PER_UNIT_TAX, amount=2.0, tax_on=TaxOn.PRODUCER)


def _layers(figure: MarketFigure) -> dict[str, object]:
    return {layer.id: layer for layer in figure.scene.layers}


def _point_label(figure: MarketFigure, layer_id: str) -> PointLabelLayer:
    label = _layers(figure)[layer_id]
    assert isinstance(label, PointLabelLayer), type(label).__name__
    return label


def _marks(figure: MarketFigure, axis: str) -> dict[str, float]:
    return {
        layer.label: layer.value
        for layer in figure.scene.layers
        if isinstance(layer, AxisMarkLayer) and layer.axis == axis
    }


def test_equilibrium_labels_are_point_labels() -> None:
    eq = solve_equilibrium(DEMAND, SUPPLY)
    figure = MarketFigure().add_equilibrium(eq)
    label = _point_label(figure, "market.equilibrium.label")
    assert label.point == pytest.approx((eq.q_star, eq.p_star))
    assert label.text == "$e^*$"


def test_comparative_statics_labels_are_point_labels() -> None:
    result = comparative_statics(
        DEMAND, SUPPLY, ShiftScenario(demand_shift=ShiftSpec(delta_intercept=1.5))
    )
    figure = MarketFigure().add_comparative_statics(result, q_max=10)
    assert _point_label(figure, "market.equilibrium.baseline.label").text == "$e_0$"
    assert _point_label(figure, "market.equilibrium.shifted.label").text == "$e_1$"


def test_curve_labels_are_point_labels_at_the_curve_end() -> None:
    figure = MarketFigure(x_max=12, y_max=12).add_curves(DEMAND, SUPPLY, q_max=11)
    demand = _point_label(figure, "market.demand.label")
    assert demand.text == "Demand"
    assert demand.point == pytest.approx((10.0, 0.0))


@pytest.mark.parametrize(
    ("build", "label_id", "prefix"),
    [
        (
            lambda f: f.add_tax_comparison(compare_tax_scenario(DEMAND, SUPPLY, TAX)),
            "market.tax.wedge.label",
            "Tax wedge",
        ),
        (
            lambda f: f.add_tax_transform(DEMAND, SUPPLY, TAX, q_max=10),
            "market.tax.shift.label",
            "$t = ",
        ),
        (
            lambda f: f.add_externality(
                analyze_externality(
                    DEMAND, SUPPLY, ExternalityScenario(marginal_external_cost=2)
                )
            ),
            "market.externality.corrective_wedge.label",
            "$t = ",
        ),
        (
            lambda f: f.add_common_resource(
                analyze_common_resource(DEMAND, SUPPLY, marginal_congestion_cost=2)
            ),
            "market.common_resource.fee.label",
            "Fee = ",
        ),
        (
            lambda f: f.add_subsidy_comparison(
                compare_subsidy_scenario(
                    DEMAND, SUPPLY, SubsidyScenario(2.0, SubsidyTo.PRODUCER)
                )
            ),
            "market.subsidy.wedge.label",
            "$s = ",
        ),
    ],
)
def test_policy_annotations_are_point_labels(build, label_id, prefix) -> None:
    figure = build(MarketFigure(x_max=12, y_max=14))
    assert _point_label(figure, label_id).text.startswith(prefix)


def test_no_text_layer_is_placed_by_a_hard_coded_offset() -> None:
    eq = solve_equilibrium(DEMAND, SUPPLY)
    figure = (
        MarketFigure(x_max=12, y_max=14)
        .add_curves(DEMAND, SUPPLY, q_max=10)
        .add_equilibrium(eq)
        .add_tax_comparison(compare_tax_scenario(DEMAND, SUPPLY, TAX))
        .add_trade(
            analyze_trade(DEMAND, SUPPLY, TradeScenario(world_price=4, tariff=1))
        )
        .add_loanable_funds(
            analyze_loanable_funds(
                SUPPLY, DEMAND, LoanableFundsScenario(government_borrowing=2)
            )
        )
    )
    loose = [
        layer.id
        for layer in figure.scene.layers
        if isinstance(layer, TextLayer) and not layer.id.startswith("axes.")
    ]
    assert loose == []


def test_trade_prices_are_axis_marks() -> None:
    figure = MarketFigure(x_max=12, y_max=14).add_trade(
        analyze_trade(DEMAND, SUPPLY, TradeScenario(world_price=4, tariff=2))
    )
    marks = _marks(figure, "y")
    assert marks["p_w"] == pytest.approx(4.0)
    assert marks["p_w + t"] == pytest.approx(6.0)


def test_welfare_guides_are_axis_marks() -> None:
    baseline = outcome_from_equilibrium(solve_equilibrium(DEMAND, SUPPLY))
    policy = outcome_from_tax(solve_tax_equilibrium(DEMAND, SUPPLY, TAX))
    surplus = compute_surplus(DEMAND, SUPPLY, policy, baseline_outcome=baseline)
    figure = MarketFigure().add_welfare_transition(
        baseline_outcome=baseline, policy_outcome=policy, surplus=surplus
    )
    assert set(_marks(figure, "x")) == {"Q_0", "Q_1"}
    assert set(_marks(figure, "y")) == {"p_0", "p_1^c", "p_1^p"}
    assert all(
        layer.math for layer in figure.scene.layers if isinstance(layer, AxisMarkLayer)
    )


def _tax_figure(**kwargs: object) -> MarketFigure:
    return MarketFigure(x_max=12, y_max=12).add_tax_comparison(
        compare_tax_scenario(DEMAND, SUPPLY, TAX), **kwargs
    )


def test_tax_wedge_marks_prices_and_a_tax_brace_outside_by_default() -> None:
    comparison = compare_tax_scenario(DEMAND, SUPPLY, TAX)
    figure = _tax_figure()
    marks = _marks(figure, "y")
    assert marks == pytest.approx(
        {
            "p_d": comparison.post_tax.consumer_price,
            "p_0": comparison.baseline_equilibrium.p_star,
            "p_s": comparison.post_tax.producer_price,
        }
    )
    (brace,) = [layer for layer in figure.scene.layers if isinstance(layer, BraceLayer)]
    assert brace.axis == "y" and brace.label == "Tax" and brace.side == "outside"
    assert (brace.start, brace.end) == pytest.approx(
        (comparison.post_tax.producer_price, comparison.post_tax.consumer_price)
    )
    assert not any(isinstance(layer, AxisNoteLayer) for layer in figure.scene.layers)


def test_tax_brace_can_sit_inside_and_notes_are_opt_in() -> None:
    figure = _tax_figure(brace_side="inside", notes=True)
    (brace,) = [layer for layer in figure.scene.layers if isinstance(layer, BraceLayer)]
    assert brace.side == "inside"
    notes = [layer for layer in figure.scene.layers if isinstance(layer, AxisNoteLayer)]
    assert len(notes) == 3


def test_welfare_tax_transition_keeps_one_mark_per_price() -> None:
    baseline = outcome_from_equilibrium(solve_equilibrium(DEMAND, SUPPLY))
    policy = outcome_from_tax(solve_tax_equilibrium(DEMAND, SUPPLY, TAX))
    surplus = compute_surplus(DEMAND, SUPPLY, policy, baseline_outcome=baseline)
    figure = (
        MarketFigure()
        .add_welfare_transition(
            baseline_outcome=baseline, policy_outcome=policy, surplus=surplus
        )
        .add_tax_comparison(compare_tax_scenario(DEMAND, SUPPLY, TAX))
    )
    assert set(_marks(figure, "y")) == {"p_d", "p_0", "p_s"}


def test_default_theme_names_palette_colours() -> None:
    model = get_color_model("default")
    assert (model.demand_color, model.supply_color, model.dwl_color) == (
        "blue",
        "red",
        "teal",
    )
    roles = PlotTheme().to_mosaickit().roles
    assert roles["principle.market.demand"].stroke.color == "blue"
    assert roles["principle.market.supply"].stroke.color == "red"
    assert roles["principle.welfare.loss"].fill.color == "teal"
    assert roles["principle.welfare.consumer"].fill.color == "blue"


def test_other_palettes_still_render(tmp_path) -> None:
    for name in ("colorblind", "nord", "monochrome"):
        figure = MarketFigure(palette=name).add_curves(DEMAND, SUPPLY, q_max=10)
        figure.save(tmp_path / f"{name}.svg")


def test_config_palette_override_recolours_the_demand_curve(tmp_path) -> None:
    palette = Palette("brand", {**DEFAULT_PALETTE.colors, "blue": "#0072B2"})
    with use_config(Config(palette=palette)):
        figure = MarketFigure().add_curves(DEMAND, SUPPLY, q_max=10)
    target = tmp_path / "recoloured.svg"
    figure.save(target)
    svg = target.read_text().lower()
    assert "#0072b2" in svg
    assert DEFAULT_PALETTE["blue"].to_hex().lower() not in svg


def test_sources_use_latex_not_unicode_symbols() -> None:
    offenders = [
        f"{path.relative_to(ROOT)}:{number}"
        for folder in ("src", "examples/scripts")
        for path in sorted((ROOT / folder).rglob("*.py"))
        for number, line in enumerate(path.read_text().splitlines(), start=1)
        if not line.isascii()
    ]
    assert offenders == []


def test_examples_raise_no_layout_warning() -> None:
    script = (
        "import runpy, sys, warnings\n"
        "from mosaickit import LayoutWarning\n"
        "sys.path.insert(0, 'examples/scripts')\n"
        "with warnings.catch_warnings(record=True) as caught:\n"
        "    warnings.simplefilter('always', LayoutWarning)\n"
        "    runpy.run_path('examples/scripts/run_all.py', run_name='__main__')\n"
        "found = [str(w.message) for w in caught if w.category is LayoutWarning]\n"
        "print('\\n'.join(found))\n"
        "sys.exit(1 if found else 0)\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        check=False,
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr[-2000:]


@pytest.mark.parametrize(
    "world_price,label,low,high",
    [(4.0, "Imports", "Q_s", "Q_d"), (8.0, "Exports", "Q_d", "Q_s")],
)
def test_trade_volume_is_a_brace_on_the_quantity_axis(
    world_price: float, label: str, low: str, high: str
) -> None:
    result = analyze_trade(DEMAND, SUPPLY, TradeScenario(world_price))
    figure = MarketFigure(x_max=12, y_max=14).add_trade(result)
    brace = next(
        layer for layer in figure.scene.layers if isinstance(layer, BraceLayer)
    )
    outcome = result.policy
    q_low, q_high = sorted((outcome.quantity_supplied, outcome.quantity_demanded))
    assert (brace.axis, brace.label) == ("x", label)
    assert (brace.start, brace.end) == pytest.approx((q_low, q_high))
    marks = _marks(figure, "x")
    assert marks[low] == pytest.approx(q_low)
    assert marks[high] == pytest.approx(q_high)


@pytest.mark.parametrize(
    "control,price,name,gap,side",
    [
        (PriceControlType.CEILING, 4.0, "Price ceiling", "Shortage", "below"),
        (PriceControlType.FLOOR, 8.0, "Price floor", "Surplus", "above"),
    ],
)
def test_binding_price_control_braces_the_gap_on_the_control_line(
    control: PriceControlType, price: float, name: str, gap: str, side: str
) -> None:
    result = evaluate_price_control(
        DEMAND, SUPPLY, PriceControlScenario(control, price)
    )
    figure = MarketFigure(x_max=12, y_max=12).add_price_control(result)
    layers = {layer.id: layer for layer in figure.scene.layers}
    assert layers["market.control.price"].legend == name
    assert isinstance(layers["market.control.price.label"], PointLabelLayer)
    assert layers["market.control.price.label"].text == name
    assert _marks(figure, "y")["p_c"] == pytest.approx(price)
    q_d, q_s = DEMAND.q_at(price), SUPPLY.q_at(price)
    marks = _marks(figure, "x")
    assert (marks["Q_d"], marks["Q_s"]) == pytest.approx((q_d, q_s))
    brace = layers["market.control.gap"]
    assert isinstance(brace, SpanBraceLayer)
    assert (brace.label, brace.side, brace.role) == (gap, side, "axes")
    low, high = sorted((q_d, q_s))
    assert brace.start == pytest.approx((low, price))
    assert brace.end == pytest.approx((high, price))


def test_price_control_gap_can_be_braced_on_the_quantity_axis() -> None:
    result = evaluate_price_control(
        DEMAND, SUPPLY, PriceControlScenario(PriceControlType.CEILING, 4.0)
    )
    figure = MarketFigure(x_max=12, y_max=12).add_price_control(
        result, gap_brace="axis"
    )
    brace = {layer.id: layer for layer in figure.scene.layers}["market.control.gap"]
    assert isinstance(brace, BraceLayer)
    assert (brace.axis, brace.label, brace.role) == ("x", "Shortage", "axes")


def test_non_binding_price_control_has_no_gap_brace() -> None:
    result = evaluate_price_control(
        DEMAND, SUPPLY, PriceControlScenario(PriceControlType.CEILING, 9.0)
    )
    figure = MarketFigure(x_max=12, y_max=12).add_price_control(result)
    assert not any(
        isinstance(layer, (BraceLayer, SpanBraceLayer)) for layer in figure.scene.layers
    )


def test_externality_quantities_are_axis_marks_not_point_labels() -> None:
    result = analyze_externality(
        DEMAND, SUPPLY, ExternalityScenario(marginal_external_cost=2)
    )
    figure = MarketFigure(x_max=12, y_max=14).add_externality(result)
    marks = _marks(figure, "x")
    assert marks["Q_m"] == pytest.approx(result.private_equilibrium.q_star)
    assert marks["Q^*"] == pytest.approx(result.social_equilibrium.q_star)
    point_texts = {
        layer.text
        for layer in figure.scene.layers
        if isinstance(layer, PointLabelLayer)
    }
    assert not point_texts & {"$Q_m$", "$Q^*$"}


def test_common_resource_quantities_are_axis_marks_not_point_labels() -> None:
    result = analyze_common_resource(DEMAND, SUPPLY, marginal_congestion_cost=2)
    figure = MarketFigure(x_max=12, y_max=14).add_common_resource(result)
    marks = _marks(figure, "x")
    assert marks[r"Q_{\mathrm{open}}"] == pytest.approx(
        result.open_access_equilibrium.q_star
    )
    assert marks["Q^*"] == pytest.approx(result.efficient_equilibrium.q_star)
    point_texts = {
        layer.text
        for layer in figure.scene.layers
        if isinstance(layer, PointLabelLayer)
    }
    assert not point_texts & {r"$Q_{\mathrm{open}}$", "$Q^*$"}
