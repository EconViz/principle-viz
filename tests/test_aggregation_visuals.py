from __future__ import annotations

import pytest
from mosaickit import TRANSPARENT, CanvasGrid, MarkerLayer, PathLayer, TextLayer

from principle_viz import (
    AggregationFigure,
    demand_aggregation_figure,
    discrete_demand_aggregation_figure,
    discrete_supply_aggregation_figure,
    supply_aggregation_figure,
)
from principle_viz.core.aggregation import AggregationError
from principle_viz.core.discrete import DiscreteDemand, DiscreteSupply
from principle_viz.core.line import Line

DEMANDS = {"A": Line.from_inverse(10.0, -2.0), "B": Line.from_inverse(6.0, -0.5)}
SUPPLIES = {"A": Line.from_inverse(2.0, 1.0), "B": Line.from_inverse(5.0, 0.5)}


def _layers(canvas) -> dict[str, object]:
    return {layer.id: layer for layer in canvas.snapshot().layers}


def _texts(canvas) -> list[str]:
    return [
        layer.text for layer in canvas.snapshot().layers if isinstance(layer, TextLayer)
    ]


def test_demand_figure_has_one_panel_per_individual_and_a_market_panel() -> None:
    figure = demand_aggregation_figure(DEMANDS, price=4.0)
    assert isinstance(figure, AggregationFigure)
    assert len(figure.panels) == 3
    assert isinstance(figure.grid, CanvasGrid)
    assert (figure.grid.rows, figure.grid.cols) == (1, 3)
    # The panels share the price axis.
    assert len({panel.spec.y_range for panel in figure.panels}) == 1


def test_demand_panels_name_their_curves_directly() -> None:
    figure = demand_aggregation_figure(DEMANDS, price=4.0)
    a, b, market = figure.panels
    assert "$D_A$" in _texts(a)
    assert "$D_B$" in _texts(b)
    assert "$D$" in _texts(market)
    curve = _layers(market)["aggregation.market.curve"]
    assert isinstance(curve, PathLayer)
    assert curve.path == ((0.0, 10.0), (2.0, 6.0), (17.0, 0.0))
    assert curve.role == "principle.market.demand"


def test_demand_guides_show_individual_quantities_and_their_sum() -> None:
    figure = demand_aggregation_figure(DEMANDS, price=4.0)
    a, b, market = figure.panels
    assert _layers(a)["aggregation.A.point"].points == ((3.0, 4.0),)
    assert _layers(b)["aggregation.B.point"].points == ((4.0, 4.0),)
    assert _layers(market)["aggregation.market.point"].points == ((7.0, 4.0),)
    guide = _layers(market)["aggregation.market.guide.quantity"]
    assert guide.path == ((7.0, 4.0), (7.0, 0.0))
    assert "$Q_A$" in _texts(a)
    assert "$Q_B$" in _texts(b)
    assert "$Q_A + Q_B = Q$" in _texts(market)
    assert all("$p_1$" in _texts(panel) for panel in figure.panels)


def test_supply_figure_names_curves_and_sums_at_the_chosen_price() -> None:
    figure = supply_aggregation_figure(SUPPLIES, price=8.0, p_max=10.0)
    a, b, market = figure.panels
    assert "$S_A$" in _texts(a) and "$S_B$" in _texts(b) and "$S$" in _texts(market)
    curve = _layers(market)["aggregation.market.curve"]
    assert curve.path == ((0.0, 2.0), (3.0, 5.0), (18.0, 10.0))
    assert curve.role == "principle.market.supply"
    assert _layers(market)["aggregation.market.point"].points == ((12.0, 8.0),)


def test_labels_use_latex_rather_than_unicode_symbols() -> None:
    figure = supply_aggregation_figure(SUPPLIES, price=8.0, p_max=10.0)
    for panel in figure.panels:
        for text in _texts(panel):
            assert text.isascii(), text


def test_figure_rejects_a_price_outside_the_curves() -> None:
    with pytest.raises(AggregationError, match="price"):
        demand_aggregation_figure(DEMANDS, price=12.0)
    with pytest.raises(AggregationError, match="price"):
        supply_aggregation_figure(SUPPLIES, price=11.0, p_max=10.0)
    with pytest.raises(AggregationError, match="individual"):
        demand_aggregation_figure({}, price=1.0)


def test_discrete_demand_figure_draws_steps_with_closed_and_open_ends() -> None:
    figure = discrete_demand_aggregation_figure(
        {"A": DiscreteDemand((10, 7, 4)), "B": DiscreteDemand((8, 5, 2))}, price=6.0
    )
    a, _, market = figure.panels
    layers = _layers(market)
    steps = [
        layer.path
        for layer_id, layer in layers.items()
        if layer_id.startswith("aggregation.market.curve.step")
    ]
    assert [path[0][1] for path in steps] == [10, 8, 7, 5, 4, 2]
    closed = layers["aggregation.market.curve.closed"]
    opened = layers["aggregation.market.curve.open"]
    assert isinstance(closed, MarkerLayer) and closed.marker.color != TRANSPARENT
    assert isinstance(opened, MarkerLayer) and opened.marker.color == TRANSPARENT
    assert "$D_A$" in _texts(a) and "$D$" in _texts(market)
    # The guide down from Q = 3 breaks around the closed endpoint (3, 5).
    upper = layers["aggregation.market.guide.quantity"].path
    lower = layers["aggregation.market.guide.quantity.1"].path
    assert upper[0] == (3.0, 6.0) and lower[1] == (3.0, 0.0)
    assert upper[1][1] > 5.0 > lower[0][1]


def test_discrete_supply_figure_sums_units_at_the_chosen_price() -> None:
    figure = discrete_supply_aggregation_figure(
        {"A": DiscreteSupply((2, 5, 8)), "B": DiscreteSupply((3, 4, 9))}, price=6.0
    )
    a, b, market = figure.panels
    assert "$S_B$" in _texts(b) and "$S$" in _texts(market)
    # Each guide breaks around the open endpoint of the last unit sold.
    a_upper = _layers(a)["aggregation.A.guide.quantity"].path
    a_lower = _layers(a)["aggregation.A.guide.quantity.1"].path
    assert a_upper[0] == (2.0, 6.0) and a_lower[1] == (2.0, 0.0)
    assert a_upper[1][1] > 5.0 > a_lower[0][1]
    assert _layers(market)["aggregation.market.guide.quantity"].path[0] == (4.0, 6.0)
    assert "$Q_A + Q_B = Q$" in _texts(market)


def test_aggregation_figure_saves(tmp_path) -> None:
    output = tmp_path / "aggregation.png"
    demand_aggregation_figure(DEMANDS, price=4.0, palette="monochrome").save(output)
    assert output.exists() and output.stat().st_size > 0


def test_an_individual_who_buys_nothing_gets_no_guides() -> None:
    # At p = 8 only A buys (B's choke price is 6).
    figure = demand_aggregation_figure(DEMANDS, price=8.0)
    b_layers = _layers(figure.panels[1])
    assert "aggregation.B.price.label" in b_layers
    assert "aggregation.B.guide.quantity" not in b_layers
    market = _layers(figure.panels[2])
    assert market["aggregation.market.point"].points == ((1.0, 8.0),)


def test_discrete_figure_rejects_a_nonpositive_price() -> None:
    with pytest.raises(AggregationError, match="positive"):
        discrete_supply_aggregation_figure({"A": DiscreteSupply((1, 2))}, price=0.0)
