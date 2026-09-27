from __future__ import annotations

from principle_viz.core.controls import (
    PriceControlScenario,
    PriceControlType,
    evaluate_price_control,
)
from principle_viz.core.line import Line


def test_binding_price_ceiling_has_shortage() -> None:
    demand = Line.from_inverse(10.0, -1.0)
    supply = Line.from_inverse(2.0, 1.0)

    result = evaluate_price_control(
        demand,
        supply,
        PriceControlScenario(control_type=PriceControlType.CEILING, control_price=4.0),
    )

    assert result.is_binding is True
    assert result.shortage > 0.0


def test_nonbinding_floor_has_no_surplus() -> None:
    demand = Line.from_inverse(10.0, -1.0)
    supply = Line.from_inverse(2.0, 1.0)

    result = evaluate_price_control(
        demand,
        supply,
        PriceControlScenario(control_type=PriceControlType.FLOOR, control_price=5.0),
    )

    assert result.is_binding is False
    assert result.surplus == 0.0
