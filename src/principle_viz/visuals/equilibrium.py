"""Equilibrium markers, labels, guides, and movements."""

from mosaickit import ArrowLayer, Marker, MarkerLayer, Stroke, TextLayer, TextStyle

from principle_viz.core.equilibrium import EquilibriumResult


def equilibrium_layers(
    equilibrium: EquilibriumResult,
    *,
    layer_id: str = "market.equilibrium",
    role: str = "principle.market.equilibrium",
    label: str = r"$e^{*}$",
    color: str | None = None,
    marker_size: float | None = None,
    label_offset: tuple[float, float] = (14, 14),
) -> tuple[MarkerLayer | TextLayer, ...]:
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
        TextLayer(
            point,
            label,
            id=f"{layer_id}.label",
            role=role,
            style=text_style,
            offset=label_offset,
            anchor="left",
            z_index=7,
        ),
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
