"""Plotting facade and render helpers."""

from principle_viz.plot.aggregation import (
    AggregationFigure,
    demand_aggregation_figure,
    discrete_demand_aggregation_figure,
    discrete_supply_aggregation_figure,
    supply_aggregation_figure,
)
from principle_viz.plot.canvas import Canvas
from principle_viz.plot.colors import (
    BUILTIN_COLOR_MODELS,
    COLORBLIND_COLOR_MODEL,
    DEFAULT_COLOR_MODEL,
    MONOCHROME_COLOR_MODEL,
    NORD_COLOR_MODEL,
    ColorModel,
    get_color_model,
    list_color_models,
)
from principle_viz.plot.figure import MarketFigure
from principle_viz.plot.theme import PlotTheme

__all__ = [
    "BUILTIN_COLOR_MODELS",
    "COLORBLIND_COLOR_MODEL",
    "DEFAULT_COLOR_MODEL",
    "MONOCHROME_COLOR_MODEL",
    "NORD_COLOR_MODEL",
    "AggregationFigure",
    "Canvas",
    "ColorModel",
    "MarketFigure",
    "PlotTheme",
    "demand_aggregation_figure",
    "discrete_demand_aggregation_figure",
    "discrete_supply_aggregation_figure",
    "get_color_model",
    "list_color_models",
    "supply_aggregation_figure",
]
