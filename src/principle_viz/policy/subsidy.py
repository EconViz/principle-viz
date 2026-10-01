"""Per-unit subsidy models, solvers, and comparative analysis."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum

from principle_viz.core.equilibrium import EquilibriumResult, solve_equilibrium
from principle_viz.core.line import Line
from principle_viz.exceptions import PolicyError


class SubsidyTo(str, Enum):
    CONSUMER = "consumer"
    PRODUCER = "producer"


@dataclass(frozen=True, slots=True)
class SubsidyScenario:
    amount: float
    subsidy_to: SubsidyTo = SubsidyTo.PRODUCER

    def __post_init__(self) -> None:
        if not math.isfinite(self.amount) or self.amount < 0:
            raise PolicyError("Subsidy amount must be finite and nonnegative.")


@dataclass(frozen=True, slots=True)
class SubsidyEquilibriumResult:
    q_star: float
    consumer_price: float
    producer_price: float
    subsidy_wedge: float
    government_expenditure: float


@dataclass(frozen=True, slots=True)
class SubsidyComparisonResult:
    baseline_equilibrium: EquilibriumResult
    post_subsidy: SubsidyEquilibriumResult
    delta_q: float
    delta_p_consumer: float
    delta_p_producer: float


def solve_subsidy_equilibrium(
    demand: Line, supply: Line, scenario: SubsidyScenario
) -> SubsidyEquilibriumResult:
    subsidy = float(scenario.amount)
    if scenario.subsidy_to == SubsidyTo.PRODUCER:
        adjusted_supply = supply.shifted(delta_intercept=-subsidy)
        equilibrium = solve_equilibrium(demand, adjusted_supply)
        consumer_price = demand.p_at(equilibrium.q_star)
        producer_price = consumer_price + subsidy
    else:
        adjusted_demand = demand.shifted(delta_intercept=subsidy)
        equilibrium = solve_equilibrium(adjusted_demand, supply)
        producer_price = supply.p_at(equilibrium.q_star)
        consumer_price = producer_price - subsidy
    return SubsidyEquilibriumResult(
        q_star=equilibrium.q_star,
        consumer_price=consumer_price,
        producer_price=producer_price,
        subsidy_wedge=producer_price - consumer_price,
        government_expenditure=subsidy * equilibrium.q_star,
    )


def compare_subsidy_scenario(
    demand: Line, supply: Line, scenario: SubsidyScenario
) -> SubsidyComparisonResult:
    baseline = solve_equilibrium(demand, supply)
    result = solve_subsidy_equilibrium(demand, supply, scenario)
    return SubsidyComparisonResult(
        baseline_equilibrium=baseline,
        post_subsidy=result,
        delta_q=result.q_star - baseline.q_star,
        delta_p_consumer=result.consumer_price - baseline.p_star,
        delta_p_producer=result.producer_price - baseline.p_star,
    )
