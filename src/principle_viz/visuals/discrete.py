"""MosaicKit layers for discrete step schedules."""

from __future__ import annotations

from itertools import pairwise

from mosaickit import (
    BraceLayer,
    DashStyle,
    Layer,
    Marker,
    MarkerLayer,
    PathLayer,
    PointLabelLayer,
    Stroke,
)

from principle_viz.core.discrete import (
    DiscreteDemand,
    DiscreteEquilibriumResult,
    DiscreteSupply,
)

OPEN_FILL = "white"
"""Face of an open endpoint: opaque, so the step behind it does not show through."""


def discrete_schedule_layers(
    schedule: DiscreteDemand | DiscreteSupply,
    *,
    schedule_id: str,
    role: str,
    color: str,
    label: str,
) -> tuple[Layer, ...]:
    """Render ``[q, q+1)`` steps: a closed point at the left end, an open point at
    the right end, and a dashed drop (or rise) from each open point to the
    closed point that starts the next step."""
    layers: list[Layer] = []
    starts: list[tuple[float, float]] = []
    ends: list[tuple[float, float]] = []
    for index, value in enumerate(schedule.values):
        start = (float(index), value)
        end = (float(index + 1), value)
        starts.append(start)
        ends.append(end)
        layers.append(
            PathLayer(
                (start, end),
                id=f"{schedule_id}.step.{index}",
                role=role,
                legend=label if index == 0 else None,
                model=schedule,
                z_index=2,
            )
        )
    connector = Stroke(color=color, width=1.0, dash=DashStyle.DASHED)
    for index, (end, following) in enumerate(pairwise(schedule.values)):
        q = float(index + 1)
        layers.append(
            PathLayer(
                ((q, end), (q, following)),
                id=f"{schedule_id}.connector.{index}",
                role=role,
                stroke=connector,
                z_index=1,
            )
        )
    layers.extend(
        (
            MarkerLayer(
                tuple(starts),
                id=f"{schedule_id}.closed",
                role=role,
                marker=Marker(
                    color=color, edge_color=color, edge_width=1.5, size=34, shape="o"
                ),
                z_index=4,
            ),
            MarkerLayer(
                tuple(ends),
                id=f"{schedule_id}.open",
                role=role,
                marker=Marker(
                    color=OPEN_FILL,
                    edge_color=color,
                    edge_width=1.5,
                    size=34,
                    shape="o",
                ),
                z_index=4,
            ),
        )
    )
    return tuple(layers)


def discrete_equilibrium_layers(
    equilibrium: DiscreteEquilibriumResult,
    *,
    x_max: float,
    color: str,
) -> tuple[Layer, ...]:
    point = (float(equilibrium.q_star), equilibrium.price)
    layers: list[Layer] = []
    if equilibrium.price_high > equilibrium.price_low:
        # Every price in the interval clears the market; guides stop at Q*.
        layers.extend(
            (
                PathLayer(
                    ((0.0, equilibrium.price_low), (point[0], equilibrium.price_low)),
                    id="market.discrete.equilibrium.price_interval.lower",
                    role="principle.market.guide",
                    z_index=1,
                ),
                PathLayer(
                    ((0.0, equilibrium.price_high), (point[0], equilibrium.price_high)),
                    id="market.discrete.equilibrium.price_interval.upper",
                    role="principle.market.guide",
                    z_index=1,
                ),
                BraceLayer(
                    "y",
                    equilibrium.price_low,
                    equilibrium.price_high,
                    rf"$p \in [{equilibrium.price_low:g}, {equilibrium.price_high:g}]$",
                    side="inside",
                    id="market.discrete.equilibrium.price_interval.label",
                    role="principle.annotation",
                    z_index=5,
                ),
            )
        )
    layers.extend(
        (
            PathLayer(
                ((0.0, equilibrium.price), point),
                id="market.discrete.equilibrium.price",
                role="principle.market.guide",
                z_index=3,
            ),
            MarkerLayer(
                (point,),
                id="market.discrete.equilibrium",
                role="principle.market.equilibrium",
                marker=Marker(
                    color=color, edge_color=color, edge_width=0, size=42, shape="o"
                ),
                model=equilibrium,
                z_index=6,
            ),
            PointLabelLayer(
                point,
                rf"$Q^* = {equilibrium.q_star},\ p^* = {equilibrium.price:g}$",
                id="market.discrete.equilibrium.label",
                role="principle.market.equilibrium",
                z_index=7,
            ),
        )
    )
    return tuple(layers)
