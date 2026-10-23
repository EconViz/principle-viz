from __future__ import annotations

import re

import pytest
from mosaickit import BraceLayer, PointLabelLayer, TextLayer

from principle_viz import Label, MarketFigure
from principle_viz.core.line import Line
from principle_viz.policy.subsidy import (
    SubsidyScenario,
    SubsidyTo,
    compare_subsidy_scenario,
)

DEMAND = Line.from_inverse(10.0, -1.0)
SUPPLY = Line.from_inverse(2.0, 1.0)


def _layers(figure: MarketFigure) -> dict[str, object]:
    return {layer.id: layer for layer in figure.scene.layers}


def test_label_override_can_be_declared_before_layer_exists() -> None:
    figure = MarketFigure(
        labels={
            "market.demand": Label(visible=False),
            "market.supply": Label(text="$S_A$"),
        }
    ).add_curves(DEMAND, SUPPLY, q_max=10)

    demand = _layers(figure)["market.demand.label"]
    supply = _layers(figure)["market.supply.label"]
    assert isinstance(demand, PointLabelLayer) and not demand.visible
    assert isinstance(supply, PointLabelLayer) and supply.text == "$S_A$"


def test_configure_label_uses_point_offset_and_keeps_stable_id() -> None:
    figure = MarketFigure().add_curves(DEMAND, SUPPLY, q_max=10)
    figure.configure_label("market.supply", text="$S_B$", offset=(8, -5))

    label = _layers(figure)["market.supply.label"]
    assert isinstance(label, TextLayer)
    assert label.text == "$S_B$"
    assert label.offset == (8, -5)
    assert "market.supply.label" in figure.label_ids


def test_subsidy_annotations_can_be_moved_or_hidden_individually() -> None:
    result = compare_subsidy_scenario(
        DEMAND,
        SUPPLY,
        SubsidyScenario(amount=2.0, subsidy_to=SubsidyTo.PRODUCER),
    )
    figure = MarketFigure(x_max=12, y_max=12).add_subsidy_comparison(result)
    figure.configure_label("market.subsidy.expenditure", offset=(-10, 6))
    figure.configure_label("market.subsidy.wedge.label", visible=False)
    figure.configure_label("market.subsidy.wedge.brace", visible=False)

    layers = _layers(figure)
    cost = layers["market.subsidy.expenditure.label"]
    wedge = layers["market.subsidy.wedge.label"]
    brace = layers["market.subsidy.wedge.brace"]
    assert isinstance(cost, TextLayer)
    assert cost.text == "Cost"
    assert cost.offset == (-10, 6)
    assert not wedge.visible
    assert isinstance(brace, BraceLayer) and not brace.visible


def test_every_provided_subsidy_label_can_be_hidden() -> None:
    result = compare_subsidy_scenario(
        DEMAND,
        SUPPLY,
        SubsidyScenario(amount=2.0, subsidy_to=SubsidyTo.PRODUCER),
    )
    figure = (
        MarketFigure(x_max=12, y_max=12)
        .add_curves(DEMAND, SUPPLY, q_max=10)
        .add_subsidy_comparison(result)
    )

    label_ids = figure.label_ids
    for layer_id in label_ids:
        figure.configure_label(layer_id, visible=False)

    layers = _layers(figure)
    assert label_ids
    assert all(not layers[layer_id].visible for layer_id in label_ids)


def test_label_rejects_invalid_offset() -> None:
    with pytest.raises(ValueError, match="two finite values"):
        Label(offset=(1, float("nan")))


def test_configure_label_reports_unknown_id() -> None:
    figure = MarketFigure().add_curves(DEMAND, SUPPLY, q_max=10)
    with pytest.raises(KeyError, match="Unknown label"):
        figure.configure_label("market.unknown", visible=False)


