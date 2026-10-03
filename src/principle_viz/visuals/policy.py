"""Policy-result visual layers."""

from mosaickit import (
    ArrowLayer,
    AxisMarkLayer,
    AxisNoteLayer,
    BraceLayer,
    DashStyle,
    FillLayer,
    Layer,
    PathLayer,
    PointLabelLayer,
    Stroke,
)

from principle_viz.core.controls import PriceControlResult, PriceControlType
from principle_viz.core.line import Line
from principle_viz.policy.subsidy import SubsidyComparisonResult
from principle_viz.visuals.direct_labels import region_label_layer


def line_label_anchor(
    level: float, crossings: tuple[float, ...], x_max: float
) -> tuple[float, float]:
    """A point on a horizontal line at ``level`` to hang its label on: halfway
    between the right-most curve crossing and the end of the line."""
    right = max((q for q in crossings if 0.0 <= q <= x_max), default=0.0)
    return (0.5 * (right + x_max), level)


def price_control_layers(
    result: PriceControlResult, *, x_max: float
) -> tuple[Layer, ...]:
    """The control line, named directly, with ``p_c`` on the price axis. A binding
    control also marks ``Q_d`` and ``Q_s`` with guides and braces the gap between
    them on the quantity axis: "Shortage" under a ceiling, "Surplus" over a floor."""
    role = "principle.policy.control"
    ceiling = result.control_type == PriceControlType.CEILING
    name = "Price ceiling" if ceiling else "Price floor"
    price = result.control_price
    layers: list[Layer] = [
        PathLayer(
            ((0.0, price), (x_max, price)),
            id="market.control.price",
            role=role,
            legend=name,
            model=result,
            z_index=3,
        ),
        PointLabelLayer(
            (x_max, price),
            name,
            id="market.control.price.label",
            role=role,
            z_index=4,
        ),
        AxisMarkLayer("y", price, "p_c", math=True, id="market.control.mark.p_c"),
    ]
    if not result.is_binding:
        return tuple(layers)
    gap = result.shortage if ceiling else result.surplus
    q_short = result.traded_quantity
    q_long = q_short + gap
    q_d, q_s = (q_long, q_short) if ceiling else (q_short, q_long)
    layers.extend(
        (
            PathLayer(
                ((q_d, 0.0), (q_d, price)),
                id="market.control.guide.q_d",
                role="principle.market.guide",
                z_index=2,
            ),
            PathLayer(
                ((q_s, 0.0), (q_s, price)),
                id="market.control.guide.q_s",
                role="principle.market.guide",
                z_index=2,
            ),
            AxisMarkLayer("x", q_d, "Q_d", math=True, id="market.control.mark.q_d"),
            AxisMarkLayer("x", q_s, "Q_s", math=True, id="market.control.mark.q_s"),
            BraceLayer(
                "x",
                q_short,
                q_long,
                "Shortage" if ceiling else "Surplus",
                side="outside",
                id="market.control.gap",
                role=role,
            ),
        )
    )
    return tuple(layers)


TAX_NOTES = {
    "p_d": "Price paid\nby buyers",
    "p_0": "Price\nwithout {policy}",
    "p_s": "Price received\nby sellers",
}
"""Explanations of the wedge price marks, shown with ``notes=True``."""


