"""MosaicKit layers and canvases for market-failure diagrams."""

from __future__ import annotations

from mosaickit import (
    AxisMarkLayer,
    Canvas,
    CanvasSpec,
    FillLayer,
    Layer,
    MarkerLayer,
    PathLayer,
    PointLabelLayer,
)

from principle_viz.core.equilibrium import EquilibriumResult
from principle_viz.core.public_goods import PublicGoodResult
from principle_viz.policy.common_resources import CommonResourceResult
from principle_viz.policy.externality import ExternalityResult
from principle_viz.visuals.axes import FIGURE_SIZE, market_axes_layers
from principle_viz.visuals.curves import curve_layer, segment_layer
from principle_viz.visuals.direct_labels import (
    curve_label_layer,
    curve_label_layers,
    region_label_layer,
)
from principle_viz.visuals.equilibrium import quantity_mark_layers
from principle_viz.visuals.theme import PlotTheme


def externality_layers(result: ExternalityResult, *, q_max: float) -> tuple[Layer, ...]:
    layers: list[Layer] = []
    if result.corrective_tax > 0:
        layers.append(
            curve_layer(
                result.social_supply,
                q_min=0,
                q_max=q_max,
                layer_id="market.externality.social_cost",
                role="principle.market.supply.shifted",
                label="$MSC$",
            )
        )
    if result.corrective_subsidy > 0:
        layers.append(
            curve_layer(
                result.social_demand,
                q_min=0,
                q_max=q_max,
                layer_id="market.externality.social_benefit",
                role="principle.market.demand.shifted",
                label="$MSB$",
            )
        )
    layers.extend(
        quantity_mark_layers(
            result.private_equilibrium, "Q_m", layer_id="market.externality.private"
        )
    )
    layers.extend(
        quantity_mark_layers(
            result.social_equilibrium,
            "Q^*",
            layer_id="market.externality.social",
            role="principle.market.equilibrium.shifted",
        )
    )
    q0 = result.private_equilibrium.q_star
    q1 = result.social_equilibrium.q_star
    q_low, q_high = min(q0, q1), max(q0, q1)
    if abs(q_high - q_low) > 1e-9:
        layers.append(
            FillLayer(
                (
                    (q_low, result.social_demand.p_at(q_low)),
                    (q_high, result.social_demand.p_at(q_high)),
                    (q_high, result.social_supply.p_at(q_high)),
                    (q_low, result.social_supply.p_at(q_low)),
                ),
                id="market.externality.dwl",
                role="principle.welfare.loss",
                legend="Deadweight loss",
                z_index=1,
            )
        )
        layers.append(
            region_label_layer("market.externality.dwl", "Deadweight loss", "DWL")
        )
    wedge = result.corrective_tax or result.corrective_subsidy
    if wedge > 0:
        role = (
            "principle.policy.tax"
            if result.corrective_tax
            else "principle.policy.subsidy"
        )
        quantity = result.social_equilibrium.q_star
        lower = min(
            result.social_demand.p_at(quantity),
            result.social_supply.p_at(quantity),
            result.private_equilibrium.p_star,
        )
        layers.extend(
            (
                PathLayer(
                    ((quantity, lower), (quantity, lower + wedge)),
                    id="market.externality.corrective_wedge",
                    role=role,
                    z_index=5,
                ),
                PointLabelLayer(
                    (quantity, lower + 0.5 * wedge),
                    f"Corrective {'tax' if result.corrective_tax else 'subsidy'} = {wedge:g}",
                    id="market.externality.corrective_wedge.label",
                    role=role,
                    z_index=6,
                ),
            )
        )
    return tuple(layers)


