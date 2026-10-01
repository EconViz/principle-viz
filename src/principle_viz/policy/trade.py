"""Small-country international-trade analysis for linear markets."""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from enum import Enum

from principle_viz.core.equilibrium import solve_equilibrium
from principle_viz.core.line import EPSILON, Line
from principle_viz.exceptions import PolicyError


class TradeDirection(str, Enum):
    IMPORT = "import"
    EXPORT = "export"
    AUTARKY = "autarky"


class QuotaRentRecipient(str, Enum):
    DOMESTIC = "domestic"
    GOVERNMENT = "government"
    FOREIGN = "foreign"


@dataclass(frozen=True, slots=True)
class TradeScenario:
    world_price: float
    tariff: float = 0.0
    import_quota: float | None = None
    quota_rent_recipient: QuotaRentRecipient = QuotaRentRecipient.DOMESTIC

    def __post_init__(self) -> None:
        values = (self.world_price, self.tariff)
        if not all(math.isfinite(value) for value in values):
            raise PolicyError("Trade prices and policy amounts must be finite.")
        if self.world_price < 0 or self.tariff < 0:
            raise PolicyError("World price and tariff must be nonnegative.")
        if self.import_quota is not None and (
            not math.isfinite(self.import_quota) or self.import_quota < 0
        ):
            raise PolicyError("Import quota must be finite and nonnegative.")
        if self.tariff > 0 and self.import_quota is not None:
            raise PolicyError("Analyze a tariff or an import quota, not both at once.")


@dataclass(frozen=True, slots=True)
class TradeOutcome:
    domestic_price: float
    quantity_demanded: float
    quantity_supplied: float
    imports: float
    exports: float
    direction: TradeDirection
    consumer_surplus: float
    producer_surplus: float
    government_revenue: float
    quota_rent: float
    national_quota_rent: float
    total_surplus: float
    gains_from_trade: float = 0.0
    is_policy_binding: bool = False


@dataclass(frozen=True, slots=True)
class TradeComparisonResult:
    autarky: TradeOutcome
    free_trade: TradeOutcome
    policy: TradeOutcome
    deadweight_loss: float


def _integral(line: Line, quantity: float) -> float:
    intercept, slope = line.to_inverse()
    return intercept * quantity + 0.5 * slope * quantity * quantity


def _quantities_at_price(
    demand: Line, supply: Line, price: float
) -> tuple[float, float]:
    return max(0.0, demand.q_at(price)), max(0.0, supply.q_at(price))


def _direction(qd: float, qs: float) -> TradeDirection:
    if qd - qs > EPSILON:
        return TradeDirection.IMPORT
    if qs - qd > EPSILON:
        return TradeDirection.EXPORT
    return TradeDirection.AUTARKY


def _make_outcome(
    demand: Line,
    supply: Line,
    *,
    price: float,
    government_revenue: float = 0.0,
    quota_rent: float = 0.0,
    national_quota_rent: float = 0.0,
    is_policy_binding: bool = False,
) -> TradeOutcome:
    qd, qs = _quantities_at_price(demand, supply, price)
    imports = max(0.0, qd - qs)
    exports = max(0.0, qs - qd)
    consumer_surplus = _integral(demand, qd) - price * qd
    producer_surplus = price * qs - _integral(supply, qs)
    total = (
        consumer_surplus + producer_surplus + government_revenue + national_quota_rent
    )
    return TradeOutcome(
        domestic_price=price,
        quantity_demanded=qd,
        quantity_supplied=qs,
        imports=imports,
        exports=exports,
        direction=_direction(qd, qs),
        consumer_surplus=consumer_surplus,
        producer_surplus=producer_surplus,
        government_revenue=government_revenue,
        quota_rent=quota_rent,
        national_quota_rent=national_quota_rent,
        total_surplus=total,
        is_policy_binding=is_policy_binding,
    )


def analyze_trade(
    demand: Line, supply: Line, scenario: TradeScenario
) -> TradeComparisonResult:
    """Compare autarky, free trade, and a tariff-or-quota policy."""
    demand_intercept, demand_slope = demand.to_inverse()
    _, supply_slope = supply.to_inverse()
    if demand_intercept <= 0 or demand_slope >= -EPSILON or supply_slope <= EPSILON:
        raise PolicyError("Trade analysis requires downward demand and upward supply.")

    equilibrium = solve_equilibrium(demand, supply)
    autarky = _make_outcome(demand, supply, price=equilibrium.p_star)
    free_trade = _make_outcome(demand, supply, price=scenario.world_price)
    free_trade = replace(
        free_trade,
        gains_from_trade=free_trade.total_surplus - autarky.total_surplus,
    )

    policy_price = scenario.world_price
    government_revenue = 0.0
    quota_rent = 0.0
    national_quota_rent = 0.0
    binding = False

    if free_trade.direction == TradeDirection.IMPORT:
        if scenario.tariff > EPSILON:
            policy_price = min(
                scenario.world_price + scenario.tariff,
                equilibrium.p_star,
            )
            binding = policy_price > scenario.world_price + EPSILON
            qd, qs = _quantities_at_price(demand, supply, policy_price)
            imports = max(0.0, qd - qs)
            government_revenue = (policy_price - scenario.world_price) * imports
        elif (
            scenario.import_quota is not None
            and scenario.import_quota < free_trade.imports - EPSILON
        ):
            share_removed = (
                free_trade.imports - scenario.import_quota
            ) / free_trade.imports
            policy_price = scenario.world_price + share_removed * (
                equilibrium.p_star - scenario.world_price
            )
            binding = True
            quota_rent = (policy_price - scenario.world_price) * scenario.import_quota
            if scenario.quota_rent_recipient != QuotaRentRecipient.FOREIGN:
                national_quota_rent = quota_rent
            if scenario.quota_rent_recipient == QuotaRentRecipient.GOVERNMENT:
                government_revenue = quota_rent
                national_quota_rent = 0.0

    policy = _make_outcome(
        demand,
        supply,
        price=policy_price,
        government_revenue=government_revenue,
        quota_rent=quota_rent,
        national_quota_rent=national_quota_rent,
        is_policy_binding=binding,
    )
    policy = replace(
        policy,
        gains_from_trade=policy.total_surplus - autarky.total_surplus,
    )
    return TradeComparisonResult(
        autarky=autarky,
        free_trade=free_trade,
        policy=policy,
        deadweight_loss=max(0.0, free_trade.total_surplus - policy.total_surplus),
    )


__all__ = [
    "QuotaRentRecipient",
    "TradeComparisonResult",
    "TradeDirection",
    "TradeOutcome",
    "TradeScenario",
    "analyze_trade",
]
