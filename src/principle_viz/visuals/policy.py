"""Policy-result visual layers."""

from typing import Literal

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
    SpanBraceLayer,
    Stroke,
)

from principle_viz.core.controls import PriceControlResult, PriceControlType
from principle_viz.core.line import Line
from principle_viz.policy.subsidy import SubsidyComparisonResult
from principle_viz.visuals.direct_labels import region_label_layer

GapBrace = Literal["line", "axis"]
"""Where a quantity gap is braced: on the price line itself or on the quantity axis."""


def gap_brace_layer(
    low: float,
    high: float,
    price: float,
    label: str,
    *,
    side: str,
    layer_id: str,
    where: GapBrace = "line",
) -> SpanBraceLayer | BraceLayer:
    """A brace over the quantities ``low``..``high`` left open at ``price``.

    ``where="line"`` braces them on the price line, on ``side`` (``"above"`` or
    ``"below"``), as textbooks mark a shortage or surplus; ``where="axis"`` braces
    them under the quantity axis instead.
    """
    if where == "axis":
        return BraceLayer("x", low, high, label, side="outside", id=layer_id)
    if where != "line":
        raise ValueError(f"gap brace must be 'line' or 'axis', got {where!r}")
    return SpanBraceLayer((low, price), (high, price), label, side=side, id=layer_id)


def price_control_layers(
    result: PriceControlResult, *, x_max: float, gap_brace: GapBrace = "line"
) -> tuple[Layer, ...]:
    """The control line, named directly, with ``p_c`` on the price axis. A binding
    control also marks ``Q_d`` and ``Q_s`` with guides and braces the gap between
    them: "Shortage" below a ceiling, "Surplus" above a floor (``gap_brace="axis"``
    braces it on the quantity axis instead)."""
    role = "principle.policy.control"
    ceiling = result.control_type == PriceControlType.CEILING
    symbol = "p_c" if ceiling else "p_f"
    name = f"${symbol}$"
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
        AxisMarkLayer(
            "y",
            price,
            symbol,
            math=True,
            id=f"market.control.mark.{symbol}",
        ),
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
            gap_brace_layer(
                q_short,
                q_long,
                price,
                "Shortage" if ceiling else "Surplus",
                side="below" if ceiling else "above",
                layer_id="market.control.gap",
                where=gap_brace,
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
    label: str | None = "$t$",
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
            stroke=Stroke(width=1.0, dash=DashStyle.DASHED),
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


MOVEMENT_ROLE = "principle.market.movement"
"""Arrows showing how a curve moves, drawn thin, black and dashed."""


def tax_shift_layers(
    *,
    quantity: float,
    base_price: float,
    taxed_price: float,
    label: str,
    layer_id: str,
) -> tuple[ArrowLayer | PointLabelLayer, ...]:
    role = MOVEMENT_ROLE
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
    role = MOVEMENT_ROLE
    return (
        ArrowLayer(start, end, id=layer_id, role=role, z_index=5),
        # Named at its tail, outside the narrow wedge between the two curves.
        PointLabelLayer(
            start,
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
