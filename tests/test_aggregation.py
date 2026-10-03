from __future__ import annotations

import pytest

from principle_viz.core.aggregation import (
    AggregationError,
    market_demand,
    market_supply,
    piecewise_surplus,
    solve_piecewise_equilibrium,
)
from principle_viz.core.discrete import (
    DiscreteDemand,
    DiscreteMarketError,
    DiscreteSupply,
    solve_discrete_equilibrium,
)
from principle_viz.core.line import Line
from principle_viz.core.piecewise import PiecewiseLinear, PiecewiseLinearError
from principle_viz.exceptions import EquilibriumError

DEMAND_A = Line.from_inverse(10.0, -2.0)  # choke 10, Q(0) = 5
DEMAND_B = Line.from_inverse(6.0, -0.5)  # choke 6, Q(0) = 12
SUPPLY_A = Line.from_inverse(2.0, 1.0)  # minimum price 2
SUPPLY_B = Line.from_inverse(5.0, 0.5)  # minimum price 5


# --- PiecewiseLinear ---------------------------------------------------------


def test_piecewise_requires_two_points_with_increasing_quantity() -> None:
    with pytest.raises(PiecewiseLinearError, match="at least two"):
        PiecewiseLinear(((0.0, 1.0),))
    with pytest.raises(PiecewiseLinearError, match="increase"):
        PiecewiseLinear(((0.0, 5.0), (0.0, 4.0)))
    with pytest.raises(PiecewiseLinearError, match="finite"):
        PiecewiseLinear(((0.0, float("nan")), (1.0, 4.0)))


def test_piecewise_requires_monotone_price() -> None:
    with pytest.raises(PiecewiseLinearError, match="monotone"):
        PiecewiseLinear(((0.0, 5.0), (1.0, 4.0), (2.0, 4.5)))
    with pytest.raises(PiecewiseLinearError, match="monotone"):
        PiecewiseLinear(((0.0, 5.0), (1.0, 5.0)))


def test_piecewise_evaluates_across_segments_and_reports_kinks() -> None:
    curve = PiecewiseLinear(((0.0, 10.0), (2.0, 6.0), (17.0, 0.0)))
    assert curve.is_downward_sloping
    assert curve.kinks == ((2.0, 6.0),)
    assert curve.domain == (0.0, 17.0)
    assert curve.price_range == (0.0, 10.0)
    assert curve.p_at(1.0) == pytest.approx(8.0)
    assert curve.p_at(2.0) == pytest.approx(6.0)
    assert curve.p_at(7.0) == pytest.approx(4.0)
    assert curve.q_at(8.0) == pytest.approx(1.0)
    assert curve.q_at(4.0) == pytest.approx(7.0)
    assert curve.q_at(0.0) == pytest.approx(17.0)


def test_piecewise_quantity_is_zero_past_the_zero_quantity_end() -> None:
    demand = PiecewiseLinear(((0.0, 10.0), (17.0, 0.0)))
    supply = PiecewiseLinear(((0.0, 2.0), (18.0, 10.0)))
    assert demand.q_at(12.0) == 0.0
    assert supply.q_at(1.0) == 0.0
    assert not supply.is_downward_sloping


def test_piecewise_rejects_points_outside_its_domain() -> None:
    supply = PiecewiseLinear(((0.0, 2.0), (18.0, 10.0)))
    with pytest.raises(PiecewiseLinearError, match="price"):
        supply.q_at(11.0)
    with pytest.raises(PiecewiseLinearError, match="quantity"):
        supply.p_at(19.0)
    with pytest.raises(PiecewiseLinearError, match="quantity"):
        supply.p_at(-1.0)
    demand = PiecewiseLinear(((0.0, 10.0), (17.0, 0.0)))
    with pytest.raises(PiecewiseLinearError, match="price"):
        demand.q_at(-1.0)


def test_piecewise_integrates_quantity_over_price() -> None:
    demand = PiecewiseLinear(((0.0, 10.0), (2.0, 6.0), (17.0, 0.0)))
    # Above 10 nothing is bought; between 6 and 10 a triangle of area 4.
    assert demand.integrate_q(6.0, 12.0) == pytest.approx(4.0)
    assert demand.integrate_q(4.0, 6.0) == pytest.approx(0.5 * (7.0 + 2.0) * 2.0)
    with pytest.raises(PiecewiseLinearError, match="p_low"):
        demand.integrate_q(5.0, 4.0)


