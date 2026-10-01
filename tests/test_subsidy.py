from __future__ import annotations

import pytest

from principle_viz.core.equilibrium import solve_equilibrium
from principle_viz.core.line import Line
from principle_viz.policy.subsidy import (
    SubsidyScenario,
    SubsidyTo,
    compare_subsidy_scenario,
    solve_subsidy_equilibrium,
)
from principle_viz.welfare.surplus import (
    compare_surplus,
    outcome_from_equilibrium,
    outcome_from_subsidy,
)


@pytest.fixture
def market() -> tuple[Line, Line]:
    return Line.from_inverse(12, -1), Line.from_inverse(2, 1)


def test_subsidy_expands_quantity_and_creates_price_wedge(
    market: tuple[Line, Line],
) -> None:
    demand, supply = market
    result = solve_subsidy_equilibrium(
        demand, supply, SubsidyScenario(2, SubsidyTo.PRODUCER)
    )

    assert result.q_star == pytest.approx(6)
    assert result.consumer_price == pytest.approx(6)
    assert result.producer_price == pytest.approx(8)
    assert result.subsidy_wedge == pytest.approx(2)
    assert result.government_expenditure == pytest.approx(12)


def test_legal_subsidy_recipient_does_not_change_economic_incidence(
    market: tuple[Line, Line],
) -> None:
    demand, supply = market
    producer = solve_subsidy_equilibrium(
        demand, supply, SubsidyScenario(2, SubsidyTo.PRODUCER)
    )
    consumer = solve_subsidy_equilibrium(
        demand, supply, SubsidyScenario(2, SubsidyTo.CONSUMER)
    )

    assert consumer == producer


def test_subsidy_welfare_includes_government_cost_and_dwl(
    market: tuple[Line, Line],
) -> None:
    demand, supply = market
    baseline = outcome_from_equilibrium(solve_equilibrium(demand, supply))
    comparison = compare_subsidy_scenario(
        demand, supply, SubsidyScenario(2, SubsidyTo.PRODUCER)
    )
    subsidized = outcome_from_subsidy(comparison.post_subsidy)

    welfare = compare_surplus(demand, supply, baseline, subsidized)

    assert welfare.policy.tax_revenue == pytest.approx(-12)
    assert welfare.policy.total_surplus == pytest.approx(24)
    assert welfare.deadweight_loss == pytest.approx(1)
