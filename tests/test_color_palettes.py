from __future__ import annotations

import pytest

from principle_viz.plot import (
    MarketFigure,
    PlotTheme,
    get_color_model,
    list_color_models,
)


def test_list_color_models_matches_econ_viz_builtin_names() -> None:
    names = set(list_color_models())
    assert {"default", "colorblind", "nord"}.issubset(names)
    assert "monochrome" in names



def test_get_color_model_resolves_known_palettes() -> None:
    default = get_color_model("default")
    colorblind = get_color_model("colorblind")
    nord = get_color_model("nord")
    monochrome = get_color_model("monochrome")

    assert default.name == "default"
    assert colorblind.name == "colorblind"
    assert nord.name == "nord"
    assert monochrome.name == "monochrome"



def test_plot_theme_from_palette() -> None:
    theme = PlotTheme.from_palette("nord")
    assert theme.color_model.name == "nord"
    assert theme.axis_color == "#2E3440"



def test_market_figure_accepts_palette_name() -> None:
    fig = MarketFigure(title="Palette", palette="colorblind")
    assert fig.theme.color_model.name == "colorblind"
    fig.close()



def test_unknown_palette_raises() -> None:
    with pytest.raises(ValueError):
        get_color_model("not-a-palette")
