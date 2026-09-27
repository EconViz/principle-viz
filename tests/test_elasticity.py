from __future__ import annotations

import pytest

from principle_viz.core.elasticity import (
    arc_price_elasticity,
    classify_elasticity,
    point_price_elasticity,
)
from principle_viz.core.line import Line


def test_point_elasticity_linear_demand() -> None:
    demand = Line.from_inverse(10.0, -2.0)
    elasticity = point_price_elasticity(demand, q=2.0)
    assert elasticity == pytest.approx(-1.5)


def test_arc_elasticity() -> None:
    elasticity = arc_price_elasticity(q0=2.0, p0=6.0, q1=3.0, p1=4.0)
    assert elasticity == pytest.approx(-1.0)


def test_elasticity_classification() -> None:
    assert classify_elasticity(-2.1) == "elastic"
    assert classify_elasticity(-1.0) == "unit_elastic"
    assert classify_elasticity(-0.4) == "inelastic"
