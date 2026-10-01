"""Tax, subsidy, trade, control, and market-failure CLI commands."""

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
from principle_viz.policy.common_resources import analyze_common_resource
from principle_viz.policy.externality import ExternalityScenario, analyze_externality
from principle_viz.policy.subsidy import (
    SubsidyScenario,
    SubsidyTo,
    compare_subsidy_scenario,
)
from principle_viz.policy.tax import TaxOn, TaxScenario, TaxType, compare_tax_scenario
from principle_viz.policy.trade import (
    QuotaRentRecipient,
    TradeScenario,
    analyze_trade,
)

COMMANDS = frozenset(
    {"tax", "subsidy", "trade", "externality", "common-resource", "controls"}
)


def register(subparsers: Any) -> None:
    tax = subparsers.add_parser("tax", help="Solve tax equilibrium")
    add_market_line_args(tax)
    tax.add_argument(
        "--tax-type", choices=[item.value for item in TaxType], required=True
    )
    tax.add_argument("--amount", type=float, required=True)
    tax.add_argument(
        "--tax-on", choices=[item.value for item in TaxOn], default=TaxOn.PRODUCER.value
    )

    subsidy = subparsers.add_parser(
        "subsidy", help="Solve per-unit subsidy equilibrium"
    )
    add_market_line_args(subsidy)
    subsidy.add_argument("--amount", type=float, required=True)
    subsidy.add_argument(
        "--subsidy-to",
        choices=[item.value for item in SubsidyTo],
        default=SubsidyTo.PRODUCER.value,
    )

    trade = subparsers.add_parser(
        "trade", help="Analyze world price, tariff, or import quota"
    )
    add_market_line_args(trade)
    trade.add_argument("--world-price", type=float, required=True)
    trade.add_argument("--tariff", type=float, default=0.0)
    trade.add_argument("--import-quota", type=float)
    trade.add_argument(
        "--quota-rent-recipient",
        choices=[item.value for item in QuotaRentRecipient],
        default=QuotaRentRecipient.DOMESTIC.value,
    )

    externality = subparsers.add_parser(
        "externality", help="Compare private and socially efficient outcomes"
    )
    add_market_line_args(externality)
    externality.add_argument("--external-cost", type=float, default=0.0)
    externality.add_argument("--external-benefit", type=float, default=0.0)

    common = subparsers.add_parser(
        "common-resource", help="Analyze open-access common-resource overuse"
    )
    add_market_line_args(common)
    common.add_argument("--congestion-cost", type=float, required=True)

    controls = subparsers.add_parser("controls", help="Evaluate price control")
    add_market_line_args(controls)
    controls.add_argument(
        "--control-type",
        choices=[item.value for item in PriceControlType],
        required=True,
    )
    controls.add_argument("--control-price", type=float, required=True)


def handle(args: argparse.Namespace) -> bool:
    if args.command not in COMMANDS:
        return False
    demand, supply = market_from_args(args)
    if args.command == "tax":
        result = compare_tax_scenario(
            demand,
            supply,
            TaxScenario(TaxType(args.tax_type), args.amount, TaxOn(args.tax_on)),
        )
    elif args.command == "subsidy":
        result = compare_subsidy_scenario(
            demand,
            supply,
            SubsidyScenario(args.amount, SubsidyTo(args.subsidy_to)),
        )
    elif args.command == "trade":
        result = analyze_trade(
            demand,
            supply,
            TradeScenario(
                args.world_price,
                args.tariff,
                args.import_quota,
                QuotaRentRecipient(args.quota_rent_recipient),
            ),
        )
    elif args.command == "externality":
        result = analyze_externality(
            demand,
            supply,
            ExternalityScenario(args.external_cost, args.external_benefit),
        )
    elif args.command == "common-resource":
        result = analyze_common_resource(
            demand, supply, marginal_congestion_cost=args.congestion_cost
        )
    else:
        result = evaluate_price_control(
            demand,
            supply,
            PriceControlScenario(
                PriceControlType(args.control_type), args.control_price
            ),
        )
    dump_result(result, args.output)
    return True


__all__ = ["COMMANDS", "handle", "register"]
