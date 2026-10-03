"""MosaicKit canvases for elasticity and total revenue."""

from mosaickit import Canvas, CanvasSpec, MarkerLayer, PathLayer, PointLabelLayer

from principle_viz.core.line import Line
from principle_viz.core.revenue import ElasticityRevenueResult
from principle_viz.visuals.axes import FIGURE_SIZE, market_axes_layers
from principle_viz.visuals.direct_labels import curve_label_layer
from principle_viz.visuals.theme import PlotTheme


def elasticity_revenue_canvases(
    demand: Line,
    result: ElasticityRevenueResult,
    *,
    theme: PlotTheme | None = None,
) -> tuple[Canvas, Canvas]:
    selected = theme or PlotTheme()
    q_max = result.choke_quantity * 1.2
    demand_canvas = Canvas(
        CanvasSpec(
            **FIGURE_SIZE,
            x_range=(0, q_max),
            y_range=(0, result.choke_price * 1.05),
            x_label="Q",
            y_label="p",
            title="Demand and Elasticity",
        ),
        theme=selected.to_mosaickit(),
    ).extend(
        market_axes_layers(q_max, result.choke_price * 1.05, x_label="Q", y_label="p")
    )
    demand_curve = PathLayer(
        ((0, demand.p_at(0)), (result.choke_quantity, 0)),
        id="elasticity.demand",
        role="principle.market.demand",
        legend="Demand",
    )
    demand_canvas.extend(
        (
            demand_curve,
            curve_label_layer(
                demand_curve,
                x_range=demand_canvas.spec.x_range,
                y_range=demand_canvas.spec.y_range,
            ),
        )
    )
    demand_canvas.add(
        MarkerLayer(
            ((result.unit_elastic_quantity, result.unit_elastic_price),),
            id="elasticity.unit.point",
            role="principle.market.equilibrium",
        )
    )
    for text, position, layer_id in (
        (
            "Elastic",
            (result.choke_quantity * 0.22, demand.p_at(result.choke_quantity * 0.22)),
            "elastic",
        ),
        (
            "Unit elastic",
            (result.unit_elastic_quantity, result.unit_elastic_price),
            "unit",
        ),
        (
            "Inelastic",
            (result.choke_quantity * 0.78, demand.p_at(result.choke_quantity * 0.78)),
            "inelastic",
        ),
    ):
        demand_canvas.add(
            PointLabelLayer(position, text, id=f"elasticity.label.{layer_id}")
        )

    revenue_canvas = Canvas(
        CanvasSpec(
            **FIGURE_SIZE,
            x_range=(0, q_max),
            y_range=(0, result.maximum_revenue * 1.15),
            x_label="Q",
            y_label="$TR$",
            title="Total Revenue",
        ),
        theme=selected.to_mosaickit(),
    ).extend(
        market_axes_layers(
            q_max, result.maximum_revenue * 1.15, x_label="Q", y_label="$TR$"
        )
    )
    revenue_canvas.add(
        PathLayer(
            tuple((point.quantity, point.total_revenue) for point in result.points),
            id="elasticity.total_revenue",
            role="principle.market.demand",
            legend="Total revenue",
        )
    )
    revenue_canvas.add(
        MarkerLayer(
            ((result.unit_elastic_quantity, result.maximum_revenue),),
            id="elasticity.revenue.maximum",
            role="principle.market.equilibrium",
        )
    )
    revenue_canvas.add(
        PointLabelLayer(
            (result.unit_elastic_quantity, result.maximum_revenue),
            r"Maximum $TR$ at $|\varepsilon| = 1$",
            id="elasticity.revenue.maximum.label",
        )
    )
    return demand_canvas, revenue_canvas
