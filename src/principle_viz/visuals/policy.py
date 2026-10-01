"""Policy-result visual layers."""

from mosaickit import ArrowLayer, DashStyle, FillLayer, PathLayer, Stroke, TextLayer

from principle_viz.core.controls import PriceControlResult
from principle_viz.core.line import Line
from principle_viz.policy.subsidy import SubsidyComparisonResult


def price_control_layers(
    result: PriceControlResult, *, x_max: float
) -> tuple[PathLayer, TextLayer]:
    note = f"{'Binding' if result.is_binding else 'Non-binding'} ({result.control_type.value})"
    role = "principle.policy.control"
    return (
        PathLayer(
            ((0.0, result.control_price), (x_max, result.control_price)),
            id="market.control.price",
            role=role,
            legend=result.control_type.value.title(),
            model=result,
            z_index=3,
        ),
        TextLayer(
            (0.02 * x_max, result.control_price),
            note,
            id="market.control.price.label",
            role=role,
            offset=(0, 8),
            anchor="left",
            z_index=4,
        ),
    )


def tax_wedge_layers(
    *,
    quantity: float,
    consumer_price: float,
    producer_price: float,
    label: str = "Tax wedge",
    layer_id: str = "market.tax.wedge",
) -> tuple[PathLayer, TextLayer]:
    midpoint = 0.5 * (consumer_price + producer_price)
    role = "principle.policy.tax"
    return (
        PathLayer(
            ((quantity, producer_price), (quantity, consumer_price)),
            id=layer_id,
            role=role,
            stroke=Stroke(dash=DashStyle.DASHED),
            z_index=5,
        ),
        TextLayer(
            (quantity, midpoint),
            label,
            id=f"{layer_id}.label",
            role=role,
            offset=(10, -16),
            anchor="left",
            z_index=6,
        ),
    )


def tax_shift_layers(
    *,
    quantity: float,
    base_price: float,
    taxed_price: float,
    label: str,
    layer_id: str,
) -> tuple[ArrowLayer | TextLayer, ...]:
    role = "principle.policy.tax"
    layers: list[ArrowLayer | TextLayer] = [
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
            TextLayer(
                (quantity, 0.5 * (base_price + taxed_price)),
                label,
                id=f"{layer_id}.label",
                role=role,
                offset=(8, 0),
                anchor="left",
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
) -> tuple[ArrowLayer, TextLayer]:
    start_q = pivot_q + delta_q
    end_q = pivot_q + 0.65 * delta_q
    start = (start_q, base_curve.p_at(start_q))
    end = (end_q, taxed_curve.p_at(end_q))
    role = "principle.policy.tax"
    return (
        ArrowLayer(start, end, id=layer_id, role=role, z_index=5),
        TextLayer(
            end,
            label,
            id=f"{layer_id}.label",
            role=role,
            offset=(8, 8),
            anchor="left",
            z_index=6,
        ),
    )


def subsidy_layers(
    result: SubsidyComparisonResult,
) -> tuple[FillLayer | PathLayer | TextLayer, ...]:
    """Render the producer-consumer subsidy wedge at the policy quantity."""
    post = result.post_subsidy
    midpoint = 0.5 * (post.consumer_price + post.producer_price)
    return (
        FillLayer(
            (
                (0.0, post.consumer_price),
                (post.q_star, post.consumer_price),
                (post.q_star, post.producer_price),
                (0.0, post.producer_price),
            ),
            id="market.subsidy.expenditure",
            role="principle.welfare.subsidy",
            legend="Government expenditure",
            z_index=0.5,
        ),
        PathLayer(
            ((post.q_star, post.consumer_price), (post.q_star, post.producer_price)),
            id="market.subsidy.wedge",
            role="principle.policy.subsidy",
            z_index=5,
        ),
        TextLayer(
            (post.q_star, midpoint),
            f"Subsidy = {post.subsidy_wedge:g}",
            id="market.subsidy.wedge.label",
            role="principle.policy.subsidy",
            offset=(10, 0),
            anchor="left",
            z_index=6,
        ),
    )
