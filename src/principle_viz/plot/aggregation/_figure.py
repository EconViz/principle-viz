"""The side-by-side aggregation figure."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from mosaickit import Canvas, CanvasGrid, GridLink

from principle_viz.plot.label import Label, Length


@dataclass(frozen=True)
class AggregationFigure:
    """Side-by-side panels: one per individual, then the market."""

    panels: tuple[Canvas, ...]
    links: tuple[GridLink, ...] = ()

    @property
    def grid(self) -> CanvasGrid:
        return CanvasGrid(self.panels, rows=1, links=self.links)

    def save(self, path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        self.grid.save(target)
        return target

    @property
    def layer_ids(self) -> tuple[str, ...]:
        return tuple(
            dict.fromkeys(id_ for panel in self.panels for id_ in panel.layer_ids)
        )

    @property
    def label_ids(self) -> tuple[str, ...]:
        return tuple(
            dict.fromkeys(id_ for panel in self.panels for id_ in panel.label_ids)
        )

    def hide(self, *layer_ids: str) -> AggregationFigure:
        return self._set_visibility(layer_ids, visible=False)

    def show(self, *layer_ids: str) -> AggregationFigure:
        return self._set_visibility(layer_ids, visible=True)

    def _set_visibility(
        self,
        layer_ids: tuple[str, ...],
        *,
        visible: bool,
    ) -> AggregationFigure:
        for layer_id in layer_ids:
            matched = False
            for panel in self.panels:
                if layer_id in panel.layer_ids:
                    panel.configure_layer(layer_id, visible=visible)
                    matched = True
            if not matched:
                raise KeyError(f"Unknown aggregation layer {layer_id!r}")
        return self

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
    ) -> AggregationFigure:
        matched = False
        for panel in self.panels:
            if layer_id in panel.label_ids or f"{layer_id}.label" in panel.label_ids:
                panel.configure_label(
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
                matched = True
        if not matched:
            raise KeyError(f"Unknown aggregation label {layer_id!r}")
        return self
