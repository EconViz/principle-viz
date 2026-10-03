from __future__ import annotations

from mosaickit import Canvas as MosaicCanvas
from mosaickit import LegendLayer, PathLayer, TextLayer

from principle_viz.plot import Canvas, MarketFigure


def test_canvas_is_mosaickit_canvas() -> None:
    assert Canvas is MosaicCanvas


def test_market_figure_uses_first_quadrant_scene_axes() -> None:
    figure = MarketFigure(x_max=10.0, y_max=8.0, title=None)

    assert figure.canvas.spec.x_range == (0.0, 10.0)
    assert figure.canvas.spec.y_range == (0.0, 8.0)
    assert {layer.id for layer in figure.scene.layers}.issuperset(
        {"axes.x", "axes.y", "axes.x.label", "axes.y.label", "axes.origin.label"}
    )
    assert any(
        isinstance(layer, TextLayer) and layer.text == "0"
        for layer in figure.scene.layers
    )
    assert not hasattr(figure, "ax")
    assert not hasattr(figure, "fig")


def test_finalize_adds_scene_legend() -> None:
    figure = MarketFigure(x_max=10.0, y_max=10.0, title=None)
    figure.add_layer(
        PathLayer(
            ((0.0, 0.0), (1.0, 1.0)),
            id="test.line",
            role="principle.market.demand",
            legend="Line",
        )
    ).finalize(legend=True)

    legend = next(layer for layer in figure.scene.layers if layer.id == "market.legend")
    assert isinstance(legend, LegendLayer)
    assert legend.entries == ("test.line",)


def test_finalize_draws_no_legend_by_default() -> None:
    figure = MarketFigure(title="No legend").add_layer(
        PathLayer(((0, 0), (1, 1)), id="test.line", legend="Line")
    )
    figure.finalize()
    assert all(layer.id != "market.legend" for layer in figure.scene.layers)
