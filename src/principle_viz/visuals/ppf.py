"""MosaicKit canvases for production-possibilities frontiers."""

from __future__ import annotations

from mosaickit import (
    Canvas,
    CanvasSpec,
    FillLayer,
    LegendLayer,
    LegendStyle,
    MarkerLayer,
    PathLayer,
    TextLayer,
)

from principle_viz.core.ppf import PointStatus, PPFAnalysisResult, PPFGrowthResult
from principle_viz.visuals.axes import market_axes_layers
from principle_viz.visuals.theme import PlotTheme

_STATUS_ROLES = {
    PointStatus.EFFICIENT: "principle.ppf.efficient",
    PointStatus.INEFFICIENT: "principle.ppf.inefficient",
    PointStatus.UNATTAINABLE: "principle.ppf.unattainable",
}


def ppf_canvas(
    result: PPFAnalysisResult,
    *,
    theme: PlotTheme | None = None,
) -> Canvas:
    frontier = result.frontier
    selected = theme or PlotTheme()
    x_max = frontier.x_intercept * 1.15
    y_max = frontier.y_intercept * 1.15
    canvas = Canvas(
        CanvasSpec(
            x_range=(0, x_max),
            y_range=(0, y_max),
            x_label=frontier.x_good,
            y_label=frontier.y_good,
            title="Production Possibilities Frontier",
        ),
        theme=selected.to_mosaickit(),
    ).extend(
        market_axes_layers(
            x_max,
            y_max,
            x_label=frontier.x_good,
            y_label=frontier.y_good,
        )
    )
    canvas.extend(
        (
            FillLayer(
                ((0.0, 0.0), *result.frontier_points, (frontier.x_intercept, 0.0)),
                id="ppf.feasible_set",
                role="principle.ppf.feasible",
                legend="Feasible set",
                z_index=0,
            ),
            PathLayer(
                result.frontier_points,
                id="ppf.frontier",
                role="principle.ppf.frontier",
                legend="PPF",
                z_index=2,
            ),
        )
    )
    legend_entries = ["ppf.feasible_set", "ppf.frontier"]
    for index, point in enumerate(result.assessed_points):
        layer_id = f"ppf.point.{index}"
        canvas.extend(
            (
                MarkerLayer(
                    ((point.x, point.y),),
                    id=layer_id,
                    role=_STATUS_ROLES[point.status],
                    legend=point.status.value.title(),
                    z_index=4,
                ),
                TextLayer(
                    (point.x, point.y),
                    point.label,
                    id=f"{layer_id}.label",
                    role="principle.annotation",
                    offset=(8, 8),
                    anchor="left",
                    z_index=5,
                ),
            )
        )
        if not any(
            result.assessed_points[previous].status == point.status
            for previous in range(index)
        ):
            legend_entries.append(layer_id)
    canvas.add(
        LegendLayer(
            entries=tuple(legend_entries),
            id="ppf.legend",
            style=LegendStyle(visible=True, location="best", frame=False),
        )
    )
    return canvas


def ppf_growth_canvas(
    result: PPFGrowthResult,
    *,
    theme: PlotTheme | None = None,
) -> Canvas:
    selected = theme or PlotTheme()
    x_max = max(result.baseline.x_intercept, result.shifted.x_intercept) * 1.1
    y_max = max(result.baseline.y_intercept, result.shifted.y_intercept) * 1.1
    canvas = Canvas(
        CanvasSpec(
            x_range=(0, x_max),
            y_range=(0, y_max),
            x_label=result.baseline.x_good,
            y_label=result.baseline.y_good,
            title="Economic Growth and the PPF",
        ),
        theme=selected.to_mosaickit(),
    ).extend(
        market_axes_layers(
            x_max,
            y_max,
            x_label=result.baseline.x_good,
            y_label=result.baseline.y_good,
        )
    )
    canvas.extend(
        (
            PathLayer(
                result.baseline_points,
                id="ppf.growth.baseline",
                role="principle.ppf.frontier",
                legend="Initial PPF",
            ),
            PathLayer(
                result.shifted_points,
                id="ppf.growth.shifted",
                role="principle.ppf.shifted",
                legend="PPF after growth",
            ),
            LegendLayer(
                entries=("ppf.growth.baseline", "ppf.growth.shifted"),
                id="ppf.growth.legend",
                style=LegendStyle(visible=True, location="best", frame=False),
            ),
        )
    )
    return canvas


__all__ = ["ppf_canvas", "ppf_growth_canvas"]
