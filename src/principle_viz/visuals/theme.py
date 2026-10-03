"""PrincipleViz semantic themes backed by MosaicKit styles."""

from __future__ import annotations

from dataclasses import dataclass, field

from mosaickit import (
    DashStyle,
    Fill,
    LegendStyle,
    Marker,
    Stroke,
    StyleBundle,
    TextStyle,
    Theme,
)

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


_COLORBLIND = {
    "axis_color": "#222222",
    "label_color": "#222222",
    "demand_color": _BLUE,
    "supply_color": _RED,
    "baseline_color": "#111111",
    "shifted_color": _GREEN,
    "tax_color": _ORANGE,
    "control_color": _PURPLE,
    "cs_color": _GREEN,
    "ps_color": _BLUE,
    "tax_revenue_color": _ORANGE,
    "dwl_color": _RED,
    "arrow_color": "#111111",
}

# Default: colours named from the active MosaicKit palette (``DEFAULT_PALETTE``
# unless ``Config(palette=...)`` or a TOML ``[palette]`` table overrides it), so
# redefining "blue" there recolours demand, consumer surplus, and everything else
# that names it. Demand is blue and supply red; consumer and producer surplus
# reuse those hues, and deadweight loss gets its own (teal).
_DEFAULT = {
    "axis_color": "grey-800",
    "label_color": "grey-900",
    "demand_color": "blue",
    "supply_color": "red",
    "baseline_color": "grey-900",
    "shifted_color": "grey-600",
    "tax_color": "red",
    "control_color": "teal",
    "cs_color": "blue",
    "ps_color": "red",
    "tax_revenue_color": "grey-400",
    "dwl_color": "teal",
    "arrow_color": "grey-900",
}

DEFAULT_COLOR_MODEL = ColorModel(name="default", **_DEFAULT)
COLORBLIND_COLOR_MODEL = ColorModel(name="colorblind", **_COLORBLIND)
NORD_COLOR_MODEL = ColorModel(
    name="nord",
    axis_color="#2E3440",
    label_color="#2E3440",
    demand_color="#88C0D0",
    supply_color="#BF616A",
    shifted_color="#A3BE8C",
    tax_color="#EBCB8B",
    control_color="#B48EAD",
    cs_color="#A3BE8C",
    ps_color="#5E81AC",
    tax_revenue_color="#EBCB8B",
    dwl_color="#BF616A",
    arrow_color="#4C566A",
)
MONOCHROME_COLOR_MODEL = ColorModel(
    name="monochrome",
    axis_color="#111111",
    label_color="#111111",
    demand_color="#111111",
    supply_color="#4A4A4A",
    baseline_color="#000000",
    shifted_color="#6E6E6E",
    tax_color="#2E2E2E",
    control_color="#595959",
    cs_color="#E0E0E0",
    ps_color="#BDBDBD",
    tax_revenue_color="#969696",
    dwl_color="#636363",
    arrow_color="#111111",
)

BUILTIN_COLOR_MODELS = {
    model.name: model
    for model in (
        DEFAULT_COLOR_MODEL,
        COLORBLIND_COLOR_MODEL,
        NORD_COLOR_MODEL,
        MONOCHROME_COLOR_MODEL,
    )
}


def list_color_models() -> tuple[str, ...]:
    return tuple(BUILTIN_COLOR_MODELS)


def get_color_model(name: str) -> ColorModel:
    key = name.strip().lower()
    try:
        return BUILTIN_COLOR_MODELS[key]
    except KeyError as exc:
        available = ", ".join(list_color_models())
        raise ValueError(
            f"Unknown color model: {name}. Available: {available}"
        ) from exc


@dataclass(frozen=True)
class PlotTheme:
    """Compatibility settings compiled into a MosaicKit theme."""

    color_model: ColorModel = field(default_factory=lambda: DEFAULT_COLOR_MODEL)
    demand_linewidth: float = 3.5
    supply_linewidth: float = 3.5
    shifted_linewidth: float = 3.5
    tax_linewidth: float = 3.5
    arrow_linewidth: float = 1.2
    equilibrium_marker_size: float = 42.25  # 6.5 pt across
    show_grid: bool = False
    show_ticks: bool = False
    show_axis_arrows: bool = True
    show_origin_label: bool = True

    @classmethod
    def from_palette(cls, palette: str, **kwargs: object) -> PlotTheme:
        return cls(color_model=get_color_model(palette), **kwargs)

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
                stroke=Stroke(color=c.control_color, width=1.8, dash=dashed),
                text=TextStyle(color=c.control_color, size=10),
            ),
            "principle.policy.tax": StyleBundle(
                stroke=Stroke(color=c.tax_color, width=self.tax_linewidth, dash=dashed),
                text=TextStyle(color=c.tax_color, size=10),
            ),
            "principle.policy.subsidy": StyleBundle(
                stroke=Stroke(
                    color=c.shifted_color, width=self.tax_linewidth, dash=dashed
                ),
                text=TextStyle(color=c.shifted_color, size=10),
            ),
            "principle.trade.world": StyleBundle(
                stroke=Stroke(color=c.axis_color, width=1.5, dash=dashed),
                text=TextStyle(color=c.label_color, size=10),
            ),
            "principle.trade.policy": StyleBundle(
                stroke=Stroke(color=c.tax_color, width=1.8, dash=dashed),
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
                stroke=Stroke(color=c.shifted_color, width=2.0, dash=dashed),
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
        return Theme(f"principle-{c.name}", roles)

    def __getattr__(self, name: str) -> str:
        if name.endswith("_color"):
            return getattr(self.color_model, name)
        raise AttributeError(name)


__all__ = [
    "BUILTIN_COLOR_MODELS",
    "COLORBLIND_COLOR_MODEL",
    "COLORBLIND_CYCLE_HEX",
    "COLORBLIND_CYCLE_RGB",
    "DEFAULT_COLOR_MODEL",
    "MONOCHROME_COLOR_MODEL",
    "NORD_COLOR_MODEL",
    "ColorModel",
    "PlotTheme",
    "get_color_model",
    "list_color_models",
]