def tax_wedge_layers(
    *,
    quantity: float,
    consumer_price: float,
    producer_price: float,
    baseline_quantity: float | None = None,
    baseline_price: float | None = None,
    label: str | None = "Tax wedge",
    layer_id: str = "market.tax.wedge",
    brace_side: str = "outside",
    notes: bool = False,
    policy: str = "tax",
) -> tuple[Layer, ...]:
    """The tax wedge at the taxed quantity, read off the price axis.

    The price axis marks ``p_d`` (paid by buyers), ``p_0`` (before the tax, when
    ``baseline_price`` is given) and ``p_s`` (received by sellers), with a "Tax"
    brace over ``p_s``..``p_d`` on ``brace_side`` (``"outside"`` in the gutter or
    ``"inside"`` the plot). ``notes=True`` adds a short explanation of each mark.
    ``policy="subsidy"`` draws the same wedge for a subsidy (``p_s`` above ``p_d``).
    """
    role = f"principle.policy.{policy}"
    guide = "principle.market.guide"
    layers: list[Layer] = [
        PathLayer(
            ((quantity, producer_price), (quantity, consumer_price)),
            id=layer_id,
            role=role,
            stroke=Stroke(dash=DashStyle.DASHED),
            z_index=5,
        ),
        PathLayer(
            ((0.0, consumer_price), (quantity, consumer_price)),
            id=f"{layer_id}.guide.p_d",
            role=guide,
            z_index=3,
        ),
        PathLayer(
            ((0.0, producer_price), (quantity, producer_price)),
            id=f"{layer_id}.guide.p_s",
            role=guide,
            z_index=3,
        ),
    ]
    prices = [("p_d", consumer_price), ("p_s", producer_price)]
    if baseline_price is not None:
        prices.insert(1, ("p_0", baseline_price))
        if baseline_quantity is not None:
            layers.append(
                PathLayer(
                    ((0.0, baseline_price), (baseline_quantity, baseline_price)),
                    id=f"{layer_id}.guide.p_0",
                    role=guide,
                    z_index=3,
                )
            )
    for symbol, price in prices:
        layers.append(
            AxisMarkLayer("y", price, symbol, math=True, id=f"{layer_id}.mark.{symbol}")
        )
        if notes:
            layers.append(
                AxisNoteLayer(
                    "y",
                    price,
                    TAX_NOTES[symbol].format(policy=policy),
                    id=f"{layer_id}.note.{symbol}",
                )
            )
    if abs(consumer_price - producer_price) > 1e-9:
        layers.append(
            BraceLayer(
                "y",
                min(producer_price, consumer_price),
                max(producer_price, consumer_price),
                policy.title(),
                side=brace_side,
                id=f"{layer_id}.brace",
            )
        )
    if label:
        layers.append(
            PointLabelLayer(
                (quantity, 0.5 * (consumer_price + producer_price)),
                label,
                id=f"{layer_id}.label",
                role=role,
                z_index=6,
            )
        )
    return tuple(layers)


def tax_shift_layers(
    *,
    quantity: float,
    base_price: float,
    taxed_price: float,
    label: str,
    layer_id: str,
) -> tuple[ArrowLayer | PointLabelLayer, ...]:
    role = "principle.policy.tax"
    layers: list[ArrowLayer | PointLabelLayer] = [
        ArrowLayer(
            (quantity, base_price),
            (quantity, taxed_price),
            id=layer_id,
            role=role,
            z_index=5,
        )
    ]
    if label:
        layers.append(
            PointLabelLayer(
                (quantity, 0.5 * (base_price + taxed_price)),
                label,
                id=f"{layer_id}.label",
                role=role,
                z_index=6,
            )
        )
    return tuple(layers)


def tax_rotation_layers(
    *,
    base_curve: Line,
    taxed_curve: Line,
    pivot_q: float,
    label: str,
    layer_id: str = "market.tax.rotation",
    delta_q: float = 1.6,
) -> tuple[ArrowLayer, PointLabelLayer]:
    start_q = pivot_q + delta_q
    end_q = pivot_q + 0.65 * delta_q
    start = (start_q, base_curve.p_at(start_q))
    end = (end_q, taxed_curve.p_at(end_q))
    role = "principle.policy.tax"
    return (
        ArrowLayer(start, end, id=layer_id, role=role, z_index=5),
        PointLabelLayer(
            ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2),
            label,
            id=f"{layer_id}.label",
            role=role,
            z_index=6,
        ),
    )


def subsidy_layers(
    result: SubsidyComparisonResult,
    *,
    brace_side: str = "outside",
    notes: bool = False,
) -> tuple[Layer, ...]:
    """The subsidy wedge at the subsidised quantity and what it costs.

    Like the tax wedge, the price axis marks ``p_s`` (received by sellers), ``p_0``
    and ``p_d`` (paid by buyers), with a "Subsidy" brace over ``p_d``..``p_s``.
    """
    post = result.post_subsidy
    baseline = result.baseline_equilibrium
    cost = (
        (0.0, post.consumer_price),
        (post.q_star, post.consumer_price),
        (post.q_star, post.producer_price),
        (0.0, post.producer_price),
    )
    return (
        FillLayer(
            cost,
            id="market.subsidy.expenditure",
            role="principle.welfare.subsidy",
            legend="Subsidy cost",
            z_index=0.5,
        ),
        *tax_wedge_layers(
            quantity=post.q_star,
            consumer_price=post.consumer_price,
            producer_price=post.producer_price,
            baseline_quantity=baseline.q_star,
            baseline_price=baseline.p_star,
            label=f"$s = {post.subsidy_wedge:g}$",
            layer_id="market.subsidy.wedge",
            brace_side=brace_side,
            notes=notes,
            policy="subsidy",
        ),
        # Unshaded, so the label is placed against the polygon itself.
        region_label_layer(
            "market.subsidy.expenditure", "Subsidy cost", "Cost", polygon=cost
        ),
    )
