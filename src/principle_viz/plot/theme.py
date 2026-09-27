"""Theme settings for diagrams, built on top of a color model."""

from __future__ import annotations

from dataclasses import dataclass, field

from principle_viz.plot.colors import DEFAULT_COLOR_MODEL, ColorModel, get_color_model


@dataclass(frozen=True)
class PlotTheme:
    """Visual theme that references a reusable color model."""

    color_model: ColorModel = field(default_factory=lambda: DEFAULT_COLOR_MODEL)

    demand_linewidth: float = 2.0
    supply_linewidth: float = 2.0
    shifted_linewidth: float = 1.8
    tax_linewidth: float = 2.0
    arrow_linewidth: float = 1.6
    equilibrium_marker_size: float = 6.0

    show_grid: bool = False
    show_ticks: bool = False
    show_axis_arrows: bool = True
    show_origin_label: bool = True

    @classmethod
    def from_palette(cls, palette: str, **kwargs) -> PlotTheme:
        """Build a theme from a named built-in palette."""
        return cls(color_model=get_color_model(palette), **kwargs)

    @property
    def axis_color(self) -> str:
        return self.color_model.axis_color

    @property
    def label_color(self) -> str:
        return self.color_model.label_color

    @property
    def demand_color(self) -> str:
        return self.color_model.demand_color

    @property
    def supply_color(self) -> str:
        return self.color_model.supply_color

    @property
    def baseline_color(self) -> str:
        return self.color_model.baseline_color

    @property
    def shifted_color(self) -> str:
        return self.color_model.shifted_color

    @property
    def tax_color(self) -> str:
        return self.color_model.tax_color

    @property
    def control_color(self) -> str:
        return self.color_model.control_color

    @property
    def cs_color(self) -> str:
        return self.color_model.cs_color

    @property
    def ps_color(self) -> str:
        return self.color_model.ps_color

    @property
    def tax_revenue_color(self) -> str:
        return self.color_model.tax_revenue_color

    @property
    def dwl_color(self) -> str:
        return self.color_model.dwl_color

    @property
    def arrow_color(self) -> str:
        return self.color_model.arrow_color
