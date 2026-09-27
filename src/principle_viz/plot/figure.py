"""Figure facade for principles market diagrams."""

from __future__ import annotations

from principle_viz.core.controls import PriceControlResult
from principle_viz.core.equilibrium import EquilibriumResult
from principle_viz.core.line import Line
from principle_viz.core.shifts import ComparativeStaticsResult
from principle_viz.plot.canvas import Canvas
from principle_viz.plot.renderers import (
    render_control_line,
    render_curve,
    render_equilibrium_point,
    render_metrics_box,
    render_movement_arrows,
    render_rotation_arrow,
    render_surplus_regions,
    render_tax_shift_arrow,
    render_tax_wedge,
    render_welfare_overlay,
)
from principle_viz.plot.theme import PlotTheme
from principle_viz.policy.tax import (
    TaxComparisonResult,
    TaxScenario,
    TaxType,
    build_tax_visual_guide,
    compare_tax_scenario,
)
from principle_viz.welfare.surplus import MarketOutcome, SurplusResult


class MarketFigure:
    """High-level market figure built on top of Canvas."""

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
        if theme is not None:
            self.theme = theme
        elif palette is not None:
            self.theme = PlotTheme.from_palette(palette)
        else:
            self.theme = PlotTheme()
        self.canvas = Canvas(
            x_max=x_max,
            y_max=y_max,
            x_label=x_label,
            y_label=y_label,
            title=title,
            theme=self.theme,
        )
        self.fig = self.canvas.fig
        self.ax = self.canvas.ax

    def add_curves(
        self,
        demand: Line,
        supply: Line,
        q_max: float,
        demand_label: str = "Demand",
        supply_label: str = "Supply",
    ) -> MarketFigure:
        render_curve(
            self.ax,
            line=demand,
            q_min=0.0,
            q_max=q_max,
            label=demand_label,
            color=self.theme.demand_color,
            linestyle="-",
            linewidth=self.theme.demand_linewidth,
        )
        render_curve(
            self.ax,
            line=supply,
            q_min=0.0,
            q_max=q_max,
            label=supply_label,
            color=self.theme.supply_color,
            linestyle="-",
            linewidth=self.theme.supply_linewidth,
        )
        return self

    def add_equilibrium(
        self,
        equilibrium: EquilibriumResult,
        label: str = r"$e^{*}$",
        color: str | None = None,
    ) -> MarketFigure:
        render_equilibrium_point(
            self.ax,
            equilibrium=equilibrium,
            label=label,
            color=color or self.theme.baseline_color,
            marker_size=self.theme.equilibrium_marker_size,
        )
        return self

    def add_comparative_statics(
        self,
        result: ComparativeStaticsResult,
        q_max: float,
    ) -> MarketFigure:
        render_curve(
            self.ax,
            result.shifted_market.shifted_demand,
            q_min=0.0,
            q_max=q_max,
            label="Demand (shifted)",
            color=self.theme.demand_color,
            linestyle="--",
            linewidth=self.theme.shifted_linewidth,
        )
        render_curve(
            self.ax,
            result.shifted_market.shifted_supply,
            q_min=0.0,
            q_max=q_max,
            label="Supply (shifted)",
            color=self.theme.supply_color,
            linestyle="--",
            linewidth=self.theme.shifted_linewidth,
        )
        render_equilibrium_point(
            self.ax,
            result.baseline_equilibrium,
            r"$e_0$",
            self.theme.baseline_color,
            marker_size=self.theme.equilibrium_marker_size,
        )
        render_equilibrium_point(
            self.ax,
            result.shifted_equilibrium,
            r"$e_1$",
            self.theme.shifted_color,
            marker_size=self.theme.equilibrium_marker_size,
        )
        render_movement_arrows(
            self.ax,
            baseline=result.baseline_equilibrium,
            shifted=result.shifted_equilibrium,
            color=self.theme.arrow_color,
            linewidth=self.theme.arrow_linewidth,
        )
        return self

    def add_tax_comparison(self, result: TaxComparisonResult) -> MarketFigure:
        baseline = result.baseline_equilibrium
        render_equilibrium_point(
            self.ax,
            baseline,
            r"$e_0$",
            self.theme.baseline_color,
            marker_size=self.theme.equilibrium_marker_size,
        )

        post_eq = EquilibriumResult(
            q_star=result.post_tax.q_star,
            p_star=result.post_tax.consumer_price,
            is_valid_market=True,
            notes=(),
        )
        render_equilibrium_point(
            self.ax,
            post_eq,
            r"$e_1$",
            self.theme.shifted_color,
            marker_size=self.theme.equilibrium_marker_size,
        )
        render_tax_wedge(
            self.ax,
            quantity=result.post_tax.q_star,
            consumer_price=result.post_tax.consumer_price,
            producer_price=result.post_tax.producer_price,
            color=self.theme.tax_color,
        )
        return self

    def add_tax_transform(
        self,
        demand: Line,
        supply: Line,
        scenario: TaxScenario,
        q_max: float,
    ) -> MarketFigure:
        """Render taxed-curve transformation from a baseline anchor point."""
        guide = build_tax_visual_guide(demand, supply, scenario)

        if guide.curve_role == "demand":
            taxed_label = "Demand (taxed)"
            curve_color = self.theme.demand_color
        else:
            taxed_label = "Supply (taxed)"
            curve_color = self.theme.supply_color

        render_curve(
            self.ax,
            guide.taxed_curve,
            q_min=0.0,
            q_max=q_max,
            label=taxed_label,
            color=curve_color,
            linestyle="--",
            linewidth=self.theme.shifted_linewidth,
        )

        anchor_q = guide.baseline_equilibrium.q_star
        comparison: TaxComparisonResult | None = None
        if guide.transform_kind == "shift":
            render_tax_shift_arrow(
                self.ax,
                quantity=anchor_q,
                base_price=guide.base_curve.p_at(anchor_q),
                taxed_price=guide.taxed_curve.p_at(anchor_q),
                color=self.theme.tax_color,
                label=f"Tax = {scenario.amount:g}",
            )
        else:
            comparison = compare_tax_scenario(demand, supply, scenario)
            q0 = comparison.baseline_equilibrium.q_star
            q1 = comparison.post_tax.q_star

            # Reference guides mimic textbook ad-valorem diagrams.
            p0 = demand.p_at(q0)
            p1 = demand.p_at(q1)
            self.ax.vlines([q0, q1], 0.0, [p0, p1], colors=self.theme.axis_color, linestyles=":", linewidth=1.0)
            self.ax.hlines([p0, p1], 0.0, [q0, q1], colors=self.theme.axis_color, linestyles=":", linewidth=1.0)

            render_rotation_arrow(
                self.ax,
                base_curve=guide.base_curve,
                taxed_curve=guide.taxed_curve,
                pivot_q=q0,
                color=self.theme.tax_color,
                label=f"Tax rate = {scenario.amount:.0%}",
            )
            tax_label = f"Tax ({scenario.amount:.0%})"
            render_tax_shift_arrow(
                self.ax,
                quantity=q0,
                base_price=guide.base_curve.p_at(q0),
                taxed_price=guide.taxed_curve.p_at(q0),
                color=self.theme.tax_color,
                label=tax_label,
            )
            render_tax_shift_arrow(
                self.ax,
                quantity=q1,
                base_price=guide.base_curve.p_at(q1),
                taxed_price=guide.taxed_curve.p_at(q1),
                color=self.theme.tax_color,
                label="",
            )
        render_equilibrium_point(
            self.ax,
            guide.baseline_equilibrium,
            r"$e^{*}$",
            self.theme.baseline_color,
            marker_size=self.theme.equilibrium_marker_size,
            curvature=0.2,
        )
        if scenario.tax_type == TaxType.AD_VALOREM_TAX:
            if comparison is None:
                comparison = compare_tax_scenario(demand, supply, scenario)
            post_eq = EquilibriumResult(
                q_star=comparison.post_tax.q_star,
                p_star=comparison.post_tax.consumer_price,
                is_valid_market=True,
                notes=(),
            )
            render_equilibrium_point(
                self.ax,
                post_eq,
                r"$e_{t}$",
                self.theme.shifted_color,
                marker_size=self.theme.equilibrium_marker_size,
                curvature=-0.18,
            )
        return self

    def add_price_control(self, result: PriceControlResult) -> MarketFigure:
        render_control_line(self.ax, result, self.theme.control_color)
        return self

    def add_welfare(self, surplus: SurplusResult) -> MarketFigure:
        render_surplus_regions(
            self.ax,
            surplus=surplus,
            cs_color=self.theme.cs_color,
            ps_color=self.theme.ps_color,
            tax_color=self.theme.tax_revenue_color,
            dwl_color=self.theme.dwl_color,
        )
        return self

    def add_welfare_transition(
        self,
        *,
        baseline_outcome: MarketOutcome,
        policy_outcome: MarketOutcome,
        surplus: SurplusResult,
    ) -> MarketFigure:
        """Render welfare regions plus baseline/policy reference guides and region letters."""
        self.add_welfare(surplus)
        render_welfare_overlay(
            self.ax,
            baseline_outcome=baseline_outcome,
            policy_outcome=policy_outcome,
            surplus=surplus,
            color=self.theme.baseline_color,
        )
        return self

    def add_metrics(
        self,
        metrics: dict[str, object],
        *,
        title: str | None = None,
        location: str = "upper right",
    ) -> MarketFigure:
        """Render a compact metrics box on the figure."""
        render_metrics_box(
            self.ax,
            metrics=metrics,
            title=title,
            location=location,
            text_color=self.theme.label_color,
            edge_color=self.theme.axis_color,
        )
        return self

    def finalize(self, legend: bool = True) -> MarketFigure:
        self.canvas.finalize(legend=legend)
        return self

    def save(self, path: str, dpi: int = 150) -> None:
        self.canvas.save(path, dpi=dpi)

    def close(self) -> None:
        self.canvas.close()
