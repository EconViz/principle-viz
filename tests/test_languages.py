"""Built-in figure text in English, Traditional and Simplified Chinese; the manual palette."""

import dataclasses

import pytest

from principle_viz.core.controls import (
    PriceControlScenario,
    PriceControlType,
    evaluate_price_control,
)
from principle_viz.core.line import Line
from principle_viz.i18n import LANGUAGES, labels, translate
from principle_viz.plot.figure import MarketFigure
from principle_viz.plot.label import Label
from principle_viz.visuals.theme import (
    BUILTIN_COLOR_MODELS,
    PlotTheme,
    get_color_model,
)

DEMAND = Line.from_inverse(10.0, -1.0)
SUPPLY = Line.from_inverse(2.0, 1.0)


def _ceiling(language: str, **figure_options) -> MarketFigure:
    result = evaluate_price_control(
        DEMAND,
        SUPPLY,
        PriceControlScenario(control_type=PriceControlType.CEILING, control_price=4.0),
    )
    figure = MarketFigure(
        x_max=12,
        y_max=12,
        title="Public Good",
        theme=PlotTheme(language=language),
        **figure_options,
    )
    figure.add_curves(DEMAND, SUPPLY, q_max=10)
    figure.add_price_control(result)
    return figure.finalize()


def _strings(value) -> set[str]:
    if isinstance(value, str):
        return {value}
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return set().union(
            *(_strings(getattr(value, f.name)) for f in dataclasses.fields(value))
        )
    if isinstance(value, (tuple, list)):
        return set().union(*(_strings(item) for item in value))
    return set()


def _texts(figure: MarketFigure) -> set[str]:
    return _strings(figure.scene.layers)


def test_the_manual_palette_is_built_in():
    manual = get_color_model("manual")

    assert "manual" in BUILTIN_COLOR_MODELS
    assert (manual.axis_color, manual.demand_color, manual.supply_color) == (
        "#1a1a1a",
        "#8c8c8c",
        "#1a1a1a",
    )
    assert PlotTheme.from_palette("manual").color_model is manual


@pytest.mark.parametrize(
    ("language", "shortage", "title"),
    [
        ("en", "Shortage", "Public Good"),
        ("zh-TW", "短缺", "公共財"),
        ("zh-CN", "短缺", "公共品"),
    ],
)
def test_built_in_text_is_drawn_in_the_theme_language(language, shortage, title):
    figure = _ceiling(language)

    assert shortage in _texts(figure)
    assert figure.canvas.spec.title == title


def test_text_the_user_sets_is_never_translated():
    figure = _ceiling("zh-TW")
    figure.configure_label("market.control.gap", Label(text="Shortage"))

    assert "Shortage" in _texts(figure)


def test_english_draws_the_original_text_and_unknown_languages_fail():
    assert labels("en") == {}
    assert translate(("Shortage",), "en") == ("Shortage",)
    with pytest.raises(ValueError, match="language"):
        PlotTheme(language="fr")


def test_every_language_translates_the_same_text():
    tables = [labels(language) for language in LANGUAGES if language != "en"]

    assert all(table.keys() == tables[0].keys() for table in tables)
    assert all(value.strip() for table in tables for value in table.values())
