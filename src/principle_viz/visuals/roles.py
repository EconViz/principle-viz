"""principle-viz's elements mapped to the shared theme roles of mosaickit.

mosaickit's shared themes (``mosaickit.themes``) give every EconViz package the same
named looks: each theme assigns a colour to a small set of roles (ink, primary,
secondary, ...) plus line, marker and label scales. This module is the only place that
says which role each principle-viz element takes, and it builds the colour models and
plot themes from those tokens. The settings file reaches the themes only through
:func:`plot_theme`, which the ``econ-viz.toml`` schema's ``base`` names call.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import MISSING, fields
from types import MappingProxyType
from typing import Any

from mosaickit.themes import SHARED_THEMES, ThemeTokens, get_tokens

from principle_viz.visuals.theme import ColorModel, PlotTheme

ELEMENT_ROLES: Mapping[str, str] = MappingProxyType(
    {
        "axis": "ink",
        "label": "ink",
        "baseline": "ink",
        "arrow": "ink",
        "demand": "primary",
        "supply": "secondary",
        "shifted": "tertiary",
        "tax": "intervention",
        "control": "intervention",
        "cs": "fill.light",
        "ps": "fill.mid",
        "dwl": "fill.dark",
        "tax_revenue": "fill.faint",
    }
)
"""The shared theme role of every ColorModel colour (the field name without ``_color``)."""

LINE_WIDTHS = (
    "demand_linewidth",
    "supply_linewidth",
    "shifted_linewidth",
    "tax_linewidth",
    "arrow_linewidth",
    "dashed_linewidth",
)
"""The PlotTheme line widths a theme's ``line_scale`` multiplies."""


def _defaults() -> dict[str, Any]:
    return {f.name: f.default for f in fields(PlotTheme) if f.default is not MISSING}


def _tokens(theme: str | ThemeTokens) -> ThemeTokens:
    if isinstance(theme, ThemeTokens):
        return theme
    key = theme.strip().lower()
    if key not in SHARED_THEMES:
        available = ", ".join(SHARED_THEMES)
        raise ValueError(f"Unknown color model: {theme}. Available: {available}")
    return get_tokens(key)


def build_color_model(tokens: ThemeTokens) -> ColorModel:
    """A ColorModel whose colours are the theme's colours for each element's role."""
    return ColorModel(
        name=tokens.name,
        **{
            f"{element}_color": tokens.colors[role]
            for element, role in ELEMENT_ROLES.items()
        },
    )


BUILTIN_COLOR_MODELS: dict[str, ColorModel] = {
    name: build_color_model(get_tokens(name)) for name in SHARED_THEMES
}
"""One colour model per shared theme, built once."""


def list_color_models() -> tuple[str, ...]:
    """The names of the shared themes, which are also the colour model names."""
    return tuple(BUILTIN_COLOR_MODELS)


def get_color_model(name: str) -> ColorModel:
    """The colour model of a shared theme (``"manual"``, ``"default"``, ``"nord"`` ...)."""
    return BUILTIN_COLOR_MODELS[_tokens(name).name]


def theme_sizes(tokens: ThemeTokens) -> dict[str, float]:
    """principle-viz's base line widths and marker size scaled by the theme.

    ``line_scale`` multiplies the line widths; ``marker_scale`` multiplies the
    equilibrium dot's diameter (PlotTheme keeps its area, so the area scales by
    the square). PlotTheme has no text sizes, so ``label_scale`` is not used.
    """
    base = _defaults()
    sizes = {name: base[name] * tokens.line_scale for name in LINE_WIDTHS}
    sizes["equilibrium_marker_size"] = (
        base["equilibrium_marker_size"] * tokens.marker_scale**2
    )
    return sizes


def plot_theme(
    theme: str | ThemeTokens, *, cls: type[PlotTheme] = PlotTheme, **overrides: Any
) -> PlotTheme:
    """The PlotTheme of a shared theme; keyword arguments override its fields."""
    tokens = _tokens(theme)
    model = (
        get_color_model(tokens.name)
        if isinstance(theme, str)
        else build_color_model(tokens)
    )
    return cls(**{"color_model": model, **theme_sizes(tokens), **overrides})


DEFAULT_COLOR_MODEL = BUILTIN_COLOR_MODELS["default"]
COLORBLIND_COLOR_MODEL = BUILTIN_COLOR_MODELS["colorblind"]
NORD_COLOR_MODEL = BUILTIN_COLOR_MODELS["nord"]
MONOCHROME_COLOR_MODEL = BUILTIN_COLOR_MODELS["monochrome"]
MANUAL_COLOR_MODEL = BUILTIN_COLOR_MODELS["manual"]

__all__ = [
    "BUILTIN_COLOR_MODELS",
    "COLORBLIND_COLOR_MODEL",
    "DEFAULT_COLOR_MODEL",
    "ELEMENT_ROLES",
    "LINE_WIDTHS",
    "MANUAL_COLOR_MODEL",
    "MONOCHROME_COLOR_MODEL",
    "NORD_COLOR_MODEL",
    "build_color_model",
    "get_color_model",
    "list_color_models",
    "plot_theme",
    "theme_sizes",
]
