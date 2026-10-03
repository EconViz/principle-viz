from __future__ import annotations

import pytest

from principle_viz.core.line import Line
from principle_viz.core.public_goods import IndividualBenefit, analyze_public_good
from principle_viz.plot.figure import MarketFigure
from principle_viz.policy.common_resources import analyze_common_resource
from principle_viz.policy.externality import ExternalityScenario, analyze_externality
from principle_viz.visuals.market_failures import public_good_canvas


@pytest.fixture
def market() -> tuple[Line, Line]:
    return Line.from_inverse(12, -1), Line.from_inverse(2, 1)


def test_negative_externality_causes_overproduction_and_corrective_tax(
    market: tuple[Line, Line],
) -> None:
    result = analyze_externality(*market, ExternalityScenario(marginal_external_cost=2))

    assert result.private_equilibrium.q_star == pytest.approx(5)
    assert result.social_equilibrium.q_star == pytest.approx(4)
    assert result.quantity_distortion == pytest.approx(1)
    assert result.corrective_tax == pytest.approx(2)
    assert result.corrective_subsidy == 0
    assert result.deadweight_loss == pytest.approx(1)


def test_positive_externality_causes_underproduction_and_corrective_subsidy(
    market: tuple[Line, Line],
) -> None:
    result = analyze_externality(
        *market, ExternalityScenario(marginal_external_benefit=2)
    )

    assert result.social_equilibrium.q_star == pytest.approx(6)
    assert result.quantity_distortion == pytest.approx(-1)
    assert result.corrective_subsidy == pytest.approx(2)
    assert result.deadweight_loss == pytest.approx(1)


def test_public_good_vertically_sums_marginal_benefits() -> None:
    result = analyze_public_good(
        (
            IndividualBenefit("A", Line.from_inverse(8, -1)),
            IndividualBenefit("B", Line.from_inverse(6, -1)),
        ),
        Line.from_inverse(5, 0),
    )

    assert result.efficient_quantity == pytest.approx(4.5)
    assert result.efficient_marginal_value == pytest.approx(5)
    assert result.private_provision_quantity == pytest.approx(3)
    assert result.free_rider_gap == pytest.approx(1.5)


def test_common_resource_open_access_overuses_resource(
    market: tuple[Line, Line],
) -> None:
    result = analyze_common_resource(*market, marginal_congestion_cost=3)

    assert result.open_access_equilibrium.q_star == pytest.approx(5)
    assert result.efficient_equilibrium.q_star == pytest.approx(3.5)
    assert result.overuse == pytest.approx(1.5)
    assert result.corrective_fee == pytest.approx(3)
    assert result.deadweight_loss == pytest.approx(2.25)


def test_market_failure_visuals_use_semantic_layers(
    market: tuple[Line, Line],
) -> None:
    externality = analyze_externality(
        *market, ExternalityScenario(marginal_external_cost=2)
    )
    figure = MarketFigure(x_max=11, y_max=14)
    figure.add_curves(*market, q_max=10).add_externality(externality)
    ids = {layer.id for layer in figure.scene.layers}
    assert "market.externality.social_cost" in ids
    assert "market.externality.dwl" in ids
    assert "market.externality.corrective_wedge" in ids

    public_good = analyze_public_good(
        (IndividualBenefit("A", Line.from_inverse(8, -1)),),
        Line.from_inverse(5, 0),
    )
    canvas = public_good_canvas(public_good)
    assert "public_good.social_benefit" in {
        layer.id for layer in canvas.snapshot().layers
    }


@pytest.mark.parametrize(
    "scenario",
    [
        ExternalityScenario(marginal_external_cost=2),
        ExternalityScenario(marginal_external_benefit=2),
    ],
)
def test_corrective_wedge_spans_private_to_social_curve_at_the_optimum(
    market: tuple[Line, Line], scenario: ExternalityScenario
) -> None:
    result = analyze_externality(*market, scenario)
    figure = MarketFigure(x_max=11, y_max=14).add_externality(result)
    wedge = {layer.id: layer for layer in figure.scene.layers}[
        "market.externality.corrective_wedge"
    ]
    q = result.social_equilibrium.q_star
    social, private = (
        (result.social_supply, market[1])
        if result.corrective_tax
        else (result.social_demand, market[0])
    )
    (bottom, top) = wedge.path
    assert bottom == pytest.approx((q, private.p_at(q)))
    assert top == pytest.approx((q, social.p_at(q)))


def test_public_good_marks_private_and_efficient_quantity_on_the_axis() -> None:
    from mosaickit import AxisMarkLayer, PointLabelLayer

    a = IndividualBenefit("Person A", Line.from_inverse(10.0, -1.0))
    b = IndividualBenefit("Person B", Line.from_inverse(6.0, -1.0))
    result = analyze_public_good((a, b), Line.from_inverse(4.0, 0.0))
    canvas = public_good_canvas(result)
    layers = canvas.snapshot().layers
    marks = {
        layer.label: layer.value
        for layer in layers
        if isinstance(layer, AxisMarkLayer) and layer.axis == "x"
    }
    assert marks["Q_p"] == pytest.approx(result.private_provision_quantity)
    assert marks["Q^*"] == pytest.approx(result.efficient_quantity)
    texts = [str(layer.text) for layer in layers if isinstance(layer, PointLabelLayer)]
    assert not any("Efficient" in t or "Private" in t for t in texts)
    # The quantity axis ends just past the curves instead of leaving empty space.
    assert canvas.spec.x_range[1] <= 1.1 * result.points[-1].quantity


def test_public_good_layers_and_labels_are_user_configurable() -> None:
    from principle_viz import Label

    result = analyze_public_good(
        (IndividualBenefit("A", Line.from_inverse(8, -1)),),
        Line.from_inverse(5, 0),
    )
    canvas = public_good_canvas(
        result,
        visibility={"public_good.private_provision": False},
        labels={"public_good.social_benefit": Label(text="$MB$")},
    )
    layers = {layer.id: layer for layer in canvas.snapshot().layers}

    assert not layers["public_good.private_provision"].visible
    assert layers["public_good.social_benefit.label"].text == "$MB$"
    canvas.hide("public_good.efficient.guide")
    canvas.configure_label("public_good.efficient.mark", text="Q_e")
    layers = {layer.id: layer for layer in canvas.snapshot().layers}
    assert not layers["public_good.efficient.guide"].visible
    assert layers["public_good.efficient.mark"].label == "Q_e"
