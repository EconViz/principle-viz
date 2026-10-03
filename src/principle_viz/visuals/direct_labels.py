"""Direct labels: name a curve beside its visible end instead of in a legend."""

from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import replace
from itertools import pairwise

from mosaickit import Layer, PathLayer, RegionLabelLayer, TextLayer

Point = tuple[float, float]
Range = tuple[float, float]

OFFSET_PT = 4.0
"""Gap between the curve end and the text box, in points."""

LINE_PT = 13.0
"""Line step used to stack labels of curves that end at the same point."""

CURVE_ROLES = (
    "principle.market.demand",
    "principle.market.supply",
    "principle.trade.world",
    "principle.trade.policy",
    "principle.ppf.frontier",
    "principle.ppf.shifted",
)
"""Roles (and their sub-roles) whose paths are named curves."""


def _clip(
    start: Point, end: Point, x_range: Range, y_range: Range
) -> tuple[Point, Point] | None:
    """Liang-Barsky: the part of a segment inside the canvas, or None."""
    (x0, y0), (x1, y1) = start, end
    dx, dy = x1 - x0, y1 - y0
    lo, hi = 0.0, 1.0
    for p, q in (
        (-dx, x0 - x_range[0]),
        (dx, x_range[1] - x0),
        (-dy, y0 - y_range[0]),
        (dy, y_range[1] - y0),
    ):
        if p == 0:
            if q < 0:
                return None
            continue
        t = q / p
        if p < 0:
            lo = max(lo, t)
        else:
            hi = min(hi, t)
    if lo > hi:
        return None
    return (x0 + lo * dx, y0 + lo * dy), (x0 + hi * dx, y0 + hi * dy)


def _on_edge(segment: tuple[Point, Point], x_range: Range, y_range: Range) -> bool:
    """Whether a segment runs along a canvas edge (e.g. a curve resting on the Q axis)."""
    (x0, y0), (x1, y1) = segment
    return any(x0 == x1 == edge for edge in x_range) or any(
        y0 == y1 == edge for edge in y_range
    )


def _visible_end(
    points: tuple[Point, ...], x_range: Range, y_range: Range, at: str = "end"
) -> tuple[Point, Point] | None:
    """The right-most (or, ``at="start"``, left-most) visible end of a path and the
    visible point next to it."""
    visible = [
        clipped
        for clipped in (_clip(a, b, x_range, y_range) for a, b in pairwise(points))
        if clipped is not None
        and clipped[0] != clipped[1]
        and not _on_edge(clipped, x_range, y_range)
    ]
    if not visible:
        return None
    first = (visible[0][0], visible[0][1])
    last = (visible[-1][1], visible[-1][0])
    # Right-most end by default; a vertical curve is named at its top.
    pick = min if at == "start" else max
    return pick(first, last, key=lambda pair: (pair[0][0], pair[0][1]))


def _anchor(end: Point, neighbour: Point, x_range: Range, y_range: Range) -> str:
    """Compound anchor that puts the text off the curve and inside the figure.

    Text runs rightwards unless the curve leaves through the right edge. A curve that
    leaves through the top is named just above its exit point, the free space past the
    end (as with the axis titles); one resting on the quantity axis is named above it.
    Otherwise the text goes to the side the curve turns away from.
    """
    tol_x = 1e-6 * (x_range[1] - x_range[0])
    tol_y = 1e-6 * (y_range[1] - y_range[0])
    extends_left = end[0] >= x_range[1] - tol_x
    at_top = end[1] >= y_range[1] - tol_y
    at_bottom = end[1] <= y_range[0] + tol_y
    falls_back = neighbour[1] <= end[1]  # walking back along the curve goes down
    up = at_top or (at_bottom and not extends_left) or falls_back
    return f"{'bottom' if up else 'top'}-{'right' if extends_left else 'left'}"


def curve_label_layer(
    path: PathLayer, *, x_range: Range, y_range: Range, at: str = "end"
) -> TextLayer | None:
    """Name ``path`` with its legend text beside its visible end.

    ``at="end"`` (default) uses the right-most end, ``at="start"`` the left-most.
    """
    if not path.legend:
        return None
    found = _visible_end(tuple(path.path), x_range, y_range, at)
    if found is None:
        return None
    end, neighbour = found
    anchor = _anchor(end, neighbour, x_range, y_range)
    vertical, horizontal = anchor.split("-")
    return TextLayer(
        end,
        path.legend,
        id=f"{path.id}.label",
        role=path.role,
        offset=(
            OFFSET_PT if horizontal == "left" else -OFFSET_PT,
            OFFSET_PT if vertical == "bottom" else -OFFSET_PT,
        ),
        anchor=anchor,
        z_index=7,
    )


def is_named_curve(layer: Layer) -> bool:
    return (
        isinstance(layer, PathLayer)
        and bool(layer.legend)
        and any(
            layer.role == role or layer.role.startswith(f"{role}.")
            for role in CURVE_ROLES
        )
    )


def _stacked(label: TextLayer, placed: list[TextLayer]) -> TextLayer:
    """Move ``label`` one line away from each placed label sharing its end and anchor."""
    clashes = sum(
        other.anchor == label.anchor
        and math.isclose(other.position[0], label.position[0], abs_tol=1e-9)
        and math.isclose(other.position[1], label.position[1], abs_tol=1e-9)
        for other in placed
    )
    if not clashes:
        return label
    step = LINE_PT if label.anchor.startswith("bottom") else -LINE_PT
    dx, dy = label.offset
    return replace(label, offset=(dx, dy + clashes * step))


def curve_label_layers(
    layers: Iterable[Layer],
    *,
    x_range: Range,
    y_range: Range,
    placed: Iterable[Layer] = (),
) -> tuple[TextLayer, ...]:
    """Direct labels for every named curve among ``layers``.

    Labels of curves that end where an already ``placed`` text (or an earlier label
    here) sits are stacked a line apart rather than drawn over each other.
    """
    taken = [layer for layer in placed if isinstance(layer, TextLayer)]
    labels: list[TextLayer] = []
    for layer in layers:
        if not is_named_curve(layer):
            continue
        label = curve_label_layer(layer, x_range=x_range, y_range=y_range)
        if label is not None:
            label = _stacked(label, taken)
            taken.append(label)
            labels.append(label)
    return tuple(labels)


def region_label_layer(
    region_id: str,
    text: str,
    short_text: str,
    *,
    polygon: tuple[tuple[float, float], ...] | None = None,
) -> RegionLabelLayer:
    """Name a filled region inside it, by its short name, or by a callout."""
    return RegionLabelLayer(
        polygon if polygon is not None else region_id,
        text,
        short_text=short_text,
        placement="auto",
        id=f"{region_id}.label",
        role="principle.annotation",
        z_index=8,
    )


__all__ = [
    "CURVE_ROLES",
    "curve_label_layer",
    "curve_label_layers",
    "is_named_curve",
    "region_label_layer",
]
