"""Direct labels: name a curve beside its visible end instead of in a legend."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import replace
from itertools import pairwise

from mosaickit import Layer, PathLayer, PointLabelLayer, RegionLabelLayer

Point = tuple[float, float]
Range = tuple[float, float]

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


def curve_label_layer(
    path: PathLayer, *, x_range: Range, y_range: Range, at: str = "end"
) -> PointLabelLayer | None:
    """Name ``path`` with its legend text beside its visible end.

    ``at="end"`` (default) uses the right-most end, ``at="start"`` the left-most.
    MosaicKit places the text right beside that end, inside the plot, covering no
    line, point, region, or other text.
    """
    if not path.legend:
        return None
    found = _visible_end(tuple(path.path), x_range, y_range, at)
    if found is None:
        return None
    end, _ = found
    return PointLabelLayer(
        end,
        path.legend,
        id=f"{path.id}.label",
        role=path.role,
        z_index=7,
    )


HEADROOM = 0.92
"""Share of the price axis a curve may climb to, leaving room for its name."""


def fit_curve(path: PathLayer, *, x_range: Range, y_range: Range) -> PathLayer:
    """A straight curve trimmed to the plot, below ``HEADROOM`` of its height.

    Curves stop short of the top edge so neither they nor their names run into
    the axis arrow or the title. Curved or invisible paths are returned as is.
    """
    if not is_curve(path) or len(path.path) != 2:
        return path
    top = y_range[0] + HEADROOM * (y_range[1] - y_range[0])
    clipped = _clip(path.path[0], path.path[1], x_range, (y_range[0], top))
    if clipped is None or clipped == tuple(path.path):
        return path
    return replace(path, path=clipped)


def is_curve(layer: Layer) -> bool:
    return isinstance(layer, PathLayer) and any(
        layer.role == role or layer.role.startswith(f"{role}.") for role in CURVE_ROLES
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


def curve_label_layers(
    layers: Iterable[Layer],
    *,
    x_range: Range,
    y_range: Range,
    placed: Iterable[Layer] = (),
) -> tuple[PointLabelLayer, ...]:
    """Direct labels for every named curve among ``layers``.

    ``placed`` is accepted for compatibility; MosaicKit now keeps labels of curves
    that end at the same point apart by itself.
    """
    del placed
    labels: list[PointLabelLayer] = []
    for layer in layers:
        if not is_named_curve(layer):
            continue
        label = curve_label_layer(layer, x_range=x_range, y_range=y_range)
        if label is not None:
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
    "HEADROOM",
    "curve_label_layer",
    "curve_label_layers",
    "fit_curve",
    "is_curve",
    "is_named_curve",
    "region_label_layer",
]
