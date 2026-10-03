"""Welfare regions and annotations as MosaicKit layers."""

import math
from collections.abc import Iterable

from mosaickit import AxisMarkLayer, FillLayer, Layer, PathLayer

from principle_viz.visuals.direct_labels import region_label_layer
from principle_viz.welfare.layout import (
    build_labeled_regions,
    build_welfare_annotation_layout,
)
from principle_viz.welfare.surplus import MarketOutcome, SurplusResult

_REGION_ROLES = {
    "cs": "principle.welfare.consumer",
    "ps": "principle.welfare.producer",
    "tax_revenue": "principle.welfare.revenue",
    "dwl": "principle.welfare.loss",
}
# Roles drawn without a fill. MosaicKit only resolves *filled* regions by id,
# so their labels are placed against the polygon itself.
_UNFILLED_ROLES = frozenset({"principle.welfare.revenue"})


def welfare_layers(
    surplus: SurplusResult,
    *,
    labels: bool = True,
    regions: Iterable[str] | None = None,
) -> tuple[Layer, ...]:
    """Shade CS, PS, tax revenue, and DWL; name each region unless ``labels`` is off.

    ``regions`` keeps only the given keys (``"cs"``, ``"ps"``, ``"tax_revenue"``,
    ``"dwl"``), e.g. just the deadweight loss where other areas would overlap.
    """
    keep = None if regions is None else set(regions)
    fills: list[Layer] = []
    names: list[Layer] = []
    for region in build_labeled_regions(surplus):
        if keep is not None and region.key not in keep:
            continue
        layer_id = f"market.welfare.{region.key}"
        role = _REGION_ROLES[region.key]
        fills.append(
            FillLayer(
                region.points,
                id=layer_id,
                role=role,
                legend=region.label,
                model=surplus,
                z_index=1,
            )
        )
        names.append(
            region_label_layer(
                layer_id,
                region.label,
                region.short_label,
                polygon=region.points if role in _UNFILLED_ROLES else None,
            )
        )
    return tuple(fills + names) if labels else tuple(fills)


def welfare_overlay_layers(
    *,
    baseline_outcome: MarketOutcome,
    policy_outcome: MarketOutcome,
    surplus: SurplusResult,
) -> tuple[Layer, ...]:
    layout = build_welfare_annotation_layout(
        baseline_outcome=baseline_outcome,
        policy_outcome=policy_outcome,
        surplus=surplus,
    )
    ref = layout.reference
    role = "principle.market.guide"
    layers: list[Layer] = [
        PathLayer(
            ((ref.baseline_quantity, 0.0), (ref.baseline_quantity, ref.baseline_price)),
            id="market.welfare.guide.q0",
            role=role,
            z_index=3,
        ),
        PathLayer(
            ((0.0, ref.baseline_price), (ref.baseline_quantity, ref.baseline_price)),
            id="market.welfare.guide.p0",
            role=role,
            z_index=3,
        ),
        PathLayer(
            (
                (ref.policy_quantity, 0.0),
                (
                    ref.policy_quantity,
                    max(ref.policy_consumer_price, ref.policy_producer_price),
                ),
            ),
            id="market.welfare.guide.q1",
            role=role,
            z_index=3,
        ),
        PathLayer(
            (
                (0.0, ref.policy_consumer_price),
                (ref.policy_quantity, ref.policy_consumer_price),
            ),
            id="market.welfare.guide.p1c",
            role=role,
            z_index=3,
        ),
        AxisMarkLayer(
            "x",
            ref.baseline_quantity,
            "Q_0",
            math=True,
            id="market.welfare.label.q0",
        ),
        AxisMarkLayer(
            "x",
            ref.policy_quantity,
            "Q_1",
            math=True,
            id="market.welfare.label.q1",
        ),
        AxisMarkLayer(
            "y",
            ref.baseline_price,
            "p_0",
            math=True,
            id="market.welfare.label.p0",
        ),
        AxisMarkLayer(
            "y",
            ref.policy_consumer_price,
            "p_1^c",
            math=True,
            id="market.welfare.label.p1c",
        ),
    ]
    if abs(ref.policy_consumer_price - ref.policy_producer_price) > 1e-9:
        layers.extend(
            (
                PathLayer(
                    (
                        (0.0, ref.policy_producer_price),
                        (ref.policy_quantity, ref.policy_producer_price),
                    ),
                    id="market.welfare.guide.p1p",
                    role=role,
                    z_index=3,
                ),
                AxisMarkLayer(
                    "y",
                    ref.policy_producer_price,
                    "p_1^p",
                    math=True,
                    id="market.welfare.label.p1p",
                ),
            )
        )
    return tuple(layers)


def _strictly_inside(
    point: tuple[float, float], polygon: tuple[tuple[float, float], ...]
) -> bool:
    """Whether ``point`` lies inside ``polygon`` and off its edges."""
    x, y = point
    inside = False
    for (x0, y0), (x1, y1) in zip(polygon, polygon[1:] + polygon[:1]):
        dx, dy = x1 - x0, y1 - y0
        length2 = dx * dx + dy * dy
        t = 0.0 if length2 == 0 else ((x - x0) * dx + (y - y0) * dy) / length2
        t = min(1.0, max(0.0, t))
        if math.hypot(x - (x0 + t * dx), y - (y0 + t * dy)) <= 1e-9:
            return False
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * dx / dy:
            inside = not inside
    return inside


def guides_through_regions(layers: Iterable[Layer]) -> tuple[str, ...]:
    """Ids of guide lines that cut through a shaded welfare region.

    A guide drawn across a region splits it, leaving its name no room; the axis
    mark at the guide's end already carries the value.
    """
    layers = tuple(layers)
    regions = [
        tuple(layer.boundary)
        for layer in layers
        if isinstance(layer, FillLayer) and layer.role.startswith("principle.welfare.")
    ]
    crossing: list[str] = []
    for layer in layers:
        if not (
            isinstance(layer, PathLayer)
            and layer.role == "principle.market.guide"
            and len(layer.path) == 2
        ):
            continue
        (x0, y0), (x1, y1) = layer.path
        samples = [
            (x0 + t * (x1 - x0), y0 + t * (y1 - y0))
            for t in (step / 20 for step in range(1, 20))
        ]
        if any(
            _strictly_inside(point, region) for region in regions for point in samples
        ):
            crossing.append(layer.id)
    return tuple(crossing)