# --- continuous aggregation --------------------------------------------------


def test_market_demand_sums_horizontally_with_a_kink_at_each_choke_price() -> None:
    market = market_demand((DEMAND_A, DEMAND_B))
    assert market.points == ((0.0, 10.0), (2.0, 6.0), (17.0, 0.0))
    assert market.kinks == ((2.0, 6.0),)
    for price in (9.0, 6.0, 4.0, 0.0, 11.0):
        expected = max(0.0, DEMAND_A.q_at(price)) + max(0.0, DEMAND_B.q_at(price))
        assert market.q_at(price) == pytest.approx(expected)


def test_market_demand_merges_equal_choke_prices() -> None:
    market = market_demand((DEMAND_A, Line.from_inverse(10.0, -1.0)))
    assert market.points == ((0.0, 10.0), (15.0, 0.0))
    assert market.kinks == ()


def test_market_demand_validates_individuals() -> None:
    with pytest.raises(AggregationError, match="at least one"):
        market_demand(())
    with pytest.raises(AggregationError, match="slope downward"):
        market_demand((SUPPLY_A,))
    with pytest.raises(AggregationError, match="choke price"):
        market_demand((Line.from_inverse(-1.0, -1.0),))
    with pytest.raises(AggregationError, match="slope downward"):
        market_demand((Line.from_standard(1.0, 0.0, -5.0),))


def test_market_supply_sums_horizontally_with_a_kink_at_each_minimum_price() -> None:
    market = market_supply((SUPPLY_A, SUPPLY_B), p_max=10.0)
    assert market.points == ((0.0, 2.0), (3.0, 5.0), (18.0, 10.0))
    assert market.kinks == ((3.0, 5.0),)
    for price in (1.0, 2.0, 4.0, 5.0, 8.0, 10.0):
        expected = max(0.0, SUPPLY_A.q_at(price)) + max(0.0, SUPPLY_B.q_at(price))
        assert market.q_at(price) == pytest.approx(expected)


def test_market_supply_validates_individuals_and_price_ceiling() -> None:
    with pytest.raises(AggregationError, match="at least one"):
        market_supply((), p_max=10.0)
    with pytest.raises(AggregationError, match="slope upward"):
        market_supply((DEMAND_A,), p_max=10.0)
    with pytest.raises(AggregationError, match="minimum price"):
        market_supply((Line.from_inverse(-1.0, 1.0),), p_max=10.0)
    with pytest.raises(AggregationError, match="p_max"):
        market_supply((SUPPLY_A, SUPPLY_B), p_max=5.0)


# --- equilibrium and welfare on aggregated curves ---------------------------


def test_piecewise_equilibrium_on_a_later_supply_segment() -> None:
    demand = market_demand((DEMAND_A, DEMAND_B))
    supply = market_supply((SUPPLY_A, SUPPLY_B), p_max=10.0)
    result = solve_piecewise_equilibrium(demand, supply)
    # Q = 17 - 2.5p (demand, p < 6) meets Q = 3p - 12 (supply, p > 5).
    assert result.p_star == pytest.approx(29 / 5.5)
    assert result.q_star == pytest.approx(3 * 29 / 5.5 - 12)
    assert result.is_valid_market


def test_piecewise_equilibrium_on_the_first_demand_segment() -> None:
    demand = market_demand((DEMAND_A, DEMAND_B))
    supply = market_supply((Line.from_inverse(7.0, 1.0),), p_max=12.0)
    result = solve_piecewise_equilibrium(demand, supply)
    # Only A buys above 6: Q = 5 - p/2 meets Q = p - 7.
    assert result.p_star == pytest.approx(8.0)
    assert result.q_star == pytest.approx(1.0)


def test_piecewise_equilibrium_at_a_kink() -> None:
    demand = market_demand((DEMAND_A, DEMAND_B))
    supply = market_supply((Line.from_inverse(4.0, 1.0),), p_max=12.0)
    result = solve_piecewise_equilibrium(demand, supply)
    assert result.p_star == pytest.approx(6.0)
    assert result.q_star == pytest.approx(2.0)


