from __future__ import annotations

from mosaickit import Canvas as MosaicCanvas
from mosaickit import LegendLayer, PathLayer, TextLayer

from principle_viz.plot import Canvas, Label, MarketFigure


def test_canvas_is_mosaickit_canvas() -> None:
    assert issubclass(Canvas, MosaicCanvas)


def test_canvas_controls_every_layer_and_text_by_stable_id() -> None:
    canvas = Canvas(
        visibility={"test.line": False},
        labels={"test.text": Label(text="New", offset=(4, -2))},
    ).extend(
        (
            PathLayer(((0, 0), (1, 1)), id="test.line"),
            TextLayer((0.5, 0.5), "Old", id="test.text"),
        )
    )
    layers = {layer.id: layer for layer in canvas.snapshot().layers}
    assert not layers["test.line"].visible
    assert layers["test.text"].text == "New"
    assert layers["test.text"].offset == (4, -2)

    canvas.show("test.line").hide("test.text")
    layers = {layer.id: layer for layer in canvas.snapshot().layers}
    assert layers["test.line"].visible
    assert not layers["test.text"].visible


def test_market_figure_uses_first_quadrant_scene_axes() -> None:
    figure = MarketFigure(x_max=10.0, y_max=8.0, title=None)

    assert figure.canvas.spec.x_range == (0.0, 10.0)
    assert figure.canvas.spec.y_range == (0.0, 8.0)
    assert {layer.id for layer in figure.scene.layers}.issuperset(
        {"axes.x", "axes.y", "axes.x.label", "axes.y.label", "axes.origin.label"}
    )
    assert any(
        isinstance(layer, TextLayer) and layer.text == "0"
        for layer in figure.scene.layers
    )
    assert not hasattr(figure, "ax")
    assert not hasattr(figure, "fig")


def test_finalize_adds_scene_legend() -> None:
    figure = MarketFigure(x_max=10.0, y_max=10.0, title=None)
    figure.add_layer(
        PathLayer(
            ((0.0, 0.0), (1.0, 1.0)),
            id="test.line",
            role="principle.market.demand",
            legend="Line",
        )
    ).finalize(legend=True)

    legend = next(layer for layer in figure.scene.layers if layer.id == "market.legend")
    assert isinstance(legend, LegendLayer)
    assert legend.entries == ("test.line",)


def test_finalize_draws_no_legend_by_default() -> None:
    figure = MarketFigure(title="No legend").add_layer(
        PathLayer(((0, 0), (1, 1)), id="test.line", legend="Line")
    )
    figure.finalize()
    assert all(layer.id != "market.legend" for layer in figure.scene.layers)


def test_finalize_hides_crossing_guides_without_discarding_them() -> None:
    from principle_viz.core.equilibrium import solve_equilibrium
    from principle_viz.core.line import Line
    from principle_viz.policy.tax import (
        TaxOn,
        TaxScenario,
        TaxType,
        solve_tax_equilibrium,
    )
    from principle_viz.welfare.surplus import (
        compare_surplus,
        outcome_from_equilibrium,
        outcome_from_tax,
    )

    demand = Line.from_inverse(10, -1)
    supply = Line.from_inverse(2, 1)
    baseline = outcome_from_equilibrium(solve_equilibrium(demand, supply))
    policy = outcome_from_tax(
        solve_tax_equilibrium(
            demand,
            supply,
            TaxScenario(TaxType.PER_UNIT_TAX, 2, TaxOn.PRODUCER),
        )
    )
    surplus = compare_surplus(demand, supply, baseline, policy).policy
    figure = MarketFigure().add_welfare_transition(
        baseline_outcome=baseline,
        policy_outcome=policy,
        surplus=surplus,
    )
    crossing = tuple(
        layer.id
        for layer in figure.scene.layers
        if layer.id.startswith("market.welfare.guide")
    )

    figure.finalize()
    layers = {layer.id: layer for layer in figure.scene.layers}
    hidden = tuple(layer_id for layer_id in crossing if not layers[layer_id].visible)
    assert hidden
    figure.show(*hidden)
    assert all(
        {layer.id: layer for layer in figure.scene.layers}[layer_id].visible
        for layer_id in hidden
    )