def test_any_supplied_layer_can_be_hidden_and_shown() -> None:
    result = compare_subsidy_scenario(
        DEMAND,
        SUPPLY,
        SubsidyScenario(amount=2.0, subsidy_to=SubsidyTo.PRODUCER),
    )
    figure = (
        MarketFigure(x_max=12, y_max=12)
        .add_curves(DEMAND, SUPPLY, q_max=10)
        .add_subsidy_comparison(result)
    )
    optional = (
        "market.demand",
        "market.equilibrium.baseline",
        "market.subsidy.expenditure",
        "market.subsidy.wedge",
        "market.subsidy.wedge.brace",
    )

    figure.hide(*optional)
    assert all(not _layers(figure)[layer_id].visible for layer_id in optional)

    figure.show(*optional)
    assert all(_layers(figure)[layer_id].visible for layer_id in optional)


def test_visibility_can_be_declared_before_layers_exist() -> None:
    figure = MarketFigure(
        visibility={"market.demand": False},
    ).add_curves(DEMAND, SUPPLY, q_max=10)

    layers = _layers(figure)
    assert not layers["market.demand"].visible
    assert layers["market.supply"].visible
    assert layers["axes.x.label"].visible
    assert layers["axes.y.label"].visible


def test_generic_visibility_survives_later_label_changes() -> None:
    figure = MarketFigure().add_curves(DEMAND, SUPPLY, q_max=10)
    figure.hide("market.supply.label")
    figure.configure_label("market.supply", text="$S_0$")

    label = _layers(figure)["market.supply.label"]
    assert label.text == "$S_0$"
    assert not label.visible


def _equilibrium_figure(**kwargs: object) -> MarketFigure:
    from principle_viz.core.equilibrium import solve_equilibrium

    return (
        MarketFigure(**kwargs)
        .add_curves(DEMAND, SUPPLY, q_max=10)
        .add_equilibrium(solve_equilibrium(DEMAND, SUPPLY))
    )


def test_label_nudge_moves_one_label_after_placement() -> None:
    from mosaickit.styles.nudge import Nudge

    figure = _equilibrium_figure(labels={"market.equilibrium": Label(top="4pt")})
    layers = _layers(figure)
    label = layers["market.equilibrium.label"]
    assert isinstance(label, PointLabelLayer)  # still placed automatically
    assert label.nudge == Nudge(0, 4)
    assert layers["market.demand.label"].nudge is None


def test_configure_label_nudges_in_points_em_and_mm() -> None:
    from mosaickit.styles.nudge import Nudge

    figure = _equilibrium_figure()
    figure.configure_label("market.supply", Label(right="8pt", bottom=2))
    figure.configure_label("market.demand", left="0.5em", top="2mm")
    layers = _layers(figure)
    assert layers["market.supply.label"].nudge == Nudge(8, -2)
    demand = layers["market.demand.label"]
    assert demand.nudge.dx == pytest.approx(-5.5)  # the label's 11 pt font
    assert demand.nudge.dy == pytest.approx(72 / 25.4 * 2)


def test_nudge_applies_after_an_offset() -> None:
    from mosaickit.styles.nudge import Nudge

    figure = _equilibrium_figure()
    figure.configure_label("market.supply", Label(offset=(8, -5), top=3))
    label = _layers(figure)["market.supply.label"]
    assert isinstance(label, TextLayer)
    assert label.offset == (8, -5)
    assert label.nudge == Nudge(0, 3)


def test_nudged_label_changes_the_drawing_and_plain_labels_do_not(tmp_path) -> None:
    def svg(**kwargs: object) -> str:
        target = tmp_path / "figure.svg"
        _equilibrium_figure(**kwargs).save(target)
        text = re.sub(r"<dc:date>.*?</dc:date>", "", target.read_text())
        return re.sub(r"\b([pm])[0-9a-f]{8,}\b", r"\1", text)

    plain = svg()
    assert svg(labels={"market.equilibrium": Label()}) == plain
    assert svg(labels={"market.equilibrium": Label(top="4pt")}) != plain


def test_label_rejects_invalid_lengths() -> None:
    with pytest.raises(ValueError, match="Label.top"):
        Label(top="4 parsecs")
    with pytest.raises(ValueError, match="Label.left"):
        Label(left=True)


def test_axis_labels_reject_nudges() -> None:
    from mosaickit import AxisMarkLayer

    from principle_viz.plot.label import apply_label

    mark = AxisMarkLayer(id="mark", axis="y", value=3.0, label="$p_0$")
    with pytest.raises(ValueError, match="Axis labels"):
        apply_label(mark, Label(top=2))
