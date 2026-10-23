"""Backward-compatible color exports."""

from principle_viz.visuals.roles import (
    BUILTIN_COLOR_MODELS,
    COLORBLIND_COLOR_MODEL,
    DEFAULT_COLOR_MODEL,
    MONOCHROME_COLOR_MODEL,
    NORD_COLOR_MODEL,
    get_color_model,
    list_color_models,
)
from principle_viz.visuals.theme import (
    COLORBLIND_CYCLE_HEX,
    COLORBLIND_CYCLE_RGB,
    ColorModel,
)

__all__ = [
    "BUILTIN_COLOR_MODELS",
    "COLORBLIND_COLOR_MODEL",
    "COLORBLIND_CYCLE_HEX",
    "COLORBLIND_CYCLE_RGB",
    "DEFAULT_COLOR_MODEL",
    "MONOCHROME_COLOR_MODEL",
    "NORD_COLOR_MODEL",
    "ColorModel",
    "get_color_model",
    "list_color_models",
]
