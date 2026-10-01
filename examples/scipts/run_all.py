"""Run all example scripts and keep image-only outputs."""

from __future__ import annotations

from basic_equilibrium import main as basic_main
from common import clear_all_outputs, remove_non_image_outputs
from discrete_market import main as discrete_main
from dwl_report import main as report_main
from elasticity_demo import main as elasticity_main
from elasticity_five_types_centered import main as elasticity_five_main
from elasticity_total_revenue import main as elasticity_revenue_main
from price_controls import main as control_main
from price_controls_welfare import main as control_welfare_main
from shift_scenarios import main as shift_main
from subsidy_welfare import main as subsidy_main
from tax_comparison import main as tax_main
from welfare_tax import main as welfare_main


def main() -> None:
    clear_all_outputs()
    remove_non_image_outputs()
    basic_main()
    discrete_main()
    shift_main()
    tax_main()
    subsidy_main()
    welfare_main()
    control_main()
    control_welfare_main()
    elasticity_main()
    elasticity_five_main()
    elasticity_revenue_main()
    report_main()
    remove_non_image_outputs()


if __name__ == "__main__":
    main()
