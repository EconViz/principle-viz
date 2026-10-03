from __future__ import annotations

import pytest
from mosaickit import (
    TRANSPARENT,
    AxisMarkLayer,
    CanvasGrid,
    MarkerLayer,
    PathLayer,
    PointLabelLayer,
    TextLayer,
)

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
from principle_viz.visuals.discrete import OPEN_FILL

DEMANDS = {"A": Line.from_inverse(10.0, -2.0), "B": Line.from_inverse(6.0, -0.5)}
SUPPLIES = {"A": Line.from_inverse(2.0, 1.0), "B": Line.from_inverse(5.0, 0.5)}


def _layers(canvas) -> dict[str, object]:
    return {layer.id: layer for layer in canvas.snapshot().layers}


def _texts(canvas) -> list[str]:
    texts: list[str] = []
    for layer in canvas.snapshot().layers:
        if isinstance(layer, (TextLayer, PointLabelLayer)):
            texts.append(layer.text)
        elif isinstance(layer, AxisMarkLayer):
            texts.append(layer.label)
    return texts


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
    assert isinstance(opened, MarkerLayer) and opened.marker.color == OPEN_FILL
    assert "$D_A$" in _texts(a) and "$D$" in _texts(market)
    # At Q = 3 the riser runs from 7 down to 5, through p = 6: the guide does
    # not double it and starts below the closed endpoint (3, 5).
    (top, bottom) = layers["aggregation.market.guide.quantity"].path
    assert top[0] == bottom[0] == 3.0 and 0 < 5.0 - top[1] < 1.0
    assert bottom == (3.0, 0.0)
    assert "aggregation.market.guide.quantity.1" not in layers


def test_discrete_supply_figure_sums_units_at_the_chosen_price() -> None:
    figure = discrete_supply_aggregation_figure(
        {"A": DiscreteSupply((2, 5, 8)), "B": DiscreteSupply((3, 4, 9))}, price=6.0
    )
    a, b, market = figure.panels
    assert "$S_B$" in _texts(b) and "$S$" in _texts(market)
    # Each guide leaves the riser at Q to the schedule and starts below the
    # open endpoint of the last unit sold.
    (top, bottom) = _layers(a)["aggregation.A.guide.quantity"].path
    assert top[0] == 2.0 and 0 < 5.0 - top[1] < 1.0 and bottom == (2.0, 0.0)
    assert _layers(market)["aggregation.market.guide.quantity"].path[0][0] == 4.0
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


def test_linked_price_line_runs_across_every_panel() -> None:
    from mosaickit import AxisMarkLayer, GridLink

    figure = demand_aggregation_figure(
        {"A": Line.from_inverse(10.0, -2.0), "B": Line.from_inverse(6.0, -0.5)},
        price=4.0,
        link_price=True,
    )
    assert len(figure.links) == 2
    for index, (link, panel) in enumerate(
        zip(figure.links, figure.panels, strict=False)
    ):
        assert isinstance(link, GridLink)
        assert (link.start_cell, link.end_cell) == (index, index + 1)
        assert link.start == (panel.spec.x_range[1], 4.0)
        assert link.end == (0.0, 4.0)
    for index, panel in enumerate(figure.panels):
        layers = _layers(panel)
        guide = layers[f"aggregation.{('A', 'B', 'market')[index]}.guide.price"]
        assert guide.path[1] == (panel.spec.x_range[1], 4.0)
        price_marks = [
            layer
            for layer in layers.values()
            if isinstance(layer, AxisMarkLayer) and layer.axis == "y"
        ]
        assert len(price_marks) == (1 if index == 0 else 0)
    assert figure.grid.links == figure.links


def test_linked_demand_can_mark_an_individual_choke_price_and_market_kink() -> None:
    figure = demand_aggregation_figure(
        DEMANDS,
        price=DEMANDS["B"].p_intercept(),
        price_label="$p_B$",
        link_price=True,
    )
    a, b, market = figure.panels

    assert _layers(a)["aggregation.A.point"].points == ((2.0, 6.0),)
    assert "aggregation.B.guide.quantity" not in _layers(b)
    assert _layers(market)["aggregation.market.point"].points == ((2.0, 6.0),)
    assert _layers(market)["aggregation.market.curve"].path[1] == (2.0, 6.0)
    assert "$p_B$" in _texts(a)


def test_price_line_is_not_linked_by_default() -> None:
    figure = supply_aggregation_figure(
        {"A": Line.from_inverse(2.0, 1.0), "B": Line.from_inverse(5.0, 0.5)},
        price=8.0,
        p_max=10.0,
    )
    assert figure.links == ()
