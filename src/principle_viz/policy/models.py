"""Tax policy models and typed result structures."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from principle_viz.core.equilibrium import EquilibriumResult


class TaxType(str, Enum):
    """Supported tax definitions."""

    FIXED_TAX = "fixed"
    PER_UNIT_TAX = "per_unit"
    AD_VALOREM_TAX = "ad_valorem"


class TaxOn(str, Enum):
    """Legal incidence side."""

    CONSUMER = "consumer"
    PRODUCER = "producer"


class AnchorMode(str, Enum):
    """Optional comparison anchor strategy."""

    NONE = "none"
    BASELINE_EQUILIBRIUM = "baseline_equilibrium"


@dataclass(frozen=True)
class TaxScenario:
    """Tax scenario configuration."""

    tax_type: TaxType
    amount: float
    tax_on: TaxOn = TaxOn.PRODUCER
    anchor_mode: AnchorMode = AnchorMode.NONE


@dataclass(frozen=True)
class TaxEquilibriumResult:
    """Solved equilibrium under tax."""

    q_star: float
    consumer_price: float
    producer_price: float
    tax_wedge: float
    tax_revenue: float


@dataclass(frozen=True)
class TaxComparisonResult:
    """Baseline vs post-tax comparison output."""

    baseline_equilibrium: EquilibriumResult
    post_tax: TaxEquilibriumResult
    delta_q: float
    delta_p_consumer: float
    delta_p_producer: float
    direction_q: str
    direction_p_consumer: str
    direction_p_producer: str
