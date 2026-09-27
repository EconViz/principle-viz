from __future__ import annotations

import pytest

from principle_viz.core.line import Line
from principle_viz.policy.tax import (
    AnchorMode,
    TaxOn,
    TaxScenario,
    TaxType,
    build_tax_visual_guide,
    compare_tax_scenario,
    solve_tax_equilibrium,
)


def test_specific_tax_consumer_vs_producer_same_quantity() -> None:
    demand = Line.from_inverse(12.0, -1.0)
    supply = Line.from_inverse(2.0, 1.0)

    by_producer = solve_tax_equilibrium(
        demand,
        supply,
        TaxScenario(tax_type=TaxType.PER_UNIT_TAX, amount=2.0, tax_on=TaxOn.PRODUCER),
    )
    by_consumer = solve_tax_equilibrium(
        demand,
        supply,
        TaxScenario(tax_type=TaxType.PER_UNIT_TAX, amount=2.0, tax_on=TaxOn.CONSUMER),
    )

    assert by_producer.q_star == pytest.approx(by_consumer.q_star)
    assert by_producer.tax_revenue == pytest.approx(by_consumer.tax_revenue)


def test_ad_valorem_tax_generates_positive_wedge() -> None:
    demand = Line.from_inverse(20.0, -2.0)
    supply = Line.from_inverse(2.0, 1.0)

    result = solve_tax_equilibrium(
        demand,
        supply,
        TaxScenario(tax_type=TaxType.AD_VALOREM_TAX, amount=0.2, tax_on=TaxOn.PRODUCER),
    )

    assert result.consumer_price > result.producer_price
    assert result.tax_wedge > 0.0


def test_compare_tax_scenario_has_directions() -> None:
    demand = Line.from_inverse(10.0, -1.0)
    supply = Line.from_inverse(2.0, 1.0)

    result = compare_tax_scenario(
        demand,
        supply,
        TaxScenario(tax_type=TaxType.FIXED_TAX, amount=1.0, tax_on=TaxOn.PRODUCER),
    )

    assert result.direction_q in {"left", "right", "none"}
    assert result.direction_p_consumer in {"up", "down", "none"}


def test_tax_visual_shift_producer_is_upward_at_anchor() -> None:
    demand = Line.from_inverse(12.0, -1.0)
    supply = Line.from_inverse(2.0, 1.0)
    scenario = TaxScenario(tax_type=TaxType.FIXED_TAX, amount=1.5, tax_on=TaxOn.PRODUCER)

    guide = build_tax_visual_guide(demand, supply, scenario)
    q0 = guide.baseline_equilibrium.q_star

    assert guide.transform_kind == "shift"
    assert guide.curve_role == "supply"
    assert guide.taxed_curve.p_at(q0) - guide.base_curve.p_at(q0) == pytest.approx(1.5)


def test_tax_visual_shift_consumer_keeps_upward_arrow_gap() -> None:
    demand = Line.from_inverse(12.0, -1.0)
    supply = Line.from_inverse(2.0, 1.0)
    scenario = TaxScenario(tax_type=TaxType.PER_UNIT_TAX, amount=1.2, tax_on=TaxOn.CONSUMER)

    guide = build_tax_visual_guide(demand, supply, scenario)
    q0 = guide.baseline_equilibrium.q_star

    assert guide.transform_kind == "shift"
    assert guide.curve_role == "demand"
    assert guide.base_curve.p_at(q0) - guide.taxed_curve.p_at(q0) == pytest.approx(1.2)


def test_tax_visual_ad_valorem_default_is_origin_scaled_rotation_for_producer() -> None:
    demand = Line.from_inverse(12.0, -1.0)
    supply = Line.from_inverse(2.0, 1.0)
    scenario = TaxScenario(tax_type=TaxType.AD_VALOREM_TAX, amount=0.25, tax_on=TaxOn.PRODUCER)

    guide = build_tax_visual_guide(demand, supply, scenario)
    q_ref = 3.0

    assert guide.transform_kind == "rotation"
    assert guide.curve_role == "supply"
    assert guide.taxed_curve.p_at(q_ref) == pytest.approx(guide.base_curve.p_at(q_ref) * 1.25)
    assert guide.taxed_curve.slope() == pytest.approx(guide.base_curve.slope() * 1.25)
    assert scenario.anchor_mode == AnchorMode.NONE


def test_tax_visual_ad_valorem_can_enable_baseline_anchor_mode() -> None:
    demand = Line.from_inverse(12.0, -1.0)
    supply = Line.from_inverse(2.0, 1.0)
    scenario = TaxScenario(
        tax_type=TaxType.AD_VALOREM_TAX,
        amount=0.2,
        tax_on=TaxOn.CONSUMER,
        anchor_mode=AnchorMode.BASELINE_EQUILIBRIUM,
    )

    guide = build_tax_visual_guide(demand, supply, scenario)
    q0 = guide.baseline_equilibrium.q_star
    p0 = guide.baseline_equilibrium.p_star

    assert guide.transform_kind == "rotation"
    assert guide.curve_role == "demand"
    assert guide.taxed_curve.p_at(q0) == pytest.approx(p0)
