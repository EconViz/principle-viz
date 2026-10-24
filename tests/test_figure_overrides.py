"""Per-figure label overrides from econ-viz.toml: [figure.<stem>.label."<id>"].

mosaickit applies them in ``Canvas.save`` / ``CanvasGrid.save`` by the output file's stem.
PrincipleViz only has to route every figure it writes through those methods.
"""

from __future__ import annotations

import dataclasses
import re
from pathlib import Path
from xml.etree import ElementTree

import pytest
from mosaickit import AxisMarkLayer, BraceLayer, RegionLabelLayer, econ_toml
from mosaickit.styles.nudge import Nudge

from principle_viz import (
    Canvas,
    Config,
    MarketFigure,
    PlotTheme,
    demand_aggregation_figure,
)
from principle_viz.core.controls import (
    PriceControlScenario,
    PriceControlType,
    evaluate_price_control,
)
from principle_viz.core.equilibrium import solve_equilibrium
from principle_viz.core.line import Line
from principle_viz.core.ppf import ProductionPossibilitiesFrontier, analyze_ppf
from principle_viz.policy.tax import (
    TaxOn,
    TaxScenario,
    TaxType,
    compare_tax_scenario,
    solve_tax_equilibrium,
)
from principle_viz.visuals.ppf import ppf_canvas
from principle_viz.welfare.surplus import (
    compare_surplus,
    outcome_from_control,
    outcome_from_equilibrium,
    outcome_from_tax,
)

DEMAND = Line.from_inverse(10.0, -1.0)
SUPPLY = Line.from_inverse(2.0, 1.0)
DWL = "market.welfare.dwl.label"
STEM = "tax_welfare"


@pytest.fixture(autouse=True)
def _clean():
    Config.reset()
    econ_toml.clear_figure_overrides()
    yield
    Config.reset()
    econ_toml.clear_figure_overrides()


def _activate(tmp_path: Path, body: str) -> None:
    path = tmp_path / "econ-viz.toml"
    path.write_text(body, encoding="utf-8")
    Config.load(path).use()


def _tax_figure(amount: float = 2.0, **kwargs: object) -> MarketFigure:
    """Welfare under a tax; with a small tax the deadweight loss is a callout."""
    scenario = TaxScenario(TaxType.PER_UNIT_TAX, amount, TaxOn.PRODUCER)
    baseline = outcome_from_equilibrium(solve_equilibrium(DEMAND, SUPPLY))
    policy = outcome_from_tax(solve_tax_equilibrium(DEMAND, SUPPLY, scenario))
    delta = compare_surplus(DEMAND, SUPPLY, baseline, policy)
    figure = MarketFigure(x_max=12, y_max=12, **kwargs)  # type: ignore[arg-type]
    figure.add_curves(DEMAND, SUPPLY, q_max=10)
    figure.add_welfare_transition(
        baseline_outcome=baseline, policy_outcome=policy, surplus=delta.policy
    )
    figure.add_tax_comparison(compare_tax_scenario(DEMAND, SUPPLY, scenario))
    return figure.finalize()


def _ceiling_figure() -> MarketFigure:
    control = evaluate_price_control(
        DEMAND, SUPPLY, PriceControlScenario(PriceControlType.CEILING, 3.5)
    )
    baseline = outcome_from_equilibrium(solve_equilibrium(DEMAND, SUPPLY))
    policy = outcome_from_control(control)
    delta = compare_surplus(DEMAND, SUPPLY, baseline, policy)
    figure = MarketFigure(x_max=12, y_max=12)
    figure.add_curves(DEMAND, SUPPLY, q_max=10).add_price_control(control)
    figure.add_welfare_transition(
        baseline_outcome=baseline, policy_outcome=policy, surplus=delta.policy
    )
    return figure.finalize()


def _theme(**nudges: Nudge) -> PlotTheme:
    return dataclasses.replace(PlotTheme(), label_nudges=nudges)


def _normalized(text: str) -> str:
    """An SVG without the date and the random clip-path ids."""
    text = re.sub(r"<dc:date>.*?</dc:date>", "", text)
    return re.sub(r"\b([pm])[0-9a-f]{8,}\b", r"\1", text)


