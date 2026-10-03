"""Equilibrium markers, labels, guides, and movements."""

from mosaickit import (
    ArrowLayer,
    AxisMarkLayer,
    Layer,
    Marker,
    MarkerLayer,
    PathLayer,
    PointLabelLayer,
    Stroke,
    TextStyle,
)

from principle_viz.core.equilibrium import EquilibriumResult


def equilibrium_layers(
    equilibrium: EquilibriumResult,
    *,
    layer_id: str = "market.equilibrium",
    role: str = "principle.market.equilibrium",
    label: str = "$e^*$",
    color: str | None = None,
    marker_size: float | None = None,
) -> tuple[MarkerLayer | PointLabelLayer, ...]:
    """A filled point and its label, which MosaicKit places beside it so it
    covers no curve, point, region, or other text."""
    point = (equilibrium.q_star, equilibrium.p_star)
    marker = None
    text_style = None
    if color is not None or marker_size is not None:
        marker = Marker(
            color=color,
            size=marker_size,
            edge_color=color,
            edge_width=0,
        )
        text_style = TextStyle(color=color)
    return (
        MarkerLayer(
            (point,),
            id=layer_id,
            role=role,
            marker=marker,
            model=equilibrium,
            z_index=6,
        ),
        PointLabelLayer(
            point,
            label,
            id=f"{layer_id}.label",
            role=role,
            style=text_style,
            z_index=7,
        ),
    )


def quantity_mark_layers(
    equilibrium: EquilibriumResult,
    symbol: str,
    *,
    layer_id: str,
    role: str = "principle.market.equilibrium",
) -> tuple[Layer, ...]:
    """A filled point named on the quantity axis instead of beside it: a guide
    drops from the point to the axis, where ``symbol`` (LaTeX, without ``$``)
    marks its quantity. Keeps crowded crossings free of text."""
    q, p = equilibrium.q_star, equilibrium.p_star
    return (
        MarkerLayer(((q, p),), id=layer_id, role=role, model=equilibrium, z_index=6),
        PathLayer(
            ((q, 0.0), (q, p)),
            id=f"{layer_id}.guide",
            role="principle.market.guide",
            z_index=2,
        ),
        AxisMarkLayer("x", q, symbol, math=True, id=f"{layer_id}.mark"),
    )


def movement_layers(
    baseline: EquilibriumResult,
    shifted: EquilibriumResult,
    *,
    layer_id: str = "market.comparison.movement",
    color: str | None = None,
    width: float | None = None,
) -> tuple[ArrowLayer, ArrowLayer]:
    corner = (shifted.q_star, baseline.p_star)
    stroke = (
        Stroke(color=color, width=width)
        if color is not None or width is not None
        else None
    )
    return (
        ArrowLayer(
            (baseline.q_star, baseline.p_star),
            corner,
            id=f"{layer_id}.quantity",
            role="principle.market.movement",
            stroke=stroke,
            z_index=5,
        ),
        ArrowLayer(
            corner,
            (shifted.q_star, shifted.p_star),
            id=f"{layer_id}.price",
            role="principle.market.movement",
            stroke=stroke,
            z_index=5,
        ),
    )
