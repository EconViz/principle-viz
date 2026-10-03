from __future__ import annotations

import pytest
from mosaickit import TRANSPARENT, DashStyle, MarkerLayer, PathLayer

from principle_viz.core.discrete import (
    DiscreteDemand,
    DiscreteSupply,
    solve_discrete_equilibrium,
)
from principle_viz.plot import MarketFigure
from principle_viz.visuals.discrete import OPEN_FILL


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
    # Open points are opaque white so the step does not show through them.
    assert opened.marker is not None and opened.marker.color == OPEN_FILL
    # A dashed drop joins each open point to the closed point of the next step.
    connectors = [
        layers[f"market.discrete.demand.connector.{index}"] for index in range(2)
    ]
    assert [layer.path for layer in connectors] == [
        ((1.0, 9.0), (1.0, 7.0)),
        ((2.0, 7.0), (2.0, 5.0)),
    ]
    assert all(layer.stroke.dash == DashStyle.DASHED for layer in connectors)
    assert "market.discrete.demand.connector.2" not in layers
    supply_rise = layers["market.discrete.supply.connector.0"]
    assert supply_rise.path == ((1.0, 1.0), (1.0, 3.0))


@pytest.mark.parametrize("side", ["demand", "supply"])
def test_a_single_discrete_schedule_can_be_drawn_alone(side: str) -> None:
    schedules = {"demand": DiscreteDemand((9, 7, 5)), "supply": DiscreteSupply((1, 3))}
    figure = MarketFigure(x_max=3.5, y_max=10).add_discrete_curves(
        **{side: schedules[side]}
    )
    ids = {layer.id for layer in figure.scene.layers}
    other = "supply" if side == "demand" else "demand"
    assert f"market.discrete.{side}.step.0" in ids
    assert not any(layer_id.startswith(f"market.discrete.{other}") for layer_id in ids)


def test_discrete_curves_need_a_schedule() -> None:
    with pytest.raises(ValueError, match="demand or a supply"):
        MarketFigure(x_max=3.5, y_max=10).add_discrete_curves()


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
