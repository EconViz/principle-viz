"""Tax and subsidy methods of the market figure."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mosaickit import (
    AxisMarkLayer,
    Layer,
)

from principle_viz.core.equilibrium import EquilibriumResult
from principle_viz.core.line import Line
from principle_viz.plot.figure._curves import _CurvesMixin
from principle_viz.policy.subsidy import SubsidyComparisonResult
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
    segment_layer,
    subsidy_layers,
    tax_rotation_layers,
    tax_shift_layers,
    tax_wedge_layers,
)

if TYPE_CHECKING:
    from principle_viz.plot.figure import MarketFigure


class _WedgeMixin(_CurvesMixin):
    """Tax and subsidy methods of the market figure."""

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
