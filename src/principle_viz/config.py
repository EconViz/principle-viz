"""Read principle-viz settings from ``econ-viz.toml``, the file every EconViz package reads.

The shared sections (see ``mosaickit.econ_toml``) set the fonts and the axis and label
colours; principle-viz's own settings live in the ``[principle]`` table::

    [font]
    text = "serif"
    math = "fonts/texgyrepagella-math.otf"

    [fonts]
    serif = ["fonts/NotoSerifTC-Regular.otf", "fonts/NotoSerifTC-Bold.otf"]

    [color]
    axis = "#1a1a1a"
    label = "#1a1a1a"

    [principle]
    palette = "manual"        # built-in colour model to start from
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

import dataclasses
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING, Any

from mosaickit import ConfigurationError, econ_toml

if TYPE_CHECKING:
    from principle_viz.visuals.theme import PlotTheme

_TABLE_KEYS = {"palette", "language", "color", "stroke", "marker"}
_STROKES = {
    "demand": "demand_linewidth",
    "supply": "supply_linewidth",
    "shifted": "shifted_linewidth",
    "tax": "tax_linewidth",
    "arrow": "arrow_linewidth",
    "dashed": "dashed_linewidth",
}
_MARKERS = {"equilibrium": "equilibrium_marker_size"}


@dataclass(frozen=True)
class Config:
    """A theme read from ``econ-viz.toml``; :meth:`use` makes it the default."""

    theme: PlotTheme = field(default_factory=lambda: _theme_module().PlotTheme())

    @classmethod
    def load(cls, path: str | Path | None = None) -> Config:
        """Read ``path``, or ``econ-viz.toml`` in the working directory."""
        if path is None:
            found = econ_toml.find()
            if found is None:
                raise ConfigurationError(
                    f"config file not found: {econ_toml.FILE_NAME}"
                )
            path = found
        source = Path(path)
        return cls.from_dict(
            econ_toml.read(source), source=str(source), base_dir=source.resolve().parent
        )

    @classmethod
    def discover(cls, directory: str | Path | None = None) -> Config:
        """``econ-viz.toml`` in ``directory`` if there is one, else the defaults."""
        found = econ_toml.find(directory)
        return cls() if found is None else cls.load(found)

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
        *,
        source: str = "config",
        base_dir: str | Path | None = None,
    ) -> Config:
        """Build the theme from parsed TOML data."""
        shared = econ_toml.shared_settings(data, base_dir=base_dir, source=source)
        table = econ_toml.package_table(data, "principle", source=source)
        unknown = set(table) - _TABLE_KEYS
        if unknown:
            raise ConfigurationError(
                f"{source}: unknown [principle] key(s) {', '.join(sorted(unknown))}; "
                f"choose from {', '.join(sorted(_TABLE_KEYS))}"
            )
        theme_module = _theme_module()
        color_roles = tuple(
            f.name.removesuffix("_color")
            for f in dataclasses.fields(theme_module.ColorModel)
            if f.name.endswith("_color")
        )
        palette = table.get("palette", "default")
        try:
            model = theme_module.get_color_model(palette)
        except (ValueError, AttributeError) as error:
            raise ConfigurationError(
                f"{source}: [principle] palette: {error}"
            ) from None
        colors = {"axis_color": shared.axis, "label_color": shared.label}
        for role, value in _subtable(table, "color", source).items():
            if role not in color_roles:
                raise ConfigurationError(
                    f"{source}: unknown [principle.color] role {role!r}; choose from {', '.join(color_roles)}"
                )
            if not isinstance(value, str):
                raise ConfigurationError(
                    f"{source}: [principle.color] {role} must be a colour string"
                )
            colors[f"{role}_color"] = value
        model = dataclasses.replace(
            model, **{k: v for k, v in colors.items() if v is not None}
        )
        sizes: dict[str, float] = {}
        sizes.update(_numbers(table, "stroke", _STROKES, source))
        sizes.update(
            {
                name: value**2
                for name, value in _numbers(table, "marker", _MARKERS, source).items()
            }
        )
        options: dict[str, Any] = {"color_model": model, **sizes}
        if "language" in table:
            options["language"] = table["language"]
        if shared.font is not None:
            options["font"] = shared.font
        if shared.fonts is not None:
            options["fonts"] = shared.fonts
        if shared.math_font is not None:
            options["math_font"] = shared.math_font
        try:
            return cls(theme=theme_module.PlotTheme(**options))
        except ValueError as error:
            raise ConfigurationError(f"{source}: {error}") from None

    def use(self) -> Config:
        """Make this the theme of every figure made without an explicit ``theme``."""
        global _active
        _active = self
        return self

    @staticmethod
    def reset() -> None:
        """Go back to the built-in default theme."""
        global _active
        _active = None

    @staticmethod
    def active() -> Config | None:
        """The config set by :meth:`use`, if any."""
        return _active


_active: Config | None = None


def default_theme(palette: str | None = None) -> PlotTheme:
    """The theme a figure uses without an explicit one.

    A ``palette`` named in the call wins; otherwise the config set by :meth:`Config.use`,
    otherwise the built-in default.
    """
    plot_theme = _theme_module().PlotTheme
    if palette is not None:
        return plot_theme.from_palette(palette)
    if _active is not None:
        return _active.theme
    return plot_theme.from_palette("default")


def _theme_module() -> ModuleType:
    # Imported on use: the plotting modules import this one, so a module-level
    # import of principle_viz.visuals would be circular.
    from principle_viz.visuals import theme

    return theme


def _subtable(table: Mapping[str, Any], key: str, source: str) -> Mapping[str, Any]:
    value = table.get(key, {})
    if not isinstance(value, Mapping):
        raise ConfigurationError(f"{source}: [principle.{key}] must be a table")
    return value


def _numbers(
    table: Mapping[str, Any], key: str, names: Mapping[str, str], source: str
) -> dict[str, float]:
    out = {}
    for name, value in _subtable(table, key, source).items():
        if name not in names:
            raise ConfigurationError(
                f"{source}: unknown [principle.{key}] key {name!r}; choose from {', '.join(names)}"
            )
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise ConfigurationError(
                f"{source}: [principle.{key}] {name} must be a positive number"
            )
        out[names[name]] = float(value)
    return out


__all__ = ["Config", "default_theme"]