def _read(path: Path) -> str:
    return _normalized(path.read_text())


def _svg(figure: MarketFigure, path: Path, **kwargs: object) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.save(path, **kwargs)  # type: ignore[arg-type]
    return _read(path)


def _group(svg: str, element_id: str) -> str:
    root = ElementTree.fromstring(svg)
    for element in root.iter():
        if element.get("id") == element_id:
            return ElementTree.tostring(element, encoding="unicode")
    raise AssertionError(f"no element {element_id!r}")


def _points(svg: str, element_id: str) -> list[tuple[float, float]]:
    """Where an element is drawn: its text origin, else the points of its path."""
    body = _group(svg, element_id)
    moved = re.search(r"transform=\"translate\(([\d.]+) ([\d.]+)\)", body)
    if moved:
        return [(float(moved[1]), float(moved[2]))]
    found = re.findall(r"[ML] ([\d.]+) ([\d.]+)", body)
    return [(float(x), float(y)) for x, y in found]


def _layers(figure: MarketFigure) -> dict[str, object]:
    return {layer.id: layer for layer in figure.scene.layers}


# ---- MarketFigure.save


def test_override_moves_the_label_and_its_leader_follows(tmp_path):
    plain = _svg(_tax_figure(), tmp_path / "plain" / "other.svg")
    assert f"{DWL}.leader" in plain  # a callout with a leader line
    _activate(tmp_path, f'[figure.{STEM}.label."{DWL}"]\ntop = "12pt"\n')
    moved = _svg(_tax_figure(), tmp_path / "moved" / f"{STEM}.svg")
    before, after = _points(plain, DWL), _points(moved, DWL)
    assert after[0][0] == before[0][0]
    assert after[0][1] == pytest.approx(before[0][1] - 12)  # top: up, in points
    start, end = _points(plain, f"{DWL}.leader"), _points(moved, f"{DWL}.leader")
    assert end[0] == start[0]  # the anchor on the region stays
    assert end[1][1] == pytest.approx(start[1][1] - 12)  # the free end follows


def test_other_stems_and_unrelated_overrides_leave_the_output_unchanged(tmp_path):
    plain = _svg(_tax_figure(), tmp_path / "a" / "tax_welfare.svg")
    _activate(
        tmp_path,
        f'[figure.{STEM}.label."{DWL}"]\ntop = "12pt"\n'
        '[figure.elsewhere.label."market.demand.label"]\nright = "9pt"\n',
    )
    assert _svg(_tax_figure(), tmp_path / "b" / "other.svg") == plain
    # an id no layer has is ignored, not an error
    _activate(tmp_path, f'[figure.{STEM}.label."no.such.label"]\ntop = "3pt"\n')
    assert _svg(_tax_figure(), tmp_path / "c" / f"{STEM}.svg") == plain


def test_stem_comes_from_the_path_passed_to_save(tmp_path):
    _activate(tmp_path, '[figure.first.label."market.demand.label"]\nright = "9pt"\n')
    figure = _tax_figure()
    first = _svg(figure, tmp_path / "x" / "first.svg")
    second = _svg(figure, tmp_path / "x" / "second.svg")
    again = _svg(figure, tmp_path / "y" / "first.svg")
    assert first != second
    assert first == again  # nothing accumulates between saves
    assert _points(first, "market.demand.label")[0][0] == pytest.approx(
        _points(second, "market.demand.label")[0][0] + 9
    )
    # saving does not touch the figure itself
    assert _layers(figure)["market.demand.label"].nudge is None


