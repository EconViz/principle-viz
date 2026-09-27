"""Tax equilibrium solvers."""

from __future__ import annotations

from principle_viz.core.equilibrium import solve_equilibrium
from principle_viz.core.line import EPSILON, Line
from principle_viz.exceptions import PolicyError
from principle_viz.policy.models import (
    TaxEquilibriumResult,
    TaxOn,
    TaxScenario,
    TaxType,
)


def _solve_specific_tax(demand: Line, supply: Line, scenario: TaxScenario) -> TaxEquilibriumResult:
    """Solve fixed/per-unit tax using shifted curves in inverse form."""
    t = float(scenario.amount)

    if scenario.tax_on == TaxOn.PRODUCER:
        adjusted_supply = supply.shifted(delta_intercept=t)
        eq = solve_equilibrium(demand, adjusted_supply)
        q_star = eq.q_star
        consumer_price = demand.p_at(q_star)
        producer_price = consumer_price - t
    else:
        adjusted_demand = demand.shifted(delta_intercept=-t)
        eq = solve_equilibrium(adjusted_demand, supply)
        q_star = eq.q_star
        producer_price = supply.p_at(q_star)
        consumer_price = producer_price + t

    wedge = consumer_price - producer_price
    return TaxEquilibriumResult(
        q_star=q_star,
        consumer_price=consumer_price,
        producer_price=producer_price,
        tax_wedge=wedge,
        tax_revenue=wedge * q_star,
    )



def _solve_ad_valorem_tax(demand: Line, supply: Line, scenario: TaxScenario) -> TaxEquilibriumResult:
    """Solve ad valorem tax under linear demand/supply."""
    rate = float(scenario.amount)
    if rate <= -1.0:
        raise PolicyError("Ad valorem rate must be greater than -1.")

    demand_intercept, demand_slope = demand.to_inverse()
    supply_intercept, supply_slope = supply.to_inverse()

    lhs_intercept = demand_intercept - (1.0 + rate) * supply_intercept
    lhs_slope = demand_slope - (1.0 + rate) * supply_slope

    if abs(lhs_slope) <= EPSILON:
        raise PolicyError("Ad valorem tax produced a degenerate quantity equation.")

    q_star = -lhs_intercept / lhs_slope

    if scenario.tax_on == TaxOn.PRODUCER:
        producer_price = supply.p_at(q_star)
        consumer_price = (1.0 + rate) * producer_price
    else:
        consumer_price = demand.p_at(q_star)
        producer_price = consumer_price / (1.0 + rate)

    wedge = consumer_price - producer_price
    return TaxEquilibriumResult(
        q_star=q_star,
        consumer_price=consumer_price,
        producer_price=producer_price,
        tax_wedge=wedge,
        tax_revenue=wedge * q_star,
    )



def solve_tax_equilibrium(demand: Line, supply: Line, scenario: TaxScenario) -> TaxEquilibriumResult:
    """Solve post-tax equilibrium under selected tax type and incidence side."""
    if scenario.tax_type in {TaxType.FIXED_TAX, TaxType.PER_UNIT_TAX}:
        return _solve_specific_tax(demand, supply, scenario)
    if scenario.tax_type == TaxType.AD_VALOREM_TAX:
        return _solve_ad_valorem_tax(demand, supply, scenario)
    raise PolicyError(f"Unsupported tax type: {scenario.tax_type}")
