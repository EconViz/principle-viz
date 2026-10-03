"""MosaicKit layers for discrete step schedules."""

from __future__ import annotations

from mosaickit import (
    TRANSPARENT,
    Layer,
    Marker,
    MarkerLayer,
    PathLayer,
    TextLayer,
)

from principle_viz.core.discrete import (
    DiscreteDemand,
    DiscreteEquilibriumResult,
    DiscreteSupply,
)


def discrete_schedule_layers(
    schedule: DiscreteDemand | DiscreteSupply,
    *,
    schedule_id: str,
    role: str,
    color: str,
    label: str,
) -> tuple[Layer, ...]:
    """Render `[q, q+1)` steps with solid-left and hollow-right endpoints."""
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
                    color=TRANSPARENT,
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
    layers: list[Layer] = []
    if equilibrium.price_high > equilibrium.price_low:
        layers.extend(
            (
                PathLayer(
                    ((0.0, equilibrium.price_low), (x_max, equilibrium.price_low)),
                    id="market.discrete.equilibrium.price_interval.lower",
                    role="principle.market.guide",
                    z_index=1,
                ),
                PathLayer(
                    ((0.0, equilibrium.price_high), (x_max, equilibrium.price_high)),
                    id="market.discrete.equilibrium.price_interval.upper",
                    role="principle.market.guide",
                    z_index=1,
                ),
                TextLayer(
                    (0.0, equilibrium.price_high),
                    f"p∈[{equilibrium.price_low:g}, {equilibrium.price_high:g}]",
                    id="market.discrete.equilibrium.price_interval.label",
                    role="principle.annotation",
                    offset=(8, 8),
                    anchor="left",
                    z_index=5,
                ),
            )
        )
    layers.extend(
        (
            PathLayer(
                ((0.0, equilibrium.price), (x_max, equilibrium.price)),
                id="market.discrete.equilibrium.price",
                role="principle.market.guide",
                z_index=3,
            ),
            MarkerLayer(
                ((float(equilibrium.q_star), equilibrium.price),),
                id="market.discrete.equilibrium",
                role="principle.market.equilibrium",
                marker=Marker(
                    color=color, edge_color=color, edge_width=0, size=42, shape="o"
                ),
                model=equilibrium,
                z_index=6,
            ),
            TextLayer(
                (float(equilibrium.q_star), equilibrium.price),
                f"Q*={equilibrium.q_star}, p*={equilibrium.price:g}",
                id="market.discrete.equilibrium.label",
                role="principle.market.equilibrium",
                offset=(12, 12),
                anchor="left",
                z_index=7,
            ),
        )
    )
    return tuple(layers)
