from __future__ import annotations

import pytest

from principle_viz.core.equilibrium import solve_equilibrium
from principle_viz.core.line import Line
from principle_viz.exceptions import CoincidentLinesError, ParallelLinesError


def test_solve_equilibrium_regular_case() -> None:
    demand = Line.from_inverse(10.0, -2.0)
    supply = Line.from_inverse(2.0, 1.0)
    result = solve_equilibrium(demand, supply)

    assert result.q_star == pytest.approx(8.0 / 3.0)
    assert result.p_star == pytest.approx(14.0 / 3.0)
    assert result.is_valid_market is True


def test_solve_equilibrium_parallel_raises() -> None:
    demand = Line.from_inverse(10.0, -1.0)
    supply = Line.from_inverse(5.0, -1.0)
    with pytest.raises(ParallelLinesError):
        solve_equilibrium(demand, supply)


def test_solve_equilibrium_coincident_raises() -> None:
    demand = Line.from_inverse(10.0, -1.0)
    supply = Line.from_inverse(10.0, -1.0)
    with pytest.raises(CoincidentLinesError):
        solve_equilibrium(demand, supply)


def test_negative_quantity_marked_invalid() -> None:
    demand = Line.from_inverse(1.0, -1.0)
    supply = Line.from_inverse(5.0, 1.0)
    result = solve_equilibrium(demand, supply)
    assert result.is_valid_market is False
    assert "Negative equilibrium quantity." in result.notes
