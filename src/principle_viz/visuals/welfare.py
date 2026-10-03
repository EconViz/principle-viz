"""Welfare regions and annotations as MosaicKit layers."""

from mosaickit import FillLayer, Layer, PathLayer, TextLayer

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


def welfare_layers(surplus: SurplusResult, *, labels: bool = True) -> tuple[Layer, ...]:
    """Shade CS, PS, tax revenue, and DWL; name each region unless ``labels`` is off."""
    fills: list[Layer] = []
    names: list[Layer] = []
    for region in build_labeled_regions(surplus):
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
        TextLayer(
            (ref.baseline_quantity, 0.0),
            r"$Q_0$",
            id="market.welfare.label.q0",
            role="principle.annotation",
            offset=(0, -12),
            anchor="bottom",
            z_index=4,
        ),
        TextLayer(
            (ref.policy_quantity, 0.0),
            r"$Q_1$",
            id="market.welfare.label.q1",
            role="principle.annotation",
            offset=(0, -12),
            anchor="bottom",
            z_index=4,
        ),
        TextLayer(
            (0.0, ref.baseline_price),
            r"$p_0$",
            id="market.welfare.label.p0",
            role="principle.annotation",
            offset=(-12, 0),
            anchor="right",
            z_index=4,
        ),
        TextLayer(
            (0.0, ref.policy_consumer_price),
            r"$p_1^c$",
            id="market.welfare.label.p1c",
            role="principle.annotation",
            offset=(-12, 0),
            anchor="right",
            z_index=4,
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
                TextLayer(
                    (0.0, ref.policy_producer_price),
                    r"$p_1^p$",
                    id="market.welfare.label.p1p",
                    role="principle.annotation",
                    offset=(-12, 0),
                    anchor="right",
                    z_index=4,
                ),
            )
        )
    return tuple(layers)
