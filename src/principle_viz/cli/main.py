"""CLI entrypoint for principle_viz."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, is_dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from principle_viz.core.controls import (
    PriceControlScenario,
    PriceControlType,
    evaluate_price_control,
)
from principle_viz.core.discrete import (
    DiscreteDemand,
    DiscreteSupply,
    EquilibriumPriceRule,
    solve_discrete_equilibrium,
)
from principle_viz.core.elasticity import (
    arc_price_elasticity,
    classify_elasticity,
    point_price_elasticity,
)
from principle_viz.core.equilibrium import solve_equilibrium
from principle_viz.core.line import Line
from principle_viz.core.shifts import ShiftScenario, ShiftSpec, comparative_statics
from principle_viz.policy.tax import (
    TaxOn,
    TaxScenario,
    TaxType,
    compare_tax_scenario,
    solve_tax_equilibrium,
)
from principle_viz.welfare.report import (
    build_dwl_report,
    save_dwl_report_csv,
    save_dwl_report_json,
)
from principle_viz.welfare.surplus import (
    compare_surplus,
    compute_surplus,
    outcome_from_control,
    outcome_from_equilibrium,
    outcome_from_tax,
)


def _to_jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return {k: _to_jsonable(v) for k, v in asdict(value).items()}
    if isinstance(value, dict):
        return {k: _to_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(v) for v in value]
    if isinstance(value, Enum):
        return value.value
    return value


def _dump_result(payload: Any, output: str | None) -> None:
    text = json.dumps(_to_jsonable(payload), indent=2)
    if output:
        target = Path(output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    print(text)


def _line_from_args(args: argparse.Namespace, prefix: str) -> Line:
    intercept = getattr(args, f"{prefix}_intercept")
    slope = getattr(args, f"{prefix}_slope")
    return Line.from_inverse(intercept=intercept, slope=slope)


def build_parser() -> argparse.ArgumentParser:
    """Build CLI parser."""
    parser = argparse.ArgumentParser(prog="principle-viz")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_market_line_args(target: argparse.ArgumentParser) -> None:
        target.add_argument("--demand-intercept", type=float, required=True)
        target.add_argument("--demand-slope", type=float, required=True)
        target.add_argument("--supply-intercept", type=float, required=True)
        target.add_argument("--supply-slope", type=float, required=True)
        target.add_argument("--output", type=str)

    eq = sub.add_parser("equilibrium", help="Solve linear market equilibrium")
    add_market_line_args(eq)

    discrete = sub.add_parser("discrete", help="Solve a discrete unit market")
    discrete.add_argument("--demand-values", type=float, nargs="+", required=True)
    discrete.add_argument("--supply-values", type=float, nargs="+", required=True)
    discrete.add_argument(
        "--price-rule",
        choices=[rule.value for rule in EquilibriumPriceRule],
        default=EquilibriumPriceRule.MIDPOINT.value,
    )
    discrete.add_argument("--output", type=str)

    sh = sub.add_parser("shift", help="Solve comparative statics with shifted lines")
    add_market_line_args(sh)
    sh.add_argument("--demand-delta-intercept", type=float, default=0.0)
    sh.add_argument("--demand-delta-slope", type=float, default=0.0)
    sh.add_argument("--supply-delta-intercept", type=float, default=0.0)
    sh.add_argument("--supply-delta-slope", type=float, default=0.0)

    tax = sub.add_parser("tax", help="Solve tax equilibrium")
    add_market_line_args(tax)
    tax.add_argument("--tax-type", choices=[t.value for t in TaxType], required=True)
    tax.add_argument("--amount", type=float, required=True)
    tax.add_argument(
        "--tax-on", choices=[s.value for s in TaxOn], default=TaxOn.PRODUCER.value
    )

    ctl = sub.add_parser("controls", help="Evaluate price control")
    add_market_line_args(ctl)
    ctl.add_argument(
        "--control-type", choices=[c.value for c in PriceControlType], required=True
    )
    ctl.add_argument("--control-price", type=float, required=True)

    wf = sub.add_parser("welfare", help="Compute welfare metrics")
    add_market_line_args(wf)
    wf.add_argument(
        "--policy", choices=["baseline", "tax", "control"], default="baseline"
    )
    wf.add_argument("--tax-type", choices=[t.value for t in TaxType])
    wf.add_argument("--amount", type=float)
    wf.add_argument(
        "--tax-on", choices=[s.value for s in TaxOn], default=TaxOn.PRODUCER.value
    )
    wf.add_argument("--control-type", choices=[c.value for c in PriceControlType])
    wf.add_argument("--control-price", type=float)

    el = sub.add_parser("elasticity", help="Compute point and optional arc elasticity")
    el.add_argument("--intercept", type=float, required=True)
    el.add_argument("--slope", type=float, required=True)
    el.add_argument("--quantity", type=float, required=True)
    el.add_argument("--q1", type=float)
    el.add_argument("--p1", type=float)
    el.add_argument("--output", type=str)

    rep = sub.add_parser("report-dwl", help="Generate one-row DWL report for a policy")
    add_market_line_args(rep)
    rep.add_argument("--policy", choices=["tax", "control"], required=True)
    rep.add_argument("--tax-type", choices=[t.value for t in TaxType])
    rep.add_argument("--amount", type=float)
    rep.add_argument(
        "--tax-on", choices=[s.value for s in TaxOn], default=TaxOn.PRODUCER.value
    )
    rep.add_argument("--control-type", choices=[c.value for c in PriceControlType])
    rep.add_argument("--control-price", type=float)
    rep.add_argument("--csv", type=str)

    return parser


def main() -> None:
    """CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "elasticity":
        line = Line.from_inverse(args.intercept, args.slope)
        point = point_price_elasticity(line, args.quantity)
        payload: dict[str, Any] = {
            "point_elasticity": point,
            "classification": classify_elasticity(point),
        }
        if args.q1 is not None and args.p1 is not None:
            p0 = line.p_at(args.quantity)
            arc = arc_price_elasticity(args.quantity, p0, args.q1, args.p1)
            payload["arc_elasticity"] = arc
            payload["arc_classification"] = classify_elasticity(arc)
        _dump_result(payload, args.output)
        return

    if args.command == "discrete":
        result = solve_discrete_equilibrium(
            DiscreteDemand(tuple(args.demand_values)),
            DiscreteSupply(tuple(args.supply_values)),
            price_rule=EquilibriumPriceRule(args.price_rule),
        )
        _dump_result(result, args.output)
        return

    demand = _line_from_args(args, "demand")
    supply = _line_from_args(args, "supply")

    if args.command == "equilibrium":
        result = solve_equilibrium(demand, supply)
        _dump_result(result, args.output)
        return

    if args.command == "shift":
        scenario = ShiftScenario(
            demand_shift=ShiftSpec(
                args.demand_delta_intercept, args.demand_delta_slope
            ),
            supply_shift=ShiftSpec(
                args.supply_delta_intercept, args.supply_delta_slope
            ),
        )
        result = comparative_statics(demand, supply, scenario)
        _dump_result(result, args.output)
        return

    if args.command == "tax":
        scenario = TaxScenario(
            tax_type=TaxType(args.tax_type),
            amount=args.amount,
            tax_on=TaxOn(args.tax_on),
        )
        result = compare_tax_scenario(demand, supply, scenario)
        _dump_result(result, args.output)
        return

    if args.command == "controls":
        scenario = PriceControlScenario(
            control_type=PriceControlType(args.control_type),
            control_price=args.control_price,
        )
        result = evaluate_price_control(demand, supply, scenario)
        _dump_result(result, args.output)
        return

    if args.command == "welfare":
        baseline_eq = solve_equilibrium(demand, supply)
        baseline_outcome = outcome_from_equilibrium(baseline_eq)

        if args.policy == "baseline":
            baseline = compute_surplus(demand, supply, baseline_outcome)
            _dump_result(baseline, args.output)
            return

        if args.policy == "tax":
            if args.tax_type is None or args.amount is None:
                raise SystemExit("--tax-type and --amount are required for policy=tax")
            tax_scenario = TaxScenario(
                tax_type=TaxType(args.tax_type),
                amount=args.amount,
                tax_on=TaxOn(args.tax_on),
            )
            tax_eq = solve_tax_equilibrium(demand, supply, tax_scenario)
            policy_outcome = outcome_from_tax(tax_eq)
        else:
            if args.control_type is None or args.control_price is None:
                raise SystemExit(
                    "--control-type and --control-price are required for policy=control"
                )
            control = evaluate_price_control(
                demand,
                supply,
                PriceControlScenario(
                    PriceControlType(args.control_type), args.control_price
                ),
            )
            policy_outcome = outcome_from_control(control)

        delta = compare_surplus(demand, supply, baseline_outcome, policy_outcome)
        _dump_result(delta, args.output)
        return

    if args.command == "report-dwl":
        baseline_eq = solve_equilibrium(demand, supply)
        baseline_outcome = outcome_from_equilibrium(baseline_eq)
        baseline = compute_surplus(demand, supply, baseline_outcome)

        if args.policy == "tax":
            if args.tax_type is None or args.amount is None:
                raise SystemExit("--tax-type and --amount are required for policy=tax")
            tax_scenario = TaxScenario(
                tax_type=TaxType(args.tax_type),
                amount=args.amount,
                tax_on=TaxOn(args.tax_on),
            )
            policy_eq = solve_tax_equilibrium(demand, supply, tax_scenario)
            policy_outcome = outcome_from_tax(policy_eq)
        else:
            if args.control_type is None or args.control_price is None:
                raise SystemExit(
                    "--control-type and --control-price are required for policy=control"
                )
            control = evaluate_price_control(
                demand,
                supply,
                PriceControlScenario(
                    PriceControlType(args.control_type), args.control_price
                ),
            )
            policy_outcome = outcome_from_control(control)

        policy = compute_surplus(
            demand, supply, policy_outcome, baseline_outcome=baseline_outcome
        )
        report = build_dwl_report([("scenario", baseline, policy)])
        if args.csv:
            save_dwl_report_csv(report, args.csv)
        _dump_result(report, args.output)
        if args.output:
            save_dwl_report_json(report, args.output)
        return

    raise SystemExit(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    main()
