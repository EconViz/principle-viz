"""Label nudges from econ-viz.toml: a default move for whole groups of labels."""

from __future__ import annotations

import dataclasses
import re

import pytest
from mosaickit import (
    CanvasSpec,
    ConfigurationError,
    FillLayer,
    PointLabelLayer,
    RegionLabelLayer,
)
from mosaickit.styles.nudge import Nudge

from principle_viz import Canvas, Config, Label, MarketFigure, PlotTheme
from principle_viz.config import SCHEMA
from principle_viz.core.controls import (
    PriceControlScenario,
    PriceControlType,
    evaluate_price_control,
)
from principle_viz.core.equilibrium import solve_equilibrium
from principle_viz.core.line import Line
from principle_viz.label_groups import LABEL_GROUPS, LABEL_SIDES, label_group
from principle_viz.welfare.surplus import compute_surplus, outcome_from_equilibrium

DEMAND = Line.from_inverse(10.0, -1.0)
SUPPLY = Line.from_inverse(2.0, 1.0)

GROUP_LABELS = {
    "point": "market.equilibrium.label",
    "curve": "market.demand.label",
    "region": "market.welfare.cs.label",
    "mark": "market.control.price.label",
    "annotation": "market.control.gap",
}


@pytest.fixture(autouse=True)
def _reset():
    yield
    Config.reset()


def _theme(**nudges: Nudge) -> PlotTheme:
    return dataclasses.replace(PlotTheme(), label_nudges=nudges)


def _figure(theme: PlotTheme | None = None, **kwargs: object) -> MarketFigure:
    eq = solve_equilibrium(DEMAND, SUPPLY)
    surplus = compute_surplus(DEMAND, SUPPLY, outcome_from_equilibrium(eq))
    control = evaluate_price_control(
        DEMAND, SUPPLY, PriceControlScenario(PriceControlType.CEILING, 4.0)
    )
    return (
        MarketFigure(x_max=12, y_max=12, theme=theme, **kwargs)
        .add_curves(DEMAND, SUPPLY, q_max=10)
        .add_equilibrium(eq)
        .add_welfare(surplus)
        .add_price_control(control)
    )


def _layers(figure: MarketFigure) -> dict[str, object]:
    return {layer.id: layer for layer in figure.scene.layers}


def _svg(figure: MarketFigure, tmp_path) -> str:
    target = tmp_path / "figure.svg"
    figure.save(target)
    text = re.sub(r"<dc:date>.*?</dc:date>", "", target.read_text())
    return re.sub(r"\b([pm])[0-9a-f]{8,}\b", r"\1", text)


# ---- the settings file


def test_schema_declares_every_group_and_side():
    for group in LABEL_GROUPS:
        for side in LABEL_SIDES:
            field = SCHEMA.fields[f"label.{group}.{side}"]
            assert field.attr == f"nudges.{group}_{side}"
    assert "# [principle.label.point]" in SCHEMA.template()


def test_toml_reads_lengths_per_group():
    theme = Config.from_dict(
        {
            "principle": {
                "label": {
                    "point": {"top": "2pt", "left": 1},
                    "region": {"right": "1mm", "bottom": "0.5cm"},
                }
            }
        }
    ).theme
    assert theme.label_nudges == {
        "point": Nudge(-1, 2),
        "region": Nudge(72 / 25.4, -72 / 2.54 * 0.5),
    }


def test_toml_without_label_settings_leaves_the_theme_alone():
    assert Config.from_dict({"principle": {"label": {}}}).theme == PlotTheme()
    assert Config.from_dict({"principle": {"label": {"point": {"top": 0}}}}).theme == (
        PlotTheme()
    )


@pytest.mark.parametrize(
    ("table", "message"),
    [
        ({"curve": {"top": "0.5em"}}, r"\[principle.label.curve\] top cannot be in em"),
        ({"curve": {"top": "x"}}, r"\[principle.label.curve\] top must be a length"),
        ({"curve": {"top": True}}, r"\[principle.label.curve\] top must be a length"),
        ({"curve": {"up": 1}}, r"unknown key 'up'"),
        ({"curves": {"top": 1}}, r"unknown key 'curves'; did you mean 'curve'"),
    ],
)
def test_toml_rejects_bad_nudges(table, message):
    with pytest.raises(ConfigurationError, match=message):
        Config.from_dict({"principle": {"label": table}})


def test_theme_rejects_unknown_groups():
    with pytest.raises(ValueError, match="unknown label group 'axis'"):
        PlotTheme(label_nudges={"axis": Nudge(1, 1)})
    with pytest.raises(TypeError, match="must be a mosaickit Nudge"):
        PlotTheme(label_nudges={"point": (1, 1)})  # type: ignore[dict-item]


# ---- the default applied per group


def test_each_group_moves_only_its_own_labels():
    plain = _layers(_figure())
    for group, label_id in GROUP_LABELS.items():
        nudge = Nudge(3, -2)
        layers = _layers(_figure(_theme(**{group: nudge})))
        moved = {
            key
            for key, layer in layers.items()
            if getattr(layer, "nudge", None) == nudge
        }
        assert label_id in moved, group
        assert all(label_group(layers[key]) == group for key in moved), group
        assert getattr(plain[label_id], "nudge", None) is None


