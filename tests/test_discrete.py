from __future__ import annotations

import pytest

from principle_viz.core.discrete import (
    DiscreteDemand,
    DiscreteMarketError,
    DiscreteSupply,
    EquilibriumPriceRule,
    solve_discrete_equilibrium,
)
from principle_viz.welfare.discrete import compute_discrete_surplus


def test_discrete_equilibrium_returns_quantity_and_supporting_price_interval() -> None:
    result = solve_discrete_equilibrium(
        DiscreteDemand((11, 9, 7, 5, 3)),
        DiscreteSupply((1, 3, 5, 8, 10)),
    )

    assert result.q_star == 3
    assert result.price_low == 5
    assert result.price_high == 7
    assert result.price == 6
    assert result.gains_from_trade == (10, 6, 2)
    assert result.is_unique_price is False


def test_discrete_price_rule_selects_interval_endpoint() -> None:
    demand = DiscreteDemand((9, 7, 4))
    supply = DiscreteSupply((2, 5, 8))

    lower = solve_discrete_equilibrium(
        demand, supply, price_rule=EquilibriumPriceRule.LOWER
    )
    upper = solve_discrete_equilibrium(
        demand, supply, price_rule=EquilibriumPriceRule.UPPER
    )

    assert lower.q_star == upper.q_star == 2
    assert lower.price == lower.price_low == 5
    assert upper.price == upper.price_high == 7


def test_discrete_market_can_have_zero_trade() -> None:
    result = solve_discrete_equilibrium(DiscreteDemand((4, 2)), DiscreteSupply((6, 8)))

    assert result.q_star == 0
    assert (result.price_low, result.price_high, result.price) == (4, 6, 5)


def test_discrete_surplus_is_sum_of_unit_gains() -> None:
    equilibrium = solve_discrete_equilibrium(
        DiscreteDemand((11, 9, 7, 5, 3)),
        DiscreteSupply((1, 3, 5, 8, 10)),
    )
    surplus = compute_discrete_surplus(equilibrium)

    assert surplus.consumer_surplus == 9
    assert surplus.producer_surplus == 9
    assert surplus.total_surplus == 18
    assert surplus.total_surplus == pytest.approx(
        surplus.consumer_surplus + surplus.producer_surplus
    )


@pytest.mark.parametrize(
    ("factory", "values"),
    [
        (DiscreteDemand, (5, 6)),
        (DiscreteSupply, (6, 5)),
        (DiscreteDemand, ()),
        (DiscreteSupply, (-1, 2)),
    ],
)
def test_discrete_schedule_validation(factory, values) -> None:
    with pytest.raises(DiscreteMarketError):
        factory(values)
