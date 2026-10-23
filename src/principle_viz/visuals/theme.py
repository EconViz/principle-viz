"""PrincipleViz semantic themes backed by MosaicKit styles."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from pathlib import Path
from types import ModuleType

from mosaickit import (
    Config,
    ConfigurationError,
    DashStyle,
    Fill,
    LegendStyle,
    Marker,
    MathFont,
    Stroke,
    StyleBundle,
    TextFonts,
    TextStyle,
    Theme,
)
from mosaickit.config import current_config

from principle_viz.i18n import validate_language

GENERIC_FONTS = ("sans", "serif", "mono")

COLORBLIND_CYCLE_RGB: tuple[tuple[int, int, int], ...] = (
    (55, 126, 184),
    (255, 127, 0),
    (77, 175, 74),
    (247, 129, 191),
    (166, 86, 40),
    (152, 78, 163),
    (153, 153, 153),
    (228, 26, 28),
    (222, 222, 0),
)


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb)


COLORBLIND_CYCLE_HEX = tuple(_rgb_to_hex(rgb) for rgb in COLORBLIND_CYCLE_RGB)
_BLUE, _ORANGE, _GREEN, _, _, _PURPLE, _, _RED, _ = COLORBLIND_CYCLE_HEX


@dataclass(frozen=True)
class ColorModel:
    """Named economics color roles retained for API compatibility.

    Each field is a ``"#hex"`` value or a MosaicKit palette name such as ``"blue"``,
    resolved against the active palette when a canvas renders.
    """

    name: str
    axis_color: str = "#222222"
    label_color: str = "#222222"
    demand_color: str = _BLUE
    supply_color: str = _RED
    baseline_color: str = "#111111"
    shifted_color: str = _GREEN
    tax_color: str = _ORANGE
    control_color: str = _PURPLE
    cs_color: str = _GREEN
    ps_color: str = _BLUE
    tax_revenue_color: str = _ORANGE
    dwl_color: str = _RED
    arrow_color: str = "#111111"


# The built-in colour models, one per mosaickit shared theme, are built from the theme
# tokens in principle_viz.visuals.roles, which imports this module; the names below are
# looked up there on first use.
_ROLES_EXPORTS = frozenset(
    {
        "BUILTIN_COLOR_MODELS",
        "COLORBLIND_COLOR_MODEL",
        "DEFAULT_COLOR_MODEL",
        "MANUAL_COLOR_MODEL",
        "MONOCHROME_COLOR_MODEL",
        "NORD_COLOR_MODEL",
    }
)


def _roles() -> ModuleType:
    from principle_viz.visuals import roles

    return roles


def __getattr__(name: str) -> object:
    if name in _ROLES_EXPORTS:
        return getattr(_roles(), name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def list_color_models() -> tuple[str, ...]:
    """The built-in colour models: one per mosaickit shared theme."""
    return _roles().list_color_models()


def get_color_model(name: str) -> ColorModel:
    """The built-in colour model called ``name`` (case and spaces ignored)."""
    return _roles().get_color_model(name)


@dataclass(frozen=True)
class PlotTheme:
    """Compatibility settings compiled into a MosaicKit theme."""

    color_model: ColorModel = field(default_factory=lambda: get_color_model("default"))
    demand_linewidth: float = 3.5
    supply_linewidth: float = 3.5
    shifted_linewidth: float = 1.0
    tax_linewidth: float = 1.0
    arrow_linewidth: float = 1.0
    dashed_linewidth: float = 1.0
    equilibrium_marker_size: float = 42.25  # 6.5 pt across
    show_grid: bool = False
    show_ticks: bool = False
    show_axis_arrows: bool = True
    show_origin_label: bool = True
    # Fonts behave as in every diagram package built on MosaicKit: a generic font, files that
    # replace the generic fonts, and a math font.
    font: str = "sans"
    fonts: TextFonts | None = None
    math_font: MathFont | str | os.PathLike[str] | None = None
    font_roles: Mapping[str, str] = field(default_factory=dict, hash=False)
    # The language of principle-viz's built-in figure text: "en", "zh-TW" or "zh-CN".
    # Chinese text needs a font that has the characters, e.g. fonts=TextFonts(serif=...).
    language: str = "en"

    def __post_init__(self) -> None:
        validate_language(self.language)
        for name in (self.font, *self.font_roles.values()):
            if name not in GENERIC_FONTS:
                raise ValueError(
                    f"font must be one of {', '.join(GENERIC_FONTS)}, got {name!r}; "
                    "to use your own font files pass fonts=TextFonts(...)"
                )
        if self.fonts is not None and not isinstance(self.fonts, TextFonts):
            raise ValueError("fonts must be a mosaickit.TextFonts or None")
        math_font = self.math_font
        if isinstance(math_font, (str, os.PathLike)):
            try:
                math_font = MathFont(Path(math_font))
            except ConfigurationError as error:
                raise ValueError(f"math_font: {error}") from None
        elif math_font is not None and not isinstance(math_font, MathFont):
            raise ValueError(
                "math_font must be a mosaickit.MathFont or the path of a math font file"
            )
        object.__setattr__(self, "math_font", math_font)

    def mosaickit_config(self) -> Config:
        """MosaicKit's current settings with this theme's font files and math font."""
        base = current_config()
        if self.fonts is None and self.math_font is None:
            return base
        return replace(
            base,
            fonts=self.fonts if self.fonts is not None else base.fonts,
            math_font=self.math_font if self.math_font is not None else base.math_font,  # type: ignore[arg-type]
        )

    @classmethod
    def from_palette(cls, palette: str, **kwargs: object) -> PlotTheme:
        """The theme of a built-in colour model, with its sizes scaled by the theme.

        ``palette`` names a mosaickit shared theme; keyword arguments override fields.
        """
        return _roles().plot_theme(palette, cls=cls, **kwargs)

    def to_mosaickit(self) -> Theme:
        c = self.color_model
        solid = DashStyle.SOLID
        dashed = DashStyle.DASHED
        dotted = DashStyle.DOTTED
        roles = {
            "axes": StyleBundle(
                stroke=Stroke(color=c.axis_color, width=1.0),
                text=TextStyle(color=c.label_color, size=11),
            ),
            # Text styles here colour the direct curve labels (shifted roles inherit).
            "principle.market.demand": StyleBundle(
                stroke=Stroke(
                    color=c.demand_color, width=self.demand_linewidth, dash=solid
                ),
                text=TextStyle(color=c.demand_color, size=11),
            ),
            "principle.market.supply": StyleBundle(
                stroke=Stroke(
                    color=c.supply_color, width=self.supply_linewidth, dash=solid
                ),
                text=TextStyle(color=c.supply_color, size=11),
            ),
            "principle.market.demand.shifted": StyleBundle(
                stroke=Stroke(
                    color=c.demand_color, width=self.shifted_linewidth, dash=dashed
                )
            ),
            "principle.market.supply.shifted": StyleBundle(
                stroke=Stroke(
                    color=c.supply_color, width=self.shifted_linewidth, dash=dashed
                )
            ),
            "principle.market.equilibrium": StyleBundle(
                marker=Marker(
                    color=c.baseline_color,
                    size=self.equilibrium_marker_size,
                    edge_color=c.baseline_color,
                    edge_width=0,
                ),
                text=TextStyle(color=c.baseline_color, size=11),
            ),
            "principle.market.equilibrium.shifted": StyleBundle(
                marker=Marker(
                    color=c.shifted_color,
                    size=self.equilibrium_marker_size,
                    edge_color=c.shifted_color,
                    edge_width=0,
                ),
                text=TextStyle(color=c.shifted_color, size=11),
            ),
            "principle.market.guide": StyleBundle(
                stroke=Stroke(color=c.axis_color, width=1.0, dash=dotted)
            ),
            # Arrows showing how something moves: thin, black, dashed.
            "principle.market.movement": StyleBundle(
                stroke=Stroke(
                    color=c.arrow_color, width=self.arrow_linewidth, dash=dashed
                ),
                text=TextStyle(color=c.label_color, size=10),
            ),
            "principle.policy.control": StyleBundle(
                stroke=Stroke(
                    color=c.control_color,
                    width=self.dashed_linewidth,
                    dash=dashed,
                ),
                text=TextStyle(color=c.control_color, size=10),
            ),
            "principle.policy.tax": StyleBundle(
                stroke=Stroke(
                    color=c.tax_color,
                    width=self.tax_linewidth,
                    dash=dashed,
                ),
                text=TextStyle(color=c.tax_color, size=10),
            ),
            "principle.policy.subsidy": StyleBundle(
                stroke=Stroke(
                    color=c.shifted_color,
                    width=self.tax_linewidth,
                    dash=dashed,
                ),
                text=TextStyle(color=c.shifted_color, size=10),
            ),
            "principle.trade.world": StyleBundle(
                stroke=Stroke(
                    color=c.axis_color,
                    width=self.dashed_linewidth,
                    dash=dashed,
                ),
                text=TextStyle(color=c.label_color, size=10),
            ),
            "principle.trade.policy": StyleBundle(
                stroke=Stroke(
                    color=c.tax_color,
                    width=self.dashed_linewidth,
                    dash=dashed,
                ),
                text=TextStyle(color=c.tax_color, size=10),
            ),
            "principle.trade.flow": StyleBundle(
                stroke=Stroke(color=c.arrow_color, width=self.arrow_linewidth),
                text=TextStyle(color=c.label_color, size=10),
            ),
            "principle.trade.rent": StyleBundle(
                fill=Fill(color=c.tax_revenue_color, opacity=0.22),
                stroke=Stroke(width=0),
            ),
            "principle.ppf.frontier": StyleBundle(
                stroke=Stroke(color=c.baseline_color, width=2.2),
                text=TextStyle(color=c.baseline_color, size=11),
            ),
            "principle.ppf.shifted": StyleBundle(
                stroke=Stroke(
                    color=c.shifted_color,
                    width=self.dashed_linewidth,
                    dash=dashed,
                ),
                text=TextStyle(color=c.shifted_color, size=11),
            ),
            "principle.ppf.feasible": StyleBundle(
                fill=Fill(color=c.cs_color, opacity=0.12),
                stroke=Stroke(width=0),
            ),
            "principle.ppf.efficient": StyleBundle(
                marker=Marker(color=c.baseline_color, size=self.equilibrium_marker_size)
            ),
            "principle.ppf.inefficient": StyleBundle(
                marker=Marker(color=c.shifted_color, size=self.equilibrium_marker_size)
            ),
            "principle.ppf.unattainable": StyleBundle(
                marker=Marker(color=c.dwl_color, size=self.equilibrium_marker_size)
            ),
            "principle.welfare.consumer": StyleBundle(
                fill=Fill(color=c.cs_color, opacity=0.15), stroke=Stroke(width=0)
            ),
            "principle.welfare.producer": StyleBundle(
                fill=Fill(color=c.ps_color, opacity=0.15), stroke=Stroke(width=0)
            ),
            # Tax revenue is named by its label, not shaded.
            "principle.welfare.revenue": StyleBundle(
                fill=Fill(color=c.tax_revenue_color, opacity=0),
                stroke=Stroke(width=0),
            ),
            # Like tax revenue, the subsidy's cost is named, not shaded.
            "principle.welfare.subsidy": StyleBundle(
                fill=Fill(color=c.shifted_color, opacity=0),
                stroke=Stroke(width=0),
            ),
            "principle.welfare.loss": StyleBundle(
                fill=Fill(color=c.dwl_color, opacity=0.45), stroke=Stroke(width=0)
            ),
            "principle.annotation": StyleBundle(
                text=TextStyle(color=c.label_color, size=10)
            ),
            "principle.annotation.strong": StyleBundle(
                text=TextStyle(color=c.label_color, size=12, weight="bold")
            ),
            "legend": StyleBundle(
                legend=LegendStyle(visible=True, frame=False, size=10)
            ),
            "canvas": StyleBundle(fill=Fill(color="#FFFFFF", opacity=1)),
            "title": StyleBundle(
                text=TextStyle(color=c.label_color, size=12, weight="normal")
            ),
        }
        for role, font in self.font_roles.items():
            roles[role] = StyleBundle(text=TextStyle(font=font)).merged_over(
                roles.get(role, StyleBundle())
            )
        return Theme(
            f"principle-{c.name}",
            roles,
            defaults=StyleBundle(text=TextStyle(font=self.font)),
        )

    def __getattr__(self, name: str) -> str:
        if name.endswith("_color"):
            return getattr(self.color_model, name)
        raise AttributeError(name)


__all__ = [
    "COLORBLIND_CYCLE_HEX",
    "COLORBLIND_CYCLE_RGB",
    "ColorModel",
    "PlotTheme",
    "get_color_model",
    "list_color_models",
]
