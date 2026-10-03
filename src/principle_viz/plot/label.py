"""User overrides for labels supplied by PrincipleViz diagrams."""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass, replace

from mosaickit import (
    AxisMarkLayer,
    AxisNoteLayer,
    BraceLayer,
    Layer,
    PointLabelLayer,
    RegionLabelLayer,
    SpanBraceLayer,
    TextLayer,
)

Offset = tuple[float, float]


@dataclass(frozen=True)
class Label:
    """Override one built-in label without discarding its default.

    ``None`` keeps the value supplied by PrincipleViz. An explicit ``offset`` is
    measured in points and opts out of automatic placement, giving the user exact
    control while MosaicKit still performs the drawing.
    """

    text: str | None = None
    visible: bool | None = None
    offset: Offset | None = None

    def __post_init__(self) -> None:
        if self.text is not None and not self.text:
            raise ValueError("Label.text must be a non-empty string")
        if self.visible is not None and not isinstance(self.visible, bool):
            raise TypeError("Label.visible must be a bool")
        if self.offset is None:
            return
        offset = tuple(self.offset)
        if len(offset) != 2 or not all(math.isfinite(value) for value in offset):
            raise ValueError("Label.offset must contain two finite values")
        object.__setattr__(self, "offset", offset)


def _region_position(
    layer: RegionLabelLayer,
    regions: Mapping[str, tuple[tuple[float, float], ...]],
) -> tuple[float, float]:
    polygon = regions[layer.region] if isinstance(layer.region, str) else layer.region
    x_values, y_values = zip(*polygon)
    return (
        0.5 * (min(x_values) + max(x_values)),
        0.5 * (min(y_values) + max(y_values)),
    )


def apply_label(
    layer: Layer,
    label: Label,
    *,
    regions: Mapping[str, tuple[tuple[float, float], ...]] | None = None,
) -> Layer:
    """Apply ``label`` to one MosaicKit label-bearing layer."""
    regions = regions or {}
    visible = layer.visible if label.visible is None else label.visible

    if isinstance(layer, PointLabelLayer):
        text = label.text or layer.text
        if label.offset is None:
            return replace(layer, text=text, visible=visible)
        return TextLayer(
            layer.point,
            text,
            style=layer.style,
            offset=label.offset,
            id=layer.id,
            role=layer.role,
            z_index=layer.z_index,
            visible=visible,
            legend=layer.legend,
            model=layer.model,
        )

    if isinstance(layer, RegionLabelLayer):
        text = label.text or layer.short_text or layer.text
        if label.offset is None:
            return replace(layer, text=label.text or layer.text, visible=visible)
        return TextLayer(
            _region_position(layer, regions),
            text,
            style=layer.style,
            offset=label.offset,
            id=layer.id,
            role=layer.role,
            z_index=layer.z_index,
            visible=visible,
            legend=layer.legend,
            model=layer.model,
        )

    if isinstance(layer, TextLayer):
        changes = {"visible": visible}
        if label.text is not None:
            changes["text"] = label.text
        if label.offset is not None:
            changes["offset"] = label.offset
        return replace(layer, **changes)

    if isinstance(layer, AxisMarkLayer):
        if label.offset is not None:
            raise ValueError("Axis mark labels do not support offset")
        return replace(
            layer,
            label=label.text or layer.label,
            visible=visible,
        )

    if isinstance(layer, AxisNoteLayer):
        if label.offset is not None:
            raise ValueError("Axis note labels do not support offset")
        return replace(
            layer,
            text=label.text or layer.text,
            visible=visible,
        )

    if isinstance(layer, (BraceLayer, SpanBraceLayer)):
        if label.offset is not None:
            raise ValueError("Brace labels do not support offset")
        return replace(
            layer,
            label=label.text or layer.label,
            visible=visible,
        )

    raise TypeError(f"Layer {layer.id!r} does not carry a configurable label")


def is_label_layer(layer: Layer) -> bool:
    """Whether ``layer`` carries text controlled by :class:`Label`."""
    return isinstance(
        layer,
        (
            AxisMarkLayer,
            AxisNoteLayer,
            BraceLayer,
            PointLabelLayer,
            RegionLabelLayer,
            SpanBraceLayer,
            TextLayer,
        ),
    )


__all__ = ["Label", "Offset", "apply_label", "is_label_layer"]
