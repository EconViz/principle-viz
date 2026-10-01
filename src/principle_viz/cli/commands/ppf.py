"""Production-possibilities CLI command."""

from __future__ import annotations

import argparse
from typing import Any

from principle_viz.cli.output import dump_result
from principle_viz.core.ppf import (
    PPFGrowthScenario,
    ProductionPossibilitiesFrontier,
    analyze_ppf,
    analyze_ppf_growth,
)

COMMANDS = frozenset({"ppf"})


def register(subparsers: Any) -> None:
    parser = subparsers.add_parser(
        "ppf", help="Analyze a production-possibilities frontier"
    )
    parser.add_argument("--x-intercept", type=float, required=True)
    parser.add_argument("--y-intercept", type=float, required=True)
    parser.add_argument("--curvature", type=float, default=1.0)
    parser.add_argument("--x-good", type=str, default="Good X")
    parser.add_argument("--y-good", type=str, default="Good Y")
    parser.add_argument("--x-growth", type=float, default=0.0)
    parser.add_argument("--y-growth", type=float, default=0.0)
    parser.add_argument("--samples", type=int, default=101)
    parser.add_argument("--output", type=str)


def handle(args: argparse.Namespace) -> bool:
    if args.command not in COMMANDS:
        return False
    frontier = ProductionPossibilitiesFrontier(
        args.x_intercept,
        args.y_intercept,
        args.curvature,
        args.x_good,
        args.y_good,
    )
    result = (
        analyze_ppf_growth(
            frontier,
            PPFGrowthScenario(args.x_growth, args.y_growth),
            samples=args.samples,
        )
        if args.x_growth or args.y_growth
        else analyze_ppf(frontier, samples=args.samples)
    )
    dump_result(result, args.output)
    return True


__all__ = ["COMMANDS", "handle", "register"]
