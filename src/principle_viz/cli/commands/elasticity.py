"""Elasticity and total-revenue CLI commands."""

from __future__ import annotations

import argparse
from typing import Any

from principle_viz.cli.output import dump_result
from principle_viz.core.elasticity import (
    arc_price_elasticity,
    classify_elasticity,
    point_price_elasticity,
)
from principle_viz.core.line import Line
from principle_viz.core.revenue import elasticity_revenue_schedule

COMMANDS = frozenset({"elasticity", "revenue"})


def register(subparsers: Any) -> None:
    elasticity = subparsers.add_parser(
        "elasticity", help="Compute point and optional arc elasticity"
    )
    elasticity.add_argument("--intercept", type=float, required=True)
    elasticity.add_argument("--slope", type=float, required=True)
    elasticity.add_argument("--quantity", type=float, required=True)
    elasticity.add_argument("--q1", type=float)
    elasticity.add_argument("--p1", type=float)
    elasticity.add_argument("--output", type=str)

    revenue = subparsers.add_parser(
        "revenue", help="Generate a demand elasticity and total-revenue schedule"
    )
    revenue.add_argument("--demand-intercept", type=float, required=True)
    revenue.add_argument("--demand-slope", type=float, required=True)
    revenue.add_argument("--samples", type=int, default=101)
    revenue.add_argument("--output", type=str)


def handle(args: argparse.Namespace) -> bool:
    if args.command not in COMMANDS:
        return False
    demand = Line.from_inverse(
        args.intercept if args.command == "elasticity" else args.demand_intercept,
        args.slope if args.command == "elasticity" else args.demand_slope,
    )
    if args.command == "revenue":
        dump_result(
            elasticity_revenue_schedule(demand, samples=args.samples), args.output
        )
        return True

    point = point_price_elasticity(demand, args.quantity)
    payload = {
        "point_elasticity": point,
        "classification": classify_elasticity(point),
    }
    if args.q1 is not None and args.p1 is not None:
        arc = arc_price_elasticity(
            args.quantity, demand.p_at(args.quantity), args.q1, args.p1
        )
        payload["arc_elasticity"] = arc
        payload["arc_classification"] = classify_elasticity(arc)
    dump_result(payload, args.output)
    return True


__all__ = ["COMMANDS", "handle", "register"]
