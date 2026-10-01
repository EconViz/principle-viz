"""Welfare regions and annotations as MosaicKit layers."""

from mosaickit import FillLayer, Layer, PathLayer, TextLayer

from principle_viz.welfare.layout import build_welfare_annotation_layout
from principle_viz.welfare.surplus import MarketOutcome, SurplusResult


def welfare_layers(surplus: SurplusResult) -> tuple[FillLayer, ...]:
    specs = (
        (
            surplus.polygons.consumer_surplus,
            "market.welfare.cs",
            "principle.welfare.consumer",
            "Consumer Surplus",
        ),
        (
            surplus.polygons.producer_surplus,
            "market.welfare.ps",
            "principle.welfare.producer",
            "Producer Surplus",
        ),
        (
            surplus.polygons.tax_revenue,
            "market.welfare.tax_revenue",
            "principle.welfare.revenue",
            "Tax Revenue",
        ),
        (
            surplus.polygons.lost_surplus,
            "market.welfare.dwl",
            "principle.welfare.loss",
            "Deadweight Loss",
        ),
    )
    return tuple(
        FillLayer(
            points,
            id=layer_id,
            role=role,
            legend=label,
            model=surplus,
            z_index=1,
        )
        for points, layer_id, role, label in specs
        if len(points) >= 3
    )


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
            r"$P_0$",
            id="market.welfare.label.p0",
            role="principle.annotation",
            offset=(-12, 0),
            anchor="right",
            z_index=4,
        ),
        TextLayer(
            (0.0, ref.policy_consumer_price),
            r"$P_1^c$",
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
                    r"$P_1^p$",
                    id="market.welfare.label.p1p",
                    role="principle.annotation",
                    offset=(-12, 0),
                    anchor="right",
                    z_index=4,
                ),
            )
        )
    for index, region in enumerate(layout.regions):
        layers.append(
            TextLayer(
                region.centroid,
                region.letter,
                id=f"market.welfare.region.{index}",
                role="principle.annotation.strong",
                z_index=5,
            )
        )
    return tuple(layers)
