from __future__ import annotations

from principle_viz.core.line import Line
from principle_viz.core.shifts import ShiftScenario, ShiftSpec, comparative_statics


def test_comparative_statics_demand_shift_up() -> None:
    demand = Line.from_inverse(10.0, -1.0)
    supply = Line.from_inverse(2.0, 1.0)

    result = comparative_statics(
        demand,
        supply,
        ShiftScenario(demand_shift=ShiftSpec(delta_intercept=2.0)),
    )

    assert result.delta_q > 0.0
    assert result.delta_p > 0.0
    assert result.direction_q == "right"
    assert result.direction_p == "up"


def test_comparative_statics_simultaneous_shift() -> None:
    demand = Line.from_inverse(10.0, -1.0)
    supply = Line.from_inverse(2.0, 1.0)

    result = comparative_statics(
        demand,
        supply,
        ShiftScenario(
            demand_shift=ShiftSpec(delta_intercept=1.0),
            supply_shift=ShiftSpec(delta_intercept=1.5),
        ),
    )

    assert result.shifted_equilibrium.q_star != result.baseline_equilibrium.q_star
