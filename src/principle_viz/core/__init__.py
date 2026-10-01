"""Core domain and solvers for linear market analysis."""

from principle_viz.core.controls import (
    PriceControlResult,
    PriceControlScenario,
    PriceControlType,
    evaluate_price_control,
)
from principle_viz.core.discrete import (
    DiscreteDemand,
    DiscreteEquilibriumResult,
    DiscreteMarketError,
    DiscreteSupply,
    EquilibriumPriceRule,
    solve_discrete_equilibrium,
)
from principle_viz.core.elasticity import (
    arc_price_elasticity,
    classify_elasticity,
    point_price_elasticity,
)
from principle_viz.core.equilibrium import EquilibriumResult, solve_equilibrium
from principle_viz.core.factor_markets import (
    LoanableFundsResult,
    LoanableFundsScenario,
    MinimumWageResult,
    analyze_loanable_funds,
    analyze_minimum_wage,
)
from principle_viz.core.line import Line
from principle_viz.core.public_goods import (
    IndividualBenefit,
    PublicGoodPoint,
    PublicGoodResult,
    analyze_public_good,
)
from principle_viz.core.revenue import (
    ElasticityRevenueResult,
    RevenuePoint,
    elasticity_revenue_schedule,
)
from principle_viz.core.shifts import (
    ComparativeStaticsResult,
    ShiftedMarket,
    ShiftScenario,
    ShiftSpec,
    apply_shifts,
    comparative_statics,
)

__all__ = [
    "ComparativeStaticsResult",
    "DiscreteDemand",
    "DiscreteEquilibriumResult",
    "DiscreteMarketError",
    "DiscreteSupply",
    "ElasticityRevenueResult",
    "EquilibriumPriceRule",
    "EquilibriumResult",
    "IndividualBenefit",
    "Line",
    "LoanableFundsResult",
    "LoanableFundsScenario",
    "MinimumWageResult",
    "PriceControlResult",
    "PriceControlScenario",
    "PriceControlType",
    "PublicGoodPoint",
    "PublicGoodResult",
    "RevenuePoint",
    "ShiftScenario",
    "ShiftSpec",
    "ShiftedMarket",
    "analyze_loanable_funds",
    "analyze_minimum_wage",
    "analyze_public_good",
    "apply_shifts",
    "arc_price_elasticity",
    "classify_elasticity",
    "comparative_statics",
    "elasticity_revenue_schedule",
    "evaluate_price_control",
    "point_price_elasticity",
    "solve_discrete_equilibrium",
    "solve_equilibrium",
]
