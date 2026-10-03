"""MosaicKit layers for small-country trade diagrams."""

from __future__ import annotations

from mosaickit import (
    AxisMarkLayer,
    BraceLayer,
    FillLayer,
    Layer,
    PathLayer,
)

from principle_viz.policy.trade import (
    TradeComparisonResult,
    TradeDirection,
    TradeOutcome,
)
from principle_viz.visuals.curves import segment_layer
from principle_viz.visuals.direct_labels import region_label_layer


def trade_layers(result: TradeComparisonResult, *, x_max: float) -> tuple[Layer, ...]:
    free = result.free_trade
    policy = result.policy
    layers: list[Layer] = [
        PathLayer(
            ((0.0, free.domestic_price), (x_max, free.domestic_price)),
            id="market.trade.world_price",
            role="principle.trade.world",
            legend="$p_w$",
            z_index=2,
        ),
        AxisMarkLayer(
            "y",
            free.domestic_price,
            "p_w",
            math=True,
            id="market.trade.world_price.mark",
        ),
    ]
    if policy.domestic_price > free.domestic_price + 1e-9:
        layers.extend(
            (
                PathLayer(
                    ((0.0, policy.domestic_price), (x_max, policy.domestic_price)),
                    id="market.trade.policy_price",
                    role="principle.trade.policy",
                    legend="$p_q$" if policy.quota_rent > 1e-9 else "$p_w + t$",
                    z_index=2,
                ),
                AxisMarkLayer(
                    "y",
                    policy.domestic_price,
                    "p_q" if policy.quota_rent > 1e-9 else "p_w + t",
                    math=True,
                    id="market.trade.policy_price.mark",
                ),
            )
        )

    outcome = policy
    if outcome.direction != TradeDirection.AUTARKY:
        layers.extend(_volume_layers(outcome))

    rent = outcome.government_revenue + outcome.national_quota_rent
    if rent > 1e-9 and outcome.imports > 1e-9:
        if outcome.government_revenue > 1e-9:
            name, short = "Tariff revenue", "Revenue"
        else:
            name, short = "Quota rent", "Rent"
        layers.append(
            FillLayer(
                (
                    (outcome.quantity_supplied, free.domestic_price),
                    (outcome.quantity_demanded, free.domestic_price),
                    (outcome.quantity_demanded, outcome.domestic_price),
                    (outcome.quantity_supplied, outcome.domestic_price),
                ),
                id="market.trade.policy_rent",
                role="principle.trade.rent",
                legend=name,
                z_index=1,
            )
        )
        layers.append(region_label_layer("market.trade.policy_rent", name, short))
    return tuple(layers)


__all__ = ["trade_layers"]


def _volume_layers(outcome: TradeOutcome) -> tuple[Layer, ...]:
    """Trade volume as a brace on the quantity axis over Q_s..Q_d, with guides
    down from the domestic supply and demand points at the domestic price."""
    price = outcome.domestic_price
    imports = outcome.direction == TradeDirection.IMPORT
    q_s, q_d = outcome.quantity_supplied, outcome.quantity_demanded
    return (
        segment_layer((q_s, 0.0), (q_s, price), layer_id="market.trade.guide.q_s"),
        segment_layer((q_d, 0.0), (q_d, price), layer_id="market.trade.guide.q_d"),
        AxisMarkLayer("x", q_s, "Q_s", math=True, id="market.trade.mark.q_s"),
        AxisMarkLayer("x", q_d, "Q_d", math=True, id="market.trade.mark.q_d"),
        BraceLayer(
            "x",
            min(q_s, q_d),
            max(q_s, q_d),
            "Imports" if imports else "Exports",
            side="outside",
            id="market.trade.volume",
        ),
    )
