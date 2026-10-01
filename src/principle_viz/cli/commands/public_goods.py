"""Public-good CLI command."""

from __future__ import annotations

import argparse
from typing import Any

from principle_viz.cli.output import dump_result
from principle_viz.core.line import Line
from principle_viz.core.public_goods import IndividualBenefit, analyze_public_good

COMMANDS = frozenset({"public-good"})


def register(subparsers: Any) -> None:
    parser = subparsers.add_parser(
        "public-good", help="Vertically sum marginal benefits for a public good"
    )
    parser.add_argument("--benefit-intercepts", type=float, nargs="+", required=True)
    parser.add_argument("--benefit-slopes", type=float, nargs="+", required=True)
    parser.add_argument("--cost-intercept", type=float, required=True)
    parser.add_argument("--cost-slope", type=float, default=0.0)
    parser.add_argument("--samples", type=int, default=101)
    parser.add_argument("--output", type=str)


def handle(args: argparse.Namespace) -> bool:
    if args.command not in COMMANDS:
        return False
    if len(args.benefit_intercepts) != len(args.benefit_slopes):
        raise SystemExit("Benefit intercepts and slopes must have equal lengths")
    individuals = tuple(
        IndividualBenefit(f"person_{index + 1}", Line.from_inverse(intercept, slope))
        for index, (intercept, slope) in enumerate(
            zip(args.benefit_intercepts, args.benefit_slopes, strict=True)
        )
    )
    result = analyze_public_good(
        individuals,
        Line.from_inverse(args.cost_intercept, args.cost_slope),
        samples=args.samples,
    )
    dump_result(result, args.output)
    return True


__all__ = ["COMMANDS", "handle", "register"]
