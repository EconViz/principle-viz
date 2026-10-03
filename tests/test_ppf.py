from __future__ import annotations

import pytest

from principle_viz.core.ppf import (
    PointStatus,
    PPFGrowthScenario,
    ProductionPossibilitiesFrontier,
    analyze_ppf,
    analyze_ppf_growth,
    compare_linear_ppfs,
)
from principle_viz.visuals.ppf import ppf_canvas, ppf_growth_canvas


def test_bowed_ppf_has_increasing_opportunity_cost() -> None:
    frontier = ProductionPossibilitiesFrontier(10, 8, curvature=2)

    assert frontier.opportunity_cost_x(2) == pytest.approx(0.32)
    assert frontier.opportunity_cost_x(8) == pytest.approx(1.28)


def test_ppf_classifies_efficient_inefficient_and_unattainable_points() -> None:
    frontier = ProductionPossibilitiesFrontier(10, 8, curvature=2)
    result = analyze_ppf(
        frontier,
        (
            (6, frontier.y_at(6), "A"),
            (4, 3, "B"),
            (7, 6, "C"),
        ),
    )

    assert tuple(point.status for point in result.assessed_points) == (
        PointStatus.EFFICIENT,
        PointStatus.INEFFICIENT,
        PointStatus.UNATTAINABLE,
    )


def test_ppf_growth_can_expand_each_axis_differently() -> None:
    frontier = ProductionPossibilitiesFrontier(10, 8, curvature=2)
    result = analyze_ppf_growth(
        frontier,
        PPFGrowthScenario(x_growth_rate=0.2, y_growth_rate=0.1),
    )

    assert result.shifted.x_intercept == pytest.approx(12)
    assert result.shifted.y_intercept == pytest.approx(8.8)
    assert result.shifted.curvature == 2


def test_comparative_advantage_uses_opportunity_cost() -> None:
    result = compare_linear_ppfs(
        "A",
        ProductionPossibilitiesFrontier(10, 5),
        "B",
        ProductionPossibilitiesFrontier(6, 6),
    )

    assert result.opportunity_cost_x_a == pytest.approx(0.5)
    assert result.opportunity_cost_x_b == pytest.approx(1)
    assert result.comparative_advantage_x == "A"
    assert result.comparative_advantage_y == "B"


def test_ppf_visual_canvases_have_semantic_layers() -> None:
    frontier = ProductionPossibilitiesFrontier(10, 8, curvature=2)
    analysis = analyze_ppf(frontier, ((4, 3, "B"),))
    canvas = ppf_canvas(analysis)
    ids = {layer.id for layer in canvas.snapshot().layers}
    assert "ppf.feasible_set" in ids
    assert "ppf.frontier" in ids
    assert "ppf.point.0" in ids

    growth = analyze_ppf_growth(frontier, PPFGrowthScenario(0.2, 0.1))
    growth_ids = {layer.id for layer in ppf_growth_canvas(growth).snapshot().layers}
    assert "ppf.growth.baseline" in growth_ids
    assert "ppf.growth.shifted" in growth_ids


def test_ppf_layers_and_labels_are_user_configurable() -> None:
    from principle_viz import Label

    frontier = ProductionPossibilitiesFrontier(10, 8, curvature=2)
    analysis = analyze_ppf(frontier, ((4, 3, "B"),))
    canvas = ppf_canvas(
        analysis,
        visibility={"ppf.feasible_set": False},
        labels={"ppf.frontier": Label(text="$F$")},
    )
    layers = {layer.id: layer for layer in canvas.snapshot().layers}

    assert not layers["ppf.feasible_set"].visible
    assert layers["ppf.frontier.label"].text == "$F$"
    canvas.hide("ppf.point.0").configure_label("ppf.point.0", text="A")
    layers = {layer.id: layer for layer in canvas.snapshot().layers}
    assert not layers["ppf.point.0"].visible
    assert layers["ppf.point.0.label"].text == "A"
