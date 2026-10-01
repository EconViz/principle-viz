"""Welfare and deadweight-loss report CLI commands."""

from __future__ import annotations

import argparse
from typing import Any

from principle_viz.cli.commands.shared import add_market_line_args, market_from_args
from principle_viz.cli.output import dump_result
from principle_viz.core.controls import (
    PriceControlScenario,
    PriceControlType,
    evaluate_price_control,
)
from principle_viz.core.equilibrium import solve_equilibrium
from principle_viz.core.line import Line
from principle_viz.policy.subsidy import (
    SubsidyScenario,
    SubsidyTo,
    solve_subsidy_equilibrium,
)
from principle_viz.policy.tax import (
    TaxOn,
    TaxScenario,
    TaxType,
    solve_tax_equilibrium,
)
from principle_viz.welfare.report import build_dwl_report, save_dwl_report_csv
from principle_viz.welfare.surplus import (
    MarketOutcome,
    compare_surplus,
    compute_surplus,
    outcome_from_control,
    outcome_from_equilibrium,
    outcome_from_subsidy,
    outcome_from_tax,
)

COMMANDS = frozenset({"welfare", "report-dwl"})


def _add_policy_args(
    parser: argparse.ArgumentParser, *, include_baseline: bool
) -> None:
    choices = ["tax", "subsidy", "control"]
    parser.add_argument(
        "--policy",
        choices=["baseline", *choices] if include_baseline else choices,
        default="baseline" if include_baseline else None,
        required=not include_baseline,
    )
    parser.add_argument("--tax-type", choices=[item.value for item in TaxType])
    parser.add_argument("--amount", type=float)
    parser.add_argument(
        "--tax-on", choices=[item.value for item in TaxOn], default=TaxOn.PRODUCER.value
    )
    parser.add_argument(
        "--subsidy-to",
        choices=[item.value for item in SubsidyTo],
        default=SubsidyTo.PRODUCER.value,
    )
    parser.add_argument(
        "--control-type", choices=[item.value for item in PriceControlType]
    )
    parser.add_argument("--control-price", type=float)


def register(subparsers: Any) -> None:
    welfare = subparsers.add_parser("welfare", help="Compute welfare metrics")
    add_market_line_args(welfare)
    _add_policy_args(welfare, include_baseline=True)

    report = subparsers.add_parser(
        "report-dwl", help="Generate one-row DWL report for a policy"
    )
    add_market_line_args(report)
    _add_policy_args(report, include_baseline=False)
    report.add_argument("--csv", type=str)


def _policy_outcome(
    args: argparse.Namespace, demand: Line, supply: Line
) -> MarketOutcome:
    if args.policy == "tax":
        if args.tax_type is None or args.amount is None:
            raise SystemExit("--tax-type and --amount are required for policy=tax")
        result = solve_tax_equilibrium(
            demand,
            supply,
            TaxScenario(TaxType(args.tax_type), args.amount, TaxOn(args.tax_on)),
        )
        return outcome_from_tax(result)
    if args.policy == "subsidy":
        if args.amount is None:
            raise SystemExit("--amount is required for policy=subsidy")
        result = solve_subsidy_equilibrium(
            demand,
            supply,
            SubsidyScenario(args.amount, SubsidyTo(args.subsidy_to)),
        )
        return outcome_from_subsidy(result)
    if args.control_type is None or args.control_price is None:
        raise SystemExit(
            "--control-type and --control-price are required for policy=control"
        )
    result = evaluate_price_control(
        demand,
        supply,
        PriceControlScenario(PriceControlType(args.control_type), args.control_price),
    )
    return outcome_from_control(result)


def handle(args: argparse.Namespace) -> bool:
    if args.command not in COMMANDS:
        return False
    demand, supply = market_from_args(args)
    baseline_outcome = outcome_from_equilibrium(solve_equilibrium(demand, supply))
    baseline = compute_surplus(demand, supply, baseline_outcome)
    if args.command == "welfare" and args.policy == "baseline":
        dump_result(baseline, args.output)
        return True

    policy_outcome = _policy_outcome(args, demand, supply)
    if args.command == "welfare":
        dump_result(
            compare_surplus(demand, supply, baseline_outcome, policy_outcome),
            args.output,
        )
        return True

    policy = compute_surplus(
        demand, supply, policy_outcome, baseline_outcome=baseline_outcome
    )
    report = build_dwl_report([("scenario", baseline, policy)])
    if args.csv:
        save_dwl_report_csv(report, args.csv)
    dump_result(report, args.output)
    return True


__all__ = ["COMMANDS", "handle", "register"]
