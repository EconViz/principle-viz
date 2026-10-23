"""principle-viz settings from ``econ-viz.toml``, the file every EconViz package reads.

mosaickit reads and checks the file (see ``mosaickit.econ_toml``); this module only
declares what principle-viz takes from it. The shared top level sets the starting colour
model (``base``), the fonts and the axis and label colours; principle-viz's own settings
live in the ``[principle]`` table::

    base = "manual"           # shared theme to start from (mosaickit.themes)

    [font]
    text = "serif"
    math = "fonts/texgyrepagella-math.otf"

    [fonts]
    serif = ["fonts/NotoSerifTC-Regular.otf", "fonts/NotoSerifTC-Bold.otf"]

    [color]
    axis = "#1a1a1a"
    label = "#1a1a1a"

    [principle]
    palette = "manual"        # colour model for principle-viz only; wins over base
    language = "zh-TW"        # language of built-in figure text

    [principle.color]         # any colour-model role, without "_color"
    demand = "#8c8c8c"
    supply = "#1a1a1a"

    [principle.stroke]        # line widths in points
    demand = 3.5
    supply = 3.5

    [principle.marker]
    equilibrium = 6.5         # equilibrium dot diameter in points

Load it once and every figure made without an explicit ``theme`` uses it::

    from principle_viz import Config
    Config.load("econ-viz.toml").use()

Relative paths are resolved against the file's directory. Anything left out keeps
the built-in default.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields, make_dataclass, replace
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING, Any

from mosaickit import MathFont, econ_toml
from mosaickit.themes import list_shared_themes

from principle_viz.i18n import LANGUAGES

if TYPE_CHECKING:
    from principle_viz.visuals.theme import ColorModel, PlotTheme

# The built-in colour models are mosaickit's shared themes; principle_viz.visuals.roles
# builds one per theme. The ColorModel colour roles are listed here because this module
# cannot import principle_viz.visuals at load time (tests check that they match).
COLOR_MODELS = list_shared_themes()
COLOR_ROLES = (
    "axis",
    "label",
    "demand",
    "supply",
    "baseline",
    "shifted",
    "tax",
    "control",
    "cs",
    "ps",
    "tax_revenue",
    "dwl",
    "arrow",
)
STROKES = ("demand", "supply", "shifted", "tax", "arrow", "dashed")

# The colour roles the file sets; None keeps the colour model's own colour.
_Colors = make_dataclass(
    "_Colors",
    [(f"{role}_color", "str | None", field(default=None)) for role in COLOR_ROLES],
    frozen=True,
)


@dataclass(frozen=True)
class _Draft:
    """What the file sets, turned into a PlotTheme by ``_finish``.

    The colours are kept apart from the theme so that ``[principle] palette``, which
    replaces the whole colour model, still keeps the colours the file names.
    """

    theme: PlotTheme
    color_model: Any = field(default_factory=_Colors)
    palette: ColorModel | None = None
    equilibrium_diameter: float | None = None


def _theme_module() -> ModuleType:
    # Imported on use: the plotting modules import this one, so a module-level
    # import of principle_viz.visuals would be circular.
    from principle_viz.visuals import theme

    return theme


def _roles_module() -> ModuleType:
    # The only place where the settings file meets the shared themes (imported on
    # use, like _theme_module).
    from principle_viz.visuals import roles

    return roles


def _base(name: str) -> Any:
    return lambda: _Draft(theme=_roles_module().plot_theme(name))


_PALETTE = econ_toml.choice("palette", COLOR_MODELS)
_POSITIVE = econ_toml.positive("")


def _palette(value: Any, ctx: econ_toml.Context) -> ColorModel:
    if isinstance(value, str):
        value = value.strip().lower()
    _PALETTE.convert(value, ctx, "palette")
    return _roles_module().get_color_model(value)


def _width(key: str) -> econ_toml.Field:
    def convert(value: Any, ctx: econ_toml.Context) -> float:
        return float(_POSITIVE.convert(value, ctx, key))

    return econ_toml.transform(f"theme.{key}_linewidth", convert)


def _diameter(value: Any, ctx: econ_toml.Context) -> float:
    return float(_POSITIVE.convert(value, ctx, "equilibrium"))


def _math_font(value: Any, ctx: econ_toml.Context) -> MathFont:
    return MathFont(Path(value))


def _finish(draft: _Draft, ctx: econ_toml.Context) -> PlotTheme:
    model = draft.palette if draft.palette is not None else draft.theme.color_model
    colors = {
        f.name: getattr(draft.color_model, f.name)
        for f in fields(draft.color_model)
        if getattr(draft.color_model, f.name) is not None
    }
    if colors:
        model = replace(model, **colors)
    changes: dict[str, Any] = {}
    if model is not draft.theme.color_model:
        changes["color_model"] = model
    if draft.equilibrium_diameter is not None:
        # PlotTheme keeps the marker's area, the square of its diameter.
        changes["equilibrium_marker_size"] = draft.equilibrium_diameter**2
    return replace(draft.theme, **changes) if changes else draft.theme


SCHEMA = econ_toml.register(
    econ_toml.Schema(
        package="principle",
        base={name: _base(name) for name in COLOR_MODELS},
        fields={
            "palette": econ_toml.transform("palette", _palette),
            "language": econ_toml.choice("theme.language", LANGUAGES),
            **{
                f"color.{role}": econ_toml.color(f"color_model.{role}_color")
                for role in COLOR_ROLES
            },
            **{f"stroke.{name}": _width(name) for name in STROKES},
            "marker.equilibrium": econ_toml.transform(
                "equilibrium_diameter", _diameter
            ),
        },
        shared={
            "font": "theme.font",
            "fonts": "theme.fonts",
            "math_font": econ_toml.transform("theme.math_font", _math_font),
            "axis": "color_model.axis_color",
            "label": "color_model.label_color",
        },
        finalize=_finish,
        docs={
            "palette": "colour model for principle-viz only; wins over base",
            "language": "language of built-in figure text",
            "marker.equilibrium": "equilibrium dot diameter in points (default 6.5)",
            **{
                f"color.{role}": "unset keeps the colour model's"
                for role in COLOR_ROLES
            },
            **{f"stroke.{name}": "line width in points" for name in STROKES},
        },
    )
)


class Config(SCHEMA.config_class()):  # type: ignore[misc]
    """A theme read from ``econ-viz.toml``; :meth:`use` makes it the default."""

    __slots__ = ()

    @property
    def theme(self) -> PlotTheme:
        """The PlotTheme the file describes."""
        return self.value


def default_theme(palette: str | None = None) -> PlotTheme:
    """The theme a figure uses without an explicit one.

    A ``palette`` named in the call wins; otherwise the config set by :meth:`Config.use`,
    otherwise the built-in default.
    """
    plot_theme = _theme_module().PlotTheme
    if palette is not None:
        return plot_theme.from_palette(palette)
    active = Config.active()
    if active is not None:
        return active.theme
    return plot_theme.from_palette("default")


__all__ = [
    "COLOR_MODELS",
    "COLOR_ROLES",
    "SCHEMA",
    "STROKES",
    "Config",
    "default_theme",
]
