"""Compatibility figure facade composed entirely from MosaicKit layers."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import replace
from pathlib import Path

from mosaickit import (
    AxisMarkLayer,
    Canvas,
    CanvasSpec,
    Layer,
    LegendLayer,
    LegendStyle,
    Scene,
)

from principle_viz.core.controls import PriceControlResult
from principle_viz.core.discrete import (
    DiscreteDemand,
    DiscreteEquilibriumResult,
    DiscreteSupply,
)
from principle_viz.core.equilibrium import EquilibriumResult
from principle_viz.core.factor_markets import LoanableFundsResult, MinimumWageResult
from principle_viz.core.line import Line
from principle_viz.core.shifts import ComparativeStaticsResult
from principle_viz.plot.theme import PlotTheme
from principle_viz.policy.common_resources import CommonResourceResult
from principle_viz.policy.externality import ExternalityResult
from principle_viz.policy.subsidy import SubsidyComparisonResult
from principle_viz.policy.tax import (
    TaxComparisonResult,
    TaxScenario,
    TaxType,
    build_tax_visual_guide,
    compare_tax_scenario,
)
from principle_viz.policy.trade import TradeComparisonResult
from principle_viz.visuals import (
    common_resource_layers,
    curve_label_layers,
    curve_layer,
    discrete_equilibrium_layers,
    discrete_schedule_layers,
    equilibrium_layers,
    externality_layers,
    loanable_funds_layers,
    market_axes_layers,
    metrics_layer,
    minimum_wage_layers,
    movement_layers,
    price_control_layers,
    segment_layer,
    subsidy_layers,
    tax_rotation_layers,
    tax_shift_layers,
    tax_wedge_layers,
    trade_layers,
    welfare_layers,
    welfare_overlay_layers,
)
from principle_viz.visuals.axes import FIGURE_SIZE
from principle_viz.welfare.surplus import MarketOutcome, SurplusResult


class MarketFigure:
    """High-level market diagram facade over a MosaicKit canvas."""

    def __init__(
        self,
        x_max: float = 20.0,
        y_max: float = 20.0,
        x_label: str = "Q",
        y_label: str = "p",
        title: str = "Market Diagram",
        theme: PlotTheme | None = None,
        palette: str | None = None,
    ) -> None:
        self.theme = theme or PlotTheme.from_palette(palette or "default")
        self.x_max = float(x_max)
        self.y_max = float(y_max)
        self.canvas = Canvas(
            CanvasSpec(
                x_range=(0.0, self.x_max),
                y_range=(0.0, self.y_max),
                **FIGURE_SIZE,
                x_label=x_label,
                y_label=y_label,
                title=title,
            ),
            theme=self.theme.to_mosaickit(),
        )
        self.canvas.extend(
            market_axes_layers(
                self.x_max,
                self.y_max,
                x_label=x_label,
                y_label=y_label,
                arrows=self.theme.show_axis_arrows,
                origin_label=self.theme.show_origin_label,
            )
        )

    @property
    def scene(self) -> Scene:
        return self.canvas.snapshot()

    def add_layer(self, layer: Layer) -> MarketFigure:
        self.canvas.add(layer)
        return self

    def add_layers(self, layers: Iterable[Layer]) -> MarketFigure:
        """Add layers; an axis mark replaces any earlier mark at the same value."""
        layers = tuple(layers)
        for mark in layers:
            if isinstance(mark, AxisMarkLayer):
                for old in self.scene.layers:
                    if (
                        isinstance(old, AxisMarkLayer)
                        and old.axis == mark.axis
                        and abs(old.value - mark.value) <= 1e-9
                    ):
                        self.canvas.remove(old.id)
        self.canvas.extend(layers)
        return self

    def _add_named_curves(self, layers: Iterable[Layer]) -> MarketFigure:
        """Add layers and name each core curve beside its visible end."""
        layers = tuple(layers)
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
        demand_label: str = "Demand",
        supply_label: str = "Supply",
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
        demand: DiscreteDemand,
        supply: DiscreteSupply,
        *,
        demand_label: str = "Demand",
        supply_label: str = "Supply",
    ) -> MarketFigure:
        self.add_layers(
            discrete_schedule_layers(
                demand,
                schedule_id="market.discrete.demand",
                role="principle.market.demand",
                color=self.theme.demand_color,
                label=demand_label,
            )
        )
        self.add_layers(
            discrete_schedule_layers(
                supply,
                schedule_id="market.discrete.supply",
                role="principle.market.supply",
                color=self.theme.supply_color,
                label=supply_label,
            )
        )
        # Name each schedule at its last step.
        steps = {layer.id: layer for layer in self.scene.layers}
        for schedule_id, schedule, label in (
            ("market.discrete.demand", demand, demand_label),
            ("market.discrete.supply", supply, supply_label),
        ):
            last = steps[f"{schedule_id}.step.{len(schedule.values) - 1}"]
            self.add_layers(
                curve_label_layers(
                    (replace(last, id=schedule_id, legend=label),),
                    x_range=(0.0, self.x_max),
                    y_range=(0.0, self.y_max),
                )
            )
        return self

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
        # A curve that did not move is drawn but not named a second time.
        demand_moved = (
            market.shifted_demand.as_tuple() != market.baseline_demand.as_tuple()
        )
        supply_moved = (
            market.shifted_supply.as_tuple() != market.baseline_supply.as_tuple()
        )
        layers: list[Layer] = [
            curve_layer(
                result.shifted_market.shifted_demand,
                q_min=0.0,
                q_max=q_max,
                layer_id="market.demand.shifted",
                role="principle.market.demand.shifted",
                label=demand_label if demand_moved else None,
            ),
            curve_layer(
                result.shifted_market.shifted_supply,
                q_min=0.0,
                q_max=q_max,
                layer_id="market.supply.shifted",
                role="principle.market.supply.shifted",
                label=supply_label if supply_moved else None,
            ),
        ]
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

    def add_tax_comparison(
        self,
        result: TaxComparisonResult,
        *,
        brace_side: str = "outside",
        notes: bool = False,
    ) -> MarketFigure:
        """Mark the tax wedge: ``p_d``, ``p_0`` and ``p_s`` on the price axis with a
        "Tax" brace over ``p_s``..``p_d``, ``"outside"`` the axis (default) or
        ``"inside"`` the plot. ``notes=True`` explains each mark beside the axis.

        The wedge itself is named "Tax wedge" unless the figure already names the
        tax revenue region, which then says the same thing.
        """
        names_revenue = any(
            layer.id == "market.welfare.tax_revenue" for layer in self.scene.layers
        )
        post_eq = EquilibriumResult(
            q_star=result.post_tax.q_star,
            p_star=result.post_tax.consumer_price,
            is_valid_market=True,
            notes=(),
        )
        layers: list[Layer] = []
        layers.extend(
            equilibrium_layers(
                result.baseline_equilibrium,
                layer_id="market.equilibrium.baseline",
                label=r"$e_0$",
            )
        )
        layers.extend(
            equilibrium_layers(
                post_eq,
                layer_id="market.equilibrium.shifted",
                role="principle.market.equilibrium.shifted",
                label=r"$e_1$",
            )
        )
        layers.extend(
            tax_wedge_layers(
                quantity=result.post_tax.q_star,
                consumer_price=result.post_tax.consumer_price,
                producer_price=result.post_tax.producer_price,
                baseline_quantity=result.baseline_equilibrium.q_star,
                baseline_price=result.baseline_equilibrium.p_star,
                label=None if names_revenue else "Tax wedge",
                brace_side=brace_side,
                notes=notes,
            )
        )
        return self.add_layers(layers)

    def add_subsidy_comparison(self, result: SubsidyComparisonResult) -> MarketFigure:
        post = result.post_subsidy
        layers: list[Layer] = []
        layers.extend(
            equilibrium_layers(
                result.baseline_equilibrium,
                layer_id="market.equilibrium.baseline",
                label=r"$e_0$",
            )
        )
        layers.extend(
            equilibrium_layers(
                EquilibriumResult(
                    q_star=post.q_star,
                    p_star=post.consumer_price,
                    is_valid_market=True,
                    notes=(),
                ),
                layer_id="market.equilibrium.subsidized",
                role="principle.market.equilibrium.shifted",
                label=r"$e_s$",
            )
        )
        layers.extend(subsidy_layers(result))
        return self.add_layers(layers)

    def add_tax_transform(
        self,
        demand: Line,
        supply: Line,
        scenario: TaxScenario,
        q_max: float,
    ) -> MarketFigure:
        guide = build_tax_visual_guide(demand, supply, scenario)
        layers: list[Layer] = [
            curve_layer(
                guide.taxed_curve,
                q_min=0.0,
                q_max=q_max,
                layer_id=f"market.{guide.curve_role}.taxed",
                role=f"principle.market.{guide.curve_role}.shifted",
                label="$S + t$" if guide.curve_role == "supply" else "$D - t$",
            )
        ]
        anchor_q = guide.baseline_equilibrium.q_star
        comparison: TaxComparisonResult | None = None
        if guide.transform_kind == "shift":
            layers.extend(
                tax_shift_layers(
                    quantity=anchor_q,
                    base_price=guide.base_curve.p_at(anchor_q),
                    taxed_price=guide.taxed_curve.p_at(anchor_q),
                    label=f"$t = {scenario.amount:g}$",
                    layer_id="market.tax.shift",
                )
            )
        else:
            comparison = compare_tax_scenario(demand, supply, scenario)
            q0 = comparison.baseline_equilibrium.q_star
            q1 = comparison.post_tax.q_star
            p0 = demand.p_at(q0)
            p1 = demand.p_at(q1)
            layers.extend(
                (
                    segment_layer((q0, 0.0), (q0, p0), layer_id="market.tax.guide.q0"),
                    segment_layer((q1, 0.0), (q1, p1), layer_id="market.tax.guide.q1"),
                    segment_layer((0.0, p0), (q0, p0), layer_id="market.tax.guide.p0"),
                    segment_layer((0.0, p1), (q1, p1), layer_id="market.tax.guide.p1"),
                    AxisMarkLayer("x", q0, "Q_0", math=True, id="market.tax.mark.q0"),
                    AxisMarkLayer("x", q1, "Q_1", math=True, id="market.tax.mark.q1"),
                    AxisMarkLayer("y", p0, "p_0", math=True, id="market.tax.mark.p0"),
                    AxisMarkLayer("y", p1, "p_1", math=True, id="market.tax.mark.p1"),
                )
            )
            layers.extend(
                tax_rotation_layers(
                    base_curve=guide.base_curve,
                    taxed_curve=guide.taxed_curve,
                    pivot_q=q0,
                    label=f"$t = {100 * scenario.amount:g}\\%$",
                )
            )
            layers.extend(
                tax_shift_layers(
                    quantity=q0,
                    base_price=guide.base_curve.p_at(q0),
                    taxed_price=guide.taxed_curve.p_at(q0),
                    label="",
                    layer_id="market.tax.shift.q0",
                )
            )
            layers.extend(
                tax_shift_layers(
                    quantity=q1,
                    base_price=guide.base_curve.p_at(q1),
                    taxed_price=guide.taxed_curve.p_at(q1),
                    label="",
                    layer_id="market.tax.shift.q1",
                )
            )
        layers.extend(
            equilibrium_layers(
                guide.baseline_equilibrium,
                layer_id="market.equilibrium.baseline",
                label="$e^*$",
            )
        )
        if scenario.tax_type == TaxType.AD_VALOREM_TAX:
            comparison = comparison or compare_tax_scenario(demand, supply, scenario)
            layers.extend(
                equilibrium_layers(
                    EquilibriumResult(
                        q_star=comparison.post_tax.q_star,
                        p_star=comparison.post_tax.consumer_price,
                        is_valid_market=True,
                        notes=(),
                    ),
                    layer_id="market.equilibrium.taxed",
                    role="principle.market.equilibrium.shifted",
                    label=r"$e_t$",
                )
            )
        return self._add_named_curves(layers)

    def add_price_control(self, result: PriceControlResult) -> MarketFigure:
        return self.add_layers(price_control_layers(result, x_max=self.x_max))

    def add_minimum_wage(self, result: MinimumWageResult) -> MarketFigure:
        return self.add_layers(minimum_wage_layers(result, x_max=self.x_max))

    def add_loanable_funds(self, result: LoanableFundsResult) -> MarketFigure:
        return self._add_named_curves(loanable_funds_layers(result, q_max=self.x_max))

    def add_externality(self, result: ExternalityResult) -> MarketFigure:
        return self._add_named_curves(externality_layers(result, q_max=self.x_max))

    def add_common_resource(self, result: CommonResourceResult) -> MarketFigure:
        return self._add_named_curves(common_resource_layers(result, q_max=self.x_max))

    def add_trade(self, result: TradeComparisonResult) -> MarketFigure:
        return self._add_named_curves(trade_layers(result, x_max=self.x_max))

    def add_welfare(
        self, surplus: SurplusResult, *, labels: bool = True
    ) -> MarketFigure:
        """Shade the welfare regions and, unless ``labels`` is off, name each one."""
        return self.add_layers(welfare_layers(surplus, labels=labels))

    def add_welfare_transition(
        self,
        *,
        baseline_outcome: MarketOutcome,
        policy_outcome: MarketOutcome,
        surplus: SurplusResult,
    ) -> MarketFigure:
        self.add_welfare(surplus)
        return self.add_layers(
            welfare_overlay_layers(
                baseline_outcome=baseline_outcome,
                policy_outcome=policy_outcome,
                surplus=surplus,
            )
        )

    def add_metrics(
        self,
        metrics: dict[str, object],
        *,
        title: str | None = None,
        location: str = "upper right",
    ) -> MarketFigure:
        metric_count = sum(
            layer.id.startswith("market.metrics.") for layer in self.scene.layers
        )
        return self.add_layer(
            metrics_layer(
                metrics,
                x_max=self.x_max,
                y_max=self.y_max,
                layer_id=f"market.metrics.{metric_count}",
                title=title,
                location=location,
            )
        )

    def finalize(self, legend: bool = False) -> MarketFigure:
        if any(layer.id == "market.legend" for layer in self.scene.layers):
            self.canvas.remove("market.legend")
        if legend:
            entries = tuple(layer.id for layer in self.scene.layers if layer.legend)
            if entries:
                self.canvas.add(
                    LegendLayer(
                        entries=entries,
                        id="market.legend",
                        style=LegendStyle(visible=True, location="best", frame=False),
                    )
                )
        return self

    def save(self, path: str | Path, dpi: int = 150) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        if dpi == self.canvas.spec.dpi:
            self.canvas.save(target)
            return
        canvas = Canvas(
            self.canvas.spec.replace(dpi=int(dpi)),
            theme=self.canvas.theme,
            config=self.canvas.config,
            renderer=self.canvas.renderer,
            role_overrides=self.canvas.role_overrides,
        ).extend(self.scene.layers)
        canvas.save(target)

    def close(self) -> None:
        """Compatibility no-op; MosaicKit closes temporary render results."""
