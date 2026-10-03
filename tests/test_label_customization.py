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


def test_label_rejects_invalid_offset() -> None:
    with pytest.raises(ValueError, match="two finite values"):
        Label(offset=(1, float("nan")))


def test_configure_label_reports_unknown_id() -> None:
    figure = MarketFigure().add_curves(DEMAND, SUPPLY, q_max=10)
    with pytest.raises(KeyError, match="Unknown label"):
        figure.configure_label("market.unknown", visible=False)
