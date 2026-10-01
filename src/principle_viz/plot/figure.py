"""Compatibility figure facade composed entirely from MosaicKit layers."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from mosaickit import Canvas, CanvasSpec, Layer, LegendLayer, LegendStyle, Scene

from principle_viz.core.controls import PriceControlResult
from principle_viz.core.equilibrium import EquilibriumResult
from principle_viz.core.line import Line
from principle_viz.core.shifts import ComparativeStaticsResult
from principle_viz.plot.theme import PlotTheme
from principle_viz.policy.tax import (
    TaxComparisonResult,
    TaxScenario,
    TaxType,
    build_tax_visual_guide,
    compare_tax_scenario,
)
from principle_viz.visuals import (
    curve_layer,
    equilibrium_layers,
    market_axes_layers,
    metrics_layer,
    movement_layers,
    price_control_layers,
    segment_layer,
    tax_rotation_layers,
    tax_shift_layers,
    tax_wedge_layers,
    welfare_layers,
    welfare_overlay_layers,
)
from principle_viz.welfare.surplus import MarketOutcome, SurplusResult


class MarketFigure:
    """High-level market diagram facade over a MosaicKit canvas."""

    def __init__(
        self,
        x_max: float = 20.0,
        y_max: float = 20.0,
        x_label: str = "Q",
        y_label: str = "P",
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
                width=7.2,
                height=5.2,
                dpi=150,
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
        self.canvas.extend(layers)
        return self

    def add_curves(
        self,
        demand: Line,
        supply: Line,
        q_max: float,
        demand_label: str = "Demand",
        supply_label: str = "Supply",
    ) -> MarketFigure:
        return self.add_layers(
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

    def add_equilibrium(
        self,
        equilibrium: EquilibriumResult,
        label: str = r"$e^{*}$",
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
        self, result: ComparativeStaticsResult, q_max: float
    ) -> MarketFigure:
        layers: list[Layer] = [
            curve_layer(
                result.shifted_market.shifted_demand,
                q_min=0.0,
                q_max=q_max,
                layer_id="market.demand.shifted",
                role="principle.market.demand.shifted",
                label="Demand (shifted)",
            ),
            curve_layer(
                result.shifted_market.shifted_supply,
                q_min=0.0,
                q_max=q_max,
                layer_id="market.supply.shifted",
                role="principle.market.supply.shifted",
                label="Supply (shifted)",
            ),
        ]
        layers.extend(
            equilibrium_layers(
                result.baseline_equilibrium,
                layer_id="market.equilibrium.baseline",
                label=r"$e_0$",
                label_offset=(14, -14),
            )
        )
        layers.extend(
            equilibrium_layers(
                result.shifted_equilibrium,
                layer_id="market.equilibrium.shifted",
                role="principle.market.equilibrium.shifted",
                label=r"$e_1$",
                label_offset=(14, 14),
            )
        )
        layers.extend(
            movement_layers(result.baseline_equilibrium, result.shifted_equilibrium)
        )
        return self.add_layers(layers)

    def add_tax_comparison(self, result: TaxComparisonResult) -> MarketFigure:
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
                label_offset=(14, -14),
            )
        )
        layers.extend(
            equilibrium_layers(
                post_eq,
                layer_id="market.equilibrium.shifted",
                role="principle.market.equilibrium.shifted",
                label=r"$e_1$",
                label_offset=(14, 14),
            )
        )
        layers.extend(
            tax_wedge_layers(
                quantity=result.post_tax.q_star,
                consumer_price=result.post_tax.consumer_price,
                producer_price=result.post_tax.producer_price,
            )
        )
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
                label=f"{guide.curve_role.title()} (taxed)",
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
                    label=f"Tax = {scenario.amount:g}",
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
                )
            )
            layers.extend(
                tax_rotation_layers(
                    base_curve=guide.base_curve,
                    taxed_curve=guide.taxed_curve,
                    pivot_q=q0,
                    label=f"Tax rate = {scenario.amount:.0%}",
                )
            )
            layers.extend(
                tax_shift_layers(
                    quantity=q0,
                    base_price=guide.base_curve.p_at(q0),
                    taxed_price=guide.taxed_curve.p_at(q0),
                    label=f"Tax ({scenario.amount:.0%})",
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
                label=r"$e^{*}$",
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
                    label_offset=(14, -14),
                )
            )
        return self.add_layers(layers)

    def add_price_control(self, result: PriceControlResult) -> MarketFigure:
        return self.add_layers(price_control_layers(result, x_max=self.x_max))

    def add_welfare(self, surplus: SurplusResult) -> MarketFigure:
        return self.add_layers(welfare_layers(surplus))

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

    def finalize(self, legend: bool = True) -> MarketFigure:
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
            renderer=self.canvas.renderer,
            role_overrides=self.canvas.role_overrides,
        ).extend(self.scene.layers)
        canvas.save(target)

    def close(self) -> None:
        """Compatibility no-op; MosaicKit closes temporary render results."""