def test_piecewise_equilibrium_reports_no_trade_and_no_crossing() -> None:
    demand = market_demand((DEMAND_B,))
    with pytest.raises(EquilibriumError, match="no trade"):
        solve_piecewise_equilibrium(
            demand, market_supply((Line.from_inverse(7.0, 1.0),), p_max=12.0)
        )
    with pytest.raises(EquilibriumError, match="p_max"):
        solve_piecewise_equilibrium(
            demand, market_supply((Line.from_inverse(1.0, 1.0),), p_max=2.0)
        )
    with pytest.raises(EquilibriumError, match="downward"):
        solve_piecewise_equilibrium(
            market_supply((SUPPLY_A,), p_max=10.0),
            market_supply((SUPPLY_A,), p_max=10.0),
        )


def test_piecewise_surplus_integrates_both_sides() -> None:
    demand = market_demand((DEMAND_A, DEMAND_B))
    supply = market_supply((Line.from_inverse(4.0, 1.0),), p_max=12.0)
    result = solve_piecewise_equilibrium(demand, supply)
    consumer, producer = piecewise_surplus(demand, supply, result)
    assert consumer == pytest.approx(0.5 * 2.0 * 4.0)
    assert producer == pytest.approx(0.5 * 2.0 * 2.0)


# --- discrete aggregation ----------------------------------------------------


def test_discrete_demand_combines_reservation_prices_highest_first() -> None:
    market = DiscreteDemand.combine(
        DiscreteDemand((10, 7, 4)), DiscreteDemand((8, 5, 2))
    )
    assert market.values == (10, 8, 7, 5, 4, 2)


def test_discrete_supply_combines_unit_costs_lowest_first() -> None:
    market = DiscreteSupply.combine(
        DiscreteSupply((2, 5, 8)), DiscreteSupply((3, 4, 9))
    )
    assert market.values == (2, 3, 4, 5, 8, 9)


def test_discrete_combination_keeps_ties_as_separate_units() -> None:
    demand = DiscreteDemand.combine(DiscreteDemand((9, 5)), DiscreteDemand((7, 5)))
    supply = DiscreteSupply.combine(DiscreteSupply((3, 3)), DiscreteSupply((3,)))
    assert demand.values == (9, 7, 5, 5)
    assert supply.values == (3, 3, 3)


def test_discrete_combination_requires_schedules_of_the_same_side() -> None:
    with pytest.raises(DiscreteMarketError, match="at least one"):
        DiscreteDemand.combine()
    with pytest.raises(DiscreteMarketError, match="DiscreteDemand"):
        DiscreteDemand.combine(DiscreteDemand((5,)), DiscreteSupply((1,)))
    with pytest.raises(DiscreteMarketError, match="DiscreteSupply"):
        DiscreteSupply.combine(DiscreteDemand((5,)))


def test_discrete_quantity_at_includes_indifferent_units() -> None:
    demand = DiscreteDemand((10, 7, 4))
    supply = DiscreteSupply((2, 5, 8))
    assert [demand.quantity_at(p) for p in (11, 10, 6, 4, 0)] == [0, 1, 2, 3, 3]
    assert [supply.quantity_at(p) for p in (1, 2, 6, 8, 20)] == [0, 1, 2, 3, 3]


def test_discrete_market_quantity_is_the_sum_of_individual_quantities() -> None:
    a, b = DiscreteDemand((10, 7, 4)), DiscreteDemand((8, 5, 2))
    market = DiscreteDemand.combine(a, b)
    for price in (11, 9, 6, 4.5, 3, 1):
        assert market.quantity_at(price) == a.quantity_at(price) + b.quantity_at(price)


def test_discrete_equilibrium_on_combined_schedules() -> None:
    demand = DiscreteDemand.combine(
        DiscreteDemand((10, 7, 4)), DiscreteDemand((8, 5, 2))
    )
    supply = DiscreteSupply.combine(
        DiscreteSupply((2, 5, 8)), DiscreteSupply((3, 4, 9))
    )
    result = solve_discrete_equilibrium(demand, supply)
    # Values 10, 8, 7, 5 meet costs 2, 3, 4, 5; the fifth unit (4 vs 8) is not traded.
    assert result.q_star == 4
    assert (result.price_low, result.price_high) == (5, 5)
