"""MosaicKit panels for summing individual curves into a market curve."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace

from mosaickit import (
    AxisMarkLayer,
    Canvas,
    CanvasSpec,
    DashStyle,
    Layer,
    MarkerLayer,
    PathLayer,
    Stroke,
)

from principle_viz.core.discrete import DiscreteDemand, DiscreteSupply
from principle_viz.visuals.axes import market_axes_layers
from principle_viz.visuals.direct_labels import curve_label_layer
from principle_viz.visuals.discrete import discrete_schedule_layers
from principle_viz.visuals.theme import PlotTheme

Point = tuple[float, float]

PANEL_WIDTH = 4.6
PANEL_HEIGHT = 4.2


def aggregation_panel(
    *,
    title: str,
    x_max: float,
    y_max: float,
    theme: PlotTheme,
    x_min: float = 0.0,
) -> Canvas:
    """An empty p/Q panel with arrowed axes at the origin.

    A negative ``x_min`` leaves room left of the price axis, so markers sitting on
    it are drawn whole.
    """
    return Canvas(
        CanvasSpec(
            x_range=(x_min, x_max),
            y_range=(0.0, y_max),
            width=PANEL_WIDTH,
            height=PANEL_HEIGHT,
            dpi=150,
            x_label="Q",
            y_label="p",
            title=title,
        ),
        theme=theme.to_mosaickit(),
    ).extend(
        market_axes_layers(
            x_max,
            y_max,
            x_label="Q",
            y_label="p",
            arrows=theme.show_axis_arrows,
            origin_label=theme.show_origin_label,
        )
    )


def _bounds(canvas: Canvas) -> dict[str, tuple[float, float]]:
    return {"x_range": canvas.spec.x_range, "y_range": canvas.spec.y_range}


def named_path_layers(
    canvas: Canvas,
    points: Sequence[Point],
    *,
    panel_id: str,
    role: str,
    label: str,
) -> tuple[Layer, ...]:
    """A curve through ``points`` named beside its right-most visible end."""
    path = PathLayer(
        tuple(points),
        id=f"aggregation.{panel_id}.curve",
        role=role,
        legend=label,
        z_index=2,
    )
    text = curve_label_layer(path, **_bounds(canvas))
    return (path,) if text is None else (path, text)


def named_schedule_layers(
    canvas: Canvas,
    schedule: DiscreteDemand | DiscreteSupply,
    *,
    panel_id: str,
    role: str,
    color: str,
    label: str,
) -> tuple[Layer, ...]:
    """Unit steps (closed left, open right) named beside the last step."""
    schedule_id = f"aggregation.{panel_id}.curve"
    layers = discrete_schedule_layers(
        schedule, schedule_id=schedule_id, role=role, color=color, label=label
    )
    last = next(
        layer
        for layer in layers
        if layer.id == f"{schedule_id}.step.{schedule.unit_count - 1}"
    )
    text = curve_label_layer(
        replace(last, id=schedule_id, legend=label), **_bounds(canvas)
    )
    return layers if text is None else (*layers, text)


def _pieces(
    top: float, *, holes: Sequence[float], hole: float
) -> list[tuple[float, float]]:
    """Spans of ``[0, top]``, from the top down, that skip each hole."""
    pieces: list[tuple[float, float]] = []
    upper = top
    for centre in sorted((h for h in holes if 0 < h < top), reverse=True):
        if upper > centre + hole:
            pieces.append((upper, centre + hole))
        upper = min(upper, centre - hole)
    if upper > 0:
        pieces.append((upper, 0.0))
    return pieces


def quantity_guide_layers(
    *,
    panel_id: str,
    price: float,
    quantity: float,
    price_label: str,
    quantity_label: str,
    point: bool = True,
    holes: Sequence[float] = (),
    hole: float = 0.0,
) -> tuple[Layer, ...]:
    """Dashed guides from the price axis to the curve and down to the Q axis.

    The price and the quantity are axis marks, beside the axes outside the plot.
    The quantity guide breaks for ``hole`` around each price in ``holes`` (such as
    a step endpoint on the guide) so it never runs through a marker.
    """
    layers: list[Layer] = [
        AxisMarkLayer(
            "y",
            price,
            price_label,
            math=True,
            id=f"aggregation.{panel_id}.price.label",
        )
    ]
    if quantity <= 0:
        return tuple(layers)
    dashed = Stroke(dash=DashStyle.DASHED)
    layers.extend(
        (
            PathLayer(
                ((0.0, price), (quantity, price)),
                id=f"aggregation.{panel_id}.guide.price",
                role="principle.market.guide",
                stroke=dashed,
                z_index=1,
            ),
            *(
                PathLayer(
                    ((quantity, top), (quantity, bottom)),
                    id=f"aggregation.{panel_id}.guide.quantity"
                    + (f".{index}" if index else ""),
                    role="principle.market.guide",
                    stroke=dashed,
                    z_index=1,
                )
                for index, (top, bottom) in enumerate(
                    _pieces(price, holes=holes, hole=hole)
                )
            ),
            AxisMarkLayer(
                "x",
                quantity,
                quantity_label,
                math=True,
                id=f"aggregation.{panel_id}.quantity.label",
            ),
        )
    )
    if point:
        layers.append(
            MarkerLayer(
                ((quantity, price),),
                id=f"aggregation.{panel_id}.point",
                role="principle.market.equilibrium",
                z_index=6,
            )
        )
    return tuple(layers)


__all__ = [
    "aggregation_panel",
    "named_path_layers",
    "named_schedule_layers",
    "quantity_guide_layers",
]
