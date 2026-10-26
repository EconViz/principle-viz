"""Attributes and methods the figure mixins rely on."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

    from mosaickit import Layer, Scene

    from principle_viz.plot.canvas import Canvas
    from principle_viz.plot.figure import MarketFigure
    from principle_viz.plot.theme import PlotTheme


class _Host:
    """What every figure mixin may use from the finished ``MarketFigure``."""

    if TYPE_CHECKING:
        theme: PlotTheme
        x_max: float
        y_max: float
        canvas: Canvas

        @property
        def scene(self) -> Scene: ...

        def add_layer(self, layer: Layer) -> MarketFigure: ...

        def add_layers(self, layers: Iterable[Layer]) -> MarketFigure: ...