@pytest.mark.parametrize("dpi", [150, 300])
def test_override_replaces_the_group_default_in_every_save_path(tmp_path, dpi):
    group = _theme(region=Nudge(0, 20))
    override = f'[figure.{STEM}.label."{DWL}"]\ntop = "12pt"\n'
    # group default only, saved under another stem
    _activate(tmp_path, override)
    group_only = _svg(_tax_figure(theme=group), tmp_path / "g" / "other.svg", dpi=dpi)
    assert _layers(_tax_figure(theme=group))[DWL].nudge == Nudge(0, 20)
    # the override alone, no group default
    alone = _svg(_tax_figure(), tmp_path / "o" / f"{STEM}.svg", dpi=dpi)
    # group default plus override: the override replaces, it does not add
    both = _svg(_tax_figure(theme=group), tmp_path / "b" / f"{STEM}.svg", dpi=dpi)
    for element in (DWL, f"{DWL}.leader"):
        assert _group(both, element) == _group(alone, element)
        assert _group(both, element) != _group(group_only, element)
    # 20pt up became 12pt up; the labels the file does not name keep the group default
    assert _points(both, DWL)[0][1] - _points(group_only, DWL)[0][1] == pytest.approx(8)
    for other in ("market.welfare.cs.label", "market.welfare.ps.label"):
        assert _group(both, other) == _group(group_only, other)
        assert _group(both, other) != _group(alone, other)
    # the figure keeps its group default; saving did not touch it
    figure = _tax_figure(theme=group)
    figure.save(tmp_path / "z" / f"{STEM}.svg", dpi=dpi)
    assert _layers(figure)[DWL].nudge == Nudge(0, 20)


def test_per_label_label_is_also_replaced(tmp_path):
    from principle_viz import Label

    own = {"market.welfare.dwl": Label(top="30pt")}
    _activate(tmp_path, f'[figure.{STEM}.label."{DWL}"]\ntop = "12pt"\n')
    with_label = _svg(_tax_figure(labels=own), tmp_path / "a" / f"{STEM}.svg")
    alone = _svg(_tax_figure(), tmp_path / "b" / f"{STEM}.svg")
    assert with_label == alone


def test_empty_override_cancels_the_group_default(tmp_path):
    _activate(tmp_path, f'[figure.{STEM}.label."{DWL}"]\n')
    figure = _tax_figure(theme=_theme(region=Nudge(0, 20)))
    plain = _svg(_tax_figure(), tmp_path / "p" / "other.svg")
    saved = _svg(figure, tmp_path / "c" / f"{STEM}.svg")
    for element in (DWL, f"{DWL}.leader"):
        assert _group(saved, element) == _group(plain, element)
    cs = "market.welfare.cs.label"
    assert _group(saved, cs) != _group(plain, cs)  # the other labels keep the default


@pytest.mark.parametrize("suffix", ["svg", "png", "pdf"])
def test_every_output_format_applies_overrides(tmp_path, suffix):
    figure = _tax_figure()
    plain = tmp_path / "plain" / f"other.{suffix}"
    moved = tmp_path / "moved" / f"{STEM}.{suffix}"
    figure.save(plain)
    _activate(tmp_path, f'[figure.{STEM}.label."{DWL}"]\ntop = "12pt"\n')
    figure.save(moved)
    unrelated = tmp_path / "same" / f"other.{suffix}"
    figure.save(unrelated)
    assert moved.read_bytes() != plain.read_bytes()
    if suffix == "svg":
        assert _read(unrelated) == _read(plain)
    else:
        assert unrelated.stat().st_size == plain.stat().st_size


def test_brace_label_ids_are_accepted(tmp_path):
    plain = _svg(_ceiling_figure(), tmp_path / "p" / "other.svg")
    brace = "market.control.gap"
    assert f"{brace}.label" in re.findall(r'<g id="([^"]+)"', plain)
    for key in (brace, f"{brace}.label"):
        _activate(tmp_path, f'[figure.f.label."{key}"]\nright = "10pt"\n')
        svg = _svg(_ceiling_figure(), tmp_path / key / "f.svg")
        before, after = _points(plain, f"{brace}.label"), _points(svg, f"{brace}.label")
        assert after[0][0] == pytest.approx(before[0][0] + 10), key


# ---- the other ways a figure is written


