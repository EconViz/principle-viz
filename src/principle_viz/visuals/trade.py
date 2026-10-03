"""MosaicKit layers for small-country trade diagrams."""

from __future__ import annotations

from mosaickit import ArrowLayer, FillLayer, Layer, PathLayer, TextLayer

from principle_viz.policy.trade import TradeComparisonResult, TradeDirection
from principle_viz.visuals.direct_labels import region_label_layer


def trade_layers(result: TradeComparisonResult, *, x_max: float) -> tuple[Layer, ...]:
    free = result.free_trade
    policy = result.policy
    layers: list[Layer] = [
        PathLayer(
            ((0.0, free.domestic_price), (x_max, free.domestic_price)),
            id="market.trade.world_price",
            role="principle.trade.world",
            legend="World price",
            z_index=2,
        ),
        TextLayer(
            (0.02 * x_max, free.domestic_price),
            r"$p_w$",
            id="market.trade.world_price.mark",
            role="principle.trade.world",
            offset=(0, -14),
            anchor="left",
            z_index=4,
        ),
    ]
    if policy.domestic_price > free.domestic_price + 1e-9:
        layers.extend(
            (
                PathLayer(
                    ((0.0, policy.domestic_price), (x_max, policy.domestic_price)),
                    id="market.trade.policy_price",
                    role="principle.trade.policy",
                    legend="Domestic policy price",
                    z_index=2,
                ),
                TextLayer(
                    (0.02 * x_max, policy.domestic_price),
                    r"$p_{policy}$",
                    id="market.trade.policy_price.mark",
                    role="principle.trade.policy",
                    offset=(0, 8),
                    anchor="left",
                    z_index=4,
                ),
            )
        )

    outcome = policy
    if outcome.direction == TradeDirection.IMPORT:
        start = (outcome.quantity_supplied, outcome.domestic_price)
        end = (outcome.quantity_demanded, outcome.domestic_price)
        label = f"Imports = {outcome.imports:g}"
    elif outcome.direction == TradeDirection.EXPORT:
        start = (outcome.quantity_demanded, outcome.domestic_price)
        end = (outcome.quantity_supplied, outcome.domestic_price)
        label = f"Exports = {outcome.exports:g}"
    else:
        start = end = None
        label = "No trade"

    if start is not None and end is not None:
        midpoint = ((start[0] + end[0]) / 2.0, outcome.domestic_price)
        layers.extend(
            (
                ArrowLayer(
                    start,
                    end,
                    id="market.trade.volume",
                    role="principle.trade.flow",
                    z_index=5,
                ),
                TextLayer(
                    midpoint,
                    label,
                    id="market.trade.volume.label",
                    role="principle.trade.flow",
                    offset=(0, 10),
                    anchor="bottom",
                    z_index=6,
                ),
            )
        )

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
