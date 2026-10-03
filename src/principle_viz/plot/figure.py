"""Compatibility figure facade composed entirely from MosaicKit layers."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import replace
from pathlib import Path

from mosaickit import (
    AxisMarkLayer,
    Canvas,
    CanvasSpec,
    FillLayer,
    Layer,
    LegendLayer,
    LegendStyle,
    PathLayer,
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
from principle_viz.plot.label import Label, apply_label, is_label_layer
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
from principle_viz.visuals.direct_labels import fit_curve
from principle_viz.visuals.policy import GapBrace
from principle_viz.visuals.welfare import guides_through_regions
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
        labels: Mapping[str, Label] | None = None,
    ) -> None:
        self.theme = theme or PlotTheme.from_palette(palette or "default")
        self.x_max = float(x_max)
        self.y_max = float(y_max)
        self._label_overrides = dict(labels or {})
        if not all(
            isinstance(label, Label) for label in self._label_overrides.values()
        ):
            raise TypeError("MarketFigure labels must map layer ids to Label values")
        self._label_defaults: dict[str, Layer] = {}
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
        return self.add_layers((layer,))

    def _regions(
        self,
        incoming: Iterable[Layer] = (),
    ) -> dict[str, tuple[tuple[float, float], ...]]:
        return {
            layer.id: tuple(layer.boundary)
            for layer in (*self.scene.layers, *incoming)
            if isinstance(layer, FillLayer)
        }

    def _label_override(self, layer_id: str) -> Label | None:
        override = self._label_overrides.get(layer_id)
        if override is not None or not layer_id.endswith(".label"):
            return override
        return self._label_overrides.get(layer_id.removesuffix(".label"))

    def _prepare_labels(self, layers: tuple[Layer, ...]) -> tuple[Layer, ...]:
        regions = self._regions(layers)
        prepared: list[Layer] = []
        for layer in layers:
            if is_label_layer(layer):
                self._label_defaults[layer.id] = layer
                override = self._label_override(layer.id)
                if override is not None:
                    layer = apply_label(layer, override, regions=regions)
            prepared.append(layer)
        return tuple(prepared)

    def add_layers(self, layers: Iterable[Layer]) -> MarketFigure:
        """Add layers; an axis mark replaces any earlier mark at the same value."""
        layers = self._prepare_labels(tuple(layers))
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

    @property
    def label_ids(self) -> tuple[str, ...]:
        """Stable ids of every built-in label currently provided by the figure."""
        return tuple(self._label_defaults)

    def configure_label(
        self,
        layer_id: str,
        label: Label | None = None,
        *,
        text: str | None = None,
        visible: bool | None = None,
        offset: tuple[float, float] | None = None,
    ) -> MarketFigure:
        """Show, hide, rename, or move one built-in label.

        ``layer_id`` may be the label id returned by :attr:`label_ids` or the id
        without its final ``".label"``. Offsets are in points.
        """
        if label is not None and any(
            value is not None for value in (text, visible, offset)
        ):
            raise ValueError("Pass either a Label or individual label options")
        selected = label or Label(text=text, visible=visible, offset=offset)
        candidates = (layer_id, f"{layer_id}.label")
        resolved_id = next(
            (candidate for candidate in candidates if candidate in self._label_defaults),
            "",
        )
        if not resolved_id:
            available = ", ".join(self.label_ids) or "none"
            raise KeyError(f"Unknown label {layer_id!r}; available labels: {available}")
        self._label_overrides[resolved_id] = selected
        default = self._label_defaults[resolved_id]
        replacement = apply_label(default, selected, regions=self._regions())
        self.canvas.remove(resolved_id)
        self.canvas.add(replacement)
        return self

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

        The wedge itself is named ``t`` unless the figure already names the tax
        revenue region.
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
                label=None if names_revenue else f"$t = {result.post_tax.tax_wedge:g}$",
                brace_side=brace_side,
                notes=notes,
            )
        )
        return self.add_layers(layers)

    def add_subsidy_comparison(
        self,
        result: SubsidyComparisonResult,
        *,
        brace_side: str = "outside",
        notes: bool = False,
    ) -> MarketFigure:
        """Mark the subsidy wedge like the tax wedge, with a "Subsidy" brace on
        ``brace_side`` of the price axis, and name the subsidy's cost."""
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
                label=r"$e_1$",
            )
        )
        layers.extend(subsidy_layers(result, brace_side=brace_side, notes=notes))
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

    def add_price_control(
        self, result: PriceControlResult, *, gap_brace: GapBrace = "line"
    ) -> MarketFigure:
        return self.add_layers(
            price_control_layers(result, x_max=self.x_max, gap_brace=gap_brace)
        )

    def add_minimum_wage(
        self, result: MinimumWageResult, *, gap_brace: GapBrace = "line"
    ) -> MarketFigure:
        return self.add_layers(
            minimum_wage_layers(result, x_max=self.x_max, gap_brace=gap_brace)
        )

    def add_loanable_funds(self, result: LoanableFundsResult) -> MarketFigure:
        return self._add_named_curves(loanable_funds_layers(result, q_max=self.x_max))

    def add_externality(self, result: ExternalityResult) -> MarketFigure:
        return self._add_named_curves(externality_layers(result, q_max=self.x_max))

    def add_common_resource(self, result: CommonResourceResult) -> MarketFigure:
        return self._add_named_curves(common_resource_layers(result, q_max=self.x_max))

    def add_trade(self, result: TradeComparisonResult) -> MarketFigure:
        return self._add_named_curves(trade_layers(result, x_max=self.x_max))

    def add_welfare(
        self,
        surplus: SurplusResult,
        *,
        labels: bool = True,
        regions: Iterable[str] | None = None,
    ) -> MarketFigure:
        """Shade the welfare regions and, unless ``labels`` is off, name each one.

        ``regions`` limits the shading to some of ``"cs"``, ``"ps"``,
        ``"tax_revenue"`` and ``"dwl"``.
        """
        return self.add_layers(welfare_layers(surplus, labels=labels, regions=regions))

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
        """Finish the figure: drop guide lines that would cut a shaded welfare
        region in two (its axis mark still names the value), and add a legend only
        when ``legend`` is on."""
        for guide_id in guides_through_regions(self.scene.layers):
            self.canvas.remove(guide_id)
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