def test_every_label_layer_has_one_group_and_axis_labels_none():
    layers = _layers(_figure()).values()
    groups = {label_group(layer) for layer in layers}
    assert set(GROUP_LABELS) <= groups
    assert groups <= {*LABEL_GROUPS, None}
    figure = _figure(_theme(**{g: Nudge(1, 1) for g in LABEL_GROUPS}))
    for layer in figure.scene.layers:
        if layer.id.startswith("axes.") or ".mark." in layer.id:
            assert getattr(layer, "nudge", None) is None, layer.id


def test_config_use_flows_into_new_figures():
    Config.from_dict({"principle": {"label": {"point": {"top": "4pt"}}}}).use()
    label = _layers(_figure())["market.equilibrium.label"]
    assert isinstance(label, PointLabelLayer) and label.nudge == Nudge(0, 4)
    assert _layers(_figure())["market.demand.label"].nudge is None


def test_default_nudge_follows_configure_label_and_copy():
    figure = _figure(_theme(curve=Nudge(0, 5)))
    figure.configure_label("market.demand", text="$D_0$")
    layer = _layers(figure)["market.demand.label"]
    assert layer.text == "$D_0$" and layer.nudge == Nudge(0, 5)
    assert figure.canvas.copy()._label_nudges == {"curve": Nudge(0, 5)}


# ---- the per-label Label


def test_label_with_its_own_nudge_replaces_the_default():
    theme = _theme(point=Nudge(1, 2))
    figure = _figure(theme, labels={"market.equilibrium": Label(top="5pt")})
    assert _layers(figure)["market.equilibrium.label"].nudge == Nudge(0, 5)
    figure = _figure(theme)
    figure.configure_label("market.equilibrium", right=7)
    assert _layers(figure)["market.equilibrium.label"].nudge == Nudge(7, 0)


def test_label_without_a_nudge_keeps_the_default():
    theme = _theme(point=Nudge(1, 2))
    figure = _figure(theme, labels={"market.equilibrium": Label(text="$E$")})
    layer = _layers(figure)["market.equilibrium.label"]
    assert layer.text == "$E$" and layer.nudge == Nudge(1, 2)
    figure = _figure(theme)
    figure.configure_label("market.equilibrium", offset=(4, 4))
    layer = _layers(figure)["market.equilibrium.label"]
    assert layer.offset == (4, 4) and layer.nudge == Nudge(1, 2)


def test_hidden_label_stays_hidden_with_a_default():
    figure = _figure(
        _theme(point=Nudge(1, 2)), labels={"market.equilibrium": Label(visible=False)}
    )
    assert not _layers(figure)["market.equilibrium.label"].visible


# ---- the drawing


def test_figures_without_nudges_are_unchanged(tmp_path):
    plain = _svg(_figure(), tmp_path)
    assert _svg(_figure(_theme()), tmp_path) == plain
    Config.from_dict({"principle": {"label": {"point": {"top": 0}}}}).use()
    assert _svg(_figure(), tmp_path) == plain


def test_a_default_nudge_changes_the_drawing(tmp_path):
    plain = _svg(_figure(), tmp_path)
    assert _svg(_figure(_theme(point=Nudge(0, 6))), tmp_path) != plain


def test_saving_at_another_dpi_keeps_the_nudge_once(tmp_path):
    figure = _figure(_theme(point=Nudge(0, 6)))
    layer = _layers(figure)["market.equilibrium.label"]
    figure.save(tmp_path / "a.png", dpi=72)
    assert _layers(figure)["market.equilibrium.label"] == layer
    assert layer.nudge == Nudge(0, 6)


def _callout(theme: PlotTheme) -> Canvas:
    return Canvas(
        CanvasSpec(x_range=(0, 10), y_range=(0, 10), title=None),
        theme=theme.to_mosaickit(),
        config=theme.mosaickit_config(),
        label_nudges=theme.label_nudges,
    ).extend(
        [
            FillLayer(((1, 1), (2, 1), (2, 2)), id="r", role="principle.welfare.loss"),
            RegionLabelLayer(
                "r",
                "Deadweight loss",
                placement="callout",
                id="r.label",
                role="principle.annotation",
            ),
        ]
    )


def _leader(canvas: Canvas, tmp_path) -> list[float]:
    target = tmp_path / "callout.svg"
    canvas.save(target)
    text = target.read_text()
    block = text[text.index('id="r.label.leader"') :]
    path = re.search(r'<path d="([^"]+)"', block)
    assert path is not None
    return [float(n) for n in re.findall(r"-?\d+\.?\d*", path.group(1))]


def test_callout_leader_follows_the_moved_label(tmp_path):
    plain = _leader(_callout(_theme()), tmp_path)
    moved_canvas = _callout(_theme(region=Nudge(0, 10)))
    layer = next(l for l in moved_canvas.snapshot().layers if l.id == "r.label")
    assert layer.nudge == Nudge(0, 10)
    moved = _leader(moved_canvas, tmp_path)
    assert moved[:2] == pytest.approx(plain[:2])  # still starts at the region
    assert moved[2:] != pytest.approx(plain[2:])  # ends where the label went
    assert moved[3] < plain[3]  # up the page is smaller y in the svg
