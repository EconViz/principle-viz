"""Welfare and surplus computations."""

from __future__ import annotations

from dataclasses import dataclass

from principle_viz.core.controls import PriceControlResult
from principle_viz.core.equilibrium import EquilibriumResult
from principle_viz.core.line import EPSILON, Line
from principle_viz.policy.subsidy import SubsidyEquilibriumResult
from principle_viz.policy.tax import TaxEquilibriumResult


@dataclass(frozen=True)
class MarketOutcome:
    """Market outcome with quantity and two-side prices."""

    quantity: float
    consumer_price: float
    producer_price: float
    label: str = ""


@dataclass(frozen=True)
class SurplusPolygons:
    """Polygon coordinates for renderer consumption."""

    consumer_surplus: tuple[tuple[float, float], ...]
    producer_surplus: tuple[tuple[float, float], ...]
    tax_revenue: tuple[tuple[float, float], ...]
    lost_surplus: tuple[tuple[float, float], ...]


@dataclass(frozen=True)
class SurplusResult:
    """Computed welfare decomposition."""

    quantity: float
    consumer_price: float
    producer_price: float
    consumer_surplus: float
    producer_surplus: float
    tax_revenue: float
    total_surplus: float
    deadweight_loss: float
    polygons: SurplusPolygons


@dataclass(frozen=True)
class SurplusDeltaResult:
    """Delta of baseline and policy welfare outcomes."""

    baseline: SurplusResult
    policy: SurplusResult
    delta_consumer_surplus: float
    delta_producer_surplus: float
    delta_tax_revenue: float
    delta_total_surplus: float
    deadweight_loss: float


def outcome_from_equilibrium(
    eq: EquilibriumResult, label: str = "baseline"
) -> MarketOutcome:
    """Create market outcome from single-price equilibrium."""
    return MarketOutcome(
        quantity=eq.q_star,
        consumer_price=eq.p_star,
        producer_price=eq.p_star,
        label=label,
    )


def outcome_from_tax(tax_eq: TaxEquilibriumResult, label: str = "tax") -> MarketOutcome:
    """Create market outcome from tax equilibrium."""
    return MarketOutcome(
        quantity=tax_eq.q_star,
        consumer_price=tax_eq.consumer_price,
        producer_price=tax_eq.producer_price,
        label=label,
    )


def outcome_from_subsidy(
    subsidy_eq: SubsidyEquilibriumResult, label: str = "subsidy"
) -> MarketOutcome:
    """Create an outcome whose negative government balance is the subsidy cost."""
    return MarketOutcome(
        quantity=subsidy_eq.q_star,
        consumer_price=subsidy_eq.consumer_price,
        producer_price=subsidy_eq.producer_price,
        label=label,
    )


def outcome_from_control(
    control: PriceControlResult, label: str = "control"
) -> MarketOutcome:
    """Create market outcome from price control result."""
    return MarketOutcome(
        quantity=control.traded_quantity,
        consumer_price=control.consumer_price,
        producer_price=control.producer_price,
        label=label,
    )


def _integral_price_curve(line: Line, quantity: float) -> float:
    intercept, slope = line.to_inverse()
    q = float(quantity)
    return intercept * q + 0.5 * slope * q * q


def _build_lost_polygon(
    demand: Line, supply: Line, q0: float, q1: float
) -> tuple[tuple[float, float], ...]:
    if abs(q0 - q1) <= EPSILON:
        return ()
    q_low = min(q0, q1)
    q_high = max(q0, q1)
    return (
        (q_low, supply.p_at(q_low)),
        (q_low, demand.p_at(q_low)),
        (q_high, demand.p_at(q_high)),
        (q_high, supply.p_at(q_high)),
    )


def compute_surplus(
    demand: Line,
    supply: Line,
    outcome: MarketOutcome,
    baseline_outcome: MarketOutcome | None = None,
) -> SurplusResult:
    """Compute CS, PS, tax revenue, TS, and DWL for one market outcome."""
    q = max(0.0, float(outcome.quantity))
    pc = float(outcome.consumer_price)
    pp = float(outcome.producer_price)

    demand_area = _integral_price_curve(demand, q)
    supply_area = _integral_price_curve(supply, q)

    consumer_surplus = demand_area - pc * q
    producer_surplus = pp * q - supply_area
    tax_revenue = (pc - pp) * q
    total_surplus = consumer_surplus + producer_surplus + tax_revenue

    if baseline_outcome is None:
        deadweight_loss = 0.0
    else:
        baseline_total = (
            _integral_price_curve(demand, baseline_outcome.quantity)
            - baseline_outcome.consumer_price * baseline_outcome.quantity
            + baseline_outcome.producer_price * baseline_outcome.quantity
            - _integral_price_curve(supply, baseline_outcome.quantity)
            + (baseline_outcome.consumer_price - baseline_outcome.producer_price)
            * baseline_outcome.quantity
        )
        deadweight_loss = max(0.0, baseline_total - total_surplus)

    if q <= EPSILON:
        cs_poly: tuple[tuple[float, float], ...] = ()
        ps_poly: tuple[tuple[float, float], ...] = ()
        tax_poly: tuple[tuple[float, float], ...] = ()
    else:
        cs_poly = (
            (0.0, pc),
            (0.0, demand.p_at(0.0)),
            (q, demand.p_at(q)),
            (q, pc),
        )
        ps_poly = (
            (0.0, supply.p_at(0.0)),
            (0.0, pp),
            (q, pp),
            (q, supply.p_at(q)),
        )
        if pc - pp > EPSILON:
            tax_poly = (
                (0.0, pp),
                (0.0, pc),
                (q, pc),
                (q, pp),
            )
        else:
            tax_poly = ()

    lost_poly = ()
    if baseline_outcome is not None:
        lost_poly = _build_lost_polygon(demand, supply, baseline_outcome.quantity, q)

    return SurplusResult(
        quantity=q,
        consumer_price=pc,
        producer_price=pp,
        consumer_surplus=consumer_surplus,
        producer_surplus=producer_surplus,
        tax_revenue=tax_revenue,
        total_surplus=total_surplus,
        deadweight_loss=deadweight_loss,
        polygons=SurplusPolygons(
            consumer_surplus=cs_poly,
            producer_surplus=ps_poly,
            tax_revenue=tax_poly,
            lost_surplus=lost_poly,
        ),
    )


def compare_surplus(
    demand: Line,
    supply: Line,
    baseline_outcome: MarketOutcome,
    policy_outcome: MarketOutcome,
) -> SurplusDeltaResult:
    """Compare baseline and policy surplus decomposition."""
    baseline = compute_surplus(demand, supply, baseline_outcome)
    policy = compute_surplus(
        demand, supply, policy_outcome, baseline_outcome=baseline_outcome
    )

    return SurplusDeltaResult(
        baseline=baseline,
        policy=policy,
        delta_consumer_surplus=policy.consumer_surplus - baseline.consumer_surplus,
        delta_producer_surplus=policy.producer_surplus - baseline.producer_surplus,
        delta_tax_revenue=policy.tax_revenue - baseline.tax_revenue,
        delta_total_surplus=policy.total_surplus - baseline.total_surplus,
        deadweight_loss=policy.deadweight_loss,
    )
