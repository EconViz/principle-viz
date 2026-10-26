"""Curve, equilibrium and comparative-statics methods of the market figure."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import replace
from typing import TYPE_CHECKING

from mosaickit import (
    Layer,
    PathLayer,
)

from principle_viz.core.discrete import (
    DiscreteDemand,
    DiscreteEquilibriumResult,
    DiscreteSupply,
)
from principle_viz.core.equilibrium import EquilibriumResult
from principle_viz.core.line import Line
from principle_viz.core.shifts import ComparativeStaticsResult
from principle_viz.plot.figure._host import _Host
from principle_viz.visuals import (
    curve_label_layers,
    curve_layer,
    discrete_equilibrium_layers,
    discrete_schedule_layers,
    equilibrium_layers,
    movement_layers,
)
from principle_viz.visuals.direct_labels import fit_curve

if TYPE_CHECKING:
    from principle_viz.plot.figure import MarketFigure


class _CurvesMixin(_Host):
    """Curve, equilibrium and comparative-statics methods of the market figure."""

    def _add_named_curves(self, layers: Iterable[Layer]) -> MarketFigure:
        """Add layers, trim straight curves below the top of the plot, and name each
        core curve beside its visible end."""
        bounds = {"x_range": (0.0, self.x_max), "y_range": (0.0, self.y_max)}
        layers = tuple(
            fit_curve(layer, **bounds) if isinstance(layer, PathLayer) else layer
            for layer in layers
        )
        labels = curve_label_layers(
            layers,
            x_range=(0.0, self.x_max),
            y_range=(0.0, self.y_max),
            placed=self.scene.layers,
        )
        return self.add_layers(layers + labels)

    def add_curves(
        self,
        demand: Line,
        supply: Line,
        q_max: float,
        demand_label: str = "$D$",
        supply_label: str = "$S$",
    ) -> MarketFigure:
        return self._add_named_curves(
            (
                curve_layer(
                    demand,
                    q_min=0.0,
                    q_max=q_max,
                    layer_id="market.demand",
                    role="principle.market.demand",
                    label=demand_label,
                ),
                curve_layer(
                    supply,
                    q_min=0.0,
                    q_max=q_max,
                    layer_id="market.supply",
                    role="principle.market.supply",
                    label=supply_label,
                ),
            )
        )

    def add_discrete_curves(
        self,
        demand: DiscreteDemand | None = None,
        supply: DiscreteSupply | None = None,
        *,
        demand_label: str = "$D$",
        supply_label: str = "$S$",
    ) -> MarketFigure:
        """Step schedules, each named at its last step; pass one or both."""
        schedules = [
            (schedule, schedule_id, role, color, label)
            for schedule, schedule_id, role, color, label in (
                (
                    demand,
                    "market.discrete.demand",
                    "principle.market.demand",
                    self.theme.demand_color,
                    demand_label,
                ),
                (
                    supply,
                    "market.discrete.supply",
                    "principle.market.supply",
                    self.theme.supply_color,
                    supply_label,
                ),
            )
            if schedule is not None
        ]
        if not schedules:
            raise ValueError("add_discrete_curves needs a demand or a supply schedule.")
        for schedule, schedule_id, role, color, label in schedules:
            layers = discrete_schedule_layers(
                schedule, schedule_id=schedule_id, role=role, color=color, label=label
            )
            self.add_layers(layers)
            last = next(
                layer
                for layer in layers
                if layer.id == f"{schedule_id}.step.{len(schedule.values) - 1}"
            )
            self.add_layers(
                curve_label_layers(
                    (replace(last, id=schedule_id, legend=label),),
                    x_range=(0.0, self.x_max),
                    y_range=(0.0, self.y_max),
                )
            )
        return self  # type: ignore[return-value]

    def add_discrete_equilibrium(
        self, equilibrium: DiscreteEquilibriumResult
    ) -> MarketFigure:
        return self.add_layers(
            discrete_equilibrium_layers(
                equilibrium,
                x_max=self.x_max,
                color=self.theme.baseline_color,
            )
        )

    def add_equilibrium(
        self,
        equilibrium: EquilibriumResult,
        label: str = "$e^*$",
        color: str | None = None,
    ) -> MarketFigure:
        return self.add_layers(
            equilibrium_layers(
                equilibrium,
                label=label,
                color=color,
                marker_size=self.theme.equilibrium_marker_size if color else None,
            )
        )

    def add_comparative_statics(
        self,
        result: ComparativeStaticsResult,
        q_max: float,
        *,
        demand_label: str = "$D_1$",
        supply_label: str = "$S_1$",
    ) -> MarketFigure:
        market = result.shifted_market
        demand_moved = (
            market.shifted_demand.as_tuple() != market.baseline_demand.as_tuple()
        )
        supply_moved = (
            market.shifted_supply.as_tuple() != market.baseline_supply.as_tuple()
        )
        # Only a curve that moved is drawn again.
        layers: list[Layer] = []
        if demand_moved:
            layers.append(
                curve_layer(
                    market.shifted_demand,
                    q_min=0.0,
                    q_max=q_max,
                    layer_id="market.demand.shifted",
                    role="principle.market.demand.shifted",
                    label=demand_label,
                )
            )
        if supply_moved:
            layers.append(
                curve_layer(
                    market.shifted_supply,
                    q_min=0.0,
                    q_max=q_max,
                    layer_id="market.supply.shifted",
                    role="principle.market.supply.shifted",
                    label=supply_label,
                )
            )
        layers.extend(
            equilibrium_layers(
                result.baseline_equilibrium,
                layer_id="market.equilibrium.baseline",
                label=r"$e_0$",
            )
        )
        layers.extend(
            equilibrium_layers(
                result.shifted_equilibrium,
                layer_id="market.equilibrium.shifted",
                role="principle.market.equilibrium.shifted",
                label=r"$e_1$",
            )
        )
        layers.extend(
            movement_layers(result.baseline_equilibrium, result.shifted_equilibrium)
        )
        return self._add_named_curves(layers)
