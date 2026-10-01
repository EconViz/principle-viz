"""Shared parser helpers for CLI commands."""

from __future__ import annotations

import argparse

from principle_viz.core.line import Line


def add_market_line_args(target: argparse.ArgumentParser) -> None:
    target.add_argument("--demand-intercept", type=float, required=True)
    target.add_argument("--demand-slope", type=float, required=True)
    target.add_argument("--supply-intercept", type=float, required=True)
    target.add_argument("--supply-slope", type=float, required=True)
    target.add_argument("--output", type=str)


def market_from_args(args: argparse.Namespace) -> tuple[Line, Line]:
    return (
        Line.from_inverse(args.demand_intercept, args.demand_slope),
        Line.from_inverse(args.supply_intercept, args.supply_slope),
    )


__all__ = ["add_market_line_args", "market_from_args"]