def common_resource_layers(
    result: CommonResourceResult, *, q_max: float
) -> tuple[Layer, ...]:
    efficient = result.efficient_equilibrium
    open_access = result.open_access_equilibrium
    layers: list[Layer] = [
        curve_layer(
            result.social_cost,
            q_min=0,
            q_max=q_max,
            layer_id="market.common_resource.social_cost",
            role="principle.market.supply.shifted",
            label="$MSC$",
        ),
        *quantity_mark_layers(
            open_access,
            "Q_{open}",
            layer_id="market.common_resource.open_access",
        ),
        *quantity_mark_layers(
            EquilibriumResult(
                efficient.q_star,
                efficient.p_star,
                efficient.is_valid_market,
                efficient.notes,
            ),
            "Q^*",
            layer_id="market.common_resource.efficient",
            role="principle.market.equilibrium.shifted",
        ),
        FillLayer(
            (
                (efficient.q_star, result.private_benefit.p_at(efficient.q_star)),
                (open_access.q_star, result.private_benefit.p_at(open_access.q_star)),
                (open_access.q_star, result.social_cost.p_at(open_access.q_star)),
                (efficient.q_star, result.social_cost.p_at(efficient.q_star)),
            ),
            id="market.common_resource.dwl",
            role="principle.welfare.loss",
            legend="Deadweight loss",
            z_index=1,
        ),
        region_label_layer("market.common_resource.dwl", "Deadweight loss", "DWL"),
        PathLayer(
            (
                (efficient.q_star, result.private_cost.p_at(efficient.q_star)),
                (efficient.q_star, result.social_cost.p_at(efficient.q_star)),
            ),
            id="market.common_resource.fee",
            role="principle.policy.tax",
            z_index=5,
        ),
        PointLabelLayer(
            (
                efficient.q_star,
                0.5
                * (
                    result.private_cost.p_at(efficient.q_star)
                    + result.social_cost.p_at(efficient.q_star)
                ),
            ),
            f"Fee = {result.corrective_fee:g}",
            id="market.common_resource.fee.label",
            role="principle.policy.tax",
            z_index=6,
        ),
    ]
    return tuple(layers)


def public_good_canvas(
    result: PublicGoodResult,
    *,
    theme: PlotTheme | None = None,
) -> Canvas:
    selected = theme or PlotTheme()
    q_max = result.points[-1].quantity * 1.08
    y_max = (
        max(
            max(point.social_marginal_benefit, point.marginal_cost)
            for point in result.points
        )
        * 1.08
    )
    canvas = Canvas(
        CanvasSpec(
            **FIGURE_SIZE,
            x_range=(0, q_max),
            y_range=(0, y_max),
            x_label="Q",
            y_label="Marginal value / cost",
            title="Public Good",
        ),
        theme=selected.to_mosaickit(),
    ).extend(market_axes_layers(q_max, y_max, x_label="Q", y_label="$MB$, $MC$"))
    curves: list[PathLayer] = []
    for index, individual in enumerate(result.individuals):
        curves.append(
            PathLayer(
                tuple(
                    (point.quantity, point.individual_benefits[index])
                    for point in result.points
                ),
                id=f"public_good.individual.{index}",
                role="principle.market.demand.shifted",
                legend=individual.name,
            )
        )
    curves.extend(
        (
            PathLayer(
                tuple(
                    (point.quantity, point.social_marginal_benefit)
                    for point in result.points
                ),
                id="public_good.social_benefit",
                role="principle.market.demand",
                legend=r"$\Sigma MB$",
            ),
            PathLayer(
                tuple((point.quantity, point.marginal_cost) for point in result.points),
                id="public_good.marginal_cost",
                role="principle.market.supply",
                legend="$MC$",
            ),
        )
    )
    canvas.extend(curves)
    # Beyond its kink the sum runs along the largest individual curve, so it is
    # named where it starts, on the price axis.
    bounds = {"x_range": (0, q_max), "y_range": (0, y_max)}
    # Individual curves are named where they start, on the price axis, away from
    # the crowded quantity axis where they end.
    individuals = curves[:-2]
    canvas.extend(curve_label_layers(curves[-1:], **bounds))
    for curve in (*individuals, curves[-2]):
        canvas.add(curve_label_layer(curve, at="start", **bounds))
    canvas.extend(
        (
            MarkerLayer(
                ((result.efficient_quantity, result.efficient_marginal_value),),
                id="public_good.efficient",
                role="principle.market.equilibrium",
            ),
            MarkerLayer(
                (
                    (
                        result.private_provision_quantity,
                        result.marginal_cost.p_at(result.private_provision_quantity),
                    ),
                ),
                id="public_good.private_provision",
                role="principle.market.equilibrium.shifted",
            ),
            segment_layer(
                (result.efficient_quantity, 0.0),
                (result.efficient_quantity, result.efficient_marginal_value),
                layer_id="public_good.efficient.guide",
            ),
            segment_layer(
                (result.private_provision_quantity, 0.0),
                (
                    result.private_provision_quantity,
                    result.marginal_cost.p_at(result.private_provision_quantity),
                ),
                layer_id="public_good.private_provision.guide",
            ),
            AxisMarkLayer(
                "x",
                result.efficient_quantity,
                "Q^*",
                math=True,
                id="public_good.efficient.mark",
            ),
            AxisMarkLayer(
                "x",
                result.private_provision_quantity,
                "Q_p",
                math=True,
                id="public_good.private_provision.mark",
            ),
        )
    )
    return canvas


__all__ = ["common_resource_layers", "externality_layers", "public_good_canvas"]
