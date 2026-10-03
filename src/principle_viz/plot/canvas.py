"""A MosaicKit canvas with stable, user-configurable PrincipleViz layers."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import replace
from typing import Any

from mosaickit import Canvas as MosaicCanvas
from mosaickit import FillLayer, Layer

from principle_viz.plot.label import Label, apply_label, is_label_layer


class Canvas(MosaicCanvas):
    """MosaicKit canvas whose supplied layers can be configured by stable id."""

    def __init__(
        self,
        *args: Any,
        labels: Mapping[str, Label] | None = None,
        visibility: Mapping[str, bool] | None = None,
        **kwargs: Any,
    ) -> None:
        self._label_overrides = dict(labels or {})
        if not all(
            isinstance(label, Label) for label in self._label_overrides.values()
        ):
            raise TypeError("labels must map layer ids to Label values")
        self._visibility_overrides = dict(visibility or {})
        if not all(
            isinstance(visible, bool)
            for visible in self._visibility_overrides.values()
        ):
            raise TypeError("visibility values must be bools")
        self._label_defaults: dict[str, Layer] = {}
        super().__init__(*args, **kwargs)

    @property
    def layer_ids(self) -> tuple[str, ...]:
        """Stable ids of every layer currently supplied by the diagram."""
        return tuple(layer.id for layer in self.snapshot().layers)

    @property
    def label_ids(self) -> tuple[str, ...]:
        """Stable ids of every configurable text label in the diagram."""
        return tuple(self._label_defaults)

    def _regions(
        self,
        incoming: Iterable[Layer] = (),
    ) -> dict[str, tuple[tuple[float, float], ...]]:
        return {
            layer.id: tuple(layer.boundary)
            for layer in (*self.snapshot().layers, *incoming)
            if isinstance(layer, FillLayer)
        }

    def _label_override(self, layer_id: str) -> Label | None:
        override = self._label_overrides.get(layer_id)
        if override is not None or not layer_id.endswith(".label"):
            return override
        return self._label_overrides.get(layer_id.removesuffix(".label"))

    def _prepare(self, layers: tuple[Layer, ...]) -> tuple[Layer, ...]:
        regions = self._regions(layers)
        prepared: list[Layer] = []
        for layer in layers:
            if layer.id in self._visibility_overrides:
                layer = replace(
                    layer,
                    visible=self._visibility_overrides[layer.id],
                )
            if is_label_layer(layer):
                self._label_defaults[layer.id] = layer
                override = self._label_override(layer.id)
                if override is not None:
                    layer = apply_label(layer, override, regions=regions)
            prepared.append(layer)
        return tuple(prepared)

    def add(self, layer: Layer) -> Canvas:
        super().add(self._prepare((layer,))[0])
        return self

    def extend(self, layers: Iterable[Layer]) -> Canvas:
        super().extend(self._prepare(tuple(layers)))
        return self

    def configure_layer(self, layer_id: str, *, visible: bool) -> Canvas:
        """Show or hide a supplied line, point, region, or annotation."""
        if not isinstance(visible, bool):
            raise TypeError("visible must be a bool")
        layer = next(
            (
                candidate
                for candidate in self.snapshot().layers
                if candidate.id == layer_id
            ),
            None,
        )
        if layer is None:
            available = ", ".join(self.layer_ids) or "none"
            raise KeyError(f"Unknown layer {layer_id!r}; available layers: {available}")
        self._visibility_overrides[layer_id] = visible
        super().remove(layer_id)
        super().add(replace(layer, visible=visible))
        return self

    def hide(self, *layer_ids: str) -> Canvas:
        """Hide supplied layers by stable id."""
        for layer_id in layer_ids:
            self.configure_layer(layer_id, visible=False)
        return self

    def show(self, *layer_ids: str) -> Canvas:
        """Show supplied layers by stable id."""
        for layer_id in layer_ids:
            self.configure_layer(layer_id, visible=True)
        return self

    def configure_label(
        self,
        layer_id: str,
        label: Label | None = None,
        *,
        text: str | None = None,
        visible: bool | None = None,
        offset: tuple[float, float] | None = None,
    ) -> Canvas:
        """Show, hide, rename, or move one supplied text label."""
        if label is not None and any(
            value is not None for value in (text, visible, offset)
        ):
            raise ValueError("Pass either a Label or individual label options")
        selected = label or Label(text=text, visible=visible, offset=offset)
        candidates = (layer_id, f"{layer_id}.label")
        resolved_id = next(
            (candidate for candidate in candidates if candidate in self._label_defaults),
            "",
        )
        if not resolved_id:
            available = ", ".join(self.label_ids) or "none"
            raise KeyError(f"Unknown label {layer_id!r}; available labels: {available}")
        self._label_overrides[resolved_id] = selected
        default = self._label_defaults[resolved_id]
        if resolved_id in self._visibility_overrides:
            default = replace(
                default,
                visible=self._visibility_overrides[resolved_id],
            )
        replacement = apply_label(default, selected, regions=self._regions())
        super().remove(resolved_id)
        super().add(replacement)
        return self

    def copy(self) -> Canvas:
        canvas = Canvas(
            self.spec,
            self.theme,
            self.config,
            self.renderer,
            role_overrides=self.role_overrides,
            labels=self._label_overrides,
            visibility=self._visibility_overrides,
        )
        canvas._scene = self._scene
        canvas._bindings = self._bindings
        canvas._label_defaults = dict(self._label_defaults)
        return canvas


__all__ = ["Canvas"]
