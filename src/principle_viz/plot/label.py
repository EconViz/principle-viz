"""User overrides for labels supplied by PrincipleViz diagrams."""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass, replace
from typing import Any

from mosaickit import (
    AxisMarkLayer,
    AxisNoteLayer,
    BraceLayer,
    Layer,
    PointLabelLayer,
    RegionLabelLayer,
    SpanBraceLayer,
    TextLayer,
    TextStyle,
    Theme,
)
from mosaickit.errors import ConfigurationError
from mosaickit.styles.nudge import Nudge, nudge_from, parse_length

Offset = tuple[float, float]
Length = float | str
"""A number of points, or a string with a unit: ``"10pt"``, ``"0.5em"``, ``"2mm"``."""

_SIDES = ("top", "bottom", "left", "right")


@dataclass(frozen=True)
class Label:
    """Override one built-in label without discarding its default.

    ``None`` keeps the value supplied by PrincipleViz. An explicit ``offset`` is
    measured in points and opts out of automatic placement, giving the user exact
    control while MosaicKit still performs the drawing.

    ``top``, ``bottom``, ``left`` and ``right`` are the softer option: the label is
    placed as usual (automatically, or at its ``offset``) and then moved that far in
    that direction. A length is a number of points or a string with a unit,
    ``"10pt"``, ``"0.5em"`` (the label's font size) or ``"2mm"``; ``top`` and
    ``bottom`` combine, as do ``right`` and ``left``.
    """

    text: str | None = None
    visible: bool | None = None
    offset: Offset | None = None
    top: Length | None = None
    bottom: Length | None = None
    left: Length | None = None
    right: Length | None = None

    def __post_init__(self) -> None:
        if self.text is not None and not self.text:
            raise ValueError("Label.text must be a non-empty string")
        if self.visible is not None and not isinstance(self.visible, bool):
            raise TypeError("Label.visible must be a bool")
        for side in _SIDES:
            value = getattr(self, side)
            if value is not None:
                try:
                    parse_length(value, font_size=1.0)
                except ConfigurationError as error:
                    raise ValueError(f"Label.{side}: {error}") from None
        if self.offset is None:
            return
        offset = tuple(self.offset)
        if len(offset) != 2 or not all(math.isfinite(value) for value in offset):
            raise ValueError("Label.offset must contain two finite values")
        object.__setattr__(self, "offset", offset)

    @property
    def has_nudge(self) -> bool:
        """Whether any of ``top``, ``bottom``, ``left`` or ``right`` is set."""
        return any(getattr(self, side) is not None for side in _SIDES)

    def nudge(self, font_size: float | None = None) -> Nudge | None:
        """The move in points, or ``None`` without one; ``em`` uses ``font_size``."""
        if not self.has_nudge:
            return None
        try:
            return nudge_from(
                **{side: getattr(self, side) for side in _SIDES},
                font_size=font_size,
            )
        except ConfigurationError as error:
            raise ValueError(f"Label: {error}") from None


def label_font_size(layer: Layer, theme: Theme | None) -> float | None:
    """The font size of ``layer``'s text: its own style first, then its theme role."""
    style = getattr(layer, "style", None)
    if isinstance(style, TextStyle) and style.size is not None:
        return float(style.size)
    if theme is None:
        return None
    text = theme.resolve(layer.role, fallback_category=layer.fallback_category).text
    return None if text is None or text.size is None else float(text.size)


def _nudged(layer: Layer, nudge: Nudge | None) -> Layer:
    if nudge is None:
        return layer
    current: Any = getattr(layer, "nudge", None)
    if current is not None:
        nudge = Nudge(current.dx + nudge.dx, current.dy + nudge.dy)
    return replace(layer, nudge=nudge)


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
    theme: Theme | None = None,
) -> Layer:
    """Apply ``label`` to one MosaicKit label-bearing layer.

    ``theme`` gives the label's font size for nudges in ``em``.
    """
    nudge = label.nudge(label_font_size(layer, theme)) if label.has_nudge else None
    if nudge is not None and isinstance(layer, (AxisMarkLayer, AxisNoteLayer)):
        raise ValueError("Axis labels do not support top, bottom, left or right")
    return _nudged(_apply(layer, label, regions or {}), nudge)


def _apply(
    layer: Layer,
    label: Label,
    regions: Mapping[str, tuple[tuple[float, float], ...]],
) -> Layer:
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


__all__ = ["Label", "Length", "Offset", "apply_label", "is_label_layer"]