def test_aggregation_figure_save_applies_overrides(tmp_path):
    demands = {"A": Line.from_inverse(10.0, -2.0), "B": Line.from_inverse(6.0, -0.5)}
    figure = demand_aggregation_figure(demands, price=4.0)
    label = next(
        layer.id
        for layer in figure.panels[0].snapshot().layers
        if layer.id.endswith(".label")
        and not layer.id.startswith("axes.")
        and hasattr(layer, "nudge")
    )
    figure.save(tmp_path / "plain" / "other.svg")
    _activate(tmp_path, f'[figure.market_demand.label."{label}"]\nleft = "10pt"\n')
    figure.save(tmp_path / "no" / "other.svg")
    figure.save(tmp_path / "yes" / "market_demand.svg")
    plain = _read(tmp_path / "plain" / "other.svg")
    assert _read(tmp_path / "no" / "other.svg") == plain
    assert _read(tmp_path / "yes" / "market_demand.svg") != plain


def test_visual_canvas_save_applies_overrides(tmp_path):
    frontier = ProductionPossibilitiesFrontier(10, 8, curvature=2)
    analysis = analyze_ppf(frontier, ((4, 3, "B"),))
    canvas = ppf_canvas(analysis)
    assert isinstance(canvas, Canvas)
    key = "ppf.point.0.label"
    for folder in ("plain", "no", "yes"):
        (tmp_path / folder).mkdir()
    canvas.save(tmp_path / "plain" / "other.svg")
    _activate(tmp_path, f'[figure.ppf_points.label."{key}"]\ntop = "15pt"\n')
    canvas.save(tmp_path / "no" / "other.svg")
    canvas.save(tmp_path / "yes" / "ppf_points.svg")
    plain = _read(tmp_path / "plain" / "other.svg")
    assert _read(tmp_path / "no" / "other.svg") == plain
    assert _points(_read(tmp_path / "yes" / "ppf_points.svg"), key)[0][1] == (
        pytest.approx(_points(plain, key)[0][1] - 15)
    )


# ---- label ids


@pytest.mark.parametrize("build", [_tax_figure, _ceiling_figure])
def test_label_ids_map_to_override_keys(build, tmp_path):
    """Every label id the figure reports is an override key, except axis marks."""
    figure = build()
    layers = _layers(figure)
    plain = _svg(build(), tmp_path / "plain" / "other.svg")
    axis_marks = []
    for label_id in figure.label_ids:
        layer = layers.get(label_id) or layers.get(label_id.removesuffix(".label"))
        if layer is None:  # an axis mark a later mark at the same value replaced
            assert ".mark." in label_id or ".label." in label_id, label_id
            continue
        if isinstance(layer, AxisMarkLayer):
            axis_marks.append(label_id)
            continue
        assert hasattr(layer, "nudge"), label_id  # a key mosaickit accepts
        _activate(tmp_path, f'[figure.f.label."{label_id}"]\ntop = "7pt"\n')
        figure.save(tmp_path / "t" / "f.svg")
        assert _read(tmp_path / "t" / "f.svg") != plain, label_id
    # axis marks are drawn with an id but take no nudge: mosaickit ignores the key
    assert axis_marks
    for label_id in axis_marks:
        _activate(tmp_path, f'[figure.f.label."{label_id}"]\ntop = "7pt"\n')
        figure.save(tmp_path / "t" / "f.svg")
        assert _read(tmp_path / "t" / "f.svg") == plain, label_id


def test_svg_label_elements_are_overridable_layer_ids(tmp_path):
    """Each label element in the SVG is a nudgeable layer id or a brace's ``<id>.label``."""
    figure = _tax_figure()
    svg = _svg(figure, tmp_path / "f.svg")
    ids = re.findall(r'<g id="([^"]+)"', svg)
    layers = _layers(figure)
    nudgeable = {key for key, layer in layers.items() if hasattr(layer, "nudge")}
    braces = {f"{key}.label" for key, l in layers.items() if isinstance(l, BraceLayer)}
    labels = [i for i in ids if i.endswith(".label") and i not in {"axes.x.label"}]
    assert labels
    for element in labels:
        assert element in nudgeable | braces, element
    assert any(isinstance(layer, RegionLabelLayer) for layer in layers.values())


# ---- decoupling


def test_principle_viz_does_not_parse_the_figure_table() -> None:
    root = Path(__file__).parents[1] / "src" / "principle_viz"
    for path in root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for name in ("figure_labels", "figure_overrides", "activate_figure_overrides"):
            assert name not in text, f"{path.name} reads [figure] itself"
