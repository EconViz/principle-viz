"""Labor and loanable-funds market models."""

from __future__ import annotations

import math
from dataclasses import dataclass

from principle_viz.core.equilibrium import EquilibriumResult, solve_equilibrium
from principle_viz.core.line import EPSILON, Line
from principle_viz.exceptions import PolicyError


@dataclass(frozen=True, slots=True)
class MinimumWageResult:
    equilibrium: EquilibriumResult
    minimum_wage: float
    is_binding: bool
    labor_demanded: float
    labor_supplied: float
    employment: float
    unemployment: float
    wage_bill: float


def analyze_minimum_wage(
    labor_demand: Line,
    labor_supply: Line,
    minimum_wage: float,
) -> MinimumWageResult:
    """Analyze a competitive labor market with a statutory wage floor."""
    if not math.isfinite(minimum_wage) or minimum_wage < 0:
        raise PolicyError("Minimum wage must be finite and nonnegative.")
    equilibrium = solve_equilibrium(labor_demand, labor_supply)
    binding = minimum_wage > equilibrium.p_star + EPSILON
    wage = minimum_wage if binding else equilibrium.p_star
    demanded = max(0.0, labor_demand.q_at(wage))
    supplied = max(0.0, labor_supply.q_at(wage))
    employment = min(demanded, supplied)
    return MinimumWageResult(
        equilibrium=equilibrium,
        minimum_wage=minimum_wage,
        is_binding=binding,
        labor_demanded=demanded,
        labor_supplied=supplied,
        employment=employment,
        unemployment=max(0.0, supplied - demanded),
        wage_bill=wage * employment,
    )


@dataclass(frozen=True, slots=True)
class LoanableFundsScenario:
    savings_quantity_shift: float = 0.0
    investment_quantity_shift: float = 0.0
    government_borrowing: float = 0.0

    def __post_init__(self) -> None:
        values = (
            self.savings_quantity_shift,
            self.investment_quantity_shift,
            self.government_borrowing,
        )
        if not all(math.isfinite(value) for value in values):
            raise PolicyError("Loanable-funds shifts must be finite.")
        if self.government_borrowing < 0:
            raise PolicyError("Government borrowing must be nonnegative.")


@dataclass(frozen=True, slots=True)
class LoanableFundsResult:
    savings_supply: Line
    investment_demand: Line
    baseline_equilibrium: EquilibriumResult
    shifted_equilibrium: EquilibriumResult
    shifted_savings: Line
    shifted_investment_demand: Line
    private_investment_after: float
    interest_rate_change: float
    crowding_out: float


def _horizontal_shift(line: Line, quantity_shift: float) -> Line:
    intercept, slope = line.to_inverse()
    return Line.from_inverse(intercept - slope * quantity_shift, slope)


def analyze_loanable_funds(
    savings_supply: Line,
    investment_demand: Line,
    scenario: LoanableFundsScenario,
) -> LoanableFundsResult:
    """Analyze savings/investment shifts and government-borrowing crowding out."""
    _, savings_slope = savings_supply.to_inverse()
    _, investment_slope = investment_demand.to_inverse()
    if savings_slope <= EPSILON or investment_slope >= -EPSILON:
        raise PolicyError(
            "Savings must slope up and investment demand must slope down."
        )
    baseline = solve_equilibrium(investment_demand, savings_supply)
    shifted_savings = _horizontal_shift(savings_supply, scenario.savings_quantity_shift)
    shifted_investment = _horizontal_shift(
        investment_demand,
        scenario.investment_quantity_shift + scenario.government_borrowing,
    )
    shifted = solve_equilibrium(shifted_investment, shifted_savings)
    private_after = max(0.0, investment_demand.q_at(shifted.p_star))
    return LoanableFundsResult(
        savings_supply=savings_supply,
        investment_demand=investment_demand,
        baseline_equilibrium=baseline,
        shifted_equilibrium=shifted,
        shifted_savings=shifted_savings,
        shifted_investment_demand=shifted_investment,
        private_investment_after=private_after,
        interest_rate_change=shifted.p_star - baseline.p_star,
        crowding_out=max(0.0, baseline.q_star - private_after),
    )


__all__ = [
    "LoanableFundsResult",
    "LoanableFundsScenario",
    "MinimumWageResult",
    "analyze_loanable_funds",
    "analyze_minimum_wage",
]
