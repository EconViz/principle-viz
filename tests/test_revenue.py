from __future__ import annotations

import pytest

from principle_viz.core.line import Line
from principle_viz.core.revenue import elasticity_revenue_schedule
from principle_viz.exceptions import LineError
from principle_viz.visuals.revenue import elasticity_revenue_canvases


def test_linear_demand_revenue_is_maximized_at_unit_elasticity() -> None:
    demand = Line.from_inverse(12, -1)
    result = elasticity_revenue_schedule(demand)

    assert result.unit_elastic_quantity == pytest.approx(6)
    assert result.unit_elastic_price == pytest.approx(6)
    assert result.maximum_revenue == pytest.approx(36)
    unit_point = next(
        point for point in result.points if point.classification == "unit_elastic"
    )
    assert unit_point.quantity == pytest.approx(6)
    assert unit_point.total_revenue == pytest.approx(36)


def test_revenue_schedule_requires_downward_sloping_demand() -> None:
    with pytest.raises(LineError):
        elasticity_revenue_schedule(Line.from_inverse(2, 1))


def test_revenue_visuals_are_mosaickit_canvases() -> None:
    demand = Line.from_inverse(12, -1)
    result = elasticity_revenue_schedule(demand)

    demand_canvas, revenue_canvas = elasticity_revenue_canvases(demand, result)

    assert "elasticity.unit.point" in {
        layer.id for layer in demand_canvas.snapshot().layers
    }
    assert "elasticity.revenue.maximum" in {
        layer.id for layer in revenue_canvas.snapshot().layers
    }


def test_revenue_layers_and_text_are_user_configurable() -> None:
    from principle_viz import Label

    demand = Line.from_inverse(12, -1)
    result = elasticity_revenue_schedule(demand)
    demand_canvas, revenue_canvas = elasticity_revenue_canvases(
        demand,
        result,
        visibility={"elasticity.unit.point": False},
        labels={"elasticity.revenue.maximum": Label(text="$TR_{max}$")},
    )
    demand_layers = {layer.id: layer for layer in demand_canvas.snapshot().layers}
    revenue_layers = {layer.id: layer for layer in revenue_canvas.snapshot().layers}

    assert not demand_layers["elasticity.unit.point"].visible
    assert revenue_layers["elasticity.revenue.maximum.label"].text == "$TR_{max}$"


def test_revenue_titles_are_parameters_not_fixed_text() -> None:
    demand = Line.from_inverse(12, -1)
    result = elasticity_revenue_schedule(demand)

    def titles(**options) -> tuple[str, str]:
        drawn = [
            c.render() for c in elasticity_revenue_canvases(demand, result, **options)
        ]
        try:
            return drawn[0].axes.get_title(), drawn[1].axes.get_title()
        finally:
            for item in drawn:
                item.close()

    assert titles() == ("Demand and Elasticity", "Total Revenue")
    assert titles(titles=("A", None)) == ("A", "")
