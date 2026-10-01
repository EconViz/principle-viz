"""Deadweight loss reporting helpers."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from principle_viz.welfare.surplus import SurplusResult


@dataclass(frozen=True)
class DWLScenarioRow:
    """Single scenario row for summary reporting."""

    scenario: str
    baseline_quantity: float
    policy_quantity: float
    delta_quantity: float
    delta_consumer_surplus: float
    delta_producer_surplus: float
    delta_tax_revenue: float
    delta_total_surplus: float
    deadweight_loss: float


def build_dwl_report(
    rows: list[tuple[str, SurplusResult, SurplusResult]],
) -> list[DWLScenarioRow]:
    """Build report rows from baseline/policy surplus results."""
    report: list[DWLScenarioRow] = []
    for scenario, baseline, policy in rows:
        report.append(
            DWLScenarioRow(
                scenario=scenario,
                baseline_quantity=baseline.quantity,
                policy_quantity=policy.quantity,
                delta_quantity=policy.quantity - baseline.quantity,
                delta_consumer_surplus=policy.consumer_surplus
                - baseline.consumer_surplus,
                delta_producer_surplus=policy.producer_surplus
                - baseline.producer_surplus,
                delta_tax_revenue=policy.tax_revenue - baseline.tax_revenue,
                delta_total_surplus=policy.total_surplus - baseline.total_surplus,
                deadweight_loss=policy.deadweight_loss,
            )
        )
    return report


def save_dwl_report_json(report: list[DWLScenarioRow], path: str | Path) -> None:
    """Save DWL report as JSON."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps([asdict(item) for item in report], indent=2), encoding="utf-8"
    )


def save_dwl_report_csv(report: list[DWLScenarioRow], path: str | Path) -> None:
    """Save DWL report as CSV."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if not report:
        target.write_text("", encoding="utf-8")
        return

    fieldnames = list(asdict(report[0]).keys())
    with target.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in report:
            writer.writerow(asdict(item))
