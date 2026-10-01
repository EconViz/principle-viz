"""Labor and loanable-funds CLI commands."""

from __future__ import annotations

import argparse
from typing import Any

from principle_viz.cli.output import dump_result
from principle_viz.core.factor_markets import (
    LoanableFundsScenario,
    analyze_loanable_funds,
    analyze_minimum_wage,
)
from principle_viz.core.line import Line

COMMANDS = frozenset({"minimum-wage", "loanable-funds"})


def register(subparsers: Any) -> None:
    labor = subparsers.add_parser(
        "minimum-wage", help="Analyze a labor-market wage floor"
    )
    labor.add_argument("--labor-demand-intercept", type=float, required=True)
    labor.add_argument("--labor-demand-slope", type=float, required=True)
    labor.add_argument("--labor-supply-intercept", type=float, required=True)
    labor.add_argument("--labor-supply-slope", type=float, required=True)
    labor.add_argument("--minimum-wage", type=float, required=True)
    labor.add_argument("--output", type=str)

    funds = subparsers.add_parser(
        "loanable-funds", help="Analyze savings, investment, and crowding out"
    )
    funds.add_argument("--savings-intercept", type=float, required=True)
    funds.add_argument("--savings-slope", type=float, required=True)
    funds.add_argument("--investment-intercept", type=float, required=True)
    funds.add_argument("--investment-slope", type=float, required=True)
    funds.add_argument("--savings-shift", type=float, default=0.0)
    funds.add_argument("--investment-shift", type=float, default=0.0)
    funds.add_argument("--government-borrowing", type=float, default=0.0)
    funds.add_argument("--output", type=str)


def handle(args: argparse.Namespace) -> bool:
    if args.command not in COMMANDS:
        return False
    if args.command == "minimum-wage":
        result = analyze_minimum_wage(
            Line.from_inverse(args.labor_demand_intercept, args.labor_demand_slope),
            Line.from_inverse(args.labor_supply_intercept, args.labor_supply_slope),
            args.minimum_wage,
        )
    else:
        result = analyze_loanable_funds(
            Line.from_inverse(args.savings_intercept, args.savings_slope),
            Line.from_inverse(args.investment_intercept, args.investment_slope),
            LoanableFundsScenario(
                args.savings_shift,
                args.investment_shift,
                args.government_borrowing,
            ),
        )
    dump_result(result, args.output)
    return True


__all__ = ["COMMANDS", "handle", "register"]
