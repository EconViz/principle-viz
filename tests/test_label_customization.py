from __future__ import annotations

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
