"""Compatibility figure facade composed entirely from MosaicKit layers."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from pathlib import Path

from mosaickit import (
    AxisMarkLayer,
    CanvasSpec,
    Layer,
    LegendLayer,
    LegendStyle,
    Scene,
)

from principle_viz.plot.canvas import Canvas
from principle_viz.plot.figure._policy import _PolicyMixin
from principle_viz.plot.label import Label, Length
from principle_viz.plot.theme import PlotTheme
from principle_viz.visuals import (
    market_axes_layers,
)
from principle_viz.visuals.axes import FIGURE_SIZE
from principle_viz.visuals.welfare import guides_through_regions


class MarketFigure(_PolicyMixin):
    """High-level market diagram facade over a MosaicKit canvas."""

    def __init__(
        self,
        x_max: float = 20.0,
        y_max: float = 20.0,
        x_label: str = "Q",
        y_label: str = "p",
        title: str = "Market Diagram",
        theme: PlotTheme | None = None,
        palette: str | None = None,
        labels: Mapping[str, Label] | None = None,
        visibility: Mapping[str, bool] | None = None,
    ) -> None:
        from principle_viz.config import default_theme  # avoids an import cycle

        self.theme = theme or default_theme(palette)
        self.x_max = float(x_max)
        self.y_max = float(y_max)
        self.canvas = Canvas(
            CanvasSpec(
                x_range=(0.0, self.x_max),
                y_range=(0.0, self.y_max),
                **FIGURE_SIZE,
                x_label=x_label,
                y_label=y_label,
                title=title,
            ),
            theme=self.theme.to_mosaickit(),
            config=self.theme.mosaickit_config(),
            language=self.theme.language,
            label_nudges=self.theme.label_nudges,
            labels=labels,
            visibility=visibility,
        )
        self.add_layers(
            market_axes_layers(
                self.x_max,
                self.y_max,
                x_label=x_label,
                y_label=y_label,
                arrows=self.theme.show_axis_arrows,
                origin_label=self.theme.show_origin_label,
            )
        )

    @property
    def scene(self) -> Scene:
        return self.canvas.snapshot()

    def add_layer(self, layer: Layer) -> MarketFigure:
        return self.add_layers((layer,))

    def add_layers(self, layers: Iterable[Layer]) -> MarketFigure:
        """Add layers; an axis mark replaces any earlier mark at the same value."""
        layers = tuple(layers)
        for mark in layers:
            if isinstance(mark, AxisMarkLayer):
                for old in self.scene.layers:
                    if (
                        isinstance(old, AxisMarkLayer)
                        and old.axis == mark.axis
                        and abs(old.value - mark.value) <= 1e-9
                    ):
                        self.canvas.remove(old.id)
        self.canvas.extend(layers)
        return self

    @property
    def layer_ids(self) -> tuple[str, ...]:
        """Stable ids of all layers currently supplied by the figure."""
        return self.canvas.layer_ids

    def configure_layer(self, layer_id: str, *, visible: bool) -> MarketFigure:
        """Show or hide any supplied line, point, region, or annotation."""
        self.canvas.configure_layer(layer_id, visible=visible)
        return self

    def hide(self, *layer_ids: str) -> MarketFigure:
        """Hide supplied layers by stable id."""
        for layer_id in layer_ids:
            self.configure_layer(layer_id, visible=False)
        return self

    def show(self, *layer_ids: str) -> MarketFigure:
        """Show supplied layers by stable id."""
        for layer_id in layer_ids:
            self.configure_layer(layer_id, visible=True)
        return self

    @property
    def label_ids(self) -> tuple[str, ...]:
        """Stable ids of every built-in label currently provided by the figure."""
        return self.canvas.label_ids

    def configure_label(
        self,
        layer_id: str,
        label: Label | None = None,
        *,
        text: str | None = None,
        visible: bool | None = None,
        offset: tuple[float, float] | None = None,
        top: Length | None = None,
        bottom: Length | None = None,
        left: Length | None = None,
        right: Length | None = None,
    ) -> MarketFigure:
        """Show, hide, rename, or move one built-in label.

        ``layer_id`` may be the label id returned by :attr:`label_ids` or the id
        without its final ``".label"``. Offsets are in points; ``top``, ``bottom``,
        ``left`` and ``right`` move the placed label (see :class:`Label`).
        """
        self.canvas.configure_label(
            layer_id,
            label,
            text=text,
            visible=visible,
            offset=offset,
            top=top,
            bottom=bottom,
            left=left,
            right=right,
        )
        return self

    def finalize(self, legend: bool = False) -> MarketFigure:
        """Finish the figure: hide guide lines that would cut a shaded welfare
        region in two (its axis mark still names the value), and add a legend only
        when ``legend`` is on."""
        for guide_id in guides_through_regions(self.scene.layers):
            self.canvas.hide(guide_id)
        if any(layer.id == "market.legend" for layer in self.scene.layers):
            self.canvas.remove("market.legend")
        if legend:
            entries = tuple(layer.id for layer in self.scene.layers if layer.legend)
            if entries:
                self.canvas.add(
                    LegendLayer(
                        entries=entries,
                        id="market.legend",
                        style=LegendStyle(visible=True, location="best", frame=False),
                    )
                )
        return self

    def save(self, path: str | Path, dpi: int = 150) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        if dpi == self.canvas.spec.dpi:
            self.canvas.save(target)
            return
        # No label_nudges: the supplied layers have been nudged already.
        canvas = Canvas(
            self.canvas.spec.replace(dpi=int(dpi)),
            theme=self.canvas.theme,
            config=self.canvas.config,
            renderer=self.canvas.renderer,
            role_overrides=self.canvas.role_overrides,
            language=self.canvas.language,
        ).extend(self.scene.layers)
        canvas.save(target)

    def close(self) -> None:
        """Compatibility no-op; MosaicKit closes temporary render results."""


__all__ = ["MarketFigure"]
