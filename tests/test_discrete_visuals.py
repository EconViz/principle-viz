from __future__ import annotations

from mosaickit import TRANSPARENT, MarkerLayer, PathLayer

from principle_viz.core.discrete import (
    DiscreteDemand,
    DiscreteSupply,
    solve_discrete_equilibrium,
)
from principle_viz.plot import MarketFigure


def test_discrete_steps_have_closed_left_and_open_right_markers() -> None:
    figure = MarketFigure(x_max=3.5, y_max=10)
    figure.add_discrete_curves(DiscreteDemand((9, 7, 5)), DiscreteSupply((1, 3, 6)))

    layers = {layer.id: layer for layer in figure.scene.layers}
    demand_steps = [
        layer
        for layer in figure.scene.layers
        if isinstance(layer, PathLayer)
        and layer.id.startswith("market.discrete.demand.step")
    ]
    assert [layer.path for layer in demand_steps] == [
        ((0.0, 9.0), (1.0, 9.0)),
        ((1.0, 7.0), (2.0, 7.0)),
        ((2.0, 5.0), (3.0, 5.0)),
    ]
    closed = layers["market.discrete.demand.closed"]
    opened = layers["market.discrete.demand.open"]
    assert isinstance(closed, MarkerLayer)
    assert isinstance(opened, MarkerLayer)
    assert closed.marker is not None and closed.marker.color != TRANSPARENT
    assert opened.marker is not None and opened.marker.color == TRANSPARENT


def test_discrete_market_figure_saves(tmp_path) -> None:
    demand = DiscreteDemand((11, 9, 7, 5, 3))
    supply = DiscreteSupply((1, 3, 5, 8, 10))
    equilibrium = solve_discrete_equilibrium(demand, supply)
    figure = MarketFigure(x_max=5.5, y_max=12, palette="monochrome")
    figure.add_discrete_curves(demand, supply).add_discrete_equilibrium(
        equilibrium
    ).finalize()

    output = tmp_path / "discrete.svg"
    figure.save(output)
    assert output.exists() and output.stat().st_size > 0
    ids = {layer.id for layer in figure.scene.layers}
    assert "market.discrete.equilibrium.price_interval.lower" in ids
    assert "market.discrete.equilibrium.price_interval.upper" in ids
    assert "market.discrete.equilibrium" in ids
