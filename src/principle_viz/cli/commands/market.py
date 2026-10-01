"""Competitive-market CLI commands."""

from __future__ import annotations

import argparse
from typing import Any

from principle_viz.cli.commands.shared import add_market_line_args, market_from_args
from principle_viz.cli.output import dump_result
from principle_viz.core.discrete import (
    DiscreteDemand,
    DiscreteSupply,
    EquilibriumPriceRule,
    solve_discrete_equilibrium,
)
from principle_viz.core.equilibrium import solve_equilibrium
from principle_viz.core.shifts import ShiftScenario, ShiftSpec, comparative_statics

COMMANDS = frozenset({"equilibrium", "discrete", "shift"})


def register(subparsers: Any) -> None:
    equilibrium = subparsers.add_parser(
        "equilibrium", help="Solve linear market equilibrium"
    )
    add_market_line_args(equilibrium)

    discrete = subparsers.add_parser("discrete", help="Solve a discrete unit market")
    discrete.add_argument("--demand-values", type=float, nargs="+", required=True)
    discrete.add_argument("--supply-values", type=float, nargs="+", required=True)
    discrete.add_argument(
        "--price-rule",
        choices=[rule.value for rule in EquilibriumPriceRule],
        default=EquilibriumPriceRule.MIDPOINT.value,
    )
    discrete.add_argument("--output", type=str)

    shift = subparsers.add_parser(
        "shift", help="Solve comparative statics with shifted lines"
    )
    add_market_line_args(shift)
    shift.add_argument("--demand-delta-intercept", type=float, default=0.0)
    shift.add_argument("--demand-delta-slope", type=float, default=0.0)
    shift.add_argument("--supply-delta-intercept", type=float, default=0.0)
    shift.add_argument("--supply-delta-slope", type=float, default=0.0)


def handle(args: argparse.Namespace) -> bool:
    if args.command not in COMMANDS:
        return False
    if args.command == "discrete":
        result = solve_discrete_equilibrium(
            DiscreteDemand(tuple(args.demand_values)),
            DiscreteSupply(tuple(args.supply_values)),
            price_rule=EquilibriumPriceRule(args.price_rule),
        )
    else:
        demand, supply = market_from_args(args)
        if args.command == "equilibrium":
            result = solve_equilibrium(demand, supply)
        else:
            result = comparative_statics(
                demand,
                supply,
                ShiftScenario(
                    demand_shift=ShiftSpec(
                        args.demand_delta_intercept, args.demand_delta_slope
                    ),
                    supply_shift=ShiftSpec(
                        args.supply_delta_intercept, args.supply_delta_slope
                    ),
                ),
            )
    dump_result(result, args.output)
    return True


__all__ = ["COMMANDS", "handle", "register"]
